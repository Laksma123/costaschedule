#!/usr/bin/env python3
"""
Costa Cruises — Restaurant Schedule Exporter
Desktop Edition — Newspaper Light Theme
Matches CostaSchedule.html visual system:
  White canvas, Poppins type, zero emoji,
  thin-line borders, Costa blue + yellow accents.
"""

import sys
import os
import json
import datetime
import webbrowser
from PIL import Image as PILImage
import customtkinter as ctk
from tkinter import filedialog, messagebox

import socket
import http.server
import socketserver
import threading
import html

import qrcode
from qrcode.constants import ERROR_CORRECT_L

from exporter import parse_schedule_excel, generate_payload, generate_compressed_payload, copy_to_clipboard

# ─────────────────────────────────────────────────────────────
# NEWSPAPER LIGHT DESIGN TOKENS  (matches CostaSchedule.html)
# ─────────────────────────────────────────────────────────────
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

TK = {
    # Surfaces
    "bg_base":        "#FFFFFF",
    "bg_elevated":    "#FFFFFF",
    "surface":        "#FFFFFF",
    "surface_card":   "#FFFFFF",
    "surface_inner":  "#F8FAFC",
    "surface_hover":  "#F1F5F9",
    "surface_active": "#E2E8F0",
    "surface_badge":  "#EBF5FA",

    # Borders (thin hairlines like newspaper columns)
    "border_subtle":  "#F1F5F9",
    "border_card":    "#E2E8F0",
    "border_hover":   "#CBD5E1",
    "border_focus":   "#0071A3",

    # Costa brand
    "accent":         "#0071A3",
    "accent_hover":   "#005F8A",
    "accent_dim":     "#EBF5FA",
    "accent_bg":      "#EBF5FA",

    # Costa yellow — primary CTA, selection
    "gold_accent":    "#F9B000",
    "gold_hover":     "#E09E00",
    "gold_dim":       "#FFF8E8",

    # Status triples
    "good_bg":        "#F1F9F5",
    "good_border":    "#C9E5D6",
    "good_ink":       "#1F7A54",
    "warn_bg":        "#FFF8E8",
    "warn_border":    "#F7DFA6",
    "warn_ink":       "#6B4E00",
    "bad_bg":         "#FCF2F0",
    "bad_border":     "#EFCFC8",
    "bad_ink":        "#B3402E",

    # Typography — Costa InterfaceGuidelines.md
    "fg_primary":     "#0A2A38",   # costa-ink
    "fg_secondary":   "#5F7079",   # costa-slate
    "fg_subtle":      "#94A6AE",   # costa-faint
    "fg_accent":      "#0071A3",
    "fg_gold":        "#F9B000",
}


# ─────────────────────────────────────────────────────────────
# FONT POOL  (create once, reuse everywhere)
# ─────────────────────────────────────────────────────────────
class Fonts:
    """Pre-allocated font objects to avoid repeated CTkFont creation."""
    _cache = {}

    @classmethod
    def get(cls, key):
        if key not in cls._cache:
            cls._cache = {
                "brand_lg":   ctk.CTkFont(family="Poppins", size=18, weight="bold"),
                "brand_sm":   ctk.CTkFont(family="Poppins", size=11, weight="bold"),
                "h1":         ctk.CTkFont(family="Poppins", size=20, weight="bold"),
                "h2":         ctk.CTkFont(family="Poppins", size=14, weight="bold"),
                "h3":         ctk.CTkFont(family="Poppins", size=12, weight="bold"),
                "body":       ctk.CTkFont(family="Poppins", size=12),
                "body_bold":  ctk.CTkFont(family="Poppins", size=12, weight="bold"),
                "small":      ctk.CTkFont(family="Poppins", size=10),
                "small_bold": ctk.CTkFont(family="Poppins", size=10, weight="bold"),
                "tiny":       ctk.CTkFont(family="Poppins", size=9, weight="bold"),
                "mono":       ctk.CTkFont(family="SF Mono", size=11),
                "mono_sm":    ctk.CTkFont(family="SF Mono", size=10),
                "btn":        ctk.CTkFont(family="Poppins", size=13, weight="bold"),
                "btn_sm":     ctk.CTkFont(family="Poppins", size=11, weight="bold"),
                "tab":        ctk.CTkFont(family="Poppins", size=11, weight="bold"),
                "stat_val":   ctk.CTkFont(family="Poppins", size=16, weight="bold"),
                "qr_label":   ctk.CTkFont(family="Poppins", size=11),
            }
        return cls._cache[key]


# ─────────────────────────────────────────────────────────────
# NETWORK & WEB BRIDGE HELPERS (3-Step Transfer Flow)
# ─────────────────────────────────────────────────────────────
def find_available_port(start_port=8080, max_tries=20):
    for port in range(start_port, start_port + max_tries):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('0.0.0.0', port))
                return port
        except OSError:
            continue
    return start_port

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
    except Exception:
        try:
            ip = socket.gethostbyname(socket.gethostname())
        except Exception:
            ip = '127.0.0.1'
    finally:
        s.close()
    return ip


class ScheduleHttpHandler(http.server.BaseHTTPRequestHandler):
    """Serve a clean, responsive mobile webpage for the manager's phone."""

    def log_message(self, format, *args):
        pass  # Quiet logging

    def do_GET(self):
        app = getattr(self.server, "costa_app", None)
        if not app or not app.schedule_data:
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"<html><body style='font-family:sans-serif;padding:24px;text-align:center;'><h2>Costa Schedule Bridge</h2><p>No schedule loaded in desktop app.</p></body></html>")
            return

        d = app.schedule_data
        ship = html.escape(str(d.get("ship", "COSTA SMERALDA")))
        date_val = html.escape(str(d.get("date", "—")))
        port_val = html.escape(str(d.get("port", "—")))
        shift_val = html.escape(str(d.get("shift", "—")))
        crew_count = app._cached_crew_count
        raw_msg = app.payload or ""

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>Costa Schedule — WhatsApp Bridge</title>
  <style>
    :root {{
      --bg: #F8FAFC;
      --card: #FFFFFF;
      --text: #0A2A38;
      --subtext: #4A6572;
      --border: #E2E8F0;
      --yellow: #F2B832;
      --yellow-hover: #D9A020;
      --blue: #003B95;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      background-color: var(--bg);
      color: var(--text);
      padding: 16px;
      line-height: 1.5;
    }}
    .container {{
      max-width: 480px;
      margin: 0 auto;
    }}
    .header {{
      text-align: center;
      padding: 16px 0 16px 0;
      border-bottom: 2px solid var(--border);
      margin-bottom: 16px;
    }}
    .brand {{
      font-size: 20px;
      font-weight: 800;
      letter-spacing: 0.5px;
      color: var(--text);
    }}
    .dot {{ color: var(--yellow); }}
    .subtitle {{
      font-size: 11px;
      font-weight: 700;
      color: var(--subtext);
      letter-spacing: 1px;
      margin-top: 2px;
    }}
    .meta-card {{
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 14px 16px;
      margin-bottom: 16px;
    }}
    .meta-row {{
      display: flex;
      justify-content: space-between;
      margin-bottom: 6px;
      font-size: 13px;
    }}
    .meta-label {{ color: var(--subtext); }}
    .meta-value {{ font-weight: 600; color: var(--text); }}
    .actions {{
      display: flex;
      flex-direction: column;
      gap: 10px;
      margin-bottom: 16px;
    }}
    .btn {{
      display: block;
      width: 100%;
      padding: 14px;
      border-radius: 10px;
      font-size: 14px;
      font-weight: 700;
      text-align: center;
      text-decoration: none;
      border: none;
      cursor: pointer;
      transition: all 0.2s;
    }}
    .btn-yellow {{
      background: var(--yellow);
      color: #0A2A38;
      box-shadow: 0 2px 4px rgba(0,0,0,0.06);
    }}
    .btn-yellow:active {{
      background: var(--yellow-hover);
    }}
    .btn-outline {{
      background: var(--card);
      color: var(--text);
      border: 1px solid var(--border);
    }}
    .preview-box {{
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 12px;
      margin-bottom: 16px;
    }}
    .preview-title {{
      font-size: 11px;
      font-weight: 700;
      color: var(--subtext);
      text-transform: uppercase;
      letter-spacing: 0.5px;
      margin-bottom: 8px;
    }}
    textarea {{
      width: 100%;
      height: 120px;
      font-family: monospace;
      font-size: 11px;
      color: var(--subtext);
      background: #F1F5F9;
      border: 1px solid var(--border);
      border-radius: 6px;
      padding: 8px;
      resize: none;
      white-space: pre;
    }}
    .instructions {{
      font-size: 12px;
      color: var(--subtext);
      text-align: center;
      line-height: 1.6;
    }}
    .toast {{
      position: fixed;
      bottom: 20px;
      left: 50%;
      transform: translateX(-50%);
      background: #0A2A38;
      color: #FFFFFF;
      padding: 10px 20px;
      border-radius: 20px;
      font-size: 13px;
      font-weight: 600;
      box-shadow: 0 4px 12px rgba(0,0,0,0.15);
      display: none;
      z-index: 100;
    }}
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <div class="brand">{ship}<span class="dot">.</span></div>
      <div class="subtitle">RESTAURANT SCHEDULE BRIDGE</div>
    </div>

    <div class="meta-card">
      <div class="meta-row">
        <span class="meta-label">Date</span>
        <span class="meta-value">{date_val}</span>
      </div>
      <div class="meta-row">
        <span class="meta-label">Port</span>
        <span class="meta-value">{port_val}</span>
      </div>
      <div class="meta-row">
        <span class="meta-label">Shift</span>
        <span class="meta-value">{shift_val}</span>
      </div>
      <div class="meta-row" style="margin-bottom:0;">
        <span class="meta-label">Active Crew</span>
        <span class="meta-value">{crew_count} Persons</span>
      </div>
    </div>

    <div class="actions">
      <button class="btn btn-yellow" onclick="copySchedule()">
        COPY FOR WHATSAPP GROUP
      </button>
      <a id="waDirectBtn" class="btn btn-outline" href="#">
        OPEN DIRECTLY IN WHATSAPP
      </a>
    </div>

    <div class="preview-box">
      <div class="preview-title">Payload Preview</div>
      <textarea id="payloadText" readonly></textarea>
    </div>

    <div class="instructions">
      Step 3 of 3: Tap <b>Copy for WhatsApp</b>, then switch to WhatsApp and paste into the crew group. Crew members will copy it into their Costa Schedule App.
    </div>
  </div>

  <div id="toast" class="toast">COPIED TO CLIPBOARD!</div>

  <script>
    var rawText = {json.dumps(raw_msg)};
    document.getElementById('payloadText').value = rawText;
    document.getElementById('waDirectBtn').href = 'whatsapp://send?text=' + encodeURIComponent(rawText);

    function copySchedule() {{
      if (navigator.clipboard && navigator.clipboard.writeText) {{
        navigator.clipboard.writeText(rawText).then(showToast).catch(fallbackCopy);
      }} else {{
        fallbackCopy();
      }}
    }}

    function fallbackCopy() {{
      var ta = document.getElementById('payloadText');
      ta.select();
      document.execCommand('copy');
      showToast();
    }}

    function showToast() {{
      var t = document.getElementById('toast');
      t.style.display = 'block';
      setTimeout(function() {{ t.style.display = 'none'; }}, 2500);
    }}
  </script>
</body>
</html>"""
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        encoded = html_content.encode("utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)


class ScheduleHttpServer:
    """Zero-dependency local HTTP micro-server for 1-QR mobile bridge."""

    def __init__(self, app_instance):
        self.app = app_instance
        self.port = find_available_port(8080)
        self.ip = get_local_ip()
        self.server = None
        self.thread = None

    @property
    def url(self):
        return f"http://{self.ip}:{self.port}"

    def start(self):
        try:
            self.server = socketserver.ThreadingTCPServer(('0.0.0.0', self.port), ScheduleHttpHandler)
            self.server.costa_app = self.app
            self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
            self.thread.start()
            print(f"[WebBridge] Server started on {self.url}")
            return True
        except Exception as e:
            print(f"[WebBridge] Failed to start server: {e}")
            return False

    def stop(self):
        if self.server:
            try:
                self.server.shutdown()
                self.server.server_close()
            except Exception:
                pass


class QRModal(ctk.CTkToplevel):
    """High-resolution modal dialog for Airgap QR scanning (pure black, integer scaled)."""

    def __init__(self, parent, segments, meta_info=None):
        super().__init__(parent)
        self.title("Costa Cruises — Airgap QR Codes")
        self.geometry("620x720")
        self.resizable(False, False)
        self.configure(fg_color=TK["bg_base"])

        self.segments = segments or []
        self.meta_info = meta_info or {}
        self.current_idx = 0
        self._qr_ref = None

        self.transient(parent)
        self.grab_set()

        self._build_ui()
        self._bind_keys()
        self._show_segment(0)

        # Center on parent window
        self.update_idletasks()
        try:
            x = parent.winfo_x() + (parent.winfo_width() - 620) // 2
            y = parent.winfo_y() + (parent.winfo_height() - 720) // 2
            self.geometry(f"+{max(0, x)}+{max(0, y)}")
        except Exception:
            pass

    def _build_ui(self):
        # Top Blue Accent Line
        ctk.CTkFrame(self, height=3, fg_color=TK["accent"], corner_radius=0).pack(fill="x")

        # Header Frame
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", padx=24, pady=(16, 8))

        title_frame = ctk.CTkFrame(hdr, fg_color="transparent")
        title_frame.pack(side="left")

        brand_row = ctk.CTkFrame(title_frame, fg_color="transparent")
        brand_row.pack(anchor="w")
        ctk.CTkLabel(brand_row, text="AIRGAP QR TRANSFER", font=Fonts.get("brand_lg"), text_color=TK["fg_primary"]).pack(side="left")
        ctk.CTkLabel(brand_row, text=".", font=Fonts.get("brand_lg"), text_color=TK["gold_accent"]).pack(side="left")

        self.lbl_subtitle = ctk.CTkLabel(
            title_frame, text="Zero network or cables required — Strict ship IT compliant",
            font=Fonts.get("small_bold"), text_color=TK["fg_subtle"], anchor="w"
        )
        self.lbl_subtitle.pack(anchor="w")

        # Close button top right
        ctk.CTkButton(
            hdr, text="Close (Esc)", font=Fonts.get("btn_sm"),
            fg_color=TK["surface_hover"], hover_color=TK["surface_active"],
            border_width=1, border_color=TK["border_card"],
            text_color=TK["fg_secondary"], width=85, height=30, corner_radius=6,
            command=self.destroy
        ).pack(side="right")

        # Hairline
        ctk.CTkFrame(self, height=1, fg_color=TK["border_card"], corner_radius=0).pack(fill="x", padx=24)

        # Main QR Container Box (480x480)
        self.qr_box = ctk.CTkFrame(
            self, width=480, height=480,
            fg_color="#FFFFFF", corner_radius=8,
            border_width=1, border_color=TK["border_card"]
        )
        self.qr_box.pack(pady=12)
        self.qr_box.pack_propagate(False)

        self.qr_image_label = ctk.CTkLabel(self.qr_box, text="")
        self.qr_image_label.pack(expand=True)

        # Instructions Banner
        self.lbl_step = ctk.CTkLabel(
            self, text="Point phone camera at QR, copy text, then paste into WhatsApp.",
            font=Fonts.get("h3"), text_color=TK["fg_primary"]
        )
        self.lbl_step.pack(pady=(0, 10))

        # Navigation Bar
        nav = ctk.CTkFrame(self, fg_color="transparent")
        nav.pack(fill="x", padx=24, pady=(0, 14))

        self.btn_prev = ctk.CTkButton(
            nav, text="◀ PREVIOUS PART",
            font=Fonts.get("btn_sm"),
            fg_color=TK["surface_hover"], hover_color=TK["surface_active"],
            border_width=1, border_color=TK["border_card"],
            text_color=TK["fg_primary"], height=38, corner_radius=8,
            command=self._on_prev
        )
        self.btn_prev.pack(side="left", fill="x", expand=True, padx=(0, 8))

        self.lbl_indicator = ctk.CTkLabel(
            nav, text="1 / 4", font=Fonts.get("brand_lg"),
            text_color=TK["fg_primary"], width=70
        )
        self.lbl_indicator.pack(side="left", padx=6)

        self.btn_next = ctk.CTkButton(
            nav, text="NEXT PART ▶",
            font=Fonts.get("btn_sm"),
            fg_color=TK["gold_accent"], hover_color=TK["gold_hover"],
            text_color=TK["fg_primary"], height=38, corner_radius=8,
            command=self._on_next
        )
        self.btn_next.pack(side="left", fill="x", expand=True, padx=(8, 0))

    def _bind_keys(self):
        self.bind("<Left>", lambda e: self._on_prev())
        self.bind("<Right>", lambda e: self._on_next())
        self.bind("<space>", lambda e: self._on_next())
        self.bind("<Escape>", lambda e: self.destroy())

    def _on_prev(self):
        if self.current_idx > 0:
            self._show_segment(self.current_idx - 1)

    def _on_next(self):
        if self.current_idx < len(self.segments) - 1:
            self._show_segment(self.current_idx + 1)
        else:
            self.destroy()

    def _show_segment(self, idx):
        if not self.segments or idx < 0 or idx >= len(self.segments):
            return
        self.current_idx = idx
        total = len(self.segments)
        data = self.segments[idx]

        # Generate large high-contrast QR code
        qr = qrcode.QRCode(
            version=None,
            error_correction=ERROR_CORRECT_L,
            box_size=5,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        pil = qr.make_image(fill_color="#000000", back_color="#FFFFFF").convert("RGB")
        pil = pil.resize((450, 450), PILImage.LANCZOS)

        ctk_img = ctk.CTkImage(light_image=pil, dark_image=pil, size=(450, 450))
        self.qr_image_label.configure(image=ctk_img, text="")
        self._qr_ref = ctk_img

        # Update UI text
        self.lbl_indicator.configure(text=f"{idx + 1} / {total}")
        self.lbl_step.configure(
            text=f"Part {idx + 1} of {total}: Point camera at QR, copy text, then paste into WhatsApp."
        )

        self.btn_prev.configure(state="normal" if idx > 0 else "disabled")
        if idx == total - 1:
            self.btn_next.configure(text="DONE (Close)", fg_color=TK["accent"], text_color="#FFFFFF")
        else:
            self.btn_next.configure(text="NEXT PART ▶", fg_color=TK["gold_accent"], text_color=TK["fg_primary"])


# ─────────────────────────────────────────────────────────────
# DND SUPPORT
# ─────────────────────────────────────────────────────────────
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    HAS_DND = True
except ImportError:
    HAS_DND = False


class CostaDesktopApp(ctk.CTk, TkinterDnD.DnDWrapper if HAS_DND else object):
    """Costa Schedule Exporter — Newspaper Light Edition."""

    def __init__(self):
        super().__init__()

        if HAS_DND:
            try:
                self.TkdndVersion = TkinterDnD._require(self)
                self.drop_target_register(DND_FILES)
                self.dnd_bind('<<Drop>>', self._on_file_drop)
            except Exception as e:
                print(f"[Warning] TkinterDnD init error: {e}")

        # Window
        self.title("Costa Cruises — Schedule Exporter")
        self.geometry("1100x800")
        self.minsize(920, 680)
        self.configure(fg_color=TK["bg_base"])

        # State
        self.current_file = self._find_default_sample()
        self.schedule_data = None
        self.payload = ""
        self.b64_data = ""
        self.qr_segments = []     # compressed QR text segments
        self.qr_compressed_b64 = ""  # full compressed b64
        self.meal_shift = "LUNCH"
        self.active_filter = "ALL"
        self.search_query = ""
        self._search_debounce_job = None
        self._toast_job = None
        self._qr_ctk_image = None
        self._cached_crew_count = 0
        self._cached_section_count = 0
        self.active_qr_mode = "bridge"

        # Web Bridge Server (3-Step Transfer)
        self.http_server = ScheduleHttpServer(self)
        self.http_server.start()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        # Logo
        self.logo_image = self._load_logo_image()

        # Build
        self._build_top_bar()
        self._build_control_strip()
        self._build_content_area()
        self._build_bottom_bar()

        # Auto-parse on start
        if self.current_file and os.path.exists(self.current_file):
            self.after(60, self.process_schedule)

    # ─────────────────────────────────────────────────────────
    # INIT HELPERS
    # ─────────────────────────────────────────────────────────
    def _find_default_sample(self):
        base = os.path.dirname(os.path.abspath(__file__))
        p = os.path.join(base, "sample", "Costa_Serena_Schedule_Sample.xlsx")
        return p if os.path.exists(p) else ""

    def _load_logo_image(self):
        base = os.path.dirname(os.path.abspath(__file__))
        logo = os.path.join(base, "logo.png")
        if os.path.exists(logo):
            try:
                pil = PILImage.open(logo)
                return ctk.CTkImage(light_image=pil, dark_image=pil, size=(32, 32))
            except Exception:
                pass
        return None

    # ─────────────────────────────────────────────────────────
    # TOP BAR  (replaces sidebar — newspaper masthead)
    # ─────────────────────────────────────────────────────────
    def _build_top_bar(self):
        bar = ctk.CTkFrame(
            self, height=56, corner_radius=0,
            fg_color=TK["bg_base"],
            border_width=0
        )
        bar.pack(fill="x")
        bar.pack_propagate(False)

        # Blue accent line at top (3px, like HTML border-top)
        accent_line = ctk.CTkFrame(bar, height=3, fg_color=TK["accent"], corner_radius=0)
        accent_line.pack(fill="x", side="top")

        inner = ctk.CTkFrame(bar, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=20)

        # Left: Logo + Brand
        brand = ctk.CTkFrame(inner, fg_color="transparent")
        brand.pack(side="left", fill="y")

        if self.logo_image:
            ctk.CTkLabel(brand, image=self.logo_image, text="").pack(side="left", padx=(0, 10))

        title_box = ctk.CTkFrame(brand, fg_color="transparent")
        title_box.pack(side="left", fill="y", pady=4)

        # "COSTA SMERALDA." with yellow dot
        title_frame = ctk.CTkFrame(title_box, fg_color="transparent")
        title_frame.pack(anchor="w")
        ctk.CTkLabel(
            title_frame, text="COSTA SMERALDA",
            font=Fonts.get("brand_lg"), text_color=TK["fg_primary"]
        ).pack(side="left")
        ctk.CTkLabel(
            title_frame, text=".",
            font=Fonts.get("brand_lg"), text_color=TK["gold_accent"]
        ).pack(side="left")

        ctk.CTkLabel(
            title_box, text="RESTAURANT SCHEDULE",
            font=Fonts.get("small_bold"), text_color=TK["fg_subtle"], anchor="w"
        ).pack(anchor="w")

        # Right: Telemetry badges
        badge_box = ctk.CTkFrame(inner, fg_color="transparent")
        badge_box.pack(side="right", fill="y")

        self.badge_vessel = self._make_badge(badge_box, "COSTA SERENA", TK["fg_accent"])
        self.badge_date = self._make_badge(badge_box, "August 23, 2026", TK["fg_secondary"])
        self.badge_port = self._make_badge(badge_box, "KAOHSIUNG", TK["fg_secondary"])

        # Bottom hairline
        ctk.CTkFrame(self, height=1, fg_color=TK["border_card"], corner_radius=0).pack(fill="x")

    def _make_badge(self, parent, text, color):
        pill = ctk.CTkFrame(
            parent, fg_color=TK["surface_inner"], corner_radius=6,
            border_width=1, border_color=TK["border_card"]
        )
        pill.pack(side="left", padx=3, pady=10)
        lbl = ctk.CTkLabel(
            pill, text=text,
            font=Fonts.get("small_bold"), text_color=color
        )
        lbl.pack(padx=10, pady=3)
        return lbl

    # ─────────────────────────────────────────────────────────
    # CONTROL STRIP  (file + shift + search + filter)
    # ─────────────────────────────────────────────────────────
    def _build_control_strip(self):
        strip = ctk.CTkFrame(self, fg_color=TK["surface_inner"], corner_radius=0)
        strip.pack(fill="x")

        inner = ctk.CTkFrame(strip, fg_color="transparent")
        inner.pack(fill="x", padx=20, pady=10)

        # Row 1: File + Shift
        r1 = ctk.CTkFrame(inner, fg_color="transparent")
        r1.pack(fill="x", pady=(0, 8))

        # File display
        file_box = ctk.CTkFrame(r1, fg_color="transparent")
        file_box.pack(side="left", fill="x", expand=True, padx=(0, 14))

        ctk.CTkLabel(
            file_box, text="SOURCE FILE",
            font=Fonts.get("tiny"), text_color=TK["fg_subtle"]
        ).pack(anchor="w")

        file_pill = ctk.CTkFrame(
            file_box, fg_color=TK["bg_base"], corner_radius=8,
            border_width=1, border_color=TK["border_card"], height=34
        )
        file_pill.pack(fill="x", pady=(3, 0))
        file_pill.pack_propagate(False)

        self.lbl_file = ctk.CTkLabel(
            file_pill, text=self._file_display_text(),
            font=Fonts.get("body"), text_color=TK["fg_secondary"], anchor="w", padx=10
        )
        self.lbl_file.pack(side="left", fill="both", expand=True)

        ctk.CTkButton(
            file_pill, text="Browse",
            font=Fonts.get("btn_sm"),
            fg_color=TK["surface_hover"], hover_color=TK["surface_active"],
            border_width=1, border_color=TK["border_card"],
            text_color=TK["fg_primary"], width=70, height=24, corner_radius=6,
            command=self.browse_file
        ).pack(side="right", padx=5)

        ctk.CTkButton(
            file_pill, text="Reload",
            font=Fonts.get("btn_sm"),
            fg_color=TK["surface_hover"], hover_color=TK["surface_active"],
            border_width=1, border_color=TK["border_card"],
            text_color=TK["fg_secondary"], width=60, height=24, corner_radius=6,
            command=self.process_schedule
        ).pack(side="right", padx=(0, 3))

        # Shift selector
        shift_box = ctk.CTkFrame(r1, fg_color="transparent")
        shift_box.pack(side="right")

        ctk.CTkLabel(
            shift_box, text="MEAL SHIFT",
            font=Fonts.get("tiny"), text_color=TK["fg_subtle"]
        ).pack(anchor="w")

        self.shift_selector = ctk.CTkSegmentedButton(
            shift_box, values=["BREAKFAST", "LUNCH", "DINNER"],
            font=Fonts.get("btn_sm"), height=34, corner_radius=8,
            border_width=1,
            selected_color=TK["accent"],
            selected_hover_color=TK["accent_hover"],
            unselected_color=TK["bg_base"],
            unselected_hover_color=TK["surface_hover"],
            text_color=TK["bg_base"],
            text_color_disabled=TK["fg_subtle"],
            command=self._on_shift_selected
        )
        self.shift_selector.pack(pady=(3, 0))
        self.shift_selector.set("LUNCH")

        # Row 2: Search + Filter pills
        r2 = ctk.CTkFrame(inner, fg_color="transparent")
        r2.pack(fill="x")

        # Search
        search_wrap = ctk.CTkFrame(
            r2, fg_color=TK["bg_base"], corner_radius=8,
            border_width=1, border_color=TK["border_card"], height=32
        )
        search_wrap.pack(side="left", fill="x", expand=True, padx=(0, 10))
        search_wrap.pack_propagate(False)

        ctk.CTkLabel(
            search_wrap, text="Search",
            font=Fonts.get("small"), text_color=TK["fg_subtle"]
        ).pack(side="left", padx=(10, 4))

        self.search_entry = ctk.CTkEntry(
            search_wrap,
            placeholder_text="Crew name, station, table, duty...",
            placeholder_text_color=TK["fg_subtle"],
            fg_color="transparent", border_width=0,
            font=Fonts.get("body"), text_color=TK["fg_primary"], height=28
        )
        self.search_entry.pack(side="left", fill="both", expand=True, padx=4)
        self.search_entry.bind("<KeyRelease>", self._on_search_key)

        ctk.CTkButton(
            search_wrap, text="x", width=22, height=20, corner_radius=4,
            fg_color="transparent", hover_color=TK["surface_hover"],
            text_color=TK["fg_subtle"], font=Fonts.get("small_bold"),
            command=self._clear_search
        ).pack(side="right", padx=4)

        # Filter pills
        self.filter_selector = ctk.CTkSegmentedButton(
            r2, values=["ALL", "MAIN DINING", "BUFFET & OUTLETS", "SIDE DUTIES"],
            font=Fonts.get("small_bold"), height=30, corner_radius=8,
            border_width=1,
            selected_color=TK["accent_dim"],
            selected_hover_color=TK["accent"],
            unselected_color=TK["bg_base"],
            unselected_hover_color=TK["surface_hover"],
            text_color=TK["fg_primary"],
            text_color_disabled=TK["fg_subtle"],
            command=self._on_filter_changed
        )
        self.filter_selector.pack(side="right")
        self.filter_selector.set("ALL")

        # Bottom hairline
        ctk.CTkFrame(self, height=1, fg_color=TK["border_subtle"], corner_radius=0).pack(fill="x")

    def _file_display_text(self):
        if not self.current_file:
            return "No file loaded — Click Browse to select roster (.xlsx)"
        return os.path.basename(self.current_file)

    # ─────────────────────────────────────────────────────────
    # CONTENT AREA  (flat scroll — dashboard + cards + QR)
    # ─────────────────────────────────────────────────────────
    def _build_content_area(self):
        self.content_scroll = ctk.CTkScrollableFrame(
            self, fg_color=TK["bg_base"], corner_radius=0
        )
        self.content_scroll.pack(fill="both", expand=True, padx=0, pady=0)

        # Inner wrapper with max-width for readability
        self.content_inner = ctk.CTkFrame(self.content_scroll, fg_color="transparent")
        self.content_inner.pack(fill="x", expand=True, padx=24, pady=16)

        # ── Stats row ──
        self.stats_frame = ctk.CTkFrame(self.content_inner, fg_color="transparent")
        self.stats_frame.pack(fill="x", pady=(0, 16))
        self.stats_frame.columnconfigure((0, 1, 2, 3), weight=1, uniform="stat")

        self.stat_port = self._make_stat_card(self.stats_frame, 0, "PORT & MEAL", "—", "—")
        self.stat_crew = self._make_stat_card(self.stats_frame, 1, "ACTIVE ROSTER", "0 Crew", "0 Sections")
        self.stat_stations = self._make_stat_card(self.stats_frame, 2, "DINING STATIONS", "0 Tables", "0 Venues")
        self.stat_payload = self._make_stat_card(self.stats_frame, 3, "ENCODED STREAM", "0 Chars", "0 Bytes")

        # ── QR Section (Dual-Mode: 1-QR Web Bridge & Airgap QR) ──
        self.qr_section = ctk.CTkFrame(
            self.content_inner, fg_color=TK["surface_inner"],
            corner_radius=12, border_width=1, border_color=TK["border_card"]
        )
        self.qr_section.pack(fill="x", pady=(0, 16))

        qr_inner = ctk.CTkFrame(self.qr_section, fg_color="transparent")
        qr_inner.pack(fill="x", padx=20, pady=16)

        # QR left: info
        qr_info = ctk.CTkFrame(qr_inner, fg_color="transparent")
        qr_info.pack(side="left", fill="both", expand=True)

        # Mode Switcher (Segmented Button)
        mode_bar = ctk.CTkFrame(qr_info, fg_color="transparent")
        mode_bar.pack(anchor="w", pady=(0, 8))

        self.seg_qr_mode = ctk.CTkSegmentedButton(
            mode_bar,
            values=["⚡ 1-QR Web Bridge (3 Steps)", "📶 Airgap QR Codes (Offline)"],
            command=self._on_qr_mode_switch,
            font=Fonts.get("small_bold"),
            selected_color=TK["accent"],
            selected_hover_color=TK["accent_hover"],
            unselected_color=TK["surface_hover"],
            unselected_hover_color=TK["surface_active"],
            text_color=TK["fg_primary"],
            height=30
        )
        self.seg_qr_mode.set("⚡ 1-QR Web Bridge (3 Steps)")
        self.seg_qr_mode.pack(side="left")

        # ── Mode 1 Frame: Web Bridge Info ──
        self.frame_bridge_info = ctk.CTkFrame(qr_info, fg_color="transparent")
        self.frame_bridge_info.pack(fill="x", expand=True)

        ctk.CTkLabel(
            self.frame_bridge_info, text="3-STEP SMART TRANSFER — 1 SCAN ONLY",
            font=Fonts.get("tiny"), text_color=TK["fg_subtle"]
        ).pack(anchor="w")

        ctk.CTkLabel(
            self.frame_bridge_info, text="Scan with camera to open WhatsApp sender",
            font=Fonts.get("h2"), text_color=TK["fg_primary"], anchor="w"
        ).pack(anchor="w", pady=(2, 4))

        self.bridge_status_label = ctk.CTkLabel(
            self.frame_bridge_info,
            text=f"1. Scan the 1 QR on the right using phone camera (Version 2, instant 0.05s scan).\n"
                 f"2. Tap the link to open Costa Schedule Bridge on your phone.\n"
                 f"3. On your phone, tap 'COPY FOR WHATSAPP' or 'OPEN IN WHATSAPP'!",
            font=Fonts.get("body"), text_color=TK["fg_secondary"],
            anchor="w", justify="left"
        )
        self.bridge_status_label.pack(anchor="w", pady=(0, 8))

        bridge_btns = ctk.CTkFrame(self.frame_bridge_info, fg_color="transparent")
        bridge_btns.pack(anchor="w")

        self.btn_copy_bridge_url = ctk.CTkButton(
            bridge_btns, text="Copy Link",
            font=Fonts.get("btn_sm"),
            fg_color=TK["surface_hover"], hover_color=TK["accent"],
            border_width=1, border_color=TK["border_card"],
            text_color=TK["fg_primary"], height=30, corner_radius=6,
            command=self.copy_bridge_url_action
        )
        self.btn_copy_bridge_url.pack(side="left", padx=(0, 6))

        ctk.CTkButton(
            bridge_btns, text="Test in Browser",
            font=Fonts.get("btn_sm"),
            fg_color=TK["surface_hover"], hover_color=TK["surface_active"],
            border_width=1, border_color=TK["border_card"],
            text_color=TK["fg_secondary"], height=30, corner_radius=6,
            command=self.open_bridge_browser_action
        ).pack(side="left", padx=(0, 6))

        self.btn_copy_payload = ctk.CTkButton(
            bridge_btns, text="Copy Payload",
            font=Fonts.get("btn_sm"),
            fg_color=TK["surface_hover"], hover_color=TK["surface_active"],
            border_width=1, border_color=TK["border_card"],
            text_color=TK["fg_secondary"], height=30, corner_radius=6,
            command=self.copy_payload_action
        )
        self.btn_copy_payload.pack(side="left")

        # ── Mode 2 Frame: Airgap Info ──
        self.frame_airgap_info = ctk.CTkFrame(qr_info, fg_color="transparent")

        ctk.CTkLabel(
            self.frame_airgap_info, text="OFFLINE AIRGAP SYSTEM — SHIP IT COMPLIANT",
            font=Fonts.get("tiny"), text_color=TK["fg_subtle"]
        ).pack(anchor="w")

        ctk.CTkLabel(
            self.frame_airgap_info, text="Zero network, cables, or WA Web required",
            font=Fonts.get("h2"), text_color=TK["fg_primary"], anchor="w"
        ).pack(anchor="w", pady=(2, 4))

        self.airgap_status_label = ctk.CTkLabel(
            self.frame_airgap_info,
            text="Optimized phone-scannable QR codes. Scan each part and paste into WhatsApp group.\n"
                 "Click 'ENLARGE FULL-SIZE QR' below for instant full-screen camera detection.",
            font=Fonts.get("body"), text_color=TK["fg_secondary"],
            anchor="w", justify="left"
        )
        self.airgap_status_label.pack(anchor="w", pady=(0, 8))

        airgap_btns = ctk.CTkFrame(self.frame_airgap_info, fg_color="transparent")
        airgap_btns.pack(anchor="w")

        self.btn_enlarge_qr = ctk.CTkButton(
            airgap_btns, text="🔍 ENLARGE FULL-SIZE QR",
            font=Fonts.get("btn"),
            fg_color=TK["gold_accent"], hover_color=TK["gold_hover"],
            text_color=TK["fg_primary"], height=34, corner_radius=6,
            command=self.open_qr_modal
        )
        self.btn_enlarge_qr.pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            airgap_btns, text="Save Backup",
            font=Fonts.get("btn_sm"),
            fg_color=TK["surface_hover"], hover_color=TK["surface_active"],
            border_width=1, border_color=TK["border_card"],
            text_color=TK["fg_secondary"], height=34, corner_radius=6,
            command=self.save_json_backup_action
        ).pack(side="left", padx=(0, 6))

        ctk.CTkButton(
            airgap_btns, text="Export JSON",
            font=Fonts.get("btn_sm"),
            fg_color=TK["surface_hover"], hover_color=TK["surface_active"],
            border_width=1, border_color=TK["border_card"],
            text_color=TK["fg_secondary"], height=34, corner_radius=6,
            command=self.export_json_action
        ).pack(side="left")

        # ── QR Right: Display Area ──
        self.qr_image_frame = ctk.CTkFrame(qr_inner, fg_color="transparent")
        self.qr_image_frame.pack(side="right", padx=(20, 0))

        # Bridge QR Container (1 Single QR)
        self.bridge_qr_wrap = ctk.CTkFrame(self.qr_image_frame, fg_color="transparent")
        self.bridge_qr_wrap.pack(side="left")

        self.bridge_qr_box = ctk.CTkFrame(
            self.bridge_qr_wrap, width=190, height=190,
            fg_color="#FFFFFF", corner_radius=8,
            border_width=1, border_color=TK["border_card"]
        )
        self.bridge_qr_box.pack()
        self.bridge_qr_box.pack_propagate(False)

        self.bridge_qr_label = ctk.CTkLabel(
            self.bridge_qr_box, text="Generating QR...",
            font=Fonts.get("small"), text_color=TK["fg_subtle"]
        )
        self.bridge_qr_label.pack(expand=True)

        self.bridge_url_caption = ctk.CTkLabel(
            self.bridge_qr_wrap, text="Scan with Phone Camera",
            font=Fonts.get("tiny"), text_color=TK["fg_accent"]
        )
        self.bridge_url_caption.pack(pady=(4, 0))

        # Airgap QR Container (side-by-side previews)
        self.airgap_qr_wrap = ctk.CTkFrame(self.qr_image_frame, fg_color="transparent")

        # QR A Preview
        qr_a_sub = ctk.CTkFrame(self.airgap_qr_wrap, fg_color="transparent")
        qr_a_sub.pack(side="left", padx=(0, 8))

        ctk.CTkLabel(qr_a_sub, text="Part 1 — Scan first", font=Fonts.get("tiny"), text_color=TK["fg_accent"]).pack()
        self.qr_a_box = ctk.CTkFrame(qr_a_sub, width=170, height=170, fg_color="#FFFFFF", corner_radius=8, border_width=1, border_color=TK["border_card"])
        self.qr_a_box.pack(pady=(3, 0))
        self.qr_a_box.pack_propagate(False)
        self.qr_a_label = ctk.CTkLabel(self.qr_a_box, text="Part 1", font=Fonts.get("small"), text_color=TK["fg_subtle"])
        self.qr_a_label.pack(expand=True)
        self.qr_a_box.bind("<Button-1>", lambda e: self.open_qr_modal())
        self.qr_a_label.bind("<Button-1>", lambda e: self.open_qr_modal())

        # QR B Preview
        qr_b_sub = ctk.CTkFrame(self.airgap_qr_wrap, fg_color="transparent")
        qr_b_sub.pack(side="left")

        ctk.CTkLabel(qr_b_sub, text="Part 2 — Scan second", font=Fonts.get("tiny"), text_color=TK["fg_accent"]).pack()
        self.qr_b_box = ctk.CTkFrame(qr_b_sub, width=170, height=170, fg_color="#FFFFFF", corner_radius=8, border_width=1, border_color=TK["border_card"])
        self.qr_b_box.pack(pady=(3, 0))
        self.qr_b_box.pack_propagate(False)
        self.qr_b_label = ctk.CTkLabel(self.qr_b_box, text="Part 2", font=Fonts.get("small"), text_color=TK["fg_subtle"])
        self.qr_b_label.pack(expand=True)
        self.qr_b_box.bind("<Button-1>", lambda e: self.open_qr_modal())
        self.qr_b_label.bind("<Button-1>", lambda e: self.open_qr_modal())

        # ── Cards container ──
        self.cards_frame = ctk.CTkFrame(self.content_inner, fg_color="transparent")
        self.cards_frame.pack(fill="x", pady=(0, 8))

        self.empty_label = ctk.CTkLabel(
            self.cards_frame,
            text="No schedule loaded. Click Browse to open an Excel roster file.",
            font=Fonts.get("body"), text_color=TK["fg_secondary"], pady=40
        )
        self.empty_label.pack(expand=True)

    def _make_stat_card(self, parent, col, tag, title, subtitle):
        card = ctk.CTkFrame(
            parent, fg_color=TK["surface_card"], corner_radius=10,
            border_width=1, border_color=TK["border_card"]
        )
        card.grid(row=0, column=col, padx=4, pady=2, sticky="nsew")

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=12, pady=10)

        # Tag with colored dot
        tag_row = ctk.CTkFrame(inner, fg_color="transparent")
        tag_row.pack(fill="x")
        dot = ctk.CTkFrame(tag_row, width=6, height=6, corner_radius=3, fg_color=TK["accent"])
        dot.pack(side="left", padx=(0, 6))
        ctk.CTkLabel(
            tag_row, text=tag, font=Fonts.get("tiny"), text_color=TK["fg_subtle"]
        ).pack(side="left")

        title_lbl = ctk.CTkLabel(
            inner, text=title, font=Fonts.get("h2"),
            text_color=TK["fg_primary"], anchor="w"
        )
        title_lbl.pack(fill="x", pady=(6, 2))

        sub_lbl = ctk.CTkLabel(
            inner, text=subtitle, font=Fonts.get("small"),
            text_color=TK["fg_secondary"], anchor="w"
        )
        sub_lbl.pack(fill="x")

        return (title_lbl, sub_lbl)

    # ─────────────────────────────────────────────────────────
    # BOTTOM BAR  (primary action + secondary)
    # ─────────────────────────────────────────────────────────
    def _build_bottom_bar(self):
        # Top hairline
        ctk.CTkFrame(self, height=1, fg_color=TK["border_card"], corner_radius=0).pack(fill="x")

        bar = ctk.CTkFrame(self, height=56, fg_color=TK["bg_base"], corner_radius=0)
        bar.pack(fill="x")
        bar.pack_propagate(False)

        inner = ctk.CTkFrame(bar, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=20)

        # Primary CTA — yellow (Costa guideline: one yellow button)
        self.btn_primary = ctk.CTkButton(
            inner, text="COPY SCHEDULE TO CLIPBOARD",
            font=Fonts.get("btn"),
            fg_color=TK["gold_accent"], hover_color=TK["gold_hover"],
            text_color=TK["fg_primary"],  # Dark text on yellow (8:1 contrast)
            height=40, corner_radius=8,
            command=self._primary_action
        )
        self.btn_primary.pack(side="left", fill="x", expand=True, padx=(0, 10))

        # Secondary: Open WebApp
        ctk.CTkButton(
            inner, text="Open WebApp",
            font=Fonts.get("btn_sm"),
            fg_color=TK["bg_base"], hover_color=TK["surface_hover"],
            border_width=1, border_color=TK["border_card"],
            text_color=TK["fg_secondary"], height=40, corner_radius=8,
            command=self.open_webapp
        ).pack(side="right")

        # Status label
        self.lbl_status = ctk.CTkLabel(
            inner, text="Ready",
            font=Fonts.get("small"), text_color=TK["good_ink"]
        )
        self.lbl_status.pack(side="right", padx=16)

    # ─────────────────────────────────────────────────────────
    # QR CODE GENERATION & MODAL ACTIONS
    # ─────────────────────────────────────────────────────────
    def _on_qr_mode_switch(self, value):
        if "1-QR" in value:
            self.active_qr_mode = "bridge"
            self.frame_airgap_info.pack_forget()
            self.airgap_qr_wrap.pack_forget()
            self.frame_bridge_info.pack(fill="x", expand=True)
            self.bridge_qr_wrap.pack(side="left")
        else:
            self.active_qr_mode = "airgap"
            self.frame_bridge_info.pack_forget()
            self.bridge_qr_wrap.pack_forget()
            self.frame_airgap_info.pack(fill="x", expand=True)
            self.airgap_qr_wrap.pack(side="left")

    def copy_bridge_url_action(self):
        if hasattr(self, "http_server") and self.http_server:
            if copy_to_clipboard(self.http_server.url):
                self._show_toast("Bridge URL copied!")

    def open_bridge_browser_action(self):
        if hasattr(self, "http_server") and self.http_server:
            webbrowser.open(self.http_server.url)

    def open_qr_modal(self):
        if not self.qr_segments:
            messagebox.showinfo("No Schedule", "Please load an Excel roster file first.")
            return
        meta = {
            "ship": self.schedule_data.get("ship", "COSTA SMERALDA") if self.schedule_data else "COSTA SMERALDA",
            "shift": self.schedule_data.get("shift", "LUNCH") if self.schedule_data else "LUNCH",
            "date": self.schedule_data.get("date", "Today") if self.schedule_data else "Today",
            "crew": self._cached_crew_count,
        }
        QRModal(self, self.qr_segments, meta)

    def _on_close(self):
        if hasattr(self, "http_server") and self.http_server:
            self.http_server.stop()
        self.destroy()

    def _make_qr_image(self, data, size=180, box_size=5):
        """Generate a crisp QR code CTkImage with proper quiet zone and contrast."""
        qr = qrcode.QRCode(
            version=None,
            error_correction=ERROR_CORRECT_L,
            box_size=box_size,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        pil = qr.make_image(fill_color="#000000", back_color="#FFFFFF").convert("RGB")
        if size:
            pil = pil.resize((size, size), PILImage.LANCZOS)

        return ctk.CTkImage(
            light_image=pil, dark_image=pil,
            size=(size or pil.size[0], size or pil.size[1])
        )

    def _generate_qr(self):
        """Generate 1-QR Web Bridge and Airgap QR codes from schedule data."""
        if not self.schedule_data:
            return

        try:
            # 1. Generate 1-QR Web Bridge
            if hasattr(self, "http_server") and self.http_server:
                bridge_url = self.http_server.url
                bridge_img = self._make_qr_image(bridge_url, size=180, box_size=6)
                self.bridge_qr_label.configure(image=bridge_img, text="")
                self._bridge_qr_ref = bridge_img
                self.bridge_url_caption.configure(text=f"Scan: {bridge_url}")

            # 2. Generate Airgap Segments (scannable Version <= 22)
            self.qr_segments, self.qr_compressed_b64 = generate_compressed_payload(
                self.schedule_data, max_seg_len=950
            )

            # Generate QR A preview (first segment)
            qr_a_img = self._make_qr_image(self.qr_segments[0], size=160, box_size=4)
            self.qr_a_label.configure(image=qr_a_img, text="")
            self._qr_a_ref = qr_a_img

            # Generate QR B preview (second segment if available)
            if len(self.qr_segments) > 1:
                qr_b_img = self._make_qr_image(self.qr_segments[1], size=160, box_size=4)
                self.qr_b_label.configure(image=qr_b_img, text="")
                self._qr_b_ref = qr_b_img

            total_parts = len(self.qr_segments)
            self.airgap_status_label.configure(
                text=f"Ready: {total_parts} scannable QR parts generated. "
                     f"Click 'ENLARGE FULL-SIZE QR' to scan comfortably."
            )

        except Exception as e:
            print(f"[Error] QR Generation failed: {e}")

    # ─────────────────────────────────────────────────────────
    # CARD RENDERING  (newspaper-style, no emoji)
    # ─────────────────────────────────────────────────────────
    def _render_cards(self):
        """Render schedule data as clean newspaper-style cards."""
        for w in self.cards_frame.winfo_children():
            w.destroy()

        d = self.schedule_data
        if not d:
            self.empty_label = ctk.CTkLabel(
                self.cards_frame,
                text="No schedule loaded. Click Browse to open an Excel roster file.",
                font=Fonts.get("body"), text_color=TK["fg_secondary"], pady=40
            )
            self.empty_label.pack(expand=True)
            return

        q = self.search_query.lower()
        filt = self.active_filter

        # Main Dining
        if filt in ("ALL", "MAIN DINING"):
            for venue in d.get("venues", []):
                assignments = venue.get("assignments", [])
                filtered = [
                    a for a in assignments
                    if not q or any(q in str(a.get(k, "")).lower()
                                   for k in ("station", "waiterName", "attendantName", "tables"))
                ]
                if filtered or not q:
                    self._card_venue(venue.get("name"), venue.get("reportTime", "—"), filtered)

        # Buffet & Outlets
        if filt in ("ALL", "BUFFET & OUTLETS"):
            for b in d.get("buffetAndVenues", []):
                crew = b.get("crew", [])
                filtered = [
                    c for c in crew
                    if not q or q in c.get("name", "").lower()
                    or q in c.get("role", "").lower()
                    or q in b.get("name", "").lower()
                ]
                if filtered or not q:
                    self._card_buffet(b.get("name"), b.get("timing", "—"), b.get("lead", ""), filtered)

        # Side Duties
        if filt in ("ALL", "SIDE DUTIES"):
            for s in d.get("sideDuties", []):
                crew = s.get("crew", [])
                filtered = [
                    c for c in crew
                    if not q or q in c.get("name", "").lower()
                    or q in s.get("name", "").lower()
                ]
                if filtered or not q:
                    self._card_side_duty(s.get("name"), s.get("timing", "—"), filtered)

        # Special Events
        if filt == "ALL" and d.get("specialEvents"):
            self._card_special_events(d.get("specialEvents", []))

        # Sick Leave
        if filt == "ALL" and d.get("sickLeave"):
            self._card_sick_leave(d.get("sickLeave", []))

    def _card_venue(self, name, report_time, assignments):
        card = self._card_shell(self.cards_frame)

        hdr = ctk.CTkFrame(card, fg_color="transparent")
        hdr.pack(fill="x", padx=16, pady=(12, 8))

        ctk.CTkLabel(
            hdr, text=name,
            font=Fonts.get("h3"), text_color=TK["fg_primary"]
        ).pack(side="left")

        ctk.CTkLabel(
            hdr, text=f"Report: {report_time}  /  {len(assignments)} stations",
            font=Fonts.get("small"), text_color=TK["fg_accent"]
        ).pack(side="right")

        # Thin divider
        ctk.CTkFrame(card, height=1, fg_color=TK["border_subtle"]).pack(fill="x", padx=16)

        body = ctk.CTkFrame(card, fg_color="transparent")
        body.pack(fill="x", padx=12, pady=(4, 10))

        for idx, a in enumerate(assignments):
            bg = TK["surface_inner"] if idx % 2 == 0 else TK["bg_base"]
            row = ctk.CTkFrame(body, fg_color=bg, corner_radius=4)
            row.pack(fill="x", pady=1, padx=4)

            # Station badge
            ctk.CTkLabel(
                row, text=a.get("station", "—"),
                font=Fonts.get("small_bold"), text_color=TK["fg_accent"],
                width=60
            ).pack(side="left", padx=8, pady=5)

            # Waiter
            ctk.CTkLabel(
                row, text=a.get("waiterName", "—"),
                font=Fonts.get("body_bold"), text_color=TK["fg_primary"], anchor="w"
            ).pack(side="left", padx=6)

            # Attendant
            if a.get("attendantName"):
                ctk.CTkLabel(
                    row, text=f"/ {a['attendantName']}",
                    font=Fonts.get("body"), text_color=TK["fg_secondary"], anchor="w"
                ).pack(side="left", padx=4)

            # Tables
            if a.get("tables"):
                ctk.CTkLabel(
                    row, text=a["tables"],
                    font=Fonts.get("mono_sm"), text_color=TK["fg_subtle"]
                ).pack(side="right", padx=8, pady=5)

    def _card_buffet(self, name, timing, lead, crew):
        card = self._card_shell(self.cards_frame)

        hdr = ctk.CTkFrame(card, fg_color="transparent")
        hdr.pack(fill="x", padx=16, pady=(12, 8))

        ctk.CTkLabel(
            hdr, text=name,
            font=Fonts.get("h3"), text_color=TK["fg_primary"]
        ).pack(side="left")

        right_text = f"{timing}  /  {len(crew)} crew"
        if lead:
            right_text = f"Lead: {lead}  /  " + right_text
        ctk.CTkLabel(
            hdr, text=right_text,
            font=Fonts.get("small"), text_color=TK["fg_secondary"]
        ).pack(side="right")

        ctk.CTkFrame(card, height=1, fg_color=TK["border_subtle"]).pack(fill="x", padx=16)

        body = ctk.CTkFrame(card, fg_color="transparent")
        body.pack(fill="x", padx=12, pady=(4, 10))

        # Crew chips in a flow layout
        chip_row = ctk.CTkFrame(body, fg_color="transparent")
        chip_row.pack(fill="x")

        for c in crew:
            role = f" — {c['role']}" if c.get("role") else ""
            chip = ctk.CTkFrame(
                chip_row, fg_color=TK["surface_inner"], corner_radius=6,
                border_width=1, border_color=TK["border_subtle"]
            )
            chip.pack(side="left", padx=2, pady=2)

            ctk.CTkLabel(
                chip, text=f"{c.get('name', '')}{role}",
                font=Fonts.get("small"), text_color=TK["fg_primary"]
            ).pack(padx=6, pady=3)

    def _card_side_duty(self, name, timing, crew):
        card = self._card_shell(self.cards_frame)

        hdr = ctk.CTkFrame(card, fg_color="transparent")
        hdr.pack(fill="x", padx=16, pady=(10, 6))

        ctk.CTkLabel(
            hdr, text=name,
            font=Fonts.get("h3"), text_color=TK["fg_primary"]
        ).pack(side="left")

        ctk.CTkLabel(
            hdr, text=f"{timing}  /  {len(crew)} crew",
            font=Fonts.get("small"), text_color=TK["fg_subtle"]
        ).pack(side="right")

        ctk.CTkFrame(card, height=1, fg_color=TK["border_subtle"]).pack(fill="x", padx=16)

        body = ctk.CTkFrame(card, fg_color="transparent")
        body.pack(fill="x", padx=12, pady=(4, 8))

        for c in crew:
            chip = ctk.CTkFrame(
                body, fg_color=TK["surface_inner"], corner_radius=4,
                border_width=1, border_color=TK["border_subtle"]
            )
            chip.pack(side="left", padx=2, pady=2)
            ctk.CTkLabel(
                chip, text=c.get("name", ""),
                font=Fonts.get("small"), text_color=TK["fg_secondary"]
            ).pack(padx=6, pady=2)

    def _card_special_events(self, events):
        card = self._card_shell(self.cards_frame)

        ctk.CTkLabel(
            card, text="SPECIAL EVENTS & TRAVEL TALK",
            font=Fonts.get("h3"), text_color=TK["gold_accent"]
        ).pack(anchor="w", padx=16, pady=(12, 6))

        ctk.CTkFrame(card, height=1, fg_color=TK["border_subtle"]).pack(fill="x", padx=16)

        body = ctk.CTkFrame(card, fg_color="transparent")
        body.pack(fill="x", padx=12, pady=(4, 10))

        for ev in events:
            ev_box = ctk.CTkFrame(
                body, fg_color=TK["surface_inner"], corner_radius=6,
                border_width=1, border_color=TK["border_subtle"]
            )
            ev_box.pack(fill="x", pady=3)

            ctk.CTkLabel(
                ev_box,
                text=f"{ev.get('title')}  —  {ev.get('location')}",
                font=Fonts.get("body_bold"), text_color=TK["fg_primary"], anchor="w"
            ).pack(fill="x", padx=10, pady=(6, 4))

            p_frame = ctk.CTkFrame(ev_box, fg_color="transparent")
            p_frame.pack(fill="x", padx=8, pady=(0, 6))
            for p in ev.get("participants", []):
                chip = ctk.CTkFrame(
                    p_frame, fg_color=TK["bg_base"], corner_radius=4,
                    border_width=1, border_color=TK["border_card"]
                )
                chip.pack(side="left", padx=2, pady=2)
                ctk.CTkLabel(
                    chip,
                    text=f"{p.get('name')} [{p.get('uniform')}]",
                    font=Fonts.get("mono_sm"), text_color=TK["fg_secondary"]
                ).pack(padx=5, pady=2)

    def _card_sick_leave(self, sick_list):
        card = self._card_shell(self.cards_frame)

        ctk.CTkLabel(
            card, text="SICK LEAVE / OFF DUTY",
            font=Fonts.get("h3"), text_color=TK["bad_ink"]
        ).pack(anchor="w", padx=16, pady=(12, 6))

        ctk.CTkFrame(card, height=1, fg_color=TK["border_subtle"]).pack(fill="x", padx=16)

        body = ctk.CTkFrame(card, fg_color="transparent")
        body.pack(fill="x", padx=12, pady=(4, 8))

        for sk in sick_list:
            chip = ctk.CTkFrame(
                body, fg_color=TK["bad_bg"], corner_radius=4,
                border_width=1, border_color=TK["bad_border"]
            )
            chip.pack(side="left", padx=3, pady=2)
            ctk.CTkLabel(
                chip, text=sk.get("name", ""),
                font=Fonts.get("small_bold"), text_color=TK["bad_ink"]
            ).pack(padx=6, pady=2)

    def _card_shell(self, parent):
        """Create a newspaper-style card frame."""
        card = ctk.CTkFrame(
            parent, fg_color=TK["surface_card"], corner_radius=10,
            border_width=1, border_color=TK["border_card"]
        )
        card.pack(fill="x", pady=5)
        return card

    # ─────────────────────────────────────────────────────────
    # BUSINESS LOGIC
    # ─────────────────────────────────────────────────────────
    def browse_file(self):
        self.update_idletasks()
        selected = filedialog.askopenfilename(
            parent=self,
            title="Select Costa Schedule Excel (.xlsx)",
            filetypes=[("Excel Files", "*.xlsx *.xls"), ("All Files", "*.*")]
        )
        if selected:
            self.current_file = selected
            self.lbl_file.configure(text=self._file_display_text())
            self.process_schedule()

    def _on_file_drop(self, event):
        raw = (event.data or "").strip()
        if raw.startswith('{') and raw.endswith('}'):
            raw = raw[1:-1]
        elif raw.startswith('"') and raw.endswith('"'):
            raw = raw[1:-1]
        path = raw.strip()
        if path.lower().endswith(('.xlsx', '.xls')) and os.path.exists(path):
            self.current_file = path
            self.lbl_file.configure(text=self._file_display_text())
            self.process_schedule()
            self._show_status("Roster loaded via drag & drop", TK["good_ink"])
        else:
            self._show_status("Drop a valid Excel file (.xlsx)", TK["warn_ink"])

    def _on_shift_selected(self, value):
        self.meal_shift = value
        if self.current_file:
            self.process_schedule()

    def _on_search_key(self, event=None):
        """Debounced search — 300ms delay before re-render."""
        if self._search_debounce_job:
            self.after_cancel(self._search_debounce_job)
        self._search_debounce_job = self.after(300, self._apply_search)

    def _apply_search(self):
        self.search_query = self.search_entry.get().strip()
        self._render_cards()

    def _clear_search(self):
        self.search_entry.delete(0, "end")
        self.search_query = ""
        self._render_cards()

    def _on_filter_changed(self, value):
        self.active_filter = value
        self._render_cards()

    def process_schedule(self):
        """Parse Excel and generate payload + QR."""
        if not self.current_file or not os.path.exists(self.current_file):
            return

        self._show_status("Parsing roster...", TK["fg_accent"])
        self.update_idletasks()

        try:
            self.schedule_data = parse_schedule_excel(self.current_file, self.meal_shift)
            self.payload, self.b64_data = generate_payload(self.schedule_data)

            # Count crew once (avoid duplicate counting)
            self._count_crew()

            self._render_results()
            self._generate_qr()
            self._show_status("Ready", TK["good_ink"])
        except Exception as err:
            self._show_status("Parse error", TK["bad_ink"])
            messagebox.showerror("Parse Error", f"Failed to parse Excel:\n\n{err}")

    def _count_crew(self):
        d = self.schedule_data
        if not d:
            return
        names = set()
        for v in d.get("venues", []):
            for a in v.get("assignments", []):
                if a.get("waiterName"):
                    names.add(a["waiterName"])
                if a.get("attendantName"):
                    names.add(a["attendantName"])
        for b in d.get("buffetAndVenues", []):
            for c in b.get("crew", []):
                if c.get("name"):
                    names.add(c["name"])
        for s in d.get("sideDuties", []):
            for c in s.get("crew", []):
                if c.get("name"):
                    names.add(c["name"])
        for sk in d.get("sickLeave", []):
            if sk.get("name"):
                names.add(sk["name"])

        self._cached_crew_count = len(names)
        self._cached_section_count = (
            len(d.get("venues", []))
            + len(d.get("buffetAndVenues", []))
            + len(d.get("sideDuties", []))
        )

    def _render_results(self):
        d = self.schedule_data
        if not d:
            return

        # Update badges
        self.badge_vessel.configure(text=d.get("ship", "COSTA"))
        self.badge_date.configure(text=d.get("date", "—"))
        self.badge_port.configure(text=d.get("port", "—"))

        # Update stat cards
        total_stations = sum(len(v.get("assignments", [])) for v in d.get("venues", []))
        total_venues = len(d.get("venues", []))

        self.stat_port[0].configure(text=f"{d.get('port', '—')} / {d.get('meal', 'LUNCH')}")
        self.stat_port[1].configure(text=d.get("date", "—"))

        self.stat_crew[0].configure(text=f"{self._cached_crew_count} Crew")
        self.stat_crew[1].configure(text=f"{self._cached_section_count} Sections")

        self.stat_stations[0].configure(text=f"{total_stations} Tables")
        self.stat_stations[1].configure(text=f"{total_venues} Venues")

        self.stat_payload[0].configure(text=f"{len(self.payload):,} Chars")
        self.stat_payload[1].configure(text=f"{len(self.b64_data):,} Bytes")

        # Render cards
        self._render_cards()

    # ─────────────────────────────────────────────────────────
    # ACTIONS
    # ─────────────────────────────────────────────────────────
    def _primary_action(self):
        """Primary CTA: copy payload + ensure QR is generated."""
        if not self.payload:
            messagebox.showwarning("No Schedule", "Load and process a schedule file first.")
            return
        self.copy_payload_action()
        self._generate_qr()

    def copy_payload_action(self):
        if not self.payload:
            messagebox.showwarning("No Schedule", "Load and process a schedule file first.")
            return
        success = copy_to_clipboard(self.payload)
        if not success:
            self.clipboard_clear()
            self.clipboard_append(self.payload)
        self._trigger_copy_feedback()

    def _trigger_copy_feedback(self):
        if self._toast_job:
            self.after_cancel(self._toast_job)

        self.btn_primary.configure(
            text="COPIED — READY TO PASTE",
            fg_color=TK["good_ink"]
        )
        self._toast_job = self.after(2400, self._restore_primary_btn)

    def _restore_primary_btn(self):
        self.btn_primary.configure(
            text="COPY SCHEDULE TO CLIPBOARD",
            fg_color=TK["gold_accent"]
        )

    def save_json_backup_action(self):
        if not self.schedule_data:
            messagebox.showwarning("No Data", "Load a schedule first.")
            return
        try:
            base = os.path.dirname(os.path.abspath(__file__))
            save_dir = os.path.join(base, "Save Data")
            os.makedirs(save_dir, exist_ok=True)

            now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            ship = str(self.schedule_data.get("ship", "Costa")).replace(" ", "_")
            meal = str(self.schedule_data.get("meal", "Schedule")).replace(" ", "_")
            fname = f"{ship}_{meal}_{now}.json"
            fpath = os.path.join(save_dir, fname)

            with open(fpath, "w", encoding="utf-8") as f:
                json.dump(self.schedule_data, f, indent=2, ensure_ascii=False)
            messagebox.showinfo("Saved", f"Backup saved:\n{fname}")
        except Exception as err:
            messagebox.showerror("Save Failed", f"Failed:\n{err}")

    def export_json_action(self):
        if not self.schedule_data:
            messagebox.showwarning("No Data", "Load a schedule first.")
            return
        out = filedialog.asksaveasfilename(
            parent=self, title="Export Schedule JSON",
            defaultextension=".json", filetypes=[("JSON", "*.json")]
        )
        if out:
            with open(out, "w", encoding="utf-8") as f:
                json.dump(self.schedule_data, f, indent=2, ensure_ascii=False)
            messagebox.showinfo("Exported", f"Saved to:\n{out}")

    def open_webapp(self):
        base = os.path.dirname(os.path.abspath(__file__))
        html = os.path.join(base, "CostaSchedule.html")
        if os.path.exists(html):
            webbrowser.open(f"file://{html}")
        else:
            messagebox.showwarning("Missing", "CostaSchedule.html not found.")

    def _show_status(self, text, color):
        try:
            self.lbl_status.configure(text=text, text_color=color)
        except Exception:
            pass


# ─────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────
def launch_gui():
    app = CostaDesktopApp()
    app.mainloop()

if __name__ == "__main__":
    launch_gui()
