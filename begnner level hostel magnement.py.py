"""
HOSTEL MANAGEMENT SYSTEM — GUI Edition
A desktop application built with Tkinter (no external libraries needed).

Run with:  python hostel_management_gui.py

Data is auto-saved to hostel_data.json in the same folder, so nothing
is lost when you close the app.
"""

import json
import os
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hostel_data.json")
ROOM_CHARGE_PER_MONTH = 5000

# --------------------------------------------------------------------------- #
#  THEME / COLORS
# --------------------------------------------------------------------------- #

BG_DARK = "#1e2430"        # sidebar background
BG_DARK_HOVER = "#2a3142"
BG_MAIN = "#f4f6fb"        # content background
BG_CARD = "#ffffff"
ACCENT = "#5b6cf9"          # primary brand color
ACCENT_DARK = "#4654d6"
TEXT_LIGHT = "#e8eaf3"
TEXT_MUTED = "#9aa3b8"
TEXT_DARK = "#222633"
SUCCESS = "#2bb673"
DANGER = "#e5534b"
WARNING = "#e0a93a"

FONT_FAMILY = "Segoe UI"


# --------------------------------------------------------------------------- #
#  DATA LAYER
# --------------------------------------------------------------------------- #

def default_data():
    return {
        "students": [],
        "rooms": [],
        "mess": [],
        "bills": [],
        "complaints": [],
        "next_ids": {"student": 1, "mess": 1, "bill": 1, "complaint": 1}
    }


def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return default_data()
    return default_data()


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def get_next_id(data, key):
    nid = data["next_ids"][key]
    data["next_ids"][key] += 1
    return nid


def find_student(data, sid):
    for s in data["students"]:
        if s["id"] == sid:
            return s
    return None


def find_room(data, room_no):
    for r in data["rooms"]:
        if r["room_no"] == room_no:
            return r
    return None


# --------------------------------------------------------------------------- #
#  REUSABLE UI WIDGETS
# --------------------------------------------------------------------------- #

class Card(tk.Frame):
    """A white rounded-look panel used to group content."""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=BG_CARD, highlightbackground="#e2e5ee",
                          highlightthickness=1, **kwargs)


def styled_button(parent, text, command, kind="primary", width=16):
    colors = {
        "primary": (ACCENT, ACCENT_DARK, "white"),
        "success": (SUCCESS, "#229960", "white"),
        "danger": (DANGER, "#c64640", "white"),
        "muted": ("#e8eaf3", "#d6dae8", TEXT_DARK),
    }
    bg, active_bg, fg = colors.get(kind, colors["primary"])
    btn = tk.Button(parent, text=text, command=command, bg=bg, fg=fg,
                     activebackground=active_bg, activeforeground=fg,
                     font=(FONT_FAMILY, 10, "bold"), bd=0, relief="flat",
                     cursor="hand2", width=width, pady=8)
    return btn


def labeled_entry(parent, label_text, row, col=0, width=28, show=None):
    lbl = tk.Label(parent, text=label_text, bg=BG_CARD, fg=TEXT_DARK,
                    font=(FONT_FAMILY, 10), anchor="w")
    lbl.grid(row=row, column=col, sticky="w", padx=(0, 10), pady=(8, 2))
    entry = tk.Entry(parent, font=(FONT_FAMILY, 10), width=width, relief="solid",
                      bd=1, show=show)
    entry.grid(row=row + 1, column=col, sticky="w", padx=(0, 20), pady=(0, 6))
    return entry


def make_table(parent, columns, height=12):
    style = ttk.Style()
    style.configure("Custom.Treeview", font=(FONT_FAMILY, 10), rowheight=28,
                     background="white", fieldbackground="white")
    style.configure("Custom.Treeview.Heading", font=(FONT_FAMILY, 10, "bold"),
                     background="#eef0f8", foreground=TEXT_DARK)
    style.map("Custom.Treeview", background=[("selected", "#dde2fb")])

    container = tk.Frame(parent, bg=BG_CARD)
    tree = ttk.Treeview(container, columns=columns, show="headings",
                         height=height, style="Custom.Treeview")
    for c in columns:
        tree.heading(c, text=c)
        tree.column(c, width=130, anchor="w")
    vsb = ttk.Scrollbar(container, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=vsb.set)
    tree.grid(row=0, column=0, sticky="nsew")
    vsb.grid(row=0, column=1, sticky="ns")
    container.grid_rowconfigure(0, weight=1)
    container.grid_columnconfigure(0, weight=1)
    return container, tree


