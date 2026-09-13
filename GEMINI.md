# Schedule Costa — Project Guidelines & Rules

## 📌 Aturan Wajib (Mandatory Rules)

### 1. Git Tracker & Auto Commit/Push
- **Setiap ada progress / perubahan / penambahan fitur / pemolesan UI pada project, WAJIB SELALU lakukan commit dan push ke git (`git push origin main`)**.
- Tujuannya adalah agar riwayat progress selalu tercatat rapi sebagai tracker.
- Jangan tunggu diingatkan oleh user; jalankan git commit & push otomatis di setiap selesai melakukan task atau progress.
- Format pesan commit: ringkas, jelas, dan representatif (contoh: `feat: ...`, `refactor: ...`, `ui: ...`, `fix: ...`).

### 2. Status Komponen Proyek
- **HTML (`CostaSchedule.html`, `web/`)**: Selesai / Done.
- **Android APK (`CostaSchedule.apk`, `android/`)**: Selesai / Done.
- **Desktop Application (`app_desktop.py`)**: Area fokus saat ini (pemangkasan elemen UI yang tidak diperlukan, pemolesan tampilan, performa, dan kegunaan).
- **Desain & Brand Guidelines**: Tetap mengacu pada estetika Costa Cruises di `costaassets/` (tipografi Poppins, warna Costa Blue `#0071A3`, aksen Costa Gold `#F9B000`, zero emojis, editorial light theme).

### 3. Production Build Pipeline (Auto-Minify)
- **Source code yang di-edit** ada di `web/app.js`, `web/style.css`, `web/index.html` — file-file ini HARUS selalu tetap READABLE (tidak di-minify) untuk keperluan maintenance.
- **`CostaSchedule.html`** adalah output build production — JANGAN edit langsung. Selalu generate ulang via build script.
- **Setiap kali ada perubahan pada file di `web/`**, WAJIB rebuild `CostaSchedule.html` dengan menjalankan:
  ```bash
  python3 build_single_html.py
  ```
  Script ini otomatis:
  - Minify JavaScript via `terser` (industri standar, reversible via beautifier)
  - Minify CSS (strip komentar, collapse whitespace)
  - Strip HTML comments
  - Inline semua assets (font, CSS, JS, logo) ke single-file HTML
  - Sync assets ke `android/app/src/main/assets/`
- **JANGAN pernah** memasukkan komentar bergaya AI/chatbot ke source code (contoh: "Here's the updated function", "As requested by user"). Kode harus terlihat ditulis profesional oleh developer manusia.

### 4. Folder Structure & Deliverable Boundaries
- **`web/`** — Source code HTML app (editable, readable, TIDAK di-minify)
- **`CostaSchedule.html`** — Production build output (minified, single-file, distributable)
- **`desktop_web/`** — Source code Desktop Exporter HTML app (editable, readable, unminified)
- **`CostaExporter.html`** — Production build output Desktop Exporter (minified, single-file, zero-install)
- **`build_desktop_html.py`** — Build script untuk me-rebuild `CostaExporter.html` dari `desktop_web/`
- **`app_desktop.py`** — Desktop exporter app (Python + customtkinter)
- **`app.py` + `frontend/`** — Desktop app alternatif (Python + pywebview + React)
- **`exporter.py`** — Core parsing & encoding engine (shared oleh semua app)
- **`dev-tools/`** — File development-only (server diagnostik, test tools). TIDAK untuk end-user.
- **`costaassets/`** — Brand assets (font Poppins, design tokens, guidelines)
- **`sample/`** — Sample Excel roster untuk demo/presentasi
- **`Save Data/`** — Auto-generated backup folder dari desktop app

### 5. Security & Code Quality Standards
- **TIDAK BOLEH** menggunakan `eval()`, `exec()`, `shell=True`, `Function()`, `document.write()`, atau `__import__()` di seluruh codebase.
- **Semua subprocess** harus pakai list syntax: `subprocess.Popen(["cmd", "arg"])`, BUKAN string.
- **Semua user-facing data** yang masuk ke `innerHTML` HARUS melalui `escapeHtml()` di sisi JS, atau text-safe rendering di sisi Python (tkinter `.configure(text=...)`).
- **File path** selalu dibangun via `os.path.join()` relative ke `__file__`, TIDAK hardcode absolute path kecuali di build script.
- Project ini 100% standalone offline — TIDAK ADA network calls, TIDAK ADA backend server di production. Data ditransfer via QR code / WhatsApp paste.
