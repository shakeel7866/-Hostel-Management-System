"""
HOSTEL MANAGEMENT SYSTEM — Mobile-Friendly Edition
Features:
  - Login Page (Admin login + Member registration with admin ID approval)
  - Mobile-friendly large touch buttons and fonts
  - Dashboard with Hostel View (room grid)
  - Mess Menu with image attachment
  - Students, Rooms, Bills, Complaints pages
  - Complaint: Solve button, Clear, Back, Skip buttons
  - All forms have Back/Clear/Skip buttons
  - Image viewer for receipts and mess menu

Run: python hostel_management_mobile.py
"""

import json
import os
import shutil
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from datetime import datetime
import hashlib

try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "hostel_data_mobile.json")
RECEIPTS_DIR = os.path.join(BASE_DIR, "receipts")
MESS_IMAGES_DIR = os.path.join(BASE_DIR, "mess_images")
os.makedirs(RECEIPTS_DIR, exist_ok=True)
os.makedirs(MESS_IMAGES_DIR, exist_ok=True)

ROOM_CHARGE_PER_MONTH = 5000

# ─── COLORS ───────────────────────────────────────────────────────────────────
BG_DARK        = "#1a1f35"
BG_MAIN        = "#f0f2f8"
BG_CARD        = "#ffffff"
ACCENT         = "#5b6cf9"
ACCENT_DARK    = "#4654d6"
ACCENT_LIGHT   = "#eef0ff"
TEXT_LIGHT     = "#e8eaf3"
TEXT_MUTED     = "#8890a8"
TEXT_DARK      = "#1e2235"
SUCCESS        = "#2bb673"
DANGER         = "#e5534b"
WARNING        = "#e0a93a"
NAV_BTN        = "#2a3050"

FF = "Segoe UI"  # Font family

# ─── HELPERS ──────────────────────────────────────────────────────────────────

def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def default_data():
    return {
        "admin": {"username": "admin", "password": hash_pw("admin123"), "admin_id": "HOSTEL2024"},
        "members": [],
        "students": [],
        "rooms": [],
        "mess": [],
        "mess_menu": [],          # list of {id, name, price, image, date}
        "bills": [],
        "complaints": [],
        "next_ids": {"student": 1, "mess": 1, "bill": 1, "complaint": 1, "menu": 1}
    }

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE) as f:
                data = json.load(f)
        except Exception:
            data = default_data()
    else:
        data = default_data()
    # back-compat
    data.setdefault("admin", {"username": "admin", "password": hash_pw("admin123"), "admin_id": "HOSTEL2024"})
    data.setdefault("members", [])
    data.setdefault("mess_menu", [])
    data["next_ids"].setdefault("menu", 1)
    for m in data.get("mess", []):
        m.setdefault("date", ""); m.setdefault("day", "")
        m.setdefault("receipt", None); m.setdefault("other_activity", 0)
        m.setdefault("other_activity_desc", "")
    for b in data.get("bills", []):
        b.setdefault("other_charges", 0); b.setdefault("receipt", None)
        b.setdefault("other_activity", 0); b.setdefault("other_activity_desc", "")
    for c in data.get("complaints", []):
        c.setdefault("solution", "")
    return data

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def get_next_id(data, key):
    nid = data["next_ids"][key]; data["next_ids"][key] += 1; return nid

def find_student(data, sid):
    for s in data["students"]:
        if s["id"] == sid: return s
    return None

def find_room(data, room_no):
    for r in data["rooms"]:
        if r["room_no"] == room_no: return r
    return None

def resolve_student(data, text):
    text = text.strip()
    if not text: return None, "Please enter a Student ID or Name."
    digits = ""
    for ch in text:
        if ch.isdigit(): digits += ch
        else: break
    if digits:
        s = find_student(data, int(digits))
        if s: return s, None
        return None, f"No student with ID {digits}."
    matches = [s for s in data["students"] if text.lower() in s["name"].lower()]
    if len(matches) == 1: return matches[0], None
    if len(matches) > 1:
        return None, "Multiple matches: " + ", ".join(f"#{m['id']} {m['name']}" for m in matches)
    return None, f"No student matching '{text}'."

def parse_date_and_day(text):
    text = text.strip()
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y"):
        try:
            dt = datetime.strptime(text, fmt)
            return dt.strftime("%Y-%m-%d"), dt.strftime("%A")
        except ValueError: continue
    return text, ""

def copy_image(src, folder, prefix):
    ext = os.path.splitext(src)[1]
    name = f"{prefix}_{datetime.now().strftime('%Y%m%d%H%M%S')}{ext}"
    dest = os.path.join(folder, name)
    shutil.copy(src, dest)
    return dest

def show_image_window(parent, path, title="Image"):
    if not path or not os.path.exists(path):
        messagebox.showinfo("No Image", "No image attached.", parent=parent); return
    win = tk.Toplevel(parent); win.title(title); win.configure(bg=BG_CARD)
    if not PIL_AVAILABLE:
        tk.Label(win, text="Install pillow:\npip install pillow", bg=BG_CARD, fg=TEXT_DARK,
                  font=(FF, 12)).pack(padx=30, pady=30)
        tk.Label(win, text=path, bg=BG_CARD, fg=TEXT_MUTED, font=(FF, 9), wraplength=340).pack(padx=20, pady=6)
        return
    try:
        img = Image.open(path)
        ratio = min(500/img.width, 650/img.height, 1.0)
        img = img.resize((max(1,int(img.width*ratio)), max(1,int(img.height*ratio))))
        tk_img = ImageTk.PhotoImage(img)
        lbl = tk.Label(win, image=tk_img, bg=BG_CARD); lbl.image = tk_img; lbl.pack(padx=12, pady=12)
    except Exception as e:
        tk.Label(win, text=f"Cannot open image:\n{e}", bg=BG_CARD, fg=DANGER, font=(FF,10)).pack(padx=20, pady=20)

# ─── REUSABLE WIDGETS ─────────────────────────────────────────────────────────

def mobtn(parent, text, cmd, color=ACCENT, fg="white", w=None, h=None, fs=12):
    """Mobile-sized button."""
    kw = dict(font=(FF, fs, "bold"), bg=color, fg=fg, activebackground=color,
              activeforeground=fg, bd=0, relief="flat", cursor="hand2",
              padx=14, pady=10, command=cmd)
    if w: kw["width"] = w
    if h: kw["height"] = h
    b = tk.Button(parent, text=text, **kw); return b

def moentry(parent, placeholder="", width=26, show=None):
    e = tk.Entry(parent, font=(FF, 12), width=width, relief="solid", bd=2,
                  highlightthickness=1, highlightcolor=ACCENT, show=show)
    if placeholder:
        e.insert(0, placeholder)
        e.config(fg=TEXT_MUTED)
        def on_focus_in(_):
            if e.get() == placeholder: e.delete(0, "end"); e.config(fg=TEXT_DARK)
        def on_focus_out(_):
            if not e.get(): e.insert(0, placeholder); e.config(fg=TEXT_MUTED)
        e.bind("<FocusIn>", on_focus_in); e.bind("<FocusOut>", on_focus_out)
    return e

def molabel(parent, text, size=12, bold=False, color=TEXT_DARK, bg=BG_CARD):
    fw = "bold" if bold else "normal"
    return tk.Label(parent, text=text, font=(FF, size, fw), fg=color, bg=bg)

def section_title(parent, text):
    f = tk.Frame(parent, bg=BG_CARD)
    f.pack(fill="x", padx=0, pady=(12, 4))
    tk.Label(f, text=text, font=(FF, 13, "bold"), fg=ACCENT, bg=BG_CARD).pack(side="left")
    tk.Frame(f, bg="#e2e5ee", height=1).pack(side="left", fill="x", expand=True, padx=(8,0), pady=6)
    return f

def make_scrollable(parent, bg=BG_CARD):
    """Returns (outer_frame, inner_frame, canvas) — pack outer into parent."""
    outer = tk.Frame(parent, bg=bg)
    canvas = tk.Canvas(outer, bg=bg, highlightthickness=0)
    sb = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=sb.set)
    sb.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)
    inner = tk.Frame(canvas, bg=bg)
    wid = canvas.create_window((0, 0), window=inner, anchor="nw")
    inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.bind("<Configure>", lambda e: canvas.itemconfig(wid, width=e.width))
    canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
    return outer, inner, canvas

