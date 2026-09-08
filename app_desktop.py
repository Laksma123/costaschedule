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

        # ── QR Preview Section ──
        self.qr_section = ctk.CTkFrame(
            self.content_inner, fg_color=TK["surface_inner"],
            corner_radius=12, border_width=1, border_color=TK["border_card"]
        )
        self.qr_section.pack(fill="x", pady=(0, 16))

        qr_inner = ctk.CTkFrame(self.qr_section, fg_color="transparent")
        qr_inner.pack(fill="x", padx=20, pady=16)

        # QR left: info
        qr_info = ctk.CTkFrame(qr_inner, fg_color="transparent")
        qr_info.pack(side="left", fill="y")

        ctk.CTkLabel(
            qr_info, text="QR CODE — ENCRYPTED SCHEDULE",
            font=Fonts.get("tiny"), text_color=TK["fg_subtle"]
        ).pack(anchor="w")

        ctk.CTkLabel(
            qr_info, text="Scan to get schedule data",
            font=Fonts.get("h2"), text_color=TK["fg_primary"], anchor="w"
        ).pack(anchor="w", pady=(4, 2))

        self.qr_status_label = ctk.CTkLabel(
            qr_info, text="No schedule loaded. Browse a roster file to generate QR.",
            font=Fonts.get("body"), text_color=TK["fg_secondary"],
            anchor="w", wraplength=400, justify="left"
        )
        self.qr_status_label.pack(anchor="w", pady=(2, 8))

        # QR action buttons row
        qr_btns = ctk.CTkFrame(qr_info, fg_color="transparent")
        qr_btns.pack(anchor="w")

        self.btn_copy_payload = ctk.CTkButton(
            qr_btns, text="Copy Payload",
            font=Fonts.get("btn_sm"),
            fg_color=TK["surface_hover"], hover_color=TK["accent"],
            border_width=1, border_color=TK["border_card"],
            text_color=TK["fg_primary"], height=30, corner_radius=6,
            command=self.copy_payload_action
        )
        self.btn_copy_payload.pack(side="left", padx=(0, 6))

        ctk.CTkButton(
            qr_btns, text="Save Backup",
            font=Fonts.get("btn_sm"),
            fg_color=TK["surface_hover"], hover_color=TK["surface_active"],
            border_width=1, border_color=TK["border_card"],
            text_color=TK["fg_secondary"], height=30, corner_radius=6,
            command=self.save_json_backup_action
        ).pack(side="left", padx=(0, 6))

        ctk.CTkButton(
            qr_btns, text="Export JSON",
            font=Fonts.get("btn_sm"),
            fg_color=TK["surface_hover"], hover_color=TK["surface_active"],
            border_width=1, border_color=TK["border_card"],
            text_color=TK["fg_secondary"], height=30, corner_radius=6,
            command=self.export_json_action
        ).pack(side="left")

        # QR right: 2 QR codes side-by-side for compressed segments
        self.qr_image_frame = ctk.CTkFrame(qr_inner, fg_color="transparent")
        self.qr_image_frame.pack(side="right", padx=(20, 0))

        # QR A
        qr_a_wrap = ctk.CTkFrame(self.qr_image_frame, fg_color="transparent")
        qr_a_wrap.pack(side="left", padx=(0, 8))

        ctk.CTkLabel(
            qr_a_wrap, text="QR A — Scan first",
            font=Fonts.get("tiny"), text_color=TK["fg_accent"]
        ).pack()

        self.qr_a_box = ctk.CTkFrame(
            qr_a_wrap, width=180, height=180,
            fg_color=TK["bg_base"], corner_radius=8,
            border_width=1, border_color=TK["border_card"]
        )
        self.qr_a_box.pack(pady=(3, 0))
        self.qr_a_box.pack_propagate(False)

        self.qr_a_label = ctk.CTkLabel(
            self.qr_a_box, text="QR A",
            font=Fonts.get("small"), text_color=TK["fg_subtle"]
        )
        self.qr_a_label.pack(expand=True)

        # QR B
        qr_b_wrap = ctk.CTkFrame(self.qr_image_frame, fg_color="transparent")
        qr_b_wrap.pack(side="left")

        ctk.CTkLabel(
            qr_b_wrap, text="QR B — Scan second",
            font=Fonts.get("tiny"), text_color=TK["fg_accent"]
        ).pack()

        self.qr_b_box = ctk.CTkFrame(
            qr_b_wrap, width=180, height=180,
            fg_color=TK["bg_base"], corner_radius=8,
            border_width=1, border_color=TK["border_card"]
        )
        self.qr_b_box.pack(pady=(3, 0))
        self.qr_b_box.pack_propagate(False)

        self.qr_b_label = ctk.CTkLabel(
            self.qr_b_box, text="QR B",
            font=Fonts.get("small"), text_color=TK["fg_subtle"]
        )
        self.qr_b_label.pack(expand=True)

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
    # QR CODE GENERATION
    # ─────────────────────────────────────────────────────────
    def _generate_qr(self):
        """Generate 2 compressed QR codes (side-by-side) from schedule data."""
        if not self.schedule_data:
            return

        try:
            self.qr_segments, self.qr_compressed_b64 = generate_compressed_payload(
                self.schedule_data
            )

            # Generate QR A
            qr_a_img = self._make_qr_image(self.qr_segments[0], size=170)
            self.qr_a_label.configure(image=qr_a_img, text="")
            self._qr_a_ref = qr_a_img  # prevent GC

            # Generate QR B
            qr_b_img = self._make_qr_image(self.qr_segments[1], size=170)
            self.qr_b_label.configure(image=qr_b_img, text="")
            self._qr_b_ref = qr_b_img  # prevent GC

            seg_a_len = len(self.qr_segments[0])
            seg_b_len = len(self.qr_segments[1])
            total_b64 = len(self.qr_compressed_b64)

            self.qr_status_label.configure(
                text=f"2 QR codes ready — compressed {len(self.payload):,} to "
                     f"{total_b64:,} chars ({100 - total_b64 * 100 // len(self.b64_data):.0f}% smaller). "
                     f"Manager: scan QR A, paste to WA, then scan QR B, paste to WA."
            )

        except Exception as e:
            self.qr_a_label.configure(image=None, text=f"Error: {e}")
            self.qr_b_label.configure(image=None, text="—")
            self.qr_status_label.configure(
                text=f"QR generation failed. Use Copy Payload button instead."
            )

    def _make_qr_image(self, data, size=170):
        """Generate a single QR code CTkImage from text data."""
        qr = qrcode.QRCode(
            version=None,
            error_correction=ERROR_CORRECT_L,
            box_size=5,
            border=2,
        )
        qr.add_data(data)
        qr.make(fit=True)
        pil = qr.make_image(fill_color="#0A2A38", back_color="#FFFFFF").convert("RGB")
        pil = pil.resize((size, size), PILImage.NEAREST)

        return ctk.CTkImage(
            light_image=pil, dark_image=pil,
            size=(size, size)
        )

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
