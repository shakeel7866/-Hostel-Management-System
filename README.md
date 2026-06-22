# 🏠 Hostel Management System (Tkinter GUI)

A desktop application for managing hostel students, rooms, mess charges, monthly bills, and complaints — built entirely with Python's built-in **Tkinter** library, with optional **Pillow** support for previewing attached receipt images.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Tkinter](https://img.shields.io/badge/GUI-Tkinter-orange)
![License](https://img.shields.io/badge/License-MIT-green)

---

## ✨ Features

- **Dashboard** — live stats: total students, total rooms, beds occupied, pending complaints, and recent complaints feed.
- **Students** — add students (name, CNIC, contact, department, semester) and search/filter the list instantly.
- **Rooms** — add rooms with bed capacity, assign students to rooms, see occupancy status at a glance.
- **Roommates** — view who shares a room, move a student to a different room, or remove them from their current room.
- **Mess Management**
  - Date field auto-fills with **today's date** but is fully **editable**.
  - **Day of the week auto-updates** as the date is typed/edited.
  - Live totals for **Total Mess Charges** and **Unpaid Mess Charges**.
  - Toggle each entry between Paid / Unpaid.
  - **Attach a receipt image** (photo/scan of a paper receipt) to any mess entry and view it anytime.
- **Monthly Bills**
  - **Editable** Room Charges, Mess Charges, and Other Charges (all in Rs).
  - **"Pull Mess Total"** button auto-fills mess charges for the selected student/month — fully overridable.
  - **Live running total** as you edit any charge field.
  - Mark bills Paid/Unpaid, generate a printable on-screen receipt, and **attach/view a receipt image**.
  - Collection summary cards: Total Billed, Collected, Pending, Unpaid Bills.
- **Complaints** — file complaints per student and mark them Resolved.
- **Local persistence** — all data auto-saves to `hostel_data.json` in the project folder; no database setup required.
- **Receipt images** — saved into a local `receipts/` folder and linked to the relevant mess/bill record.

---

## 📦 Requirements

- Python 3.8+
- Tkinter (included with most standard Python installations)
- [Pillow](https://pypi.org/project/Pillow/) — optional, only needed to preview attached receipt images

Install Pillow if you want receipt image previews:

```bash
pip install pillow
```

> If Tkinter is missing on Linux, install it with:
> `sudo apt-get install python3-tk`

---

## 🚀 Getting Started

1. Clone the repository:
   ```bash
   git clone https://github.com/<your-username>/<your-repo>.git
   cd <your-repo>
   ```

2. (Optional) Install Pillow for receipt image previews:
   ```bash
   pip install pillow
   ```

3. Run the app:
   ```bash
   python hostel_management_gui.py
   ```

That's it — no database or server setup needed. The app creates `hostel_data.json` and a `receipts/` folder automatically on first run.

---

## 🗂️ Project Structure

```
.
├── hostel_management_gui.py   # Main application (run this)
├── hostel_data.json            # Auto-created — stores all app data
├── receipts/                   # Auto-created — stores attached receipt images
└── README.md
```

---

## 🖼️ Attaching Receipt Images

1. Go to the **Mess** or **Monthly Bills** page.
2. Select a row in the table.
3. Click **Attach Receipt** (Mess) or **Attach Receipt Image** (Bills).
4. Choose a photo/scan of the paper receipt from your computer.
5. Click **View Receipt** anytime to preview it in a popup window.

---

## ⚙️ Configuration

- `ROOM_CHARGE_PER_MONTH` in `hostel_management_gui.py` sets the default room charge suggestion (currently `5000`). This is just a starting value — it's fully editable per bill.

---

## 🤝 Contributing

Issues and pull requests are welcome. If you spot a bug or want a new feature (e.g. calendar date-picker, multi-currency support, PDF receipt export), feel free to open an issue.

---

## 📄 License

This project is released under the MIT License — feel free to use, modify, and distribute it.
