#!/usr/bin/env python3
"""
Costa Cruises — Schedule Exporter (Modern Edition)
═══════════════════════════════════════════════════
Python backend + React frontend via pywebview
Fully offline, native OS window, web-grade UI
═══════════════════════════════════════════════════
"""

import os
import sys
import json
import datetime
import webbrowser
import webview

from exporter import parse_schedule_excel, generate_payload, copy_to_clipboard


class BackendApi:
    """Python API exposed to React frontend via pywebview JS bridge.
    
    Every public method here becomes available as:
      window.pywebview.api.method_name() → returns a Promise
    """

    def __init__(self):
        self._window = None
        self._current_file = self._find_default_sample()
        self._schedule_data = None
        self._payload = ""
        self._b64_data = ""

    def set_window(self, window):
        self._window = window

    # ── File Discovery ──
    def _find_default_sample(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        sample_path = os.path.join(base_dir, "sample", "Costa_Serena_Schedule_Sample.xlsx")
        if os.path.exists(sample_path):
            return sample_path
        return ""

    # ── API Methods (called from JavaScript) ──

    def get_initial_data(self):
        """Auto-parse default sample file on app launch."""
        if self._current_file and os.path.exists(self._current_file):
            return self.parse_schedule(self._current_file, "LUNCH")
        return {"status": "no_file", "file": ""}

    def browse_file(self):
        """Open native OS file dialog and return selected path."""
        if not self._window:
            return {"status": "error", "message": "Window not ready"}

        result = self._window.create_file_dialog(
            webview.OPEN_DIALOG,
            allow_multiple=False,
            file_types=("Excel Files (*.xlsx;*.xls)", "All Files (*.*)")
        )

        if result and len(result) > 0:
            self._current_file = result[0]
            return {"status": "ok", "file": self._current_file}
        return {"status": "cancelled"}

    def parse_schedule(self, file_path=None, shift="LUNCH"):
        """Parse Excel schedule and generate payload."""
        target = file_path or self._current_file
        if not target or not os.path.exists(target):
            return {"status": "error", "message": "File not found"}

        try:
            self._current_file = target
            self._schedule_data = parse_schedule_excel(target, shift)
            self._payload, self._b64_data = generate_payload(self._schedule_data)

            # Compute crew count
            all_crew_names = set()
            for v in self._schedule_data.get("venues", []):
                for a in v.get("assignments", []):
                    if a.get("waiterName"):
                        all_crew_names.add(a["waiterName"])
                    if a.get("attendantName"):
                        all_crew_names.add(a["attendantName"])
            for b in self._schedule_data.get("buffetAndVenues", []):
                for c in b.get("crew", []):
                    if c.get("name"):
                        all_crew_names.add(c["name"])
            for s in self._schedule_data.get("sideDuties", []):
                for c in s.get("crew", []):
                    if c.get("name"):
                        all_crew_names.add(c["name"])
            for sk in self._schedule_data.get("sickLeave", []):
                if sk.get("name"):
                    all_crew_names.add(sk["name"])

            total_sections = (
                len(self._schedule_data.get("venues", []))
                + len(self._schedule_data.get("buffetAndVenues", []))
                + len(self._schedule_data.get("sideDuties", []))
            )

            total_stations = sum(
                len(v.get("assignments", []))
                for v in self._schedule_data.get("venues", [])
            )

            return {
                "status": "ok",
                "file": os.path.basename(target),
                "filePath": target,
                "data": self._schedule_data,
                "payload": self._payload,
                "b64Length": len(self._b64_data),
                "telemetry": {
                    "crewCount": len(all_crew_names),
                    "sectionCount": total_sections,
                    "stationCount": total_stations,
                    "payloadChars": len(self._payload),
                    "b64Bytes": len(self._b64_data),
                }
            }
        except Exception as err:
            return {"status": "error", "message": str(err)}

    def parse_schedule_from_base64(self, b64_content, filename="dropped_schedule.xlsx", shift="LUNCH"):
        """Parse Excel file uploaded or dropped directly from frontend via Base64."""
        if not b64_content:
            return {"status": "error", "message": "No file content provided"}
        try:
            import base64
            import tempfile

            if "," in b64_content:
                b64_content = b64_content.split(",", 1)[1]
            raw_bytes = base64.b64decode(b64_content)

            temp_dir = os.path.join(tempfile.gettempdir(), "costa_schedules")
            os.makedirs(temp_dir, exist_ok=True)
            temp_path = os.path.join(temp_dir, filename)
            with open(temp_path, "wb") as f:
                f.write(raw_bytes)

            return self.parse_schedule(temp_path, shift)
        except Exception as err:
            return {"status": "error", "message": f"Failed to parse dropped Excel file: {str(err)}"}

    def update_schedule_data(self, data):
        """Update active schedule data from edits, regenerate payload & telemetry."""
        if not data:
            return {"status": "error", "message": "No data provided"}

        try:
            self._schedule_data = data
            self._payload, self._b64_data = generate_payload(self._schedule_data)

            # Compute crew count
            all_crew_names = set()
            for v in self._schedule_data.get("venues", []):
                for a in v.get("assignments", []):
                    if a.get("waiterName"):
                        all_crew_names.add(a["waiterName"])
                    if a.get("attendantName"):
                        all_crew_names.add(a["attendantName"])
            for b in self._schedule_data.get("buffetAndVenues", []):
                for c in b.get("crew", []):
                    if c.get("name"):
                        all_crew_names.add(c["name"])
            for s in self._schedule_data.get("sideDuties", []):
                for c in s.get("crew", []):
                    if c.get("name"):
                        all_crew_names.add(c["name"])
            for sk in self._schedule_data.get("sickLeave", []):
                if sk.get("name"):
                    all_crew_names.add(sk["name"])

            total_sections = (
                len(self._schedule_data.get("venues", []))
                + len(self._schedule_data.get("buffetAndVenues", []))
                + len(self._schedule_data.get("sideDuties", []))
            )

            total_stations = sum(
                len(v.get("assignments", []))
                for v in self._schedule_data.get("venues", [])
            )

            return {
                "status": "ok",
                "payload": self._payload,
                "b64Length": len(self._b64_data),
                "telemetry": {
                    "crewCount": len(all_crew_names),
                    "sectionCount": total_sections,
                    "stationCount": total_stations,
                    "payloadChars": len(self._payload),
                    "b64Bytes": len(self._b64_data),
                }
            }
        except Exception as err:
            return {"status": "error", "message": str(err)}

    def save_json_backup(self, data=None):
        """Save active (edited or unedited) schedule data to 'Save Data' folder with timestamp."""
        target_data = data if data is not None else self._schedule_data
        if not target_data:
            return {"status": "error", "message": "No schedule data to save"}

        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            save_dir = os.path.join(base_dir, "Save Data")
            os.makedirs(save_dir, exist_ok=True)

            now_str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            ship_slug = str(target_data.get("ship", "Costa")).replace(" ", "_")
            meal_slug = str(target_data.get("meal", "Schedule")).replace(" ", "_")
            filename = f"{ship_slug}_{meal_slug}_{now_str}.json"
            filepath = os.path.join(save_dir, filename)

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(target_data, f, indent=2, ensure_ascii=False)

            return {
                "status": "ok",
                "filename": filename,
                "filePath": filepath,
                "folder": "Save Data",
                "timestamp": now_str
            }
        except Exception as err:
            return {"status": "error", "message": str(err)}

    def copy_payload(self):
        """Copy current payload to system clipboard."""
        if not self._payload:
            return {"status": "error", "message": "No payload generated"}

        success = copy_to_clipboard(self._payload)
        return {
            "status": "ok" if success else "fallback",
            "chars": len(self._payload)
        }

    def copy_text(self, text):
        """Copy arbitrary text to system clipboard."""
        if not text:
            return {"status": "error", "message": "No text provided"}
        success = copy_to_clipboard(text)
        return {"status": "ok" if success else "error"}

    def export_json(self):
        """Save schedule data as JSON via native save dialog."""
        if not self._schedule_data:
            return {"status": "error", "message": "No data to export"}
        if not self._window:
            return {"status": "error", "message": "Window not ready"}

        result = self._window.create_file_dialog(
            webview.SAVE_DIALOG,
            save_filename="costa_schedule.json",
            file_types=("JSON Files (*.json)",)
        )

        if result:
            path = result if isinstance(result, str) else result[0] if result else None
            if path:
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(self._schedule_data, f, indent=2, ensure_ascii=False)
                return {"status": "ok", "path": path}
        return {"status": "cancelled"}

    def open_webapp(self):
        """Open the HTML webapp in default browser."""
        base_dir = os.path.dirname(os.path.abspath(__file__))
        html_path = os.path.join(base_dir, "CostaSchedule.html")
        if os.path.exists(html_path):
            webbrowser.open(f"file://{html_path}")
            return {"status": "ok"}
        return {"status": "error", "message": "CostaSchedule.html not found"}

    def get_payload_text(self):
        """Return the current payload text."""
        return self._payload or ""


def get_entrypoint():
    """
    Returns Vite dev server URL in development,
    or bundled dist/index.html path in production / PyInstaller.
    """
    dev_mode = os.environ.get("ENV") == "development"
    if dev_mode:
        return "http://localhost:5173"

    # In PyInstaller, files are unpacked to sys._MEIPASS
    if getattr(sys, "frozen", False):
        base_dir = sys._MEIPASS
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))

    # Try frontend/dist first (development layout), then dist/ (bundled)
    for candidate in ["frontend/dist/index.html", "dist/index.html"]:
        full = os.path.join(base_dir, candidate)
        if os.path.exists(full):
            return full

    # Fallback
    return os.path.join(base_dir, "frontend", "dist", "index.html")


def main():
    api = BackendApi()

    window = webview.create_window(
        title="Costa Cruises — Schedule Exporter",
        url=get_entrypoint(),
        js_api=api,
        width=1200,
        height=840,
        min_size=(980, 720),
        background_color="#050506",
    )
    api.set_window(window)

    webview.start(debug=("--debug" in sys.argv), http_server=True)


if __name__ == "__main__":
    main()