def make_table(parent, columns, height=8):
    style = ttk.Style()
    style.configure("M.Treeview", font=(FF, 11), rowheight=32,
                     background="white", fieldbackground="white")
    style.configure("M.Treeview.Heading", font=(FF, 11, "bold"),
                     background="#eef0f8", foreground=TEXT_DARK)
    style.map("M.Treeview", background=[("selected", "#dde2fb")])
    container = tk.Frame(parent, bg=BG_CARD)
    tree = ttk.Treeview(container, columns=columns, show="headings", height=height, style="M.Treeview")
    for c in columns:
        tree.heading(c, text=c); tree.column(c, width=140, anchor="w")
    vsb = ttk.Scrollbar(container, orient="vertical", command=tree.yview)
    hsb = ttk.Scrollbar(container, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    tree.grid(row=0, column=0, sticky="nsew")
    vsb.grid(row=0, column=1, sticky="ns"); hsb.grid(row=1, column=0, sticky="ew")
    container.grid_rowconfigure(0, weight=1); container.grid_columnconfigure(0, weight=1)
    return container, tree

# ─── TOP NAV BAR ──────────────────────────────────────────────────────────────

class TopBar(tk.Frame):
    def __init__(self, parent, title, back_cmd=None, **kw):
        super().__init__(parent, bg=BG_DARK, height=56, **kw)
        self.pack_propagate(False)
        if back_cmd:
            tk.Button(self, text="← Back", bg=BG_DARK, fg="white",
                       font=(FF,11), bd=0, relief="flat", cursor="hand2",
                       activebackground=NAV_BTN, command=back_cmd, padx=12, pady=8
                       ).pack(side="left", padx=(4,0))
        tk.Label(self, text=title, bg=BG_DARK, fg="white",
                  font=(FF, 14, "bold")).pack(side="left", padx=12)

# ═══════════════════════════════════════════════════════════════════════════════
#  MAIN APP
# ═══════════════════════════════════════════════════════════════════════════════

class HostelApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Hostel Management System")
        self.geometry("480x820")
        self.minsize(420, 600)
        self.configure(bg=BG_MAIN)
        self.resizable(True, True)

        self.data = load_data()
        self.current_user = None   # {"role": "admin"/"member", "username": ...}

        self._show_login()

    # ──────────────────────────────────────────────────────── CONTENT SWAP ────

    def _clear(self):
        for w in self.winfo_children(): w.destroy()

    # ═══════════════════════════════════════════════════════════════════════════
    #  LOGIN & REGISTER
    # ═══════════════════════════════════════════════════════════════════════════

    def _show_login(self):
        self._clear()
        self.current_user = None

        root = tk.Frame(self, bg=BG_MAIN); root.pack(fill="both", expand=True)

        # Header
        hdr = tk.Frame(root, bg=BG_DARK, height=140); hdr.pack(fill="x"); hdr.pack_propagate(False)
        tk.Label(hdr, text="🏠", bg=BG_DARK, font=(FF, 36)).pack(pady=(20,0))
        tk.Label(hdr, text="HOSTEL MS", bg=BG_DARK, fg="white", font=(FF, 18, "bold")).pack()
        tk.Label(hdr, text="Management System", bg=BG_DARK, fg=TEXT_MUTED, font=(FF, 10)).pack()

        card = tk.Frame(root, bg=BG_CARD, highlightbackground="#dde2f0", highlightthickness=1)
        card.pack(fill="both", expand=True, padx=20, pady=20)
        card.pack_propagate(False)

        outer, inner, _ = make_scrollable(card)
        outer.pack(fill="both", expand=True)

        tk.Label(inner, text="Sign In", bg=BG_CARD, fg=TEXT_DARK, font=(FF, 16, "bold")).pack(pady=(24,4))

        # Role tabs
        tab_f = tk.Frame(inner, bg="#eef0f8", bd=0); tab_f.pack(fill="x", padx=20, pady=(8,16))
        self._login_role = tk.StringVar(value="admin")
        for val, lbl in [("admin","Admin"), ("member","Member")]:
            tk.Radiobutton(tab_f, text=lbl, variable=self._login_role, value=val,
                           bg="#eef0f8", fg=TEXT_DARK, font=(FF,12), activebackground="#eef0f8",
                           selectcolor=ACCENT, indicatoron=0, padx=18, pady=6,
                           relief="flat").pack(side="left", expand=True, fill="x")

        tk.Label(inner, text="Username", bg=BG_CARD, fg=TEXT_MUTED, font=(FF,10), anchor="w").pack(fill="x", padx=24, pady=(4,2))
        uname_e = moentry(inner, width=30); uname_e.pack(padx=24, pady=(0,10))

        tk.Label(inner, text="Password", bg=BG_CARD, fg=TEXT_MUTED, font=(FF,10), anchor="w").pack(fill="x", padx=24, pady=(4,2))
        pw_e = moentry(inner, width=30, show="•"); pw_e.pack(padx=24, pady=(0,16))

        msg_var = tk.StringVar()
        tk.Label(inner, textvariable=msg_var, bg=BG_CARD, fg=DANGER, font=(FF,10), wraplength=340).pack()

        def do_login():
            role = self._login_role.get()
            u = uname_e.get().strip(); p = pw_e.get().strip()
            if not u or not p: msg_var.set("Enter username and password."); return
            if role == "admin":
                adm = self.data["admin"]
                if u == adm["username"] and hash_pw(p) == adm["password"]:
                    self.current_user = {"role": "admin", "username": u}
                    self._show_main()
                else:
                    msg_var.set("❌ Invalid admin credentials.")
            else:
                mem = next((m for m in self.data["members"] if m["username"] == u and m["password"] == hash_pw(p)), None)
                if mem:
                    self.current_user = {"role": "member", "username": u}
                    self._show_main()
                else:
                    msg_var.set("❌ Invalid member credentials.")

        mobtn(inner, "Sign In", do_login, ACCENT, w=28, fs=13).pack(pady=(8,4))

        tk.Label(inner, text="─── or ───", bg=BG_CARD, fg=TEXT_MUTED, font=(FF,9)).pack(pady=6)

        mobtn(inner, "Create Member Account", self._show_register, color="#6c757d", w=28, fs=11).pack(pady=(0,20))

    # ─── REGISTER ─────────────────────────────────────────────────────────────

    def _show_register(self):
        self._clear()
        root = tk.Frame(self, bg=BG_MAIN); root.pack(fill="both", expand=True)
        TopBar(root, "Create Account", back_cmd=self._show_login).pack(fill="x")

        card = tk.Frame(root, bg=BG_CARD); card.pack(fill="both", expand=True, padx=16, pady=16)
        outer, inner, _ = make_scrollable(card); outer.pack(fill="both", expand=True)

        tk.Label(inner, text="New Member Registration", bg=BG_CARD, fg=TEXT_DARK,
                  font=(FF,15,"bold")).pack(pady=(20,4))
        tk.Label(inner, text="Requires Admin ID for approval", bg=BG_CARD, fg=TEXT_MUTED, font=(FF,10)).pack(pady=(0,12))

        fields = {}
        for key, label in [("name","Full Name"),("username","Username"),
                            ("password","Password"),("confirm","Confirm Password"),
                            ("admin_id","Admin ID (get from admin)")]:
            tk.Label(inner, text=label, bg=BG_CARD, fg=TEXT_MUTED, font=(FF,10), anchor="w").pack(fill="x", padx=24, pady=(6,2))
            show = "•" if "assword" in label or "onfirm" in label else None
            e = moentry(inner, width=30, show=show); e.pack(padx=24, pady=(0,2))
            fields[key] = e

        msg_var = tk.StringVar()
        tk.Label(inner, textvariable=msg_var, bg=BG_CARD, fg=DANGER, font=(FF,10), wraplength=340).pack(pady=4)

        def do_register():
            vals = {k: v.get().strip() for k, v in fields.items()}
            if not all(vals.values()): msg_var.set("All fields are required."); return
            if vals["password"] != vals["confirm"]: msg_var.set("Passwords do not match."); return
            if vals["admin_id"] != self.data["admin"]["admin_id"]:
                msg_var.set("❌ Invalid Admin ID."); return
            if any(m["username"] == vals["username"] for m in self.data["members"]):
                msg_var.set("Username already taken."); return
            self.data["members"].append({
                "username": vals["username"],
                "name": vals["name"],
                "password": hash_pw(vals["password"])
            })
            save_data(self.data)
            messagebox.showinfo("Success", f"Account created for {vals['name']}!\nYou can now sign in as Member.")
            self._show_login()

        mobtn(inner, "Create Account", do_register, SUCCESS, w=28, fs=13).pack(pady=(10,6))
        mobtn(inner, "← Back to Login", self._show_login, "#6c757d", w=28, fs=11).pack(pady=(0,24))

    # ═══════════════════════════════════════════════════════════════════════════
    #  MAIN SCREEN (after login)
    # ═══════════════════════════════════════════════════════════════════════════

    def _show_main(self):
        self._clear()
        root = tk.Frame(self, bg=BG_MAIN); root.pack(fill="both", expand=True)

        # ── Top bar ──────────────────────────────────────────────────────────
        hdr = tk.Frame(root, bg=BG_DARK, height=58)
        hdr.pack(fill="x"); hdr.pack_propagate(False)
        tk.Label(hdr, text="🏠 HOSTEL MS", bg=BG_DARK, fg="white",
                  font=(FF, 15, "bold")).pack(side="left", padx=16, pady=10)
        role_lbl = f"👤 {self.current_user['username']} ({self.current_user['role'].title()})"
        tk.Label(hdr, text=role_lbl, bg=BG_DARK, fg=TEXT_MUTED,
                  font=(FF, 9)).pack(side="left", pady=10)
        mobtn(hdr, "Logout", self._show_login, "#e5534b", fs=9).pack(
            side="right", padx=12, pady=10)

        is_admin = self.current_user["role"] == "admin"

        # ── Proper scrollable canvas (fixes tile visibility) ──────────────────
        canvas = tk.Canvas(root, bg=BG_MAIN, highlightthickness=0)
        vsb    = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        inner = tk.Frame(canvas, bg=BG_MAIN)
        win_id = canvas.create_window((0, 0), window=inner, anchor="nw")

        def _on_inner_configure(e):
            canvas.configure(scrollregion=canvas.bbox("all"))
        def _on_canvas_configure(e):
            canvas.itemconfig(win_id, width=e.width)
        def _on_mousewheel(e):
            canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")

        inner.bind("<Configure>",  _on_inner_configure)
        canvas.bind("<Configure>", _on_canvas_configure)
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # ── Stats row ─────────────────────────────────────────────────────────
        total_stu  = len(self.data["students"])
        total_occ  = sum(len(r["occupants"]) for r in self.data["rooms"])
        total_cap  = sum(r["capacity"]        for r in self.data["rooms"])
        pending_c  = sum(1 for c in self.data["complaints"] if c["status"] == "Pending")
        pending_b  = sum(1 for b in self.data["bills"]      if not b["paid"])

        stats_f = tk.Frame(inner, bg=BG_MAIN)
        stats_f.pack(fill="x", padx=14, pady=(14, 8))

        for i, (val, lbl, col) in enumerate([
            (total_stu,                "Students",   ACCENT),
            (f"{total_occ}/{total_cap}", "Beds",     SUCCESS),
            (pending_c,                "Complaints", WARNING),
            (pending_b,                "Bills Due",  DANGER),
        ]):
            stats_f.grid_columnconfigure(i, weight=1)
            card = tk.Frame(stats_f, bg=BG_CARD,
                             highlightbackground="#e2e5ee", highlightthickness=1)
            card.grid(row=0, column=i, padx=4, sticky="nsew")
            tk.Frame(card, bg=col, width=4).pack(side="left", fill="y")
            ins = tk.Frame(card, bg=BG_CARD)
            ins.pack(side="left", fill="both", expand=True, padx=8, pady=8)
            tk.Label(ins, text=str(val),  bg=BG_CARD, fg=TEXT_DARK,
                      font=(FF, 14, "bold")).pack(anchor="w")
            tk.Label(ins, text=lbl,       bg=BG_CARD, fg=TEXT_MUTED,
                      font=(FF, 8)).pack(anchor="w")

        # ── Navigation label ──────────────────────────────────────────────────
        tk.Label(inner, text="Navigation", bg=BG_MAIN, fg=TEXT_MUTED,
                  font=(FF, 10), anchor="w").pack(fill="x", padx=20, pady=(14, 4))

        # ── Navigation tiles (packed as rows of 2) ────────────────────────────
        tiles_data = [
            ("🏨 Hostel View",    self._page_hostel_view,  ACCENT),
            ("🍽️ Mess Menu",      self._page_mess_menu,    "#9b59b6"),
            ("🧑‍🎓 Students",       self._page_students,     "#2980b9"),
            ("🛏️ Rooms",          self._page_rooms,         "#27ae60"),
            ("🍽️ Mess Charges",   self._page_mess,          "#e67e22"),
            ("💰 Bills",          self._page_bills,         "#c0392b"),
            ("📝 Complaints",     self._page_complaints,   "#8e44ad"),
        ]
        if is_admin:
            tiles_data.append(("⚙️ Admin Settings", self._page_admin, "#546e7a"))

        # Build rows of 2 tiles each
        tiles_outer = tk.Frame(inner, bg=BG_MAIN)
        tiles_outer.pack(fill="x", padx=14, pady=(0, 20))

        def _make_tile(parent, label, cmd, col):
            tile = tk.Frame(parent, bg=col, cursor="hand2", height=72)
            tile.pack_propagate(False)
            lbl_w = tk.Label(tile, text=label, bg=col, fg="white",
                              font=(FF, 12, "bold"), wraplength=180, justify="center")
            lbl_w.place(relx=0.5, rely=0.5, anchor="center")
            for w in (tile, lbl_w):
                w.bind("<Button-1>", lambda e, fn=cmd: fn())
            return tile

        for pair_start in range(0, len(tiles_data), 2):
            row_f = tk.Frame(tiles_outer, bg=BG_MAIN)
            row_f.pack(fill="x", pady=5)
            pair = tiles_data[pair_start:pair_start + 2]
            for label, cmd, col in pair:
                t = _make_tile(row_f, label, cmd, col)
                t.pack(side="left", fill="x", expand=True, padx=4)

    # ═══════════════════════════════════════════════════════════════════════════
    #  HOSTEL VIEW (room grid)
    # ═══════════════════════════════════════════════════════════════════════════

    def _page_hostel_view(self):
        self._clear()
        root = tk.Frame(self, bg=BG_MAIN); root.pack(fill="both", expand=True)
        TopBar(root, "🏨 Hostel View", back_cmd=self._show_main).pack(fill="x")

        outer, inner, _ = make_scrollable(root, BG_MAIN)
        outer.pack(fill="both", expand=True)

        tk.Label(inner, text="Room Occupancy Grid", bg=BG_MAIN, fg=TEXT_DARK,
                  font=(FF,13,"bold")).pack(pady=(14,6), padx=16, anchor="w")

        if not self.data["rooms"]:
            tk.Label(inner, text="No rooms added yet.", bg=BG_MAIN, fg=TEXT_MUTED, font=(FF,12)).pack(pady=40)
            return

        grid_f = tk.Frame(inner, bg=BG_MAIN); grid_f.pack(fill="x", padx=14, pady=4)
        grid_f.grid_columnconfigure(0, weight=1); grid_f.grid_columnconfigure(1, weight=1)

        for i, room in enumerate(self.data["rooms"]):
            r, c = divmod(i, 2)
            occ = len(room["occupants"]); cap = room["capacity"]; free = cap - occ
            col = SUCCESS if free > 0 else DANGER
            card = tk.Frame(grid_f, bg=BG_CARD, highlightbackground=col, highlightthickness=2)
            card.grid(row=r, column=c, padx=6, pady=6, sticky="nsew", ipadx=6, ipady=6)

            bar = tk.Frame(card, bg=col, height=4); bar.pack(fill="x")
            tk.Label(card, text=f"Room {room['room_no']}", bg=BG_CARD, fg=TEXT_DARK, font=(FF,13,"bold")).pack(pady=(8,2))
            tk.Label(card, text=f"{'Available' if free > 0 else 'Full'} — {occ}/{cap} beds",
                      bg=BG_CARD, fg=col, font=(FF,10)).pack()

            names = [find_student(self.data, sid)["name"] for sid in room["occupants"] if find_student(self.data, sid)]
            for n in names:
                tk.Label(card, text=f"• {n}", bg=BG_CARD, fg=TEXT_DARK, font=(FF,9), anchor="w").pack(fill="x", padx=10)
            if not names:
                tk.Label(card, text="(empty)", bg=BG_CARD, fg=TEXT_MUTED, font=(FF,9)).pack()
            tk.Label(card, text="", bg=BG_CARD).pack(pady=2)

        # Legend
        leg = tk.Frame(inner, bg=BG_MAIN); leg.pack(pady=(8,16), padx=16, anchor="w")
        for col, lbl in [(SUCCESS,"Available"), (DANGER,"Full")]:
            tk.Frame(leg, bg=col, width=16, height=16).pack(side="left")
            tk.Label(leg, text=f" {lbl}   ", bg=BG_MAIN, fg=TEXT_DARK, font=(FF,10)).pack(side="left")

    # ═══════════════════════════════════════════════════════════════════════════
    #  MESS MENU (with image)
    # ═══════════════════════════════════════════════════════════════════════════

    def _page_mess_menu(self):
        self._clear()
        root = tk.Frame(self, bg=BG_MAIN); root.pack(fill="both", expand=True)
        TopBar(root, "🍽️ Mess Menu", back_cmd=self._show_main).pack(fill="x")

        outer, inner, _ = make_scrollable(root, BG_MAIN)
        outer.pack(fill="both", expand=True)

        is_admin = self.current_user["role"] == "admin"

        if is_admin:
            section_title(inner, "Add Menu Item")

            f = tk.Frame(inner, bg=BG_CARD); f.pack(fill="x", padx=14, pady=4)
            tk.Label(f, text="Item Name", bg=BG_CARD, fg=TEXT_MUTED, font=(FF,10), anchor="w").pack(fill="x", padx=14, pady=(10,2))
            name_e = moentry(f, width=30); name_e.pack(padx=14, pady=(0,4))
            tk.Label(f, text="Price (Rs)", bg=BG_CARD, fg=TEXT_MUTED, font=(FF,10), anchor="w").pack(fill="x", padx=14, pady=(4,2))
            price_e = moentry(f, width=30); price_e.pack(padx=14, pady=(0,4))
            tk.Label(f, text="Date", bg=BG_CARD, fg=TEXT_MUTED, font=(FF,10), anchor="w").pack(fill="x", padx=14, pady=(4,2))
            date_e = moentry(f, width=30); date_e.pack(padx=14, pady=(0,4))
            date_e.insert(0, datetime.now().strftime("%Y-%m-%d"))

            img_path_var = tk.StringVar(value="")
            img_lbl = tk.Label(f, text="No image selected", bg=BG_CARD, fg=TEXT_MUTED, font=(FF,9), anchor="w")
            img_lbl.pack(fill="x", padx=14)

            def pick_image():
                path = filedialog.askopenfilename(
                    parent=self, title="Select Menu Image",
                    filetypes=[("Images","*.png *.jpg *.jpeg *.gif *.bmp *.webp"), ("All","*.*")])
                if path:
                    dest = copy_image(path, MESS_IMAGES_DIR, "menu")
                    img_path_var.set(dest)
                    img_lbl.config(text=f"✅ {os.path.basename(dest)}", fg=SUCCESS)

            btn_row_m = tk.Frame(f, bg=BG_CARD); btn_row_m.pack(fill="x", padx=14, pady=6)
            mobtn(btn_row_m, "📷 Attach Image", pick_image, "#6c757d", fs=10).pack(side="left", padx=(0,6))

            def add_menu_item():
                n = name_e.get().strip(); p = price_e.get().strip(); d = date_e.get().strip()
                if not n or not p: messagebox.showwarning("Missing", "Enter name and price.", parent=self); return
                try: price = float(p)
                except: messagebox.showwarning("Invalid", "Price must be a number."); return
                mid = get_next_id(self.data, "menu")
                self.data["mess_menu"].append({
                    "id": mid, "name": n, "price": price,
                    "date": d, "image": img_path_var.get() or None
                })
                save_data(self.data)
                messagebox.showinfo("Added", f"'{n}' added to menu.")
                self._page_mess_menu()

            def clear_form():
                name_e.delete(0,"end"); price_e.delete(0,"end")
                img_path_var.set(""); img_lbl.config(text="No image selected", fg=TEXT_MUTED)

            action_f = tk.Frame(f, bg=BG_CARD); action_f.pack(fill="x", padx=14, pady=(4,14))
            mobtn(action_f, "✅ Add Item", add_menu_item, SUCCESS, fs=11).pack(side="left", padx=(0,6))
            mobtn(action_f, "🗑 Clear", clear_form, "#6c757d", fs=11).pack(side="left")

        section_title(inner, "Today's Menu")

        menus = sorted(self.data["mess_menu"], key=lambda x: x.get("date",""), reverse=True)
        if not menus:
            tk.Label(inner, text="No menu items yet.", bg=BG_MAIN, fg=TEXT_MUTED, font=(FF,12)).pack(pady=20)
        else:
            for item in menus:
                card = tk.Frame(inner, bg=BG_CARD, highlightbackground="#e2e5ee", highlightthickness=1)
                card.pack(fill="x", padx=14, pady=5)
                hf = tk.Frame(card, bg=BG_CARD); hf.pack(fill="x", padx=12, pady=(10,4))
                tk.Label(hf, text=item["name"], bg=BG_CARD, fg=TEXT_DARK, font=(FF,13,"bold")).pack(side="left")
                tk.Label(hf, text=f"Rs {item['price']:,.0f}", bg=BG_CARD, fg=SUCCESS, font=(FF,12,"bold")).pack(side="right")
                tk.Label(card, text=f"📅 {item.get('date','')}", bg=BG_CARD, fg=TEXT_MUTED, font=(FF,9)).pack(padx=12, anchor="w")
                btn_r = tk.Frame(card, bg=BG_CARD); btn_r.pack(fill="x", padx=12, pady=(4,10))
                if item.get("image"):
                    mobtn(btn_r, "🖼 View Image", lambda i=item: show_image_window(self, i["image"], i["name"]), ACCENT, fs=9).pack(side="left", padx=(0,6))
                if is_admin:
                    def del_item(iid=item["id"]):
                        if messagebox.askyesno("Delete", "Remove this menu item?", parent=self):
                            self.data["mess_menu"] = [m for m in self.data["mess_menu"] if m["id"] != iid]
                            save_data(self.data); self._page_mess_menu()
                    mobtn(btn_r, "🗑 Delete", del_item, DANGER, fs=9).pack(side="left")

    # ═══════════════════════════════════════════════════════════════════════════
    #  STUDENTS
    # ═══════════════════════════════════════════════════════════════════════════

    def _page_students(self):
        self._clear()
        root = tk.Frame(self, bg=BG_MAIN); root.pack(fill="both", expand=True)
        TopBar(root, "🧑‍🎓 Students", back_cmd=self._show_main).pack(fill="x")

        outer, inner, _ = make_scrollable(root, BG_MAIN)
        outer.pack(fill="both", expand=True)

        is_admin = self.current_user["role"] == "admin"

        if is_admin:
            section_title(inner, "Add Student")
            f = tk.Frame(inner, bg=BG_CARD); f.pack(fill="x", padx=14, pady=4)
            entries = {}
            for key, lbl in [("name","Full Name"),("cnic","CNIC / ID No."),
                               ("contact","Contact Number"),("dept","Department"),("sem","Semester")]:
                tk.Label(f, text=lbl, bg=BG_CARD, fg=TEXT_MUTED, font=(FF,10), anchor="w").pack(fill="x", padx=14, pady=(8,2))
                e = moentry(f, width=30); e.pack(padx=14, pady=(0,2)); entries[key] = e

            def add_student():
                v = {k: e.get().strip() for k, e in entries.items()}
                if not all(v.values()): messagebox.showwarning("Missing", "Fill all fields.", parent=self); return
                sid = get_next_id(self.data, "student")
                self.data["students"].append({
                    "id": sid, "name": v["name"], "cnic": v["cnic"],
                    "contact": v["contact"], "dept": v["dept"], "semester": v["sem"], "room_no": None
                })
                save_data(self.data)
                messagebox.showinfo("Added", f"Student added — ID #{sid}")
                self._page_students()

            def clear_student():
                for e in entries.values(): e.delete(0,"end")

            ar = tk.Frame(f, bg=BG_CARD); ar.pack(fill="x", padx=14, pady=(6,14))
            mobtn(ar, "✅ Add Student", add_student, SUCCESS, fs=11).pack(side="left", padx=(0,8))
            mobtn(ar, "🗑 Clear", clear_student, "#6c757d", fs=11).pack(side="left")

        section_title(inner, f"All Students ({len(self.data['students'])})")
        if not self.data["students"]:
            tk.Label(inner, text="No students yet.", bg=BG_MAIN, fg=TEXT_MUTED, font=(FF,12)).pack(pady=16)
        for s in self.data["students"]:
            card = tk.Frame(inner, bg=BG_CARD, highlightbackground="#e2e5ee", highlightthickness=1)
            card.pack(fill="x", padx=14, pady=4)
            hf = tk.Frame(card, bg=BG_CARD); hf.pack(fill="x", padx=12, pady=(10,2))
            tk.Label(hf, text=f"#{s['id']} — {s['name']}", bg=BG_CARD, fg=TEXT_DARK, font=(FF,13,"bold")).pack(side="left")
            room_tag = s["room_no"] or "No Room"
            tag_col = ACCENT if s["room_no"] else TEXT_MUTED
            tk.Label(hf, text=f"🛏 {room_tag}", bg=BG_CARD, fg=tag_col, font=(FF,10)).pack(side="right")
            detail = f"CNIC: {s['cnic']}   |   {s['dept']} — Sem {s['semester']}   |   📞 {s['contact']}"
            tk.Label(card, text=detail, bg=BG_CARD, fg=TEXT_MUTED, font=(FF,9), anchor="w", wraplength=400).pack(fill="x", padx=12, pady=(0,10))

    # ═══════════════════════════════════════════════════════════════════════════
    #  ROOMS
    # ═══════════════════════════════════════════════════════════════════════════

    def _page_rooms(self):
        self._clear()
        root = tk.Frame(self, bg=BG_MAIN); root.pack(fill="both", expand=True)
        TopBar(root, "🛏️ Rooms", back_cmd=self._show_main).pack(fill="x")

        outer, inner, _ = make_scrollable(root, BG_MAIN)
        outer.pack(fill="both", expand=True)

        is_admin = self.current_user["role"] == "admin"

        if is_admin:
            section_title(inner, "Add Room")
            f = tk.Frame(inner, bg=BG_CARD); f.pack(fill="x", padx=14, pady=4)
            tk.Label(f, text="Room Number", bg=BG_CARD, fg=TEXT_MUTED, font=(FF,10), anchor="w").pack(fill="x", padx=14, pady=(10,2))
            room_e = moentry(f, width=26); room_e.pack(padx=14, pady=(0,4))
            tk.Label(f, text="Capacity (beds)", bg=BG_CARD, fg=TEXT_MUTED, font=(FF,10), anchor="w").pack(fill="x", padx=14, pady=(4,2))
            cap_e = moentry(f, width=26); cap_e.pack(padx=14, pady=(0,4))

            def add_room():
                rno = room_e.get().strip(); cap = cap_e.get().strip()
                if not rno or not cap.isdigit(): messagebox.showwarning("Invalid", "Enter room number and numeric capacity."); return
                if find_room(self.data, rno): messagebox.showerror("Duplicate", f"Room {rno} already exists."); return
                self.data["rooms"].append({"room_no": rno, "capacity": int(cap), "occupants": []})
                save_data(self.data)
                messagebox.showinfo("Added", f"Room {rno} added.")
                self._page_rooms()

            ar = tk.Frame(f, bg=BG_CARD); ar.pack(fill="x", padx=14, pady=(4,6))
            mobtn(ar, "✅ Add Room", add_room, SUCCESS, fs=11).pack(side="left", padx=(0,8))
            mobtn(ar, "🗑 Clear", lambda: [room_e.delete(0,"end"), cap_e.delete(0,"end")], "#6c757d", fs=11).pack(side="left")

            section_title(inner, "Assign Student to Room")
            af = tk.Frame(inner, bg=BG_CARD); af.pack(fill="x", padx=14, pady=4)
            tk.Label(af, text="Student ID or Name", bg=BG_CARD, fg=TEXT_MUTED, font=(FF,10), anchor="w").pack(fill="x", padx=14, pady=(10,2))
            asid_e = moentry(af, width=26); asid_e.pack(padx=14, pady=(0,4))
            tk.Label(af, text="Room Number", bg=BG_CARD, fg=TEXT_MUTED, font=(FF,10), anchor="w").pack(fill="x", padx=14, pady=(4,2))
            arno_e = moentry(af, width=26); arno_e.pack(padx=14, pady=(0,4))

            def assign():
                s, err = resolve_student(self.data, asid_e.get())
                if not s: messagebox.showerror("Not Found", err); return
                rm = find_room(self.data, arno_e.get().strip())
                if not rm: messagebox.showerror("Not Found", "Room not found."); return
                if s["room_no"]: messagebox.showerror("Already Assigned", f"Already in room {s['room_no']}."); return
                if len(rm["occupants"]) >= rm["capacity"]: messagebox.showerror("Full", "Room is full."); return
                rm["occupants"].append(s["id"]); s["room_no"] = rm["room_no"]
                save_data(self.data)
                messagebox.showinfo("Done", f"{s['name']} assigned to Room {rm['room_no']}.")
                self._page_rooms()

            ar2 = tk.Frame(af, bg=BG_CARD); ar2.pack(fill="x", padx=14, pady=(4,14))
            mobtn(ar2, "✅ Assign", assign, ACCENT, fs=11).pack(side="left", padx=(0,8))
            mobtn(ar2, "🗑 Clear", lambda: [asid_e.delete(0,"end"), arno_e.delete(0,"end")], "#6c757d", fs=11).pack(side="left")

        section_title(inner, f"Rooms ({len(self.data['rooms'])})")
        for room in self.data["rooms"]:
            occ = len(room["occupants"]); free = room["capacity"] - occ
            col = SUCCESS if free > 0 else DANGER
            card = tk.Frame(inner, bg=BG_CARD, highlightbackground=col, highlightthickness=2)
            card.pack(fill="x", padx=14, pady=5)
            hf = tk.Frame(card, bg=BG_CARD); hf.pack(fill="x", padx=12, pady=(10,4))
            tk.Label(hf, text=f"Room {room['room_no']}", bg=BG_CARD, fg=TEXT_DARK, font=(FF,13,"bold")).pack(side="left")
            tk.Label(hf, text=f"{occ}/{room['capacity']} beds  {'✅' if free>0 else '🔴 Full'}",
                      bg=BG_CARD, fg=col, font=(FF,11)).pack(side="right")
            names = [find_student(self.data, s)["name"] for s in room["occupants"] if find_student(self.data, s)]
            tk.Label(card, text=", ".join(names) if names else "(empty)", bg=BG_CARD,
                      fg=TEXT_MUTED, font=(FF,9), anchor="w", wraplength=380).pack(fill="x", padx=12, pady=(0,10))

    # ═══════════════════════════════════════════════════════════════════════════
    #  MESS CHARGES
    # ═══════════════════════════════════════════════════════════════════════════

    def _page_mess(self):
        self._clear()
        root = tk.Frame(self, bg=BG_MAIN); root.pack(fill="both", expand=True)
        TopBar(root, "🍽️ Mess Charges", back_cmd=self._show_main).pack(fill="x")

        outer, inner, _ = make_scrollable(root, BG_MAIN)
        outer.pack(fill="both", expand=True)

        is_admin = self.current_user["role"] == "admin"

        if is_admin:
            section_title(inner, "Add Mess Charge")
            f = tk.Frame(inner, bg=BG_CARD); f.pack(fill="x", padx=14, pady=4)

            tk.Label(f, text="Student ID or Name", bg=BG_CARD, fg=TEXT_MUTED, font=(FF,10), anchor="w").pack(fill="x", padx=14, pady=(10,2))
            sid_e = moentry(f, width=30); sid_e.pack(padx=14, pady=(0,4))

            tk.Label(f, text="Date (YYYY-MM-DD)", bg=BG_CARD, fg=TEXT_MUTED, font=(FF,10), anchor="w").pack(fill="x", padx=14, pady=(4,2))
            date_e = moentry(f, width=30); date_e.pack(padx=14, pady=(0,4))
            date_e.insert(0, datetime.now().strftime("%Y-%m-%d"))

            day_var = tk.StringVar(value=datetime.now().strftime("%A"))
            drow = tk.Frame(f, bg=BG_CARD); drow.pack(fill="x", padx=14)
            tk.Label(drow, text="Day:", bg=BG_CARD, fg=TEXT_MUTED, font=(FF,9)).pack(side="left")
            tk.Label(drow, textvariable=day_var, bg=BG_CARD, fg=ACCENT, font=(FF,9,"bold")).pack(side="left", padx=4)
            date_e.bind("<KeyRelease>", lambda *_: day_var.set(parse_date_and_day(date_e.get())[1]))

            tk.Label(f, text="Mess Amount (Rs)", bg=BG_CARD, fg=TEXT_MUTED, font=(FF,10), anchor="w").pack(fill="x", padx=14, pady=(8,2))
            amt_e = moentry(f, width=30); amt_e.pack(padx=14, pady=(0,4))

            tk.Label(f, text="Other Activity Amount (Rs)", bg=BG_CARD, fg=TEXT_MUTED, font=(FF,10), anchor="w").pack(fill="x", padx=14, pady=(4,2))
            oact_e = moentry(f, width=30); oact_e.pack(padx=14, pady=(0,4)); oact_e.insert(0,"0")

            tk.Label(f, text="Activity Description (optional)", bg=BG_CARD, fg=TEXT_MUTED, font=(FF,10), anchor="w").pack(fill="x", padx=14, pady=(4,2))
            odesc_e = moentry(f, width=30); odesc_e.pack(padx=14, pady=(0,4))

            total_var = tk.StringVar(value="Total: Rs 0")
            tk.Label(f, textvariable=total_var, bg="#eef7f1", fg=SUCCESS, font=(FF,13,"bold"),
                      anchor="w", padx=12, pady=6).pack(fill="x", padx=14, pady=4)

            def recalc(*_):
                try: a = float(amt_e.get() or 0)
                except: a = 0
                try: o = float(oact_e.get() or 0)
                except: o = 0
                total_var.set(f"Total: Rs {a+o:,.0f}")

            amt_e.bind("<KeyRelease>", recalc); oact_e.bind("<KeyRelease>", recalc)

            def add_mess():
                s, err = resolve_student(self.data, sid_e.get())
                if not s: messagebox.showerror("Not Found", err); return
                try: amt = float(amt_e.get())
                except: messagebox.showwarning("Invalid","Enter a valid amount."); return
                try: oamt = float(oact_e.get() or 0)
                except: oamt = 0
                nd, day = parse_date_and_day(date_e.get())
                month = nd[:7] if len(nd) >= 7 and nd[4:5] == "-" else nd
                mid = get_next_id(self.data, "mess")
                self.data["mess"].append({
                    "id": mid, "student_id": s["id"], "month": month,
                    "date": nd, "day": day, "amount": amt,
                    "other_activity": oamt, "other_activity_desc": odesc_e.get().strip(),
                    "status": "Unpaid", "receipt": None
                })
                save_data(self.data)
                messagebox.showinfo("Added", f"Mess charge added for {s['name']}\nTotal: Rs {amt+oamt:,.0f}")
                self._page_mess()

            def clear_mess():
                sid_e.delete(0,"end"); amt_e.delete(0,"end"); odesc_e.delete(0,"end")
                oact_e.delete(0,"end"); oact_e.insert(0,"0")
                date_e.delete(0,"end"); date_e.insert(0, datetime.now().strftime("%Y-%m-%d"))
                recalc()

            ar = tk.Frame(f, bg=BG_CARD); ar.pack(fill="x", padx=14, pady=(4,14))
            mobtn(ar, "✅ Add", add_mess, SUCCESS, fs=11).pack(side="left", padx=(0,6))
            mobtn(ar, "🗑 Clear", clear_mess, "#6c757d", fs=11).pack(side="left")

        section_title(inner, f"Mess Records ({len(self.data['mess'])})")
        for m in reversed(self.data["mess"]):
            s = find_student(self.data, m["student_id"])
            sname = s["name"] if s else "Unknown"
            other = m.get("other_activity", 0); total = m["amount"] + other
            paid = m["status"] == "Paid"
            col = SUCCESS if paid else DANGER

            card = tk.Frame(inner, bg=BG_CARD, highlightbackground=col, highlightthickness=1)
            card.pack(fill="x", padx=14, pady=4)
            hf = tk.Frame(card, bg=BG_CARD); hf.pack(fill="x", padx=12, pady=(10,2))
            tk.Label(hf, text=f"#{m['id']} — {sname}", bg=BG_CARD, fg=TEXT_DARK, font=(FF,12,"bold")).pack(side="left")
            tk.Label(hf, text=f"Rs {total:,.0f}", bg=BG_CARD, fg=col, font=(FF,12,"bold")).pack(side="right")
            detail = f"{m.get('date','')} ({m.get('day','')})  |  Mess: {m['amount']:,.0f}"
            if other: detail += f"  +  Other: {other:,.0f} ({m.get('other_activity_desc','')})"
            tk.Label(card, text=detail, bg=BG_CARD, fg=TEXT_MUTED, font=(FF,9), anchor="w", wraplength=380).pack(fill="x", padx=12)

            if is_admin:
                br = tk.Frame(card, bg=BG_CARD); br.pack(fill="x", padx=12, pady=(4,10))
                def tog_paid(rec=m):
                    rec["status"] = "Unpaid" if rec["status"] == "Paid" else "Paid"
                    save_data(self.data); self._page_mess()
                def att_rec(rec=m):
                    path = filedialog.askopenfilename(parent=self, title="Select Receipt",
                        filetypes=[("Images","*.png *.jpg *.jpeg *.gif *.bmp"),("All","*.*")])
                    if path:
                        rec["receipt"] = copy_image(path, RECEIPTS_DIR, f"mess_{rec['id']}")
                        save_data(self.data); messagebox.showinfo("Done","Receipt attached.")
                def view_rec(rec=m): show_image_window(self, rec.get("receipt"), f"Receipt #{rec['id']}")
                mobtn(br, "✅ Toggle Paid", tog_paid, SUCCESS if not paid else WARNING, fs=9).pack(side="left", padx=(0,4))
                mobtn(br, "📷 Receipt", att_rec, ACCENT, fs=9).pack(side="left", padx=(0,4))
                mobtn(br, "🖼 View", view_rec, "#6c757d", fs=9).pack(side="left")
            else:
                tk.Label(card, text=f"Status: {m['status']}", bg=BG_CARD, fg=col, font=(FF,10,"bold")).pack(padx=12, pady=(4,10), anchor="w")

    # ═══════════════════════════════════════════════════════════════════════════
    #  BILLS
    # ═══════════════════════════════════════════════════════════════════════════

    def _page_bills(self):
        self._clear()
        root = tk.Frame(self, bg=BG_MAIN); root.pack(fill="both", expand=True)
        TopBar(root, "💰 Monthly Bills", back_cmd=self._show_main).pack(fill="x")

        outer, inner, _ = make_scrollable(root, BG_MAIN)
        outer.pack(fill="both", expand=True)

        is_admin = self.current_user["role"] == "admin"

        if is_admin:
            section_title(inner, "Generate Bill")
            f = tk.Frame(inner, bg=BG_CARD); f.pack(fill="x", padx=14, pady=4)
            entries = {}
            for key, lbl, default in [
                ("sid","Student ID or Name",""),
                ("month","Month (e.g. 2026-06)",""),
                ("room","Room Charges (Rs)",str(ROOM_CHARGE_PER_MONTH)),
                ("mess","Mess Charges (Rs)","0"),
                ("other","Other Charges (Rs)","0"),
                ("act_amt","Other Activity Amount (Rs)","0"),
                ("act_desc","Activity Description",""),
            ]:
                tk.Label(f, text=lbl, bg=BG_CARD, fg=TEXT_MUTED, font=(FF,10), anchor="w").pack(fill="x", padx=14, pady=(8,2))
                e = moentry(f, width=30); e.pack(padx=14, pady=(0,2))
                if default: e.insert(0, default)
                entries[key] = e

            total_var = tk.StringVar(value="Total: Rs 0")
            tk.Label(f, textvariable=total_var, bg="#eef7f1", fg=SUCCESS, font=(FF,13,"bold"),
                      anchor="w", padx=12, pady=6).pack(fill="x", padx=14, pady=4)

            def sf(e):
                try: return float(entries[e].get() or 0)
                except: return 0.0

            def recalc_bill(*_):
                total_var.set(f"Total: Rs {sf('room')+sf('mess')+sf('other')+sf('act_amt'):,.0f}")

            for k in ("room","mess","other","act_amt"):
                entries[k].bind("<KeyRelease>", recalc_bill)

            def pull_mess():
                s, err = resolve_student(self.data, entries["sid"].get())
                if not s: messagebox.showerror("Not Found", err); return
                month = entries["month"].get().strip()
                total = sum(m["amount"] for m in self.data["mess"] if m["student_id"] == s["id"] and m.get("month") == month)
                entries["mess"].delete(0,"end"); entries["mess"].insert(0, str(total)); recalc_bill()

            mobtn(f, "📥 Pull Mess Total", pull_mess, "#6c757d", fs=10).pack(padx=14, pady=(0,4), anchor="w")
            recalc_bill()

            def gen_bill():
                s, err = resolve_student(self.data, entries["sid"].get())
                if not s: messagebox.showerror("Not Found", err); return
                month = entries["month"].get().strip()
                if not month: messagebox.showwarning("Missing","Enter month."); return
                r = sf("room"); me = sf("mess"); o = sf("other"); a = sf("act_amt")
                total = r + me + o + a
                bid = get_next_id(self.data, "bill")
                self.data["bills"].append({
                    "id": bid, "student_id": s["id"], "month": month,
                    "room_charges": r, "mess_charges": me, "other_charges": o,
                    "other_activity": a, "other_activity_desc": entries["act_desc"].get().strip(),
                    "total": total, "paid": False, "receipt": None
                })
                save_data(self.data)
                messagebox.showinfo("Generated", f"Bill #{bid} — Rs {total:,.0f}")
                self._page_bills()

            def clear_bill():
                for k, v in [("sid",""),("month",""),("mess","0"),("other","0"),("act_amt","0"),("act_desc",""),
                              ("room",str(ROOM_CHARGE_PER_MONTH))]:
                    entries[k].delete(0,"end"); entries[k].insert(0, v)
                recalc_bill()

            ar = tk.Frame(f, bg=BG_CARD); ar.pack(fill="x", padx=14, pady=(4,14))
            mobtn(ar, "✅ Generate Bill", gen_bill, SUCCESS, fs=11).pack(side="left", padx=(0,6))
            mobtn(ar, "🗑 Clear", clear_bill, "#6c757d", fs=11).pack(side="left")

        section_title(inner, f"Bills ({len(self.data['bills'])})")
        for b in reversed(self.data["bills"]):
            s = find_student(self.data, b["student_id"])
            sname = s["name"] if s else "Unknown"
            col = SUCCESS if b["paid"] else DANGER
            card = tk.Frame(inner, bg=BG_CARD, highlightbackground=col, highlightthickness=1)
            card.pack(fill="x", padx=14, pady=4)
            hf = tk.Frame(card, bg=BG_CARD); hf.pack(fill="x", padx=12, pady=(10,2))
            tk.Label(hf, text=f"#{b['id']} — {sname}", bg=BG_CARD, fg=TEXT_DARK, font=(FF,12,"bold")).pack(side="left")
            tk.Label(hf, text=f"Rs {b['total']:,.0f}", bg=BG_CARD, fg=col, font=(FF,12,"bold")).pack(side="right")
            detail = f"{b['month']}  |  Room: {b['room_charges']:,.0f}  Mess: {b['mess_charges']:,.0f}  Other: {b.get('other_charges',0):,.0f}"
            if b.get("other_activity"): detail += f"  Activity: {b['other_activity']:,.0f}"
            tk.Label(card, text=detail, bg=BG_CARD, fg=TEXT_MUTED, font=(FF,9), anchor="w", wraplength=380).pack(fill="x", padx=12)
            tk.Label(card, text=f"{'✅ PAID' if b['paid'] else '⚠️ UNPAID'}", bg=BG_CARD, fg=col, font=(FF,10,"bold")).pack(anchor="w", padx=12, pady=(2,2))

            if is_admin:
                br = tk.Frame(card, bg=BG_CARD); br.pack(fill="x", padx=12, pady=(4,10))
                def tog_bill(bill=b):
                    bill["paid"] = not bill["paid"]; save_data(self.data); self._page_bills()
                def att_bill(bill=b):
                    path = filedialog.askopenfilename(parent=self, title="Select Receipt",
                        filetypes=[("Images","*.png *.jpg *.jpeg *.gif *.bmp"),("All","*.*")])
                    if path:
                        bill["receipt"] = copy_image(path, RECEIPTS_DIR, f"bill_{bill['id']}")
                        save_data(self.data); messagebox.showinfo("Done","Receipt attached.")
                def view_bill_rec(bill=b): show_image_window(self, bill.get("receipt"), f"Bill #{bill['id']} Receipt")
                mobtn(br, "✅ Toggle Paid", tog_bill, SUCCESS if not b["paid"] else WARNING, fs=9).pack(side="left", padx=(0,4))
                mobtn(br, "📷 Attach", att_bill, ACCENT, fs=9).pack(side="left", padx=(0,4))
                mobtn(br, "🖼 Receipt", view_bill_rec, "#6c757d", fs=9).pack(side="left")

    # ═══════════════════════════════════════════════════════════════════════════
    #  COMPLAINTS — with Solve, Clear, Back, Skip buttons + solution box
    # ═══════════════════════════════════════════════════════════════════════════

    def _page_complaints(self):
        self._clear()
        root = tk.Frame(self, bg=BG_MAIN); root.pack(fill="both", expand=True)
        TopBar(root, "📝 Complaints", back_cmd=self._show_main).pack(fill="x")

        outer, inner, _ = make_scrollable(root, BG_MAIN)
        outer.pack(fill="both", expand=True)

        is_admin = self.current_user["role"] == "admin"

        # File complaint form
        section_title(inner, "File a Complaint")
        f = tk.Frame(inner, bg=BG_CARD); f.pack(fill="x", padx=14, pady=4)
        tk.Label(f, text="Student ID or Name", bg=BG_CARD, fg=TEXT_MUTED, font=(FF,10), anchor="w").pack(fill="x", padx=14, pady=(10,2))
        sid_e = moentry(f, width=30); sid_e.pack(padx=14, pady=(0,4))

        tk.Label(f, text="Complaint Details", bg=BG_CARD, fg=TEXT_MUTED, font=(FF,10), anchor="w").pack(fill="x", padx=14, pady=(4,2))
        txt = tk.Text(f, font=(FF,11), width=30, height=4, relief="solid", bd=2,
                       highlightthickness=1, highlightcolor=ACCENT)
        txt.pack(padx=14, pady=(0,6))

        msg_var = tk.StringVar()
        tk.Label(f, textvariable=msg_var, bg=BG_CARD, fg=DANGER, font=(FF,9)).pack(anchor="w", padx=14)

        def file_complaint():
            s, err = resolve_student(self.data, sid_e.get())
            if not s: msg_var.set(err); return
            text = txt.get("1.0","end").strip()
            if not text: msg_var.set("Enter complaint details."); return
            cid = get_next_id(self.data, "complaint")
            self.data["complaints"].append({
                "id": cid, "student_id": s["id"], "text": text,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "status": "Pending", "solution": ""
            })
            save_data(self.data)
            messagebox.showinfo("Filed", f"Complaint #{cid} filed.")
            self._page_complaints()

        def clear_complaint():
            sid_e.delete(0,"end"); txt.delete("1.0","end"); msg_var.set("")

        def skip_complaint():
            """Clear form and move to viewing complaints."""
            clear_complaint()
            # scroll down to list — just clear and show a notice
            msg_var.set("Form cleared. View complaints below ↓")

        ar = tk.Frame(f, bg=BG_CARD); ar.pack(fill="x", padx=14, pady=(4,14))
        mobtn(ar, "📝 Submit", file_complaint, ACCENT, fs=11).pack(side="left", padx=(0,6))
        mobtn(ar, "🗑 Clear", clear_complaint, "#6c757d", fs=11).pack(side="left", padx=(0,6))
        mobtn(ar, "⏩ Skip", skip_complaint, WARNING, fs=11).pack(side="left")

        # Complaints list
        total_c = len(self.data["complaints"])
        pending = sum(1 for c in self.data["complaints"] if c["status"] == "Pending")
        resolved = total_c - pending

        section_title(inner, f"Complaints — {total_c} total  |  {pending} pending  |  {resolved} resolved")

        if not self.data["complaints"]:
            tk.Label(inner, text="No complaints yet.", bg=BG_MAIN, fg=TEXT_MUTED, font=(FF,12)).pack(pady=20)

        for comp in reversed(self.data["complaints"]):
            s = find_student(self.data, comp["student_id"])
            sname = s["name"] if s else "Unknown"
            is_pending = comp["status"] == "Pending"
            col = DANGER if is_pending else SUCCESS

            card = tk.Frame(inner, bg=BG_CARD, highlightbackground=col, highlightthickness=1)
            card.pack(fill="x", padx=14, pady=5)

            hf = tk.Frame(card, bg=BG_CARD); hf.pack(fill="x", padx=12, pady=(10,2))
            tk.Label(hf, text=f"#{comp['id']} — {sname}", bg=BG_CARD, fg=TEXT_DARK, font=(FF,12,"bold")).pack(side="left")
            status_badge = "⚠️ Pending" if is_pending else "✅ Resolved"
            tk.Label(hf, text=status_badge, bg=BG_CARD, fg=col, font=(FF,10,"bold")).pack(side="right")

            tk.Label(card, text=comp["text"], bg=BG_CARD, fg=TEXT_DARK, font=(FF,10),
                      anchor="w", wraplength=380, justify="left").pack(fill="x", padx=12, pady=(2,2))
            tk.Label(card, text=f"📅 {comp['date']}", bg=BG_CARD, fg=TEXT_MUTED, font=(FF,8)).pack(anchor="w", padx=12)

            # Show solution if exists
            if comp.get("solution"):
                sol_f = tk.Frame(card, bg="#eef7f1"); sol_f.pack(fill="x", padx=12, pady=(4,2))
                tk.Label(sol_f, text="💡 Solution:", bg="#eef7f1", fg=SUCCESS, font=(FF,9,"bold")).pack(anchor="w", padx=6, pady=(4,0))
                tk.Label(sol_f, text=comp["solution"], bg="#eef7f1", fg=TEXT_DARK, font=(FF,9),
                          anchor="w", wraplength=360, justify="left").pack(fill="x", padx=6, pady=(0,6))

            if is_admin and is_pending:
                br = tk.Frame(card, bg=BG_CARD); br.pack(fill="x", padx=12, pady=(6,10))

                def open_solve(complaint=comp):
                    """Open solve dialog with solution text input."""
                    win = tk.Toplevel(self); win.title("Solve Complaint"); win.configure(bg=BG_CARD)
                    win.geometry("420x340"); win.resizable(False, False); win.grab_set()

                    tk.Label(win, text=f"Complaint #{complaint['id']}", bg=BG_CARD, fg=TEXT_DARK, font=(FF,13,"bold")).pack(pady=(18,4), padx=20, anchor="w")
                    tk.Label(win, text=complaint["text"], bg=BG_CARD, fg=TEXT_MUTED, font=(FF,10),
                              wraplength=380, justify="left").pack(padx=20, anchor="w")
                    tk.Label(win, text="Solution / Response:", bg=BG_CARD, fg=TEXT_DARK, font=(FF,11,"bold")).pack(pady=(14,4), padx=20, anchor="w")
                    sol_txt = tk.Text(win, font=(FF,10), width=44, height=5, relief="solid", bd=2)
                    sol_txt.pack(padx=20, pady=(0,10))
                    if complaint.get("solution"): sol_txt.insert("1.0", complaint["solution"])

                    br2 = tk.Frame(win, bg=BG_CARD); br2.pack(pady=6)

                    def do_solve():
                        sol = sol_txt.get("1.0","end").strip()
                        if not sol: messagebox.showwarning("Empty","Enter a solution text.",parent=win); return
                        complaint["status"] = "Resolved"; complaint["solution"] = sol
                        save_data(self.data); win.destroy()
                        messagebox.showinfo("Solved", "Complaint marked as Resolved.")
                        self._page_complaints()

                    def do_skip():
                        complaint["status"] = "Resolved"; complaint["solution"] = "Resolved without notes."
                        save_data(self.data); win.destroy(); self._page_complaints()

                    mobtn(br2, "✅ Mark Solved", do_solve, SUCCESS, fs=11).pack(side="left", padx=6)
                    mobtn(br2, "⏩ Skip / Quick Resolve", do_skip, WARNING, fs=10).pack(side="left", padx=6)
                    mobtn(br2, "✖ Cancel", win.destroy, "#6c757d", fs=10).pack(side="left", padx=6)

                mobtn(br, "🔧 Solve Complaint", open_solve, SUCCESS, fs=10).pack(side="left", padx=(0,6))

            elif is_admin and not is_pending:
                # Re-open option
                def reopen(complaint=comp):
                    complaint["status"] = "Pending"; save_data(self.data); self._page_complaints()
                br3 = tk.Frame(card, bg=BG_CARD); br3.pack(fill="x", padx=12, pady=(4,10))
                mobtn(br3, "🔄 Re-open", reopen, WARNING, fs=9).pack(side="left")

    # ═══════════════════════════════════════════════════════════════════════════
    #  ADMIN SETTINGS
    # ═══════════════════════════════════════════════════════════════════════════

    def _page_admin(self):
        self._clear()
        root = tk.Frame(self, bg=BG_MAIN); root.pack(fill="both", expand=True)
        TopBar(root, "⚙️ Admin Settings", back_cmd=self._show_main).pack(fill="x")

        outer, inner, _ = make_scrollable(root, BG_MAIN)
        outer.pack(fill="both", expand=True)

        section_title(inner, "Change Admin Credentials")
        f = tk.Frame(inner, bg=BG_CARD); f.pack(fill="x", padx=14, pady=4)

        tk.Label(f, text="Current Admin ID Code (share this with new members):", bg=BG_CARD,
                  fg=TEXT_MUTED, font=(FF,10)).pack(padx=14, pady=(12,2), anchor="w")
        tk.Label(f, text=self.data["admin"]["admin_id"], bg=ACCENT_LIGHT, fg=ACCENT,
                  font=(FF,14,"bold"), padx=14, pady=8).pack(fill="x", padx=14, pady=(0,8))

        tk.Label(f, text="New Admin ID Code", bg=BG_CARD, fg=TEXT_MUTED, font=(FF,10), anchor="w").pack(fill="x", padx=14, pady=(4,2))
        new_id_e = moentry(f, width=26); new_id_e.pack(padx=14, pady=(0,4))
        tk.Label(f, text="New Password", bg=BG_CARD, fg=TEXT_MUTED, font=(FF,10), anchor="w").pack(fill="x", padx=14, pady=(4,2))
        new_pw_e = moentry(f, width=26, show="•"); new_pw_e.pack(padx=14, pady=(0,4))
        tk.Label(f, text="Confirm Password", bg=BG_CARD, fg=TEXT_MUTED, font=(FF,10), anchor="w").pack(fill="x", padx=14, pady=(4,2))
        conf_pw_e = moentry(f, width=26, show="•"); conf_pw_e.pack(padx=14, pady=(0,4))

        def update_admin():
            nid = new_id_e.get().strip(); npw = new_pw_e.get().strip(); cpw = conf_pw_e.get().strip()
            if nid: self.data["admin"]["admin_id"] = nid
            if npw:
                if npw != cpw: messagebox.showerror("Mismatch","Passwords do not match."); return
                self.data["admin"]["password"] = hash_pw(npw)
            save_data(self.data); messagebox.showinfo("Updated","Admin settings updated.")
            self._page_admin()

        mobtn(f, "💾 Update Settings", update_admin, ACCENT, fs=11).pack(padx=14, pady=(6,14), anchor="w")

        section_title(inner, f"Registered Members ({len(self.data['members'])})")
        if not self.data["members"]:
            tk.Label(inner, text="No members registered.", bg=BG_MAIN, fg=TEXT_MUTED, font=(FF,11)).pack(pady=12)
        for mem in self.data["members"]:
            card = tk.Frame(inner, bg=BG_CARD, highlightbackground="#e2e5ee", highlightthickness=1)
            card.pack(fill="x", padx=14, pady=4)
            hf = tk.Frame(card, bg=BG_CARD); hf.pack(fill="x", padx=12, pady=(10,6))
            tk.Label(hf, text=f"👤 {mem['name']}", bg=BG_CARD, fg=TEXT_DARK, font=(FF,12,"bold")).pack(side="left")
            tk.Label(hf, text=f"@{mem['username']}", bg=BG_CARD, fg=TEXT_MUTED, font=(FF,10)).pack(side="right")
            def del_mem(m=mem):
                if messagebox.askyesno("Remove","Remove this member?", parent=self):
                    self.data["members"].remove(m); save_data(self.data); self._page_admin()
            mobtn(card, "🗑 Remove", del_mem, DANGER, fs=9).pack(anchor="w", padx=12, pady=(0,10))


if __name__ == "__main__":
    app = HostelApp()
    app.mainloop()