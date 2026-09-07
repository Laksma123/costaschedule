#!/usr/bin/env python3
"""
Costa Cruises — Restaurant Schedule Exporter
═══════════════════════════════════════════════════════════════
Linear / Modern Precision Design System
Fast, fluid, high-contrast dark aesthetic with layered depth,
refined typography, subtle ambient glows, and 0% idle CPU.
═══════════════════════════════════════════════════════════════
"""

import sys
import os
import json
import datetime
import webbrowser
from PIL import Image
import customtkinter as ctk
from tkinter import filedialog, messagebox

from exporter import parse_schedule_excel, generate_payload, copy_to_clipboard

# ─────────────────────────────────────────────────────────────
# LINEAR / MODERN DESIGN TOKENS (The DNA)
# ─────────────────────────────────────────────────────────────
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

TK = {
    # ── Backgrounds (light, dark) ──
    "bg_deep":        ("#F4F6F8", "#001824"),
    "bg_base":        ("#FFFFFF", "#002235"),
    "bg_elevated":    ("#FFFFFF", "#002B40"),
    "surface":        ("#FFFFFF", "#00324A"),
    "surface_card":   ("#FFFFFF", "#003852"),
    "surface_inner":  ("#F8FAFC", "#00263B"),
    "surface_hover":  ("#EBF3F8", "#00415E"),
    "surface_active": ("#D5E8F3", "#004A6B"),
    "surface_badge":  ("#EBF3F8", "#003B57"),

    # ── Borders ──
    "border_subtle":  ("#E2E8F0", "#003B57"),
    "border_card":    ("#CBD5E1", "#004766"),
    "border_hover":   ("#94A6AE", "#005E85"),
    "border_focus":   ("#0071A3", "#0071A3"),
    "border_accent":  ("#BAE6FD", "#00557A"),

    # ── Accent Brand Blue (Costa #0071A3) ──
    "accent":         ("#0071A3", "#0071A3"),
    "accent_hover":   ("#005F8A", "#0088C4"),
    "accent_dim":     ("#D1E9F5", "#00324A"),
    "accent_bg":      ("#EBF5FA", "#002235"),
    "accent_glow":    ("#D0E8F5", "#003A55"),

    # ── Status Colors (Costa Yellow #F9B000) ──
    "gold_accent":    ("#F9B000", "#F9B000"),
    "gold_hover":     ("#E09E00", "#FFBE1A"),
    "gold_dim":       ("#FEF8E7", "#332400"),
    "cyan_accent":    ("#0071A3", "#38BDF8"),
    "cyan_dim":       ("#E0F2FE", "#092535"),
    "green_success":  ("#059669", "#10B981"),
    "green_hover":    ("#047857", "#059669"),
    "green_dim":      ("#D1FAE5", "#06281D"),
    "purple_accent":  ("#7C3AED", "#A855F7"),
    "purple_dim":     ("#EDE9FE", "#230F38"),
    "coral_accent":   ("#E11D48", "#FB7185"),
    "coral_dim":      ("#FFE4E6", "#2E0E15"),

    # ── Typography ──
    "fg_primary":     ("#0A2A38", "#FFFFFF"),
    "fg_secondary":   ("#5F7079", "#B2C1C9"),
    "fg_subtle":      ("#94A6AE", "#7A8F99"),
    "fg_accent":      ("#0071A3", "#38BDF8"),
}

def get_active_tokens():
    mode = ctk.get_appearance_mode().lower()
    idx = 1 if mode == "dark" else 0
    return {k: v[idx] if isinstance(v, (tuple, list)) else v for k, v in TK.items()}


try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    HAS_DND = True
except ImportError:
    HAS_DND = False

class CostaDesktopApp(ctk.CTk, TkinterDnD.DnDWrapper if HAS_DND else object):
    def __init__(self):
        super().__init__()

        # ── Setup Drag & Drop Support ──
        if HAS_DND:
            try:
                self.TkdndVersion = TkinterDnD._require(self)
                self.drop_target_register(DND_FILES)
                self.dnd_bind('<<Drop>>', self._on_file_drop)
            except Exception as e:
                print(f"[Warning] TkinterDnD initialization error: {e}")

        # ── Window Setup & Frame Metrics ──
        self.title("Costa Cruises — Schedule Exporter")
        self.geometry("1180x840")
        self.minsize(980, 720)
        self.configure(fg_color=TK["bg_base"])

        # ── Reactive State ──
        self.current_file = self._find_default_sample()
        self.schedule_data = None
        self.payload = ""
        self.b64_data = ""
        self.meal_shift = "LUNCH"
        self.active_filter = "ALL"
        self.search_query = ""
        self._toast_job = None

        # ── Asset Management ──
        self.logo_image = self._load_logo_image()

        # ── Build Layout Primitives ──
        self._build_sidebar()
        self._build_main_view()

        # ── Initial Auto-Parse ──
        if self.current_file and os.path.exists(self.current_file):
            self.after(60, self.process_schedule)

    # ─────────────────────────────────────────────────────────────
    # INITIALIZATION HELPERS
    # ─────────────────────────────────────────────────────────────
    def _find_default_sample(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        sample_path = os.path.join(base_dir, "sample", "Costa_Serena_Schedule_Sample.xlsx")
        if os.path.exists(sample_path):
            return sample_path
        return ""

    def _load_logo_image(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        logo_path = os.path.join(base_dir, "logo.png")
        if os.path.exists(logo_path):
            try:
                pil_img = Image.open(logo_path)
                return ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(38, 38))
            except Exception as e:
                print(f"[Warning] Could not load logo: {e}")
        return None

    # ─────────────────────────────────────────────────────────────
    # SIDEBAR: MINIMALIST PRECISION TOOLBAR
    # ─────────────────────────────────────────────────────────────
    def _build_sidebar(self):
        sidebar = ctk.CTkFrame(
            self,
            width=260,
            corner_radius=0,
            fg_color=TK["bg_elevated"],
            border_width=1,
            border_color=TK["border_subtle"]
        )
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        # ── Brand Header ──
        brand_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        brand_frame.pack(fill="x", padx=16, pady=(20, 14))

        if self.logo_image:
            logo_lbl = ctk.CTkLabel(brand_frame, image=self.logo_image, text="")
            logo_lbl.pack(side="left", padx=(0, 12))

        title_box = ctk.CTkFrame(brand_frame, fg_color="transparent")
        title_box.pack(side="left", fill="both", expand=True)

        ctk.CTkLabel(
            title_box,
            text="COSTA",
            font=ctk.CTkFont(family="Poppins", size=17, weight="bold"),
            text_color=TK["fg_primary"],
            anchor="w"
        ).pack(fill="x")

        tag_pill = ctk.CTkFrame(
            title_box,
            fg_color=TK["accent_bg"],
            corner_radius=4,
            border_width=1,
            border_color=TK["accent_dim"]
        )
        tag_pill.pack(anchor="w", pady=(2, 0))

        ctk.CTkLabel(
            tag_pill,
            text=" PRECISION ENGINE v2.6 ",
            font=ctk.CTkFont(family="Poppins", size=8, weight="bold"),
            text_color=TK["fg_accent"]
        ).pack(padx=2, pady=1)

        # ── Hairline Divider ──
        self._create_divider(sidebar, pady=8)

        # ── Section 1: Workflow Actions ──
        ctk.CTkLabel(
            sidebar,
            text="WORKFLOW ACTIONS",
            font=ctk.CTkFont(family="Poppins", size=9, weight="bold"),
            text_color=TK["fg_subtle"],
            anchor="w"
        ).pack(fill="x", padx=18, pady=(4, 6))

        nav_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        nav_frame.pack(fill="x", padx=14, pady=0)

        self.btn_browse = ctk.CTkButton(
            nav_frame,
            text=" 📂   Browse Roster (.xlsx)",
            font=ctk.CTkFont(family="Poppins", size=12, weight="bold"),
            fg_color=TK["surface"],
            hover_color=TK["surface_hover"],
            border_width=1,
            border_color=TK["border_card"],
            text_color=TK["fg_primary"],
            anchor="w",
            height=36,
            corner_radius=8,
            command=self.browse_file
        )
        self.btn_browse.pack(fill="x", pady=3)

        self.btn_refresh = ctk.CTkButton(
            nav_frame,
            text=" 🔄   Reload Active File",
            font=ctk.CTkFont(family="Poppins", size=12, weight="bold"),
            fg_color=TK["surface"],
            hover_color=TK["surface_hover"],
            border_width=1,
            border_color=TK["border_card"],
            text_color=TK["fg_secondary"],
            anchor="w",
            height=36,
            corner_radius=8,
            command=self.process_schedule
        )
        self.btn_refresh.pack(fill="x", pady=3)

        ctk.CTkLabel(
            nav_frame,
            text="💡 Tip: Drag & Drop .xlsx here",
            font=ctk.CTkFont(family="Poppins", size=9, weight="bold"),
            text_color=TK["fg_subtle"],
            anchor="center"
        ).pack(fill="x", pady=(2, 0))

        # ── Hairline Divider ──
        self._create_divider(sidebar, pady=10)

        # ── Section 2: Telemetry Snapshot ──
        ctk.CTkLabel(
            sidebar,
            text="TELEMETRY SUMMARY",
            font=ctk.CTkFont(family="Poppins", size=9, weight="bold"),
            text_color=TK["fg_subtle"],
            anchor="w"
        ).pack(fill="x", padx=18, pady=(2, 6))

        stats_card = ctk.CTkFrame(
            sidebar,
            fg_color=TK["surface_inner"],
            corner_radius=8,
            border_width=1,
            border_color=TK["border_subtle"]
        )
        stats_card.pack(fill="x", padx=14, pady=2)

        self.side_stat_crew = self._create_stat_row(stats_card, "👥 Total Crew Roster", "0 crew")
        self.side_stat_venues = self._create_stat_row(stats_card, "🏛️ Active Venues", "0 sections")
        self.side_stat_stream = self._create_stat_row(stats_card, "⚡ Encrypted Stream", "0 chars")

        # ── Sidebar Flexible Spacer ──
        ctk.CTkFrame(sidebar, fg_color="transparent").pack(fill="both", expand=True)

        # ── Sidebar Footer / Status & Theme ──
        footer = ctk.CTkFrame(sidebar, fg_color="transparent")
        footer.pack(fill="x", padx=14, pady=14)

        theme_row = ctk.CTkFrame(footer, fg_color="transparent")
        theme_row.pack(fill="x", pady=(0, 8))

        ctk.CTkLabel(
            theme_row,
            text="Appearance Mode",
            font=ctk.CTkFont(family="Poppins", size=10),
            text_color=TK["fg_subtle"]
        ).pack(side="left")

        self.theme_menu = ctk.CTkOptionMenu(
            theme_row,
            values=["Dark", "Light", "System"],
            width=84,
            height=24,
            corner_radius=6,
            fg_color=TK["surface"],
            button_color=TK["border_card"],
            button_hover_color=TK["accent"],
            text_color=TK["fg_primary"],
            font=ctk.CTkFont(family="Poppins", size=10),
            command=self._on_theme_changed
        )
        self.theme_menu.pack(side="right")
        self.theme_menu.set("Dark")

        status_box = ctk.CTkFrame(
            footer,
            fg_color=TK["surface_inner"],
            corner_radius=8,
            border_width=1,
            border_color=TK["border_subtle"]
        )
        status_box.pack(fill="x")

        self.lbl_system_status = ctk.CTkLabel(
            status_box,
            text="● Engine Ready (0% CPU)",
            font=ctk.CTkFont(family="Poppins", size=11, weight="bold"),
            text_color=TK["green_success"],
            pady=6
        )
        self.lbl_system_status.pack(anchor="center")

    def _create_stat_row(self, parent, label, value):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=10, pady=4)

        ctk.CTkLabel(
            row,
            text=label,
            font=ctk.CTkFont(family="Poppins", size=10),
            text_color=TK["fg_subtle"]
        ).pack(side="left")

        val_lbl = ctk.CTkLabel(
            row,
            text=value,
            font=ctk.CTkFont(family="Poppins", size=10, weight="bold"),
            text_color=TK["fg_secondary"]
        )
        val_lbl.pack(side="right")
        return val_lbl

    # ─────────────────────────────────────────────────────────────
    # MAIN VIEW CONTAINER
    # ─────────────────────────────────────────────────────────────
    def _build_main_view(self):
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(side="right", fill="both", expand=True, padx=20, pady=16)

        # ── 1. Top Header Banner & Telemetry ──
        self._build_header(main_frame)

        # ── 2. Bento Control Strip (Active File + Shift + Live Search) ──
        self._build_control_card(main_frame)

        # ── 3. Tabbed Interactive Workspaces ──
        self._build_content_tabs(main_frame)

        # ── 4. Bottom Precision Action Bar ──
        self._build_action_bar(main_frame)

    # ─────────────────────────────────────────────────────────────
    # TOP HEADER & TELEMETRY PILLS
    # ─────────────────────────────────────────────────────────────
    def _build_header(self, parent):
        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.pack(fill="x", pady=(0, 12))

        # Title & Subtitle with refined typography
        title_box = ctk.CTkFrame(header, fg_color="transparent")
        title_box.pack(side="left", fill="y")

        ctk.CTkLabel(
            title_box,
            text="Costa Schedule Exporter",
            font=ctk.CTkFont(family="Poppins", size=22, weight="bold"),
            text_color=TK["fg_primary"]
        ).pack(anchor="w")

        ctk.CTkLabel(
            title_box,
            text="Extract rosters, map multi-venue stations & generate encrypted WhatsApp payloads.",
            font=ctk.CTkFont(family="Poppins", size=12),
            text_color=TK["fg_secondary"]
        ).pack(anchor="w", pady=(2, 0))

        # Right-side Telemetry Badges
        self.badge_box = ctk.CTkFrame(header, fg_color="transparent")
        self.badge_box.pack(side="right", fill="y")

        self.badge_vessel = self._create_badge(self.badge_box, "🚢", "COSTA SERENA", TK["accent"], TK["accent_bg"])
        self.badge_date = self._create_badge(self.badge_box, "📅", "August 23, 2026", TK["gold_accent"], TK["gold_dim"])
        self.badge_port = self._create_badge(self.badge_box, "📍", "KAOHSIUNG", TK["cyan_accent"], TK["cyan_dim"])

    def _create_badge(self, parent, icon, text, fg_color, bg_tint):
        card = ctk.CTkFrame(
            parent,
            fg_color=TK["surface"],
            corner_radius=8,
            border_width=1,
            border_color=TK["border_card"]
        )
        card.pack(side="left", padx=3)

        lbl = ctk.CTkLabel(
            card,
            text=f"{icon}  {text}",
            font=ctk.CTkFont(family="Poppins", size=11, weight="bold"),
            text_color=fg_color,
            padx=10,
            pady=5
        )
        lbl.pack()
        return lbl

    # ─────────────────────────────────────────────────────────────
    # CONTROL CARD (FILE STATUS, SHIFT SELECTOR & LIVE SEARCH)
    # ─────────────────────────────────────────────────────────────
    def _build_control_card(self, parent):
        card = ctk.CTkFrame(
            parent,
            fg_color=TK["surface"],
            corner_radius=10,
            border_width=1,
            border_color=TK["border_card"]
        )
        card.pack(fill="x", pady=(0, 10))

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=14, pady=10)

        # Row 1: File Pill & Shift Selector
        r1 = ctk.CTkFrame(inner, fg_color="transparent")
        r1.pack(fill="x", pady=(0, 8))

        # Left: Active File Pill
        file_box = ctk.CTkFrame(r1, fg_color="transparent")
        file_box.pack(side="left", fill="x", expand=True, padx=(0, 14))

        ctk.CTkLabel(
            file_box,
            text="SOURCE ROSTER FILE",
            font=ctk.CTkFont(family="Poppins", size=9, weight="bold"),
            text_color=TK["fg_subtle"]
        ).pack(anchor="w")

        file_pill = ctk.CTkFrame(
            file_box,
            fg_color=TK["surface_inner"],
            corner_radius=8,
            border_width=1,
            border_color=TK["border_subtle"],
            height=34
        )
        file_pill.pack(fill="x", pady=(4, 0))
        file_pill.pack_propagate(False)

        self.lbl_file_display = ctk.CTkLabel(
            file_pill,
            text=self._format_file_display_text(),
            font=ctk.CTkFont(family="Poppins", size=11),
            text_color=TK["fg_secondary"],
            anchor="w",
            padx=10
        )
        self.lbl_file_display.pack(side="left", fill="both", expand=True)

        btn_browse_inline = ctk.CTkButton(
            file_pill,
            text="Browse...",
            font=ctk.CTkFont(family="Poppins", size=11, weight="bold"),
            fg_color=TK["surface_hover"],
            hover_color=TK["surface_active"],
            border_width=1,
            border_color=TK["border_card"],
            text_color=TK["fg_primary"],
            width=70,
            height=24,
            corner_radius=6,
            command=self.browse_file
        )
        btn_browse_inline.pack(side="right", padx=5)

        # Right: Shift Selector
        shift_box = ctk.CTkFrame(r1, fg_color="transparent")
        shift_box.pack(side="right")

        ctk.CTkLabel(
            shift_box,
            text="MEAL SHIFT",
            font=ctk.CTkFont(family="Poppins", size=9, weight="bold"),
            text_color=TK["fg_subtle"]
        ).pack(anchor="w")

        self.shift_selector = ctk.CTkSegmentedButton(
            shift_box,
            values=["BREAKFAST", "LUNCH", "DINNER"],
            font=ctk.CTkFont(family="Poppins", size=11, weight="bold"),
            height=34,
            corner_radius=20,
            border_width=2,
            selected_color=TK["accent"],
            selected_hover_color=TK["accent_hover"],
            unselected_color=TK["surface_inner"],
            unselected_hover_color=TK["surface_hover"],
            text_color=TK["fg_primary"],
            text_color_disabled=TK["fg_subtle"],
            command=self._on_shift_selected
        )
        self.shift_selector.pack(pady=(4, 0))
        self.shift_selector.set("LUNCH")

        # Row 2: Live Search & Quick Category Filters
        r2 = ctk.CTkFrame(inner, fg_color="transparent")
        r2.pack(fill="x")

        # Search Bar
        search_wrap = ctk.CTkFrame(
            r2,
            fg_color=TK["surface_inner"],
            corner_radius=8,
            border_width=1,
            border_color=TK["border_subtle"],
            height=32
        )
        search_wrap.pack(side="left", fill="x", expand=True, padx=(0, 10))
        search_wrap.pack_propagate(False)

        ctk.CTkLabel(
            search_wrap,
            text=" 🔍",
            font=ctk.CTkFont(family="Poppins", size=11),
            text_color=TK["fg_subtle"]
        ).pack(side="left", padx=(8, 2))

        self.search_entry = ctk.CTkEntry(
            search_wrap,
            placeholder_text="Filter crew name, ID, station, table, or duty...",
            placeholder_text_color=TK["fg_subtle"],
            fg_color="transparent",
            border_width=0,
            font=ctk.CTkFont(family="Poppins", size=11),
            text_color=TK["fg_primary"],
            height=28
        )
        self.search_entry.pack(side="left", fill="both", expand=True, padx=4)
        self.search_entry.bind("<KeyRelease>", self._on_search_changed)

        btn_clear = ctk.CTkButton(
            search_wrap,
            text="✕",
            width=24,
            height=20,
            corner_radius=4,
            fg_color="transparent",
            hover_color=TK["surface_hover"],
            text_color=TK["fg_subtle"],
            font=ctk.CTkFont(family="Poppins", size=10, weight="bold"),
            command=self._clear_search
        )
        btn_clear.pack(side="right", padx=4)

        # Quick Filter Pills
        self.filter_selector = ctk.CTkSegmentedButton(
            r2,
            values=["ALL", "MAIN DINING", "BUFFET & OUTLETS", "SIDE DUTIES"],
            font=ctk.CTkFont(family="Poppins", size=10, weight="bold"),
            height=30,
            corner_radius=20,
            border_width=2,
            selected_color=TK["accent_dim"],
            selected_hover_color=TK["accent"],
            unselected_color=TK["surface_inner"],
            unselected_hover_color=TK["surface_hover"],
            text_color=TK["fg_primary"],
            text_color_disabled=TK["fg_subtle"],
            command=self._on_filter_changed
        )
        self.filter_selector.pack(side="right")
        self.filter_selector.set("ALL")

    def _format_file_display_text(self):
        if not self.current_file:
            return "No file loaded — Click 'Browse...' to select roster (.xlsx)"
        name = os.path.basename(self.current_file)
        return f"📄 {name}  —  {self.current_file}"

    # ─────────────────────────────────────────────────────────────
    # TABBED INTERACTIVE CONTENT CENTER
    # ─────────────────────────────────────────────────────────────
    def _build_content_tabs(self, parent):
        tabview = ctk.CTkTabview(
            parent,
            fg_color=TK["surface"],
            corner_radius=12,
            border_width=1,
            border_color=TK["border_card"],
            segmented_button_fg_color=TK["surface_inner"],
            segmented_button_selected_color=TK["accent"],
            segmented_button_selected_hover_color=TK["accent_hover"],
            segmented_button_unselected_hover_color=TK["surface_hover"],
            segmented_button_unselected_color=TK["surface_inner"]
        )
        tabview._segmented_button.configure(
            font=ctk.CTkFont(family="Poppins", size=12, weight="bold"),
            corner_radius=20,
            border_width=2,
            height=36,
            text_color=TK["fg_primary"],
            text_color_disabled=TK["fg_subtle"]
        )
        tabview.pack(fill="both", expand=True, pady=(0, 10))

        # Tab 1: Visual Bento Explorer
        tab_bento = tabview.add("✨ Visual Bento Explorer")
        self._build_bento_tab(tab_bento)

        # Tab 2: WhatsApp Encrypted Payload
        tab_payload = tabview.add("💬 WhatsApp Payload (Live)")
        self._build_payload_tab(tab_payload)

        # Tab 3: Formatted Overview & JSON Inspector
        tab_overview = tabview.add("📊 Structured Overview & Raw Data")
        self._build_overview_tab(tab_overview)

        self.tabview = tabview

    # ─────────────────────────────────────────────────────────────
    # TAB 1: VISUAL BENTO EXPLORER
    # ─────────────────────────────────────────────────────────────
    def _build_bento_tab(self, parent):
        self.bento_scroll = ctk.CTkScrollableFrame(
            parent,
            fg_color="transparent",
            corner_radius=0
        )
        self.bento_scroll.pack(fill="both", expand=True, padx=2, pady=2)

        self.lbl_bento_empty = ctk.CTkLabel(
            self.bento_scroll,
            text="No schedule loaded. Click 'Browse Roster' to open an Excel file.",
            font=ctk.CTkFont(family="Poppins", size=13),
            text_color=TK["fg_secondary"],
            pady=40
        )
        self.lbl_bento_empty.pack(expand=True)

    def _render_bento_cards(self):
        for widget in self.bento_scroll.winfo_children():
            widget.destroy()

        d = self.schedule_data
        if not d:
            self.lbl_bento_empty = ctk.CTkLabel(
                self.bento_scroll,
                text="No schedule loaded. Click 'Browse Roster' to open an Excel file.",
                font=ctk.CTkFont(family="Poppins", size=13),
                text_color=TK["fg_secondary"],
                pady=40
            )
            self.lbl_bento_empty.pack(expand=True)
            return

        q = self.search_query.lower()
        active_filter = self.active_filter

        # ── 1. Top Metrics Bento Grid (4-card row) ──
        metrics_frame = ctk.CTkFrame(self.bento_scroll, fg_color="transparent")
        metrics_frame.pack(fill="x", pady=(0, 12))
        metrics_frame.columnconfigure((0, 1, 2, 3), weight=1, uniform="bento_stat")

        total_venues = len(d.get("venues", []))
        total_buffet = len(d.get("buffetAndVenues", []))
        total_side = len(d.get("sideDuties", []))
        
        all_crew_names = set()
        for v in d.get("venues", []):
            for a in v.get("assignments", []):
                if a.get("waiterName"): all_crew_names.add(a.get("waiterName"))
                if a.get("attendantName"): all_crew_names.add(a.get("attendantName"))
        for b in d.get("buffetAndVenues", []):
            for c in b.get("crew", []):
                if c.get("name"): all_crew_names.add(c.get("name"))
        for s in d.get("sideDuties", []):
            for c in s.get("crew", []):
                if c.get("name"): all_crew_names.add(c.get("name"))
        for sk in d.get("sickLeave", []):
            if sk.get("name"): all_crew_names.add(sk.get("name"))

        total_stations = sum(len(v.get("assignments", [])) for v in d.get("venues", []))

        self._build_metric_bento_card(metrics_frame, 0, "📍 PORT & MEAL", f"{d.get('port', '—')} • {d.get('meal', 'LUNCH')}", "📅 " + d.get('date', '—'), TK["cyan_accent"], TK["cyan_dim"])
        self._build_metric_bento_card(metrics_frame, 1, "👥 ACTIVE ROSTER", f"{len(all_crew_names)} Crew Members", f"{total_venues + total_buffet + total_side} Duty Sections", TK["accent"], TK["accent_bg"])
        self._build_metric_bento_card(metrics_frame, 2, "🍽️ DINING STATIONS", f"{total_stations} Active Tables", f"{total_venues} Restaurant Venues", TK["gold_accent"], TK["gold_dim"])
        self._build_metric_bento_card(metrics_frame, 3, "⚡ STREAM ENCODING", f"{len(self.payload):,} Chars Payload", f"{len(self.b64_data):,} Bytes Base64", TK["green_success"], TK["green_dim"])

        # ── 2. Main Dining Restaurants Bento Section ──
        if active_filter in ("ALL", "MAIN DINING"):
            for venue in d.get("venues", []):
                assignments = venue.get("assignments", [])
                filtered_assignments = [
                    a for a in assignments
                    if not q or (
                        q in a.get("station", "").lower()
                        or q in a.get("waiterName", "").lower()
                        or q in a.get("attendantName", "").lower()
                        or q in a.get("tables", "").lower()
                    )
                ]

                if filtered_assignments or not q:
                    self._build_venue_bento_card(self.bento_scroll, venue.get("name"), venue.get("reportTime", "—"), filtered_assignments)

        # ── 3. Buffet & Specialty Restaurants Bento Section ──
        if active_filter in ("ALL", "BUFFET & OUTLETS"):
            buffets = d.get("buffetAndVenues", [])
            for b in buffets:
                crew = b.get("crew", [])
                filtered_crew = [
                    c for c in crew
                    if not q or (
                        q in c.get("name", "").lower()
                        or q in c.get("role", "").lower()
                        or q in b.get("name", "").lower()
                    )
                ]

                if filtered_crew or not q:
                    self._build_buffet_bento_card(self.bento_scroll, b.get("name"), b.get("timing", "—"), b.get("lead", ""), filtered_crew)

        # ── 4. Sub-Teams & Side Duties Bento Section ──
        if active_filter in ("ALL", "SIDE DUTIES"):
            side_duties = d.get("sideDuties", [])
            for s in side_duties:
                crew = s.get("crew", [])
                filtered_crew = [
                    c for c in crew
                    if not q or (
                        q in c.get("name", "").lower()
                        or q in s.get("name", "").lower()
                    )
                ]

                if filtered_crew or not q:
                    self._build_side_duty_bento_card(self.bento_scroll, s.get("name"), s.get("timing", "—"), filtered_crew)

        # ── 5. Special Events & Sick Leave ──
        if active_filter == "ALL":
            if d.get("specialEvents"):
                self._build_special_events_card(self.bento_scroll, d.get("specialEvents", []), q)
            if d.get("sickLeave"):
                self._build_sick_leave_card(self.bento_scroll, d.get("sickLeave", []), q)

    def _build_metric_bento_card(self, parent, col, tag, title, subtitle, accent_color, bg_tint):
        card = ctk.CTkFrame(
            parent,
            fg_color=TK["surface_card"],
            corner_radius=10,
            border_width=1,
            border_color=TK["border_card"]
        )
        card.grid(row=0, column=col, padx=4, pady=2, sticky="nsew")

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=12, pady=10)

        tag_row = ctk.CTkFrame(inner, fg_color="transparent")
        tag_row.pack(fill="x")

        dot = ctk.CTkFrame(tag_row, width=6, height=6, corner_radius=3, fg_color=accent_color)
        dot.pack(side="left", padx=(0, 6))

        ctk.CTkLabel(
            tag_row,
            text=tag,
            font=ctk.CTkFont(family="Poppins", size=9, weight="bold"),
            text_color=TK["fg_subtle"]
        ).pack(side="left")

        ctk.CTkLabel(
            inner,
            text=title,
            font=ctk.CTkFont(family="Poppins", size=14, weight="bold"),
            text_color=TK["fg_primary"],
            anchor="w"
        ).pack(fill="x", pady=(6, 2))

        ctk.CTkLabel(
            inner,
            text=subtitle,
            font=ctk.CTkFont(family="Poppins", size=10),
            text_color=TK["fg_secondary"],
            anchor="w"
        ).pack(fill="x")

    def _build_venue_bento_card(self, parent, venue_name, report_time, assignments):
        card = ctk.CTkFrame(
            parent,
            fg_color=TK["surface_card"],
            corner_radius=10,
            border_width=1,
            border_color=TK["border_card"]
        )
        card.pack(fill="x", pady=6)

        hdr = ctk.CTkFrame(card, fg_color="transparent")
        hdr.pack(fill="x", padx=14, pady=(12, 8))

        ctk.CTkLabel(
            hdr,
            text=f"🏛️  {venue_name}",
            font=ctk.CTkFont(family="Poppins", size=13, weight="bold"),
            text_color=TK["fg_primary"]
        ).pack(side="left")

        pill = ctk.CTkFrame(
            hdr,
            fg_color=TK["accent_bg"],
            corner_radius=6,
            border_width=1,
            border_color=TK["accent_dim"]
        )
        pill.pack(side="right")

        ctk.CTkLabel(
            pill,
            text=f"⏰ Report: {report_time}  •  {len(assignments)} Stations",
            font=ctk.CTkFont(family="Poppins", size=10, weight="bold"),
            text_color=TK["fg_accent"]
        ).pack(padx=8, pady=3)

        body = ctk.CTkFrame(card, fg_color="transparent")
        body.pack(fill="x", padx=10, pady=(0, 10))

        for idx, a in enumerate(assignments):
            row_bg = TK["surface_inner"] if idx % 2 == 0 else TK["surface"]
            row = ctk.CTkFrame(
                body,
                fg_color=row_bg,
                corner_radius=6,
                border_width=1,
                border_color=TK["border_subtle"]
            )
            row.pack(fill="x", pady=2, padx=4)

            stn_pill = ctk.CTkFrame(
                row,
                fg_color=TK["surface_badge"],
                corner_radius=4,
                border_width=1,
                border_color=TK["border_card"]
            )
            stn_pill.pack(side="left", padx=8, pady=6)

            ctk.CTkLabel(
                stn_pill,
                text=a.get("station", "—"),
                font=ctk.CTkFont(family="Poppins", size=10, weight="bold"),
                text_color=TK["cyan_accent"]
            ).pack(padx=6, pady=2)

            waiter_text = f"👤 {a.get('waiterName', '—')}" if a.get('waiterName') else "—"
            ctk.CTkLabel(
                row,
                text=waiter_text,
                font=ctk.CTkFont(family="Poppins", size=11, weight="bold"),
                text_color=TK["fg_primary"],
                anchor="w"
            ).pack(side="left", padx=8)

            if a.get("attendantName"):
                att_text = f"👥 Attendant: {a.get('attendantName', '')}"
                ctk.CTkLabel(
                    row,
                    text=att_text,
                    font=ctk.CTkFont(family="Poppins", size=11),
                    text_color=TK["fg_secondary"],
                    anchor="w"
                ).pack(side="left", padx=8)

            if a.get("tables"):
                tbl_pill = ctk.CTkFrame(
                    row,
                    fg_color=TK["gold_dim"],
                    corner_radius=4,
                    border_width=1,
                    border_color=TK["border_subtle"]
                )
                tbl_pill.pack(side="right", padx=8, pady=6)

                ctk.CTkLabel(
                    tbl_pill,
                    text=f"🪑 {a.get('tables')}",
                    font=ctk.CTkFont(family="Poppins", size=10, weight="bold"),
                    text_color=TK["gold_accent"]
                ).pack(padx=6, pady=2)

    def _build_buffet_bento_card(self, parent, name, timing, lead, crew):
        card = ctk.CTkFrame(
            parent,
            fg_color=TK["surface_card"],
            corner_radius=10,
            border_width=1,
            border_color=TK["border_card"]
        )
        card.pack(fill="x", pady=6)

        hdr = ctk.CTkFrame(card, fg_color="transparent")
        hdr.pack(fill="x", padx=14, pady=(12, 8))

        ctk.CTkLabel(
            hdr,
            text=f"🥗  {name}",
            font=ctk.CTkFont(family="Poppins", size=13, weight="bold"),
            text_color=TK["fg_primary"]
        ).pack(side="left")

        if lead:
            lead_pill = ctk.CTkFrame(
                hdr,
                fg_color=TK["gold_dim"],
                corner_radius=6,
                border_width=1,
                border_color=TK["border_subtle"]
            )
            lead_pill.pack(side="left", padx=10)

            ctk.CTkLabel(
                lead_pill,
                text=f"⭐ Lead: {lead}",
                font=ctk.CTkFont(family="Poppins", size=10, weight="bold"),
                text_color=TK["gold_accent"]
            ).pack(padx=8, pady=2)

        pill = ctk.CTkFrame(
            hdr,
            fg_color=TK["surface_badge"],
            corner_radius=6,
            border_width=1,
            border_color=TK["border_card"]
        )
        pill.pack(side="right")

        ctk.CTkLabel(
            pill,
            text=f"⏰ {timing}  •  {len(crew)} Crew",
            font=ctk.CTkFont(family="Poppins", size=10, weight="bold"),
            text_color=TK["fg_secondary"]
        ).pack(padx=8, pady=3)

        body = ctk.CTkFrame(card, fg_color="transparent")
        body.pack(fill="x", padx=12, pady=(0, 12))

        chip_frame = ctk.CTkFrame(body, fg_color="transparent")
        chip_frame.pack(fill="x")

        for c in crew:
            role_suffix = f" — {c.get('role')}" if c.get('role') else ""
            chip = ctk.CTkFrame(
                chip_frame,
                fg_color=TK["surface_inner"],
                corner_radius=6,
                border_width=1,
                border_color=TK["border_subtle"]
            )
            chip.pack(side="left", padx=3, pady=3)

            ctk.CTkLabel(
                chip,
                text=f"{c.get('name', '')}{role_suffix}",
                font=ctk.CTkFont(family="Poppins", size=10),
                text_color=TK["fg_primary"]
            ).pack(padx=6, pady=3)

    def _build_side_duty_bento_card(self, parent, name, timing, crew):
        card = ctk.CTkFrame(
            parent,
            fg_color=TK["surface_card"],
            corner_radius=10,
            border_width=1,
            border_color=TK["border_card"]
        )
        card.pack(fill="x", pady=6)

        hdr = ctk.CTkFrame(card, fg_color="transparent")
        hdr.pack(fill="x", padx=14, pady=(10, 6))

        ctk.CTkLabel(
            hdr,
            text=f"⚡  {name}",
            font=ctk.CTkFont(family="Poppins", size=12, weight="bold"),
            text_color=TK["fg_primary"]
        ).pack(side="left")

        pill = ctk.CTkFrame(
            hdr,
            fg_color=TK["purple_dim"],
            corner_radius=6,
            border_width=1,
            border_color=TK["border_subtle"]
        )
        pill.pack(side="right")

        ctk.CTkLabel(
            pill,
            text=f"⏰ {timing}  •  {len(crew)} Crew",
            font=ctk.CTkFont(family="Poppins", size=10, weight="bold"),
            text_color=TK["purple_accent"]
        ).pack(padx=8, pady=2)

        body = ctk.CTkFrame(card, fg_color="transparent")
        body.pack(fill="x", padx=12, pady=(0, 10))

        for c in crew:
            chip = ctk.CTkFrame(
                body,
                fg_color=TK["surface_inner"],
                corner_radius=6,
                border_width=1,
                border_color=TK["border_subtle"]
            )
            chip.pack(side="left", padx=3, pady=2)

            ctk.CTkLabel(
                chip,
                text=f"{c.get('name', '')}",
                font=ctk.CTkFont(family="Poppins", size=10),
                text_color=TK["fg_secondary"]
            ).pack(padx=6, pady=2)

    def _build_special_events_card(self, parent, events, query):
        card = ctk.CTkFrame(
            parent,
            fg_color=TK["surface_card"],
            corner_radius=10,
            border_width=1,
            border_color=TK["border_card"]
        )
        card.pack(fill="x", pady=6)

        hdr = ctk.CTkFrame(card, fg_color="transparent")
        hdr.pack(fill="x", padx=14, pady=(10, 6))

        ctk.CTkLabel(
            hdr,
            text="🎭  SPECIAL EVENTS & TRAVEL TALK",
            font=ctk.CTkFont(family="Poppins", size=12, weight="bold"),
            text_color=TK["gold_accent"]
        ).pack(side="left")

        body = ctk.CTkFrame(card, fg_color="transparent")
        body.pack(fill="x", padx=12, pady=(0, 10))

        for ev in events:
            ev_box = ctk.CTkFrame(body, fg_color=TK["surface_inner"], corner_radius=6, border_width=1, border_color=TK["border_subtle"])
            ev_box.pack(fill="x", pady=3)

            ctk.CTkLabel(
                ev_box,
                text=f"📌 {ev.get('title')}  —  {ev.get('location')}",
                font=ctk.CTkFont(family="Poppins", size=11, weight="bold"),
                text_color=TK["fg_primary"],
                anchor="w"
            ).pack(fill="x", padx=8, pady=(6, 4))

            p_frame = ctk.CTkFrame(ev_box, fg_color="transparent")
            p_frame.pack(fill="x", padx=6, pady=(0, 6))

            for p in ev.get("participants", []):
                chip = ctk.CTkFrame(p_frame, fg_color=TK["surface_badge"], corner_radius=4, border_width=1, border_color=TK["border_card"])
                chip.pack(side="left", padx=2, pady=2)

                ctk.CTkLabel(
                    chip,
                    text=f"{p.get('name')} [{p.get('uniform')}]",
                    font=ctk.CTkFont(family="Poppins", size=9),
                    text_color=TK["fg_secondary"]
                ).pack(padx=5, pady=2)

    def _build_sick_leave_card(self, parent, sick_list, query):
        card = ctk.CTkFrame(
            parent,
            fg_color=TK["surface_card"],
            corner_radius=10,
            border_width=1,
            border_color=TK["border_card"]
        )
        card.pack(fill="x", pady=6)

        hdr = ctk.CTkFrame(card, fg_color="transparent")
        hdr.pack(fill="x", padx=14, pady=(10, 6))

        ctk.CTkLabel(
            hdr,
            text="🏥  SICK LEAVE / OFF DUTY",
            font=ctk.CTkFont(family="Poppins", size=12, weight="bold"),
            text_color=TK["coral_accent"]
        ).pack(side="left")

        body = ctk.CTkFrame(card, fg_color="transparent")
        body.pack(fill="x", padx=12, pady=(0, 10))

        for sk in sick_list:
            chip = ctk.CTkFrame(body, fg_color=TK["coral_dim"], corner_radius=4, border_width=1, border_color=TK["border_subtle"])
            chip.pack(side="left", padx=3, pady=2)

            ctk.CTkLabel(
                chip,
                text=f"{sk.get('name')}",
                font=ctk.CTkFont(family="Poppins", size=10, weight="bold"),
                text_color=TK["coral_accent"]
            ).pack(padx=6, pady=2)

    # ─────────────────────────────────────────────────────────────
    # TAB 2: WHATSAPP ENCRYPTED PAYLOAD
    # ─────────────────────────────────────────────────────────────
    def _build_payload_tab(self, parent):
        info_bar = ctk.CTkFrame(parent, fg_color="transparent")
        info_bar.pack(fill="x", padx=6, pady=(6, 8))

        tag_box = ctk.CTkFrame(info_bar, fg_color="transparent")
        tag_box.pack(side="left")

        ctk.CTkLabel(
            tag_box,
            text="● ENCRYPTED TRANSMISSION STREAM",
            font=ctk.CTkFont(family="Poppins", size=10, weight="bold"),
            text_color=TK["accent"]
        ).pack(side="left")

        right_bar = ctk.CTkFrame(info_bar, fg_color="transparent")
        right_bar.pack(side="right")

        self.lbl_payload_metrics = ctk.CTkLabel(
            right_bar,
            text="0 characters · 0 bytes base64",
            font=ctk.CTkFont(family="SF Mono", size=11),
            text_color=TK["fg_subtle"]
        )
        self.lbl_payload_metrics.pack(side="left", padx=(0, 10))

        btn_copy_tab2 = ctk.CTkButton(
            right_bar,
            text="📋 Copy Stream",
            font=ctk.CTkFont(family="Poppins", size=10, weight="bold"),
            fg_color=TK["surface_hover"],
            hover_color=TK["accent"],
            text_color=TK["fg_primary"],
            width=88,
            height=24,
            corner_radius=6,
            command=self.copy_payload_action
        )
        btn_copy_tab2.pack(side="left")

        self.txt_payload = ctk.CTkTextbox(
            parent,
            font=ctk.CTkFont(family="SF Mono", size=11),
            fg_color=TK["surface_inner"],
            text_color=TK["fg_primary"],
            border_width=1,
            border_color=TK["border_subtle"],
            corner_radius=8,
            wrap="char"
        )
        self.txt_payload.pack(fill="both", expand=True, padx=4, pady=(0, 6))

    # ─────────────────────────────────────────────────────────────
    # TAB 3: STRUCTURED OVERVIEW & JSON
    # ─────────────────────────────────────────────────────────────
    def _build_overview_tab(self, parent):
        top_bar = ctk.CTkFrame(parent, fg_color="transparent")
        top_bar.pack(fill="x", padx=6, pady=(6, 6))

        ctk.CTkLabel(
            top_bar,
            text="STRUCTURED PARSED TEXT STREAM",
            font=ctk.CTkFont(family="Poppins", size=10, weight="bold"),
            text_color=TK["fg_subtle"]
        ).pack(side="left")

        actions_bar = ctk.CTkFrame(top_bar, fg_color="transparent")
        actions_bar.pack(side="right")

        btn_copy_text = ctk.CTkButton(
            actions_bar,
            text="📋 Copy Text",
            font=ctk.CTkFont(family="Poppins", size=10, weight="bold"),
            fg_color=TK["surface_hover"],
            hover_color=TK["accent"],
            text_color=TK["fg_primary"],
            width=76,
            height=24,
            corner_radius=6,
            command=self.copy_overview_text_action
        )
        btn_copy_text.pack(side="left", padx=(0, 6))

        btn_backup = ctk.CTkButton(
            actions_bar,
            text="💾 Save Backup (Timestamp)",
            font=ctk.CTkFont(family="Poppins", size=10, weight="bold"),
            fg_color=TK["green_success"],
            hover_color=TK["green_hover"],
            text_color="#FFFFFF",
            width=150,
            height=24,
            corner_radius=6,
            command=self.save_json_backup_action
        )
        btn_backup.pack(side="left", padx=(0, 6))

        btn_export = ctk.CTkButton(
            actions_bar,
            text="📁 Export As...",
            font=ctk.CTkFont(family="Poppins", size=10, weight="bold"),
            fg_color=TK["surface_hover"],
            hover_color=TK["accent"],
            text_color=TK["fg_primary"],
            width=88,
            height=24,
            corner_radius=6,
            command=self.export_json_action
        )
        btn_export.pack(side="left")

        self.txt_overview = ctk.CTkTextbox(
            parent,
            font=ctk.CTkFont(family="SF Mono", size=11),
            fg_color=TK["surface_inner"],
            text_color=TK["fg_primary"],
            border_width=1,
            border_color=TK["border_subtle"],
            corner_radius=8,
            wrap="word"
        )
        self.txt_overview.pack(fill="both", expand=True, padx=4, pady=4)

    # ─────────────────────────────────────────────────────────────
    # BOTTOM ACTION BAR (LINEAR SIGNATURE ACCENT CTA)
    # ─────────────────────────────────────────────────────────────
    def _build_action_bar(self, parent):
        action_bar = ctk.CTkFrame(parent, fg_color="transparent")
        action_bar.pack(fill="x", padx=2)

        self.btn_primary_copy = ctk.CTkButton(
            action_bar,
            text="📋  COPY ENCRYPTED SCHEDULE TO CLIPBOARD",
            font=ctk.CTkFont(family="Poppins", size=13, weight="bold"),
            fg_color=TK["accent"],
            hover_color=TK["accent_hover"],
            text_color="#FFFFFF",
            height=44,
            corner_radius=8,
            command=self.copy_payload_action
        )
        self.btn_primary_copy.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.btn_secondary_web = ctk.CTkButton(
            action_bar,
            text="🌐 Open WebApp Viewer",
            font=ctk.CTkFont(family="Poppins", size=12, weight="bold"),
            fg_color=TK["surface"],
            hover_color=TK["surface_hover"],
            border_width=1,
            border_color=TK["border_card"],
            text_color=TK["fg_primary"],
            height=44,
            corner_radius=8,
            command=self.open_webapp
        )
        self.btn_secondary_web.pack(side="right", padx=0)

    # ─────────────────────────────────────────────────────────────
    # BUSINESS LOGIC & ROSTER PROCESSING
    # ─────────────────────────────────────────────────────────────
    def browse_file(self):
        """Open native Mac/Windows file chooser with instant zero freeze."""
        self.update_idletasks()
        selected = filedialog.askopenfilename(
            parent=self,
            title="Select Costa Schedule Excel (.xlsx)",
            filetypes=[("Excel Files", "*.xlsx *.xls"), ("All Files", "*.*")]
        )
        if selected:
            self.current_file = selected
            self.lbl_file_display.configure(text=self._format_file_display_text())
            self.process_schedule()

    def _on_file_drop(self, event):
        """Handle Drag & Drop of Excel schedule files."""
        raw_data = (event.data or "").strip()
        if raw_data.startswith('{') and raw_data.endswith('}'):
            raw_data = raw_data[1:-1]
        elif raw_data.startswith('"') and raw_data.endswith('"'):
            raw_data = raw_data[1:-1]

        file_path = raw_data.strip()
        if file_path.lower().endswith(('.xlsx', '.xls')) and os.path.exists(file_path):
            self.current_file = file_path
            self.lbl_file_display.configure(text=self._format_file_display_text())
            self.process_schedule()
            self._show_toast("📥 Roster Loaded via Drag & Drop", color=TK["green_success"][1])
        else:
            self._show_toast("⚠️ Please drop a valid Excel file (.xlsx)", color=TK["gold_accent"][1])

    def _on_shift_selected(self, value):
        self.meal_shift = value
        if self.current_file:
            self.process_schedule()

    def _on_search_changed(self, event=None):
        self.search_query = self.search_entry.get().strip()
        self._render_bento_cards()

    def _clear_search(self):
        self.search_entry.delete(0, "end")
        self.search_query = ""
        self._render_bento_cards()

    def _on_filter_changed(self, value):
        self.active_filter = value
        self._render_bento_cards()

    def process_schedule(self):
        """Parse active Excel file and generate compressed payload."""
        if not self.current_file or not os.path.exists(self.current_file):
            return

        self.lbl_system_status.configure(text="● Parsing Roster...", text_color=TK["accent"])
        self.update_idletasks()

        try:
            self.schedule_data = parse_schedule_excel(self.current_file, self.meal_shift)
            self.payload, self.b64_data = generate_payload(self.schedule_data)
            self._render_results()
            self.lbl_system_status.configure(text="● Engine Ready (0% CPU)", text_color=TK["green_success"])
        except Exception as err:
            self.lbl_system_status.configure(text="● Parse Error", text_color="#EF4444")
            messagebox.showerror("Parsing Error", f"Failed to parse Excel schedule:\n\n{err}")

    def _render_results(self):
        d = self.schedule_data
        if not d:
            return

        # 1. Update Telemetry Badges
        self.badge_vessel.configure(text=f"🚢  {d.get('ship', 'COSTA')}")
        self.badge_date.configure(text=f"📅  {d.get('date', '—')}")
        self.badge_port.configure(text=f"📍  {d.get('port', '—')}")

        # 2. Update Sidebar Telemetry
        all_crew_names = set()
        for v in d.get("venues", []):
            for a in v.get("assignments", []):
                if a.get("waiterName"): all_crew_names.add(a.get("waiterName"))
                if a.get("attendantName"): all_crew_names.add(a.get("attendantName"))
        for b in d.get("buffetAndVenues", []):
            for c in b.get("crew", []):
                if c.get("name"): all_crew_names.add(c.get("name"))
        for s in d.get("sideDuties", []):
            for c in s.get("crew", []):
                if c.get("name"): all_crew_names.add(c.get("name"))
        for sk in d.get("sickLeave", []):
            if sk.get("name"): all_crew_names.add(sk.get("name"))

        total_sections = len(d.get('venues', [])) + len(d.get('buffetAndVenues', [])) + len(d.get('sideDuties', []))
        self.side_stat_crew.configure(text=f"{len(all_crew_names)} crew")
        self.side_stat_venues.configure(text=f"{total_sections} sections")
        self.side_stat_stream.configure(text=f"{len(self.payload):,} chars")

        # 3. Update Payload Metrics & Stream
        chars = len(self.payload)
        b64_len = len(self.b64_data)
        self.lbl_payload_metrics.configure(text=f"{chars:,} chars · {b64_len:,} bytes encoded")

        self.txt_payload.delete("1.0", "end")
        self.txt_payload.insert("1.0", self.payload)

        # 4. Update Structured Overview Stream
        overview_text = self._build_overview_text(d)
        self.txt_overview.delete("1.0", "end")
        self.txt_overview.insert("1.0", overview_text)

        # 5. Render Interactive Bento Cards
        self._render_bento_cards()

    def _build_overview_text(self, d):
        lines = []
        lines.append(f"🚢 VESSEL : {d.get('ship', '')}")
        lines.append(f"📅 DATE   : {d.get('date', '')}  |  PORT: {d.get('port', '')}")
        lines.append(f"🍽️ SHIFT  : {d.get('shift', '')} [{d.get('meal', '')}]")
        lines.append("─" * 68)
        lines.append("")

        # Venues
        lines.append("🏛️ MAIN RESTAURANTS & STATIONS:")
        for v in d.get("venues", []):
            lines.append(f"  ┌ {v.get('name')} (Report: {v.get('reportTime', '—')})")
            for a in v.get("assignments", []):
                waiter = f"{a.get('waiterName')}" if a.get('waiterName') else "—"
                attendant = f" / Attendant: {a.get('attendantName')}" if a.get('attendantName') else ""
                lines.append(f"  │  • {a.get('station')}: {waiter}{attendant} [{a.get('tables')}]")
            lines.append("  └" + "─" * 40)
        lines.append("")

        # Buffet & Special Outlets
        lines.append("🥗 BUFFET & SPECIALTY RESTAURANTS:")
        for b in d.get("buffetAndVenues", []):
            lead = f" (Lead: {b.get('lead')})" if b.get('lead') else ""
            lines.append(f"  • {b.get('name')} | Timing: {b.get('timing', '—')}{lead}")
            crew_list = [f"{c.get('name')}" + (f" ({c.get('role')})" if c.get('role') else "") for c in b.get('crew', [])]
            if crew_list:
                lines.append(f"      Crew ({len(crew_list)}): " + ", ".join(crew_list))
        lines.append("")

        # Side Duties
        lines.append("⚡ SUB-TEAMS & SIDE DUTIES:")
        for s in d.get("sideDuties", []):
            lines.append(f"  • {s.get('name')} (Timing: {s.get('timing', '—')})")
            crew_str = ", ".join([f"{c.get('name')}" for c in s.get('crew', [])])
            lines.append(f"      Crew: {crew_str}")
        lines.append("")

        # Special Events
        if d.get("specialEvents"):
            lines.append("🎭 SPECIAL EVENTS & TRAVEL TALK:")
            for ev in d.get("specialEvents", []):
                lines.append(f"  • {ev.get('title')} ({ev.get('location')})")
                for p in ev.get("participants", []):
                    lines.append(f"      - {p.get('name')} [{p.get('uniform')}]")
            lines.append("")

        # Sick Leave
        if d.get("sickLeave"):
            lines.append("🏥 SICK LEAVE / OFF:")
            for sk in d.get("sickLeave", []):
                lines.append(f"  • {sk.get('name')}")

        return "\n".join(lines)

    # ─────────────────────────────────────────────────────────────
    # CLIPBOARD & NOTIFICATIONS
    # ─────────────────────────────────────────────────────────────
    def copy_payload_action(self):
        """Copy active payload to clipboard with precision feedback."""
        if not self.payload:
            messagebox.showwarning("No Schedule", "Please load and process a schedule file first.")
            return

        success = copy_to_clipboard(self.payload)
        if not success:
            self.clipboard_clear()
            self.clipboard_append(self.payload)

        self._trigger_copy_feedback()

    def copy_overview_text_action(self):
        txt = self.txt_overview.get("1.0", "end").strip()
        if not txt:
            return
        success = copy_to_clipboard(txt)
        if not success:
            self.clipboard_clear()
            self.clipboard_append(txt)
        messagebox.showinfo("Copied", "Structured overview text copied to clipboard.")

    def _trigger_copy_feedback(self):
        if self._toast_job:
            self.after_cancel(self._toast_job)

        self.btn_primary_copy.configure(
            text="✓  COPIED TO CLIPBOARD! READY TO PASTE ON WHATSAPP",
            fg_color=TK["green_success"],
            hover_color=TK["green_hover"],
            text_color="#FFFFFF"
        )

        self._toast_job = self.after(2400, self._restore_copy_buttons)

    def _restore_copy_buttons(self):
        self.btn_primary_copy.configure(
            text="📋  COPY ENCRYPTED SCHEDULE TO CLIPBOARD",
            fg_color=TK["accent"],
            hover_color=TK["accent_hover"],
            text_color="#FFFFFF"
        )

    # ─────────────────────────────────────────────────────────────
    # EXPORT DATA
    # ─────────────────────────────────────────────────────────────
    def save_json_backup_action(self):
        if not self.schedule_data:
            messagebox.showwarning("No Data", "Please load a schedule first.")
            return

        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            save_dir = os.path.join(base_dir, "Save Data")
            os.makedirs(save_dir, exist_ok=True)

            now_str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            ship_slug = str(self.schedule_data.get("ship", "Costa")).replace(" ", "_")
            meal_slug = str(self.schedule_data.get("meal", "Schedule")).replace(" ", "_")
            filename = f"{ship_slug}_{meal_slug}_{now_str}.json"
            filepath = os.path.join(save_dir, filename)

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(self.schedule_data, f, indent=2, ensure_ascii=False)

            messagebox.showinfo("Backup Saved", f"Schedule saved to Save Data:\n{filename}\n\nPath:\n{filepath}")
        except Exception as err:
            messagebox.showerror("Save Failed", f"Failed to save backup:\n{err}")

    def export_json_action(self):
        if not self.schedule_data:
            messagebox.showwarning("No Data", "Please load a schedule first.")
            return

        out_path = filedialog.asksaveasfilename(
            parent=self,
            title="Export Schedule JSON",
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json")]
        )
        if out_path:
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(self.schedule_data, f, indent=2, ensure_ascii=False)
            messagebox.showinfo("Export Successful", f"Schedule saved to:\n{out_path}")

    # ─────────────────────────────────────────────────────────────
    # EXTERNAL LAUNCHERS
    # ─────────────────────────────────────────────────────────────
    def open_webapp(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        html_path = os.path.join(base_dir, "CostaSchedule.html")
        if os.path.exists(html_path):
            webbrowser.open(f"file://{html_path}")
        else:
            messagebox.showwarning("File Missing", "CostaSchedule.html not found in project directory.")

    def _create_divider(self, parent, pady=8):
        t = get_active_tokens()
        div = ctk.CTkFrame(parent, height=1, fg_color=t["border_subtle"])
        div.pack(fill="x", padx=16, pady=pady)
        return div

    # ─────────────────────────────────────────────────────────────
    # THEME SWITCHING ENGINE
    # ─────────────────────────────────────────────────────────────
    def _on_theme_changed(self, mode):
        """Apply theme change and rebuild UI with correct token set."""
        ctk.set_appearance_mode(mode)

        # Small delay to let ctk finish mode switch before we re-color
        self.after(50, self._apply_theme_colors)

    def _apply_theme_colors(self):
        """Re-apply all color tokens to match current appearance mode."""
        t = get_active_tokens()

        # Window base
        self.configure(fg_color=t["bg_base"])

        # Re-apply key segmented button colors
        try:
            self.shift_selector.configure(
                selected_color=t["accent"],
                selected_hover_color=t["accent_hover"],
                unselected_color=t["surface_inner"],
                unselected_hover_color=t["surface_hover"],
                text_color=t["fg_primary"]
            )
            self.filter_selector.configure(
                selected_color=t["accent_dim"],
                selected_hover_color=t["accent"],
                unselected_color=t["surface_inner"],
                unselected_hover_color=t["surface_hover"],
                text_color=t["fg_primary"]
            )
            # Tab pills
            self.tabview.configure(
                fg_color=t["surface"],
                border_color=t["border_card"],
                segmented_button_fg_color=t["surface_inner"],
                segmented_button_selected_color=t["accent"],
                segmented_button_selected_hover_color=t["accent_hover"],
                segmented_button_unselected_hover_color=t["surface_hover"]
            )
            self.tabview._segmented_button.configure(
                text_color=t["fg_primary"]
            )
            # Payload & overview textboxes
            self.txt_payload.configure(
                fg_color=t["surface_inner"],
                text_color=t["fg_primary"],
                border_color=t["border_subtle"]
            )
            self.txt_overview.configure(
                fg_color=t["surface_inner"],
                text_color=t["fg_primary"],
                border_color=t["border_subtle"]
            )
            # Action bar primary CTA
            self.btn_primary_copy.configure(
                fg_color=t["accent"],
                hover_color=t["accent_hover"]
            )
            self.btn_secondary_web.configure(
                fg_color=t["surface"],
                hover_color=t["surface_hover"],
                border_color=t["border_card"],
                text_color=t["fg_primary"]
            )
            # System status
            self.lbl_system_status.configure(
                text_color=t["green_success"]
            )
        except Exception:
            pass  # Graceful degradation if widgets not yet built


# ─────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────
def launch_gui():
    app = CostaDesktopApp()
    app.mainloop()

if __name__ == "__main__":
    launch_gui()