# --------------------------------------------------------------------------- #
#  MAIN APPLICATION
# --------------------------------------------------------------------------- #

class HostelApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Hostel Management System")
        self.geometry("1180x720")
        self.minsize(1000, 640)
        self.configure(bg=BG_MAIN)

        self.data = load_data()

        self.nav_buttons = {}
        self.current_page = None

        self._build_layout()
        self.show_page("dashboard")

    # ----------------------------------------------------------------- #
    #  LAYOUT
    # ----------------------------------------------------------------- #

    def _build_layout(self):
        # Sidebar
        self.sidebar = tk.Frame(self, bg=BG_DARK, width=230)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        title_frame = tk.Frame(self.sidebar, bg=BG_DARK)
        title_frame.pack(fill="x", pady=(26, 30), padx=20)
        tk.Label(title_frame, text="🏠 HOSTEL MS", bg=BG_DARK, fg="white",
                  font=(FONT_FAMILY, 16, "bold")).pack(anchor="w")
        tk.Label(title_frame, text="Management System", bg=BG_DARK, fg=TEXT_MUTED,
                  font=(FONT_FAMILY, 9)).pack(anchor="w")

        nav_items = [
            ("dashboard", "📊  Dashboard"),
            ("students", "🧑‍🎓  Students"),
            ("rooms", "🛏️  Rooms"),
            ("roommates", "👥  Roommates"),
            ("mess", "🍽️  Mess"),
            ("bills", "💰  Monthly Bills"),
            ("complaints", "📝  Complaints"),
        ]
        for key, label in nav_items:
            self._make_nav_button(key, label)

        bottom_frame = tk.Frame(self.sidebar, bg=BG_DARK)
        bottom_frame.pack(side="bottom", fill="x", pady=20, padx=20)
        tk.Label(bottom_frame, text="Data auto-saves locally", bg=BG_DARK,
                  fg=TEXT_MUTED, font=(FONT_FAMILY, 8)).pack(anchor="w")

        # Main content area
        self.content = tk.Frame(self, bg=BG_MAIN)
        self.content.pack(side="left", fill="both", expand=True)

    def _make_nav_button(self, key, label):
        btn = tk.Button(self.sidebar, text=label, anchor="w", bg=BG_DARK, fg=TEXT_LIGHT,
                         font=(FONT_FAMILY, 11), bd=0, relief="flat", cursor="hand2",
                         activebackground=BG_DARK_HOVER, activeforeground="white",
                         padx=20, pady=12, command=lambda: self.show_page(key))
        btn.pack(fill="x")
        self.nav_buttons[key] = btn

    def _highlight_nav(self, active_key):
        for key, btn in self.nav_buttons.items():
            if key == active_key:
                btn.configure(bg=ACCENT, fg="white")
            else:
                btn.configure(bg=BG_DARK, fg=TEXT_LIGHT)

    def show_page(self, key):
        self._highlight_nav(key)
        for widget in self.content.winfo_children():
            widget.destroy()

        pages = {
            "dashboard": self.page_dashboard,
            "students": self.page_students,
            "rooms": self.page_rooms,
            "roommates": self.page_roommates,
            "mess": self.page_mess,
            "bills": self.page_bills,
            "complaints": self.page_complaints,
        }
        pages[key]()

    def page_header(self, title, subtitle=""):
        header = tk.Frame(self.content, bg=BG_MAIN)
        header.pack(fill="x", padx=30, pady=(26, 10))
        tk.Label(header, text=title, bg=BG_MAIN, fg=TEXT_DARK,
                  font=(FONT_FAMILY, 20, "bold")).pack(anchor="w")
        if subtitle:
            tk.Label(header, text=subtitle, bg=BG_MAIN, fg=TEXT_MUTED,
                      font=(FONT_FAMILY, 10)).pack(anchor="w", pady=(2, 0))
        return header

    # ----------------------------------------------------------------- #
    #  DASHBOARD
    # ----------------------------------------------------------------- #

    def page_dashboard(self):
        self.page_header("Dashboard", "Quick overview of your hostel")

        stats_frame = tk.Frame(self.content, bg=BG_MAIN)
        stats_frame.pack(fill="x", padx=30, pady=10)

        total_students = len(self.data["students"])
        total_rooms = len(self.data["rooms"])
        occupied_beds = sum(len(r["occupants"]) for r in self.data["rooms"])
        total_capacity = sum(r["capacity"] for r in self.data["rooms"])
        pending_complaints = sum(1 for c in self.data["complaints"] if c["status"] == "Pending")
        unpaid_bills = sum(1 for b in self.data["bills"] if not b["paid"])

        stats = [
            ("Total Students", total_students, ACCENT),
            ("Total Rooms", total_rooms, SUCCESS),
            ("Beds Occupied", f"{occupied_beds}/{total_capacity}", WARNING),
            ("Pending Complaints", pending_complaints, DANGER),
        ]

        for i, (label, value, color) in enumerate(stats):
            card = Card(stats_frame, width=250, height=110)
            card.grid(row=0, column=i, padx=(0, 16), sticky="nsew")
            card.grid_propagate(False)
            stats_frame.grid_columnconfigure(i, weight=1)

            bar = tk.Frame(card, bg=color, width=5)
            bar.pack(side="left", fill="y")
            inner = tk.Frame(card, bg=BG_CARD)
            inner.pack(side="left", fill="both", expand=True, padx=16, pady=14)
            tk.Label(inner, text=str(value), bg=BG_CARD, fg=TEXT_DARK,
                      font=(FONT_FAMILY, 22, "bold")).pack(anchor="w")
            tk.Label(inner, text=label, bg=BG_CARD, fg=TEXT_MUTED,
                      font=(FONT_FAMILY, 9)).pack(anchor="w")

        # Recent complaints panel
        panel = Card(self.content)
        panel.pack(fill="both", expand=True, padx=30, pady=(20, 20))
        tk.Label(panel, text="Recent Complaints", bg=BG_CARD, fg=TEXT_DARK,
                  font=(FONT_FAMILY, 12, "bold")).pack(anchor="w", padx=18, pady=(16, 6))

        table_wrap, tree = make_table(panel, ["ID", "Student", "Complaint", "Date", "Status"], height=8)
        table_wrap.pack(fill="both", expand=True, padx=18, pady=(0, 18))

        recent = sorted(self.data["complaints"], key=lambda c: c["id"], reverse=True)[:8]
        for c in recent:
            s = find_student(self.data, c["student_id"])
            sname = s["name"] if s else "Unknown"
            tree.insert("", "end", values=(c["id"], sname, c["text"], c["date"], c["status"]))

        if not recent:
            tk.Label(panel, text="No complaints filed yet.", bg=BG_CARD, fg=TEXT_MUTED,
                      font=(FONT_FAMILY, 10)).pack(pady=10)

    # ----------------------------------------------------------------- #
    #  STUDENTS PAGE
    # ----------------------------------------------------------------- #

    def page_students(self):
        self.page_header("Students", "Add, view and search hostel students")

        wrapper = tk.Frame(self.content, bg=BG_MAIN)
        wrapper.pack(fill="both", expand=True, padx=30, pady=(0, 20))
        wrapper.grid_columnconfigure(0, weight=0)
        wrapper.grid_columnconfigure(1, weight=1)
        wrapper.grid_rowconfigure(0, weight=1)

        # Left: Add student form
        form_card = Card(wrapper, width=300)
        form_card.grid(row=0, column=0, sticky="ns", padx=(0, 20))
        form_card.grid_propagate(False)

        inner = tk.Frame(form_card, bg=BG_CARD)
        inner.pack(fill="both", padx=18, pady=18)
        tk.Label(inner, text="Add New Student", bg=BG_CARD, fg=TEXT_DARK,
                  font=(FONT_FAMILY, 12, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 6))

        name_e = labeled_entry(inner, "Full Name", 1)
        cnic_e = labeled_entry(inner, "CNIC / ID No.", 3)
        contact_e = labeled_entry(inner, "Contact Number", 5)
        dept_e = labeled_entry(inner, "Department", 7)
        sem_e = labeled_entry(inner, "Semester", 9)

        def submit():
            name = name_e.get().strip()
            cnic = cnic_e.get().strip()
            contact = contact_e.get().strip()
            dept = dept_e.get().strip()
            sem = sem_e.get().strip()
            if not all([name, cnic, contact, dept, sem]):
                messagebox.showwarning("Missing Info", "Please fill in all fields.")
                return
            sid = get_next_id(self.data, "student")
            self.data["students"].append({
                "id": sid, "name": name, "cnic": cnic, "contact": contact,
                "dept": dept, "semester": sem, "room_no": None
            })
            save_data(self.data)
            messagebox.showinfo("Success", f"Student added with ID {sid}")
            self.show_page("students")

        styled_button(inner, "Add Student", submit, "primary", width=24).grid(
            row=11, column=0, sticky="w", pady=(10, 0))

        # Right: search + table
        right = tk.Frame(wrapper, bg=BG_MAIN)
        right.grid(row=0, column=1, sticky="nsew")
        right.grid_rowconfigure(1, weight=1)
        right.grid_columnconfigure(0, weight=1)

        search_frame = tk.Frame(right, bg=BG_MAIN)
        search_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        tk.Label(search_frame, text="🔍", bg=BG_MAIN, font=(FONT_FAMILY, 12)).pack(side="left")
        search_entry = tk.Entry(search_frame, font=(FONT_FAMILY, 10), width=30, relief="solid", bd=1)
        search_entry.pack(side="left", padx=8)
        search_entry.insert(0, "")

        table_card = Card(right)
        table_card.grid(row=1, column=0, sticky="nsew")
        table_wrap, tree = make_table(table_card,
                                       ["ID", "Name", "CNIC", "Department", "Semester", "Contact", "Room"])
        table_wrap.pack(fill="both", expand=True, padx=14, pady=14)

        def refresh(filter_text=""):
            tree.delete(*tree.get_children())
            for s in self.data["students"]:
                if filter_text and filter_text.lower() not in s["name"].lower() and str(s["id"]) != filter_text:
                    continue
                tree.insert("", "end", values=(s["id"], s["name"], s["cnic"], s["dept"],
                                                s["semester"], s["contact"], s["room_no"] or "—"))

        def on_search(*_):
            refresh(search_entry.get().strip())

        search_entry.bind("<KeyRelease>", on_search)
        refresh()

    # ----------------------------------------------------------------- #
    #  ROOMS PAGE
    # ----------------------------------------------------------------- #

    def page_rooms(self):
        self.page_header("Rooms", "Add rooms and assign students")

        wrapper = tk.Frame(self.content, bg=BG_MAIN)
        wrapper.pack(fill="both", expand=True, padx=30, pady=(0, 20))
        wrapper.grid_columnconfigure(0, weight=0)
        wrapper.grid_columnconfigure(1, weight=1)
        wrapper.grid_rowconfigure(0, weight=1)

        form_card = Card(wrapper, width=300)
        form_card.grid(row=0, column=0, sticky="ns", padx=(0, 20))
        form_card.grid_propagate(False)
        inner = tk.Frame(form_card, bg=BG_CARD)
        inner.pack(fill="both", padx=18, pady=18)

        tk.Label(inner, text="Add New Room", bg=BG_CARD, fg=TEXT_DARK,
                  font=(FONT_FAMILY, 12, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 6))
        room_no_e = labeled_entry(inner, "Room Number", 1, width=20)
        cap_e = labeled_entry(inner, "Capacity (beds)", 3, width=20)

        def add_room_action():
            room_no = room_no_e.get().strip()
            cap = cap_e.get().strip()
            if not room_no or not cap.isdigit():
                messagebox.showwarning("Missing Info", "Enter a valid room number and capacity.")
                return
            if find_room(self.data, room_no):
                messagebox.showerror("Duplicate", "A room with this number already exists.")
                return
            self.data["rooms"].append({"room_no": room_no, "capacity": int(cap), "occupants": []})
            save_data(self.data)
            messagebox.showinfo("Success", f"Room {room_no} added.")
            self.show_page("rooms")

        styled_button(inner, "Add Room", add_room_action, "primary", width=20).grid(
            row=5, column=0, sticky="w", pady=(10, 16))

        tk.Frame(inner, bg="#e2e5ee", height=1).grid(row=6, column=0, sticky="ew", pady=10)

        tk.Label(inner, text="Assign Student to Room", bg=BG_CARD, fg=TEXT_DARK,
                  font=(FONT_FAMILY, 12, "bold")).grid(row=7, column=0, sticky="w", pady=(6, 6))
        sid_e = labeled_entry(inner, "Student ID", 8, width=20)
        room_assign_e = labeled_entry(inner, "Room Number", 10, width=20)

        def assign_action():
            sid_text = sid_e.get().strip()
            room_no = room_assign_e.get().strip()
            if not sid_text.isdigit() or not room_no:
                messagebox.showwarning("Missing Info", "Enter a valid Student ID and Room Number.")
                return
            sid = int(sid_text)
            student = find_student(self.data, sid)
            room = find_room(self.data, room_no)
            if not student:
                messagebox.showerror("Not Found", "Student not found.")
                return
            if not room:
                messagebox.showerror("Not Found", "Room not found.")
                return
            if student["room_no"]:
                messagebox.showerror("Already Assigned", f"Student already in room {student['room_no']}.")
                return
            if len(room["occupants"]) >= room["capacity"]:
                messagebox.showerror("Room Full", "This room has no free beds.")
                return
            room["occupants"].append(sid)
            student["room_no"] = room_no
            save_data(self.data)
            messagebox.showinfo("Success", f"{student['name']} assigned to Room {room_no}.")
            self.show_page("rooms")

        styled_button(inner, "Assign Room", assign_action, "success", width=20).grid(
            row=12, column=0, sticky="w", pady=(10, 0))

        # Right: rooms table
        right = tk.Frame(wrapper, bg=BG_MAIN)
        right.grid(row=0, column=1, sticky="nsew")
        right.grid_rowconfigure(0, weight=1)
        right.grid_columnconfigure(0, weight=1)

        table_card = Card(right)
        table_card.grid(row=0, column=0, sticky="nsew")
        table_wrap, tree = make_table(table_card, ["Room No.", "Capacity", "Occupied", "Free Beds", "Status"])
        table_wrap.pack(fill="both", expand=True, padx=14, pady=14)

        for r in self.data["rooms"]:
            occ = len(r["occupants"])
            free = r["capacity"] - occ
            status = "Full" if free <= 0 else "Available"
            tree.insert("", "end", values=(r["room_no"], r["capacity"], occ, free, status))

    # ----------------------------------------------------------------- #
    #  ROOMMATES PAGE
    # ----------------------------------------------------------------- #

    def page_roommates(self):
        self.page_header("Roommates", "Manage who shares which room")

        wrapper = tk.Frame(self.content, bg=BG_MAIN)
        wrapper.pack(fill="both", expand=True, padx=30, pady=(0, 20))
        wrapper.grid_columnconfigure(0, weight=0)
        wrapper.grid_columnconfigure(1, weight=1)
        wrapper.grid_rowconfigure(0, weight=1)

        form_card = Card(wrapper, width=300)
        form_card.grid(row=0, column=0, sticky="ns", padx=(0, 20))
        form_card.grid_propagate(False)
        inner = tk.Frame(form_card, bg=BG_CARD)
        inner.pack(fill="both", padx=18, pady=18)

        tk.Label(inner, text="View Room Occupants", bg=BG_CARD, fg=TEXT_DARK,
                  font=(FONT_FAMILY, 12, "bold")).grid(row=0, column=0, sticky="w")
        view_room_e = labeled_entry(inner, "Room Number", 1, width=20)

        result_label = tk.Label(form_card, text="", bg=BG_CARD, fg=TEXT_DARK,
                                  font=(FONT_FAMILY, 9), justify="left", wraplength=260)
        result_label.pack(padx=18, pady=(0, 10), anchor="w")

        def view_action():
            room_no = view_room_e.get().strip()
            room = find_room(self.data, room_no)
            if not room:
                messagebox.showerror("Not Found", "Room not found.")
                return
            names = []
            for sid in room["occupants"]:
                s = find_student(self.data, sid)
                if s:
                    names.append(f"#{s['id']} {s['name']}")
            text = f"Room {room_no} ({len(room['occupants'])}/{room['capacity']}):\n" + \
                   ("\n".join(names) if names else "No occupants yet.")
            result_label.configure(text=text)

        styled_button(inner, "View Roommates", view_action, "primary", width=20).grid(
            row=3, column=0, sticky="w", pady=(10, 16))

        tk.Frame(inner, bg="#e2e5ee", height=1).grid(row=4, column=0, sticky="ew", pady=8)

        tk.Label(inner, text="Move Student to Another Room", bg=BG_CARD, fg=TEXT_DARK,
                  font=(FONT_FAMILY, 12, "bold")).grid(row=5, column=0, sticky="w", pady=(6, 6))
        move_sid_e = labeled_entry(inner, "Student ID", 6, width=20)
        move_room_e = labeled_entry(inner, "New Room Number", 8, width=20)

        def move_action():
            sid_text = move_sid_e.get().strip()
            new_room_no = move_room_e.get().strip()
            if not sid_text.isdigit() or not new_room_no:
                messagebox.showwarning("Missing Info", "Enter a valid Student ID and Room.")
                return
            sid = int(sid_text)
            student = find_student(self.data, sid)
            if not student or not student["room_no"]:
                messagebox.showerror("Error", "Student not found or has no current room.")
                return
            new_room = find_room(self.data, new_room_no)
            if not new_room:
                messagebox.showerror("Not Found", "New room not found.")
                return
            if len(new_room["occupants"]) >= new_room["capacity"]:
                messagebox.showerror("Room Full", "New room has no free beds.")
                return
            old_room = find_room(self.data, student["room_no"])
            if old_room and sid in old_room["occupants"]:
                old_room["occupants"].remove(sid)
            new_room["occupants"].append(sid)
            student["room_no"] = new_room_no
            save_data(self.data)
            messagebox.showinfo("Success", f"{student['name']} moved to Room {new_room_no}.")
            self.show_page("roommates")

        styled_button(inner, "Move Student", move_action, "success", width=20).grid(
            row=10, column=0, sticky="w", pady=(10, 16))

        def remove_action():
            sid_text = move_sid_e.get().strip()
            if not sid_text.isdigit():
                messagebox.showwarning("Missing Info", "Enter a valid Student ID above to remove.")
                return
            sid = int(sid_text)
            student = find_student(self.data, sid)
            if not student or not student["room_no"]:
                messagebox.showerror("Error", "Student not found or has no current room.")
                return
            room = find_room(self.data, student["room_no"])
            if room and sid in room["occupants"]:
                room["occupants"].remove(sid)
            student["room_no"] = None
            save_data(self.data)
            messagebox.showinfo("Removed", f"{student['name']} removed from their room.")
            self.show_page("roommates")

        styled_button(inner, "Remove from Room", remove_action, "danger", width=20).grid(
            row=11, column=0, sticky="w")

        # Right: all rooms with occupants overview
        right = tk.Frame(wrapper, bg=BG_MAIN)
        right.grid(row=0, column=1, sticky="nsew")
        right.grid_rowconfigure(0, weight=1)
        right.grid_columnconfigure(0, weight=1)

        table_card = Card(right)
        table_card.grid(row=0, column=0, sticky="nsew")
        table_wrap, tree = make_table(table_card, ["Room No.", "Occupants"])
        table_wrap.pack(fill="both", expand=True, padx=14, pady=14)
        tree.column("Occupants", width=420)

        for r in self.data["rooms"]:
            names = []
            for sid in r["occupants"]:
                s = find_student(self.data, sid)
                if s:
                    names.append(s["name"])
            tree.insert("", "end", values=(r["room_no"], ", ".join(names) if names else "Empty"))

    # ----------------------------------------------------------------- #
    #  MESS PAGE
    # ----------------------------------------------------------------- #

    def page_mess(self):
        self.page_header("Mess Management", "Track monthly mess charges per student")

        wrapper = tk.Frame(self.content, bg=BG_MAIN)
        wrapper.pack(fill="both", expand=True, padx=30, pady=(0, 20))
        wrapper.grid_columnconfigure(0, weight=0)
        wrapper.grid_columnconfigure(1, weight=1)
        wrapper.grid_rowconfigure(0, weight=1)

        form_card = Card(wrapper, width=300)
        form_card.grid(row=0, column=0, sticky="ns", padx=(0, 20))
        form_card.grid_propagate(False)
        inner = tk.Frame(form_card, bg=BG_CARD)
        inner.pack(fill="both", padx=18, pady=18)

        tk.Label(inner, text="Add Mess Charges", bg=BG_CARD, fg=TEXT_DARK,
                  font=(FONT_FAMILY, 12, "bold")).grid(row=0, column=0, sticky="w")
        sid_e = labeled_entry(inner, "Student ID", 1, width=20)
        month_e = labeled_entry(inner, "Month (e.g. June 2026)", 3, width=20)
        amount_e = labeled_entry(inner, "Amount (Rs)", 5, width=20)

        def add_mess_action():
            sid_text = sid_e.get().strip()
            month = month_e.get().strip()
            amount_text = amount_e.get().strip()
            if not sid_text.isdigit() or not month or not amount_text:
                messagebox.showwarning("Missing Info", "Fill all fields correctly.")
                return
            try:
                amount = float(amount_text)
            except ValueError:
                messagebox.showwarning("Invalid Amount", "Enter a valid number for amount.")
                return
            sid = int(sid_text)
            student = find_student(self.data, sid)
            if not student:
                messagebox.showerror("Not Found", "Student not found.")
                return
            mid = get_next_id(self.data, "mess")
            self.data["mess"].append({"id": mid, "student_id": sid, "month": month,
                                       "amount": amount, "status": "Unpaid"})
            save_data(self.data)
            messagebox.showinfo("Success", f"Mess charges added for {student['name']}.")
            self.show_page("mess")

        styled_button(inner, "Add Charges", add_mess_action, "primary", width=20).grid(
            row=7, column=0, sticky="w", pady=(10, 0))

        right = tk.Frame(wrapper, bg=BG_MAIN)
        right.grid(row=0, column=1, sticky="nsew")
        right.grid_rowconfigure(0, weight=1)
        right.grid_columnconfigure(0, weight=1)

        table_card = Card(right)
        table_card.grid(row=0, column=0, sticky="nsew")
        table_wrap, tree = make_table(table_card, ["ID", "Student", "Month", "Amount (Rs)", "Status"])
        table_wrap.pack(fill="both", expand=True, padx=14, pady=14)

        for m in self.data["mess"]:
            s = find_student(self.data, m["student_id"])
            sname = s["name"] if s else "Unknown"
            tree.insert("", "end", values=(m["id"], sname, m["month"], m["amount"], m["status"]))

    # ----------------------------------------------------------------- #
    #  BILLS PAGE
    # ----------------------------------------------------------------- #

    def page_bills(self):
        self.page_header("Monthly Bills", "Generate and track student bills")

        wrapper = tk.Frame(self.content, bg=BG_MAIN)
        wrapper.pack(fill="both", expand=True, padx=30, pady=(0, 20))
        wrapper.grid_columnconfigure(0, weight=0)
        wrapper.grid_columnconfigure(1, weight=1)
        wrapper.grid_rowconfigure(0, weight=1)

        form_card = Card(wrapper, width=300)
        form_card.grid(row=0, column=0, sticky="ns", padx=(0, 20))
        form_card.grid_propagate(False)
        inner = tk.Frame(form_card, bg=BG_CARD)
        inner.pack(fill="both", padx=18, pady=18)

        tk.Label(inner, text="Generate Bill", bg=BG_CARD, fg=TEXT_DARK,
                  font=(FONT_FAMILY, 12, "bold")).grid(row=0, column=0, sticky="w")
        sid_e = labeled_entry(inner, "Student ID", 1, width=20)
        month_e = labeled_entry(inner, "Month (e.g. June 2026)", 3, width=20)

        summary_label = tk.Label(form_card, text="", bg=BG_CARD, fg=TEXT_DARK,
                                   font=(FONT_FAMILY, 9), justify="left", wraplength=260)

        def generate_action():
            sid_text = sid_e.get().strip()
            month = month_e.get().strip()
            if not sid_text.isdigit() or not month:
                messagebox.showwarning("Missing Info", "Enter a valid Student ID and Month.")
                return
            sid = int(sid_text)
            student = find_student(self.data, sid)
            if not student:
                messagebox.showerror("Not Found", "Student not found.")
                return
            mess_total = sum(m["amount"] for m in self.data["mess"]
                              if m["student_id"] == sid and m["month"] == month)
            room_charge = ROOM_CHARGE_PER_MONTH if student["room_no"] else 0
            total = mess_total + room_charge
            bid = get_next_id(self.data, "bill")
            self.data["bills"].append({
                "id": bid, "student_id": sid, "month": month, "room_charges": room_charge,
                "mess_charges": mess_total, "total": total, "paid": False
            })
            save_data(self.data)
            summary_label.configure(
                text=f"Bill #{bid} for {student['name']} ({month})\n"
                     f"Room Charges: Rs {room_charge}\nMess Charges: Rs {mess_total}\n"
                     f"TOTAL: Rs {total}\nStatus: Unpaid"
            )
            summary_label.pack(padx=18, pady=(0, 10), anchor="w")
            self.show_page("bills")

        styled_button(inner, "Generate Bill", generate_action, "primary", width=20).grid(
            row=5, column=0, sticky="w", pady=(10, 0))

        right = tk.Frame(wrapper, bg=BG_MAIN)
        right.grid(row=0, column=1, sticky="nsew")
        right.grid_rowconfigure(0, weight=1)
        right.grid_columnconfigure(0, weight=1)

        table_card = Card(right)
        table_card.grid(row=0, column=0, sticky="nsew")
        table_wrap, tree = make_table(table_card,
                                       ["Bill ID", "Student", "Month", "Room", "Mess", "Total", "Status"])
        table_wrap.pack(fill="both", expand=True, padx=14, pady=(14, 6))

        for b in self.data["bills"]:
            s = find_student(self.data, b["student_id"])
            sname = s["name"] if s else "Unknown"
            status = "Paid" if b["paid"] else "Unpaid"
            tree.insert("", "end", iid=str(b["id"]),
                        values=(b["id"], sname, b["month"], b["room_charges"],
                                b["mess_charges"], b["total"], status))

        action_row = tk.Frame(table_card, bg=BG_CARD)
        action_row.pack(fill="x", padx=14, pady=(0, 14))

        def mark_paid():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning("No Selection", "Select a bill row first.")
                return
            bid = int(sel[0])
            for b in self.data["bills"]:
                if b["id"] == bid:
                    b["paid"] = True
            save_data(self.data)
            self.show_page("bills")

        styled_button(action_row, "Mark Selected as Paid", mark_paid, "success", width=22).pack(side="left")

    # ----------------------------------------------------------------- #
    #  COMPLAINTS PAGE
    # ----------------------------------------------------------------- #

    def page_complaints(self):
        self.page_header("Complaints", "File and resolve student complaints")

        wrapper = tk.Frame(self.content, bg=BG_MAIN)
        wrapper.pack(fill="both", expand=True, padx=30, pady=(0, 20))
        wrapper.grid_columnconfigure(0, weight=0)
        wrapper.grid_columnconfigure(1, weight=1)
        wrapper.grid_rowconfigure(0, weight=1)

        form_card = Card(wrapper, width=300)
        form_card.grid(row=0, column=0, sticky="ns", padx=(0, 20))
        form_card.grid_propagate(False)
        inner = tk.Frame(form_card, bg=BG_CARD)
        inner.pack(fill="both", padx=18, pady=18)

        tk.Label(inner, text="File a Complaint", bg=BG_CARD, fg=TEXT_DARK,
                  font=(FONT_FAMILY, 12, "bold")).grid(row=0, column=0, sticky="w")
        sid_e = labeled_entry(inner, "Student ID", 1, width=20)

        tk.Label(inner, text="Complaint Details", bg=BG_CARD, fg=TEXT_DARK,
                  font=(FONT_FAMILY, 10), anchor="w").grid(row=3, column=0, sticky="w", pady=(8, 2))
        text_box = tk.Text(inner, font=(FONT_FAMILY, 10), width=26, height=5, relief="solid", bd=1)
        text_box.grid(row=4, column=0, sticky="w", pady=(0, 6))

        def file_action():
            sid_text = sid_e.get().strip()
            text = text_box.get("1.0", "end").strip()
            if not sid_text.isdigit() or not text:
                messagebox.showwarning("Missing Info", "Enter Student ID and complaint text.")
                return
            sid = int(sid_text)
            student = find_student(self.data, sid)
            if not student:
                messagebox.showerror("Not Found", "Student not found.")
                return
            cid = get_next_id(self.data, "complaint")
            self.data["complaints"].append({
                "id": cid, "student_id": sid, "text": text,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M"), "status": "Pending"
            })
            save_data(self.data)
            messagebox.showinfo("Filed", f"Complaint #{cid} filed for {student['name']}.")
            self.show_page("complaints")

        styled_button(inner, "File Complaint", file_action, "primary", width=20).grid(
            row=5, column=0, sticky="w", pady=(8, 0))

        right = tk.Frame(wrapper, bg=BG_MAIN)
        right.grid(row=0, column=1, sticky="nsew")
        right.grid_rowconfigure(0, weight=1)
        right.grid_columnconfigure(0, weight=1)

        table_card = Card(right)
        table_card.grid(row=0, column=0, sticky="nsew")
        table_wrap, tree = make_table(table_card, ["ID", "Student", "Complaint", "Date", "Status"])
        table_wrap.pack(fill="both", expand=True, padx=14, pady=(14, 6))
        tree.column("Complaint", width=280)

        for c in self.data["complaints"]:
            s = find_student(self.data, c["student_id"])
            sname = s["name"] if s else "Unknown"
            tree.insert("", "end", iid=str(c["id"]),
                        values=(c["id"], sname, c["text"], c["date"], c["status"]))

        action_row = tk.Frame(table_card, bg=BG_CARD)
        action_row.pack(fill="x", padx=14, pady=(0, 14))

        def resolve_action():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning("No Selection", "Select a complaint row first.")
                return
            cid = int(sel[0])
            for c in self.data["complaints"]:
                if c["id"] == cid:
                    c["status"] = "Resolved"
            save_data(self.data)
            self.show_page("complaints")

        styled_button(action_row, "Mark Selected as Resolved", resolve_action, "success", width=24).pack(side="left")


if __name__ == "__main__":
    app = HostelApp()
    app.mainloop()