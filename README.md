# Simple Invoice System

A simple backend system for generating and managing invoices using Python.

---

## 🚀 Features
- Create invoices
- Store invoice data
- Export data (PDF/Excel ready)
- FastAPI backend (if applicable)

---

## 🛠 Tech Stack
- Python
- FastAPI
- SQLite
- ReportLab (PDF generation)
- Pandas (Excel export)

---

## 📂 Project Structure
- main.py → API entry point
- pdf_parser.py → PDF handling
- excel_export.py → Excel export logic
- faktura.db → database (ignored in git)

---

## ▶️ How to Run

```bash
pip install -r requirements.txt
uvicorn main:app --reload