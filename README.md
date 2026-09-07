# 🚢 Costa Serena — Restaurant Schedule System
**Zero-Internet Smart Digital Schedule for Costa Serena F&B Department**

---

## 📌 1. Summary of Updated Features

1. **Python Exporter (Standalone Tool):**
   * No macro or VBA modification to company-licensed Excel.
   * Reads `.xlsx` files directly, extracts complex multi-venue tables, dates, ports, and sub-duties, and generates the WhatsApp message.
   * Copies the payload to clipboard automatically.
   * Easily bundleable to a single `.exe` file for Windows via PyInstaller when needed.

2. **Full Costa Serena Schedule Format:**
   * Parsed hierarchy: **Ceres Main**, **Ceres Refilling Teams (A & B)**, **Ceres Resetting Team**, **Ceres Labeling Team**, **Ceres Upper**, **Vesta Upper**, **Buffet Deck 9 (Prometeo)**, **Specialty Outlets (Noodle Bar, Pizzeria, Salty Beach, Sushino, Casanova, Steakhouse, Hot Pot)**, **Travel Talk Uniforms**, and **Sick Leave**.

3. **Smart Personalization & Dynamic Reporting Pill:**
   * **User Greeting Bar:** Displays `👋 Welcome, <FULL NAME> #<ID>` above the date/port banner.
   * **Personal Shift Pill:** Highlights the exact venue & report time (e.g. `CERES MAIN • 11:00`, `REFILLING A • 10:45`, `BUFFET 9 • 07:00`) directly on the top banner!
   * **Smart Name Matching:** Matches crew full names accurately across separate first/last name columns without false substring hits.
   * **Persistent Storage:** Stored in device local memory (persists on both Android APK and iPhone single-file HTML).

---

## 📂 2. File & Directory Structure

```text
/Schedule Costa/
├── exporter.py                      --> Python Desktop Schedule Exporter (CLI / Script)
├── CostaSchedule.apk                --> Standalone Offline Android APK (Installed on phone)
├── CostaSchedule.html               --> Portable Single-File WebApp for iPhone / Mac
│
├── web/                             --> WebApp / PWA Source Files
│   ├── index.html                   --> Costa Serena UI (100% English)
│   ├── style.css                    --> Responsive Navy & Gold Theme
│   ├── app.js                       --> Smart Name Matcher, Parser & Engine
│   ├── manifest.json                --> PWA Manifest
│   └── sw.js                        --> Service Worker for Offline Cache
│
└── sample/                          --> Test Files
    ├── Costa_Serena_Schedule_Sample.xlsx --> Sample Excel spreadsheet (Kaohsiung)
    ├── create_sample_excel.py       --> Script to generate sample Excel
    └── sample_whatsapp_messages.txt --> Ready-to-copy WhatsApp test messages
```

---

## 💻 3. How to Use the Python Exporter

Run in Terminal:
```bash
# Export active schedule from Excel to WhatsApp clipboard
python3 exporter.py sample/Costa_Serena_Schedule_Sample.xlsx

# Export with specific shift override:
python3 exporter.py sample/Costa_Serena_Schedule_Sample.xlsx --shift DINNER
```
*The script will automatically parse the schedule and copy the WhatsApp message to your clipboard!*

---

## 📱 4. How to Use on iPhone & Android

* **On Android:** Open the pre-installed **Costa Schedule** app from your home screen / app drawer.
* **On iPhone:** AirDrop [`CostaSchedule.html`](file:///Users/dianjulie/Documents/Schedule%20Costa/CostaSchedule.html) to the iPhone, open it in **Files** / **Safari**, tap **Share** &rarr; **Add to Home Screen**.
