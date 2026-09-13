#!/usr/bin/env python3
"""
Costa Cruises — Restaurant Schedule Exporter
Desktop Edition — Newspaper Elegance Light Theme
═══════════════════════════════════════════════════
Strictly follows Costa Interface Guidelines (/costaassets):
  - Pure white canvas (#FFFFFF) with hairlines (#E2E8F0, #CBD5E1)
  - Official Poppins typography loaded from costaassets/Poppins
  - Title with signature Costa yellow/orange dot (. in #F9B000, +20% size)
  - Zero emojis: 100% crisp antialiased vector line icons
  - Outline pill buttons matching CostaSchedule.html (.outline-pill-btn)
  - Perfectly proportioned side-by-side Airgap QR code preview (no cutoff)
  - One primary action per screen rule (#F9B000 with #0A2A38 dark text)
  - 100% English interface
═══════════════════════════════════════════════════
"""

import os
import sys
import json
import datetime
import webbrowser
import io
from PIL import Image as PILImage, ImageDraw
import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog, messagebox

try:
    import fitz
    HAS_FITZ = True
except ImportError:
    HAS_FITZ = False

import qrcode
from qrcode.constants import ERROR_CORRECT_L

from exporter import (
    parse_schedule_excel,
    generate_payload,
    generate_compressed_payload,
    copy_to_clipboard
)

# ─────────────────────────────────────────────────────────────
# LOAD OFFICIAL COSTA FONTS (Poppins from /costaassets)
# ─────────────────────────────────────────────────────────────
def _load_brand_fonts():
    """Load all Poppins font variants from costaassets/Poppins into CustomTkinter."""
    base = os.path.dirname(os.path.abspath(__file__))
    font_dir = os.path.join(base, "costaassets", "Poppins")
    if os.path.exists(font_dir):
        for fname in os.listdir(font_dir):
            if fname.endswith(".ttf"):
                try:
                    ctk.FontManager.load_font(os.path.join(font_dir, fname))
                except Exception:
                    pass

_load_brand_fonts()

# ─────────────────────────────────────────────────────────────
# COSTA NEWSPAPER LIGHT DESIGN TOKENS  (InterfaceGuidelines.md)
# ─────────────────────────────────────────────────────────────
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

TK = {
    # Surfaces & Canvas (Newspaper editorial pure white)
    "bg_base":        "#FFFFFF",
    "bg_elevated":    "#FFFFFF",
    "surface":        "#FFFFFF",
    "surface_card":   "#FFFFFF",
    "surface_inner":  "#F8FAFC",
    "surface_hover":  "#F1F5F9",
    "surface_active": "#E2E8F0",
    "surface_badge":  "#EBF5FA",

    # Hairline Borders (thin lines like newspaper divisions)
    "border_subtle":  "#F1F5F9",
    "border_card":    "#CBD5E1",
    "border_inner":   "#E2E8F0",
    "border_focus":   "#0071A3",

    # Costa Institutional Blue (RAL 5015 / Pantone 7690 C)
    "accent":         "#0071A3",
    "accent_hover":   "#005F8A",
    "accent_dim":     "#EBF5FA",
    "accent_border":  "#BAE6FD",

    # Costa Yellow/Orange (RAL 1003 / Pantone 143 C — One Primary CTA)
    "gold_accent":    "#F9B000",
    "gold_hover":     "#E09E00",
    "gold_dim":       "#FFF8E8",

    # Status Triples (Background, Border, Text)
    "good_bg":        "#F1F9F5",
    "good_border":    "#C9E5D6",
    "good_ink":       "#1F7A54",
    "warn_bg":        "#FFF8E8",
    "warn_border":    "#F7DFA6",
    "warn_ink":       "#6B4E00",
    "bad_bg":         "#FCF2F0",
    "bad_border":     "#EFCFC8",
    "bad_ink":        "#B3402E",

    # Typography — Costa ink & slate (Contrast 8:1 on gold)
    "fg_primary":     "#0A2A38",   # costa-ink
    "fg_secondary":   "#5F7079",   # costa-slate
    "fg_subtle":      "#94A6AE",   # costa-faint
    "fg_accent":      "#0071A3",
    "fg_gold":        "#F9B000",
}


# ─────────────────────────────────────────────────────────────
# FONT POOL  (Pre-allocated Poppins font cache)
# ─────────────────────────────────────────────────────────────
class Fonts:
    """Pre-allocated Poppins font objects to avoid repeated creation."""
    _cache = {}

    @classmethod
    def get(cls, key):
        if key not in cls._cache:
            cls._cache = {
                # Title & Dot (Dot is 20% larger than text, per costaassets/text guidelines.png)
                "brand_title": ctk.CTkFont(family="Poppins", size=20, weight="bold"),
                "title_dot":   ctk.CTkFont(family="Poppins", size=24, weight="bold"),
                "modal_title": ctk.CTkFont(family="Poppins", size=18, weight="bold"),
                "modal_dot":   ctk.CTkFont(family="Poppins", size=22, weight="bold"),
                "brand_sub":   ctk.CTkFont(family="Poppins", size=9, weight="bold"),
                
                # Headings
                "h1":          ctk.CTkFont(family="Poppins", size=18, weight="bold"),
                "h2":          ctk.CTkFont(family="Poppins", size=14, weight="bold"),
                "h3":          ctk.CTkFont(family="Poppins", size=12, weight="bold"),
                
                # Body Text
                "body":        ctk.CTkFont(family="Poppins", size=12),
                "body_bold":   ctk.CTkFont(family="Poppins", size=12, weight="bold"),
                "small":       ctk.CTkFont(family="Poppins", size=10),
                "small_bold":  ctk.CTkFont(family="Poppins", size=10, weight="bold"),
                "tiny":        ctk.CTkFont(family="Poppins", size=9, weight="bold"),
                
                # Monospace (Numbers, tables, codes)
                "mono":        ctk.CTkFont(family="SF Mono", size=11),
                "mono_sm":     ctk.CTkFont(family="SF Mono", size=10),
                
                # Buttons & Pills
                "btn":         ctk.CTkFont(family="Poppins", size=13, weight="bold"),
                "btn_sm":      ctk.CTkFont(family="Poppins", size=11, weight="bold"),
                "pill":        ctk.CTkFont(family="Poppins", size=11, weight="bold"),
                "stat_val":    ctk.CTkFont(family="Poppins", size=16, weight="bold"),
                "qr_label":    ctk.CTkFont(family="Poppins", size=9, weight="bold"),
            }
        return cls._cache[key]


# ─────────────────────────────────────────────────────────────
# VECTOR ICON ENGINE  (Smooth Lucide Curves, Zero Emojis)
# ─────────────────────────────────────────────────────────────
class VectorIcons:
    """Renders crisp vector line icons via PyMuPDF SVG engine with supersampled antialiasing."""
    _cache = {}

    SVG_ICONS = {
        "search": '<svg viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>',
        "clear": '<svg viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>',
        "zoom": '<svg viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 3 21 3 21 9"/><polyline points="9 21 3 21 3 15"/><polyline points="21 15 21 21 15 21"/><polyline points="3 9 3 3 9 3"/></svg>',
        "enlarge": '<svg viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 3 21 3 21 9"/><polyline points="9 21 3 21 3 15"/><polyline points="21 15 21 21 15 21"/><polyline points="3 9 3 3 9 3"/></svg>',
        "ship": '<svg viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 21c.6.5 1.2 1 2.5 1 2.5 0 2.5-2 5-2 2.5 0 2.5 2 5 2 2.5 0 2.5-2 5-2 1.3 0 1.9.5 2.5 1"/><path d="M19.38 20A11.6 11.6 0 0 0 21 14l-9-4-9 4c0 2.9.94 5.34 2.81 7.76"/><path d="M19 13V7a2 2 0 0 0-2-2H7a2 2 0 0 0-2 2v6"/><line x1="12" y1="2" x2="12" y2="5"/></svg>',
        "calendar": '<svg viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>',
        "map_pin": '<svg viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>',
        "copy": '<svg viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>',
        "check": '<svg viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>',
        "folder": '<svg viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>',
        "refresh": '<svg viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 4 23 10 17 10"/><polyline points="1 20 1 14 7 14"/><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/></svg>',
        "save": '<svg viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/><polyline points="17 21 17 13 7 13 7 21"/><polyline points="7 3 7 8 15 8"/></svg>',
        "export": '<svg viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>',
        "external": '<svg viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>',
        "users": '<svg viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>',
        "utensils": '<svg viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 2v20M2 2v8a4 4 0 0 0 4 4h0a4 4 0 0 0 4-4V2M6 2v20"/></svg>',
        "qr": '<svg viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="3" height="3"/><rect x="18" y="18" width="3" height="3"/></svg>'
    }

    @classmethod
    def get(cls, name, size=16, color=None):
        if color is None:
            color = TK["fg_primary"]
        cache_key = (name, size, color)
        if cache_key in cls._cache:
            return cls._cache[cache_key]

        svg_template = cls.SVG_ICONS.get(name)
        if svg_template and HAS_FITZ:
            try:
                xml = svg_template.replace("{color}", color)
                doc = fitz.open(stream=xml.encode("utf-8"), filetype="svg")
                page = doc[0]
                pix = page.get_pixmap(alpha=True, dpi=72 * 4)
                pil = PILImage.open(io.BytesIO(pix.tobytes("png")))
                pil = pil.resize((size, size), PILImage.Resampling.LANCZOS)
                ctk_img = ctk.CTkImage(light_image=pil, dark_image=pil, size=(size, size))
                cls._cache[cache_key] = ctk_img
                return ctk_img
            except Exception:
                pass

        scale = 4
        dim = size * scale
        im = PILImage.new("RGBA", (dim, dim), (0, 0, 0, 0))
        draw = ImageDraw.Draw(im)
        w = max(1, int(1.8 * scale))

        if name == "search":
            r = dim * 0.30
            cx, cy = dim * 0.40, dim * 0.40
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=color, width=w)
            draw.line([cx + r * 0.7, cy + r * 0.7, dim * 0.88, dim * 0.88], fill=color, width=w)
        elif name == "clear":
            p = int(dim * 0.25)
            draw.line([(p, p), (dim - p, dim - p)], fill=color, width=w)
            draw.line([(dim - p, p), (p, dim - p)], fill=color, width=w)
        elif name in ("zoom", "enlarge"):
            p = int(dim * 0.16)
            k = int(dim * 0.26)
            draw.line([(p, p + k), (p, p), (p + k, p)], fill=color, width=w)
            draw.line([(dim - p - k, p), (dim - p, p), (dim - p, p + k)], fill=color, width=w)
            draw.line([(p, dim - p - k), (p, dim - p), (p + k, dim - p)], fill=color, width=w)
            draw.line([(dim - p - k, dim - p), (dim - p, dim - p), (dim - p, dim - p - k)], fill=color, width=w)
        elif name == "ship":
            draw.polygon([
                (dim * 0.15, dim * 0.75),
                (dim * 0.85, dim * 0.75),
                (dim * 0.75, dim * 0.90),
                (dim * 0.25, dim * 0.90)
            ], outline=color, fill=None)
            draw.rectangle([dim * 0.30, dim * 0.50, dim * 0.70, dim * 0.75], outline=color, width=w)
            draw.rectangle([dim * 0.55, dim * 0.30, dim * 0.65, dim * 0.50], fill=color)
        elif name == "calendar":
            p = int(dim * 0.15)
            draw.rounded_rectangle([p, p + int(dim*0.1), dim - p, dim - p], radius=int(dim*0.08), outline=color, width=w)
            draw.line([(p + int(dim*0.2), p), (p + int(dim*0.2), p + int(dim*0.2))], fill=color, width=w)
            draw.line([(dim - p - int(dim*0.2), p), (dim - p - int(dim*0.2), p + int(dim*0.2))], fill=color, width=w)
            draw.line([(p, p + int(dim*0.35)), (dim - p, p + int(dim*0.35))], fill=color, width=w)
        elif name == "map_pin":
            r = dim * 0.24
            cx, cy = dim * 0.50, dim * 0.38
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=color, width=w)
            draw.polygon([(cx - r*0.8, cy + r*0.5), (cx + r*0.8, cy + r*0.5), (cx, dim * 0.92)], fill=color)
            draw.ellipse([cx - r*0.35, cy - r*0.35, cx + r*0.35, cy + r*0.35], fill="#FFFFFF")
        elif name == "copy":
            p = int(dim * 0.15)
            draw.rectangle([p + int(dim*0.2), p, dim - p, dim - p - int(dim*0.2)], outline=color, width=w)
            draw.rectangle([p, p + int(dim*0.2), dim - p - int(dim*0.2), dim - p], outline=color, width=w)
        elif name == "check":
            draw.line([(dim * 0.2, dim * 0.55), (dim * 0.42, dim * 0.78), (dim * 0.85, dim * 0.25)], fill=color, width=int(w*1.2))
        elif name == "folder":
            p = int(dim * 0.15)
            draw.line([
                (p, p + int(dim*0.2)),
                (p + int(dim*0.3), p + int(dim*0.2)),
                (p + int(dim*0.45), p + int(dim*0.35)),
                (dim - p, p + int(dim*0.35)),
                (dim - p, dim - p),
                (p, dim - p),
                (p, p + int(dim*0.2))
            ], fill=color, width=w)
        elif name == "refresh":
            cx, cy, r = dim * 0.5, dim * 0.5, dim * 0.32
            draw.arc([cx - r, cy - r, cx + r, cy + r], start=30, end=300, fill=color, width=w)
            draw.polygon([
                (cx + r * 0.85, cy - r * 0.3),
                (cx + r * 1.15, cy + r * 0.1),
                (cx + r * 0.55, cy + r * 0.1)
            ], fill=color)
        elif name == "save":
            p = int(dim * 0.15)
            draw.rectangle([p, p, dim - p, dim - p], outline=color, width=w)
            draw.rectangle([p + int(dim*0.2), p, dim - p - int(dim*0.2), p + int(dim*0.3)], fill=color)
            draw.rectangle([p + int(dim*0.15), p + int(dim*0.45), dim - p - int(dim*0.15), dim - p], outline=color, width=w)
        elif name == "export":
            p = int(dim * 0.15)
            draw.line([(p, dim * 0.65), (p, dim - p), (dim - p, dim - p), (dim - p, dim * 0.65)], fill=color, width=w)
            draw.line([(dim * 0.5, p), (dim * 0.5, dim * 0.68)], fill=color, width=w)
            draw.line([(dim * 0.32, dim * 0.48), (dim * 0.5, dim * 0.68), (dim * 0.68, dim * 0.48)], fill=color, width=w)
        elif name == "external":
            p = int(dim * 0.18)
            draw.line([(p, dim * 0.45), (p, dim - p), (dim - p, dim - p), (dim - p, dim * 0.45)], fill=color, width=w)
            draw.line([(dim * 0.45, dim * 0.55), (dim - p, p)], fill=color, width=w)
            draw.line([(dim * 0.65, p), (dim - p, p), (dim - p, dim * 0.35)], fill=color, width=w)
        elif name == "clock":
            cx, cy, r = dim * 0.5, dim * 0.5, dim * 0.35
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=color, width=w)
            draw.line([(cx, cy), (cx, cy - r * 0.6)], fill=color, width=w)
            draw.line([(cx, cy), (cx + r * 0.5, cy)], fill=color, width=w)
        elif name == "users":
            r = dim * 0.16
            draw.ellipse([dim * 0.40 - r, dim * 0.32 - r, dim * 0.40 + r, dim * 0.32 + r], outline=color, width=w)
            draw.ellipse([dim * 0.68 - r, dim * 0.36 - r, dim * 0.68 + r, dim * 0.36 + r], outline=color, width=w)
            draw.arc([dim * 0.18, dim * 0.52, dim * 0.62, dim * 0.90], start=180, end=0, fill=color, width=w)
            draw.arc([dim * 0.48, dim * 0.56, dim * 0.88, dim * 0.90], start=180, end=0, fill=color, width=w)
        elif name == "user":
            r = dim * 0.22
            cx, cy = dim * 0.5, dim * 0.32
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=color, width=w)
            draw.arc([dim * 0.20, dim * 0.54, dim * 0.80, dim * 0.96], start=180, end=0, fill=color, width=w)
        elif name == "utensils":
            draw.line([(dim * 0.35, dim * 0.15), (dim * 0.35, dim * 0.85)], fill=color, width=w)
            draw.line([(dim * 0.25, dim * 0.15), (dim * 0.25, dim * 0.45)], fill=color, width=w)
            draw.line([(dim * 0.45, dim * 0.15), (dim * 0.45, dim * 0.45)], fill=color, width=w)
            draw.line([(dim * 0.25, dim * 0.45), (dim * 0.45, dim * 0.45)], fill=color, width=w)
            draw.line([(dim * 0.65, dim * 0.15), (dim * 0.65, dim * 0.85)], fill=color, width=w)
            draw.arc([dim * 0.55, dim * 0.15, dim * 0.75, dim * 0.50], start=270, end=90, fill=color, width=w)
        elif name == "qr":
            s = int(dim * 0.3)
            p = int(dim * 0.1)
            draw.rectangle([p, p, p + s, p + s], outline=color, width=w)
            draw.rectangle([p + int(s*0.3), p + int(s*0.3), p + int(s*0.7), p + int(s*0.7)], fill=color)
            draw.rectangle([dim - p - s, p, dim - p, p + s], outline=color, width=w)
            draw.rectangle([dim - p - int(s*0.7), p + int(s*0.3), dim - p - int(s*0.3), p + int(s*0.7)], fill=color)
            draw.rectangle([p, dim - p - s, p + s, dim - p], outline=color, width=w)
            draw.rectangle([p + int(s*0.3), dim - p - int(s*0.7), p + int(s*0.7), dim - p - int(s*0.3)], fill=color)
        else:
            p = int(dim * 0.2)
            draw.ellipse([p, p, dim - p, dim - p], outline=color, width=w)

        # Keep supersampled 4x image for razor-sharp Retina/High-DPI rendering
        ctk_img = ctk.CTkImage(light_image=im, dark_image=im, size=(size, size))
        cls._cache[cache_key] = ctk_img
        return ctk_img


# ─────────────────────────────────────────────────────────────
# OUTLINE PILL SWITCHER COMPONENT  (Matches CostaSchedule.html)
# ─────────────────────────────────────────────────────────────
class OutlinePillGroup(ctk.CTkFrame):
    """Segmented pill switchers strictly matching CostaSchedule.html .outline-pill-group & .outline-pill-btn."""

    def __init__(self, parent, values, initial_value=None, command=None, height=32, corner_radius=16):
        super().__init__(parent, fg_color="transparent")
        self.values = values
        self.command = command
        self.current_value = initial_value or (values[0] if values else "")
        self.buttons = {}

        for val in values:
            btn = ctk.CTkButton(
                self,
                text=val,
                font=Fonts.get("pill"),
                height=height,
                corner_radius=corner_radius,
                border_width=1,
                command=lambda v=val: self.set(v, trigger_command=True)
            )
            btn.pack(side="left", padx=3)
            self.buttons[val] = btn

        self._update_styles()

    def set(self, value, trigger_command=False):
        if value in self.values and value != self.current_value:
            self.current_value = value
            self._update_styles()
            if trigger_command and self.command:
                self.command(value)
        elif value in self.values:
            self.current_value = value
            self._update_styles()

    def get(self):
        return self.current_value

    def _update_styles(self):
        for val, btn in self.buttons.items():
            if val == self.current_value:
                # Active pill: Solid Costa Ink background, white text, 1px border
                btn.configure(
                    fg_color=TK["fg_primary"],
                    hover_color=TK["fg_primary"],
                    border_color=TK["fg_primary"],
                    text_color="#FFFFFF"
                )
            else:
                # Inactive pill: Clean white background, subtle border, Costa Ink text
                btn.configure(
                    fg_color=TK["bg_base"],
                    hover_color=TK["surface_hover"],
                    border_color=TK["border_card"],
                    text_color=TK["fg_primary"]
                )


# ─────────────────────────────────────────────────────────────
# AIRGAP QR MODAL (Full-Screen High Contrast Zoom)
# ─────────────────────────────────────────────────────────────
class QRModal(ctk.CTkToplevel):
    """High-resolution modal dialog for Airgap QR scanning (pure black, integer scaled)."""

    def __init__(self, parent, segments, meta_info=None, initial_idx=0):
        super().__init__(parent)
        self.withdraw()  # Hide window immediately off-screen to avoid bottom-right flash

        self.title("Costa Cruises — Airgap QR Codes")
        self.resizable(False, False)
        self.configure(fg_color=TK["bg_base"])

        self.segments = segments or []
        self.meta_info = meta_info or {}
        self.current_idx = max(0, min(initial_idx, len(self.segments) - 1)) if self.segments else 0
        self._qr_ref = None

        self.transient(parent)

        # Pre-compute exact center position relative to parent window
        w, h = 640, 740
        try:
            parent.update_idletasks()
            px = parent.winfo_rootx()
            py = parent.winfo_rooty()
            pw = parent.winfo_width()
            ph = parent.winfo_height()
            x = max(0, px + (pw - w) // 2)
            y = max(0, py + (ph - h) // 2)
            self.geometry(f"{w}x{h}+{x}+{y}")
        except Exception:
            self.geometry(f"{w}x{h}")

        self._build_ui()
        self._bind_keys()
        self._show_segment(self.current_idx)

        # Ensure all widgets inside modal are drawn before showing
        self.update_idletasks()

        # Reveal smoothly at center, grab focus, and elevate
        self.deiconify()
        self.grab_set()
        self.lift()
        self.focus_force()
        self.after(60, self._ensure_focus)

    def _ensure_focus(self):
        try:
            self.lift()
            self.focus_force()
        except Exception:
            pass

    def _build_ui(self):
        # Top Blue Accent Line (3px)
        ctk.CTkFrame(self, height=3, fg_color=TK["accent"], corner_radius=0).pack(fill="x")

        # Header Frame
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", padx=24, pady=(16, 8))

        title_frame = ctk.CTkFrame(hdr, fg_color="transparent")
        title_frame.pack(side="left")

        # Brand title with orange dot (. in #F9B000, +20% size)
        brand_row = ctk.CTkFrame(title_frame, fg_color="transparent")
        brand_row.pack(anchor="w")
        ctk.CTkLabel(
            brand_row, text="AIRGAP QR TRANSFER",
            font=Fonts.get("modal_title"), text_color=TK["fg_primary"]
        ).pack(side="left")
        ctk.CTkLabel(
            brand_row, text=".",
            font=Fonts.get("modal_dot"), text_color=TK["gold_accent"]
        ).pack(side="left")

        self.lbl_subtitle = ctk.CTkLabel(
            title_frame, text="Zero network or cables required — Strict ship IT compliant",
            font=Fonts.get("small_bold"), text_color=TK["fg_subtle"], anchor="w"
        )
        self.lbl_subtitle.pack(anchor="w")

        # Close button top right
        ctk.CTkButton(
            hdr, text="Close (Esc)", font=Fonts.get("btn_sm"),
            fg_color=TK["bg_base"], hover_color=TK["surface_hover"],
            border_width=1, border_color=TK["border_card"],
            text_color=TK["fg_secondary"], width=90, height=32, corner_radius=16,
            command=self.destroy
        ).pack(side="right")

        # Hairline
        ctk.CTkFrame(self, height=1, fg_color=TK["border_card"], corner_radius=0).pack(fill="x", padx=24)

        # Main QR Container Box (500x500)
        self.qr_box = ctk.CTkFrame(
            self, width=500, height=500,
            fg_color="#FFFFFF", corner_radius=8,
            border_width=1, border_color=TK["border_card"]
        )
        self.qr_box.pack(pady=12)
        self.qr_box.pack_propagate(False)

        self.qr_image_label = ctk.CTkLabel(self.qr_box, text="")
        self.qr_image_label.pack(expand=True)

        # Instructions Banner
        self.lbl_step = ctk.CTkLabel(
            self, text="Point phone camera at QR, tap 'Copy text', then paste into WhatsApp.",
            font=Fonts.get("h3"), text_color=TK["fg_primary"]
        )
        self.lbl_step.pack(pady=(0, 10))

        # Navigation Bar
        nav = ctk.CTkFrame(self, fg_color="transparent")
        nav.pack(fill="x", padx=24, pady=(0, 14))

        self.btn_prev = ctk.CTkButton(
            nav, text="◀ PREVIOUS PART",
            font=Fonts.get("btn_sm"),
            fg_color=TK["bg_base"], hover_color=TK["surface_hover"],
            border_width=1, border_color=TK["border_card"],
            text_color=TK["fg_primary"], height=38, corner_radius=16,
            command=self._on_prev
        )
        self.btn_prev.pack(side="left", fill="x", expand=True, padx=(0, 8))

        self.lbl_indicator = ctk.CTkLabel(
            nav, text="Part 1 of 2", font=Fonts.get("brand_title"),
            text_color=TK["fg_primary"], width=110
        )
        self.lbl_indicator.pack(side="left", padx=6)

        self.btn_next = ctk.CTkButton(
            nav, text="NEXT PART (Space) ▶",
            font=Fonts.get("btn_sm"),
            fg_color=TK["gold_accent"], hover_color=TK["gold_hover"],
            text_color=TK["fg_primary"], height=38, corner_radius=16,
            command=self._on_next
        )
        self.btn_next.pack(side="left", fill="x", expand=True, padx=(8, 0))

    def _bind_keys(self):
        self.bind("<KeyPress>", self._on_key_press)
        # Re-claim focus if user clicks anywhere in the modal dialog
        self.bind("<Button-1>", lambda e: self.focus_set())
        if hasattr(self, "qr_box"):
            self.qr_box.bind("<Button-1>", lambda e: self.focus_set())
        if hasattr(self, "qr_image_label"):
            self.qr_image_label.bind("<Button-1>", lambda e: self.focus_set())

    def _on_key_press(self, event):
        keysym = (event.keysym or "").lower()
        if keysym in ("escape", "esc"):
            self.destroy()
            return "break"
        elif keysym in ("space", "return"):
            self._on_next()
            return "break"
        elif keysym in ("left", "up"):
            self._on_prev()
            return "break"
        elif keysym in ("right", "down"):
            self._on_next()
            return "break"

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

        qr = qrcode.QRCode(
            version=None,
            error_correction=ERROR_CORRECT_L,
            box_size=5,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        pil = qr.make_image(fill_color="#000000", back_color="#FFFFFF").convert("RGB")
        pil = pil.resize((920, 920), PILImage.NEAREST)

        ctk_img = ctk.CTkImage(light_image=pil, dark_image=pil, size=(460, 460))
        self.qr_image_label.configure(image=ctk_img, text="")
        self._qr_ref = ctk_img

        self.lbl_indicator.configure(text=f"Part {idx + 1} of {total}")
        self.lbl_step.configure(
            text=f"Part {idx + 1} of {total}: Point camera at QR, tap 'Copy text', then paste into WhatsApp."
        )

        self.btn_prev.configure(state="normal" if idx > 0 else "disabled")
        if idx == total - 1:
            self.btn_next.configure(text="DONE (Close)", fg_color=TK["accent"], text_color="#FFFFFF")
        else:
            self.btn_next.configure(text="NEXT PART (Space) ▶", fg_color=TK["gold_accent"], text_color=TK["fg_primary"])


# ─────────────────────────────────────────────────────────────
# DND SUPPORT
# ─────────────────────────────────────────────────────────────
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    HAS_DND = True
except ImportError:
    HAS_DND = False


# ─────────────────────────────────────────────────────────────
# MAIN DESKTOP APPLICATION CLASS
# ─────────────────────────────────────────────────────────────
class CostaDesktopApp(ctk.CTk, TkinterDnD.DnDWrapper if HAS_DND else object):
    """Costa Schedule Exporter — Newspaper Elegance Edition."""

    def __init__(self):
        super().__init__()

        if HAS_DND:
            try:
                self.TkdndVersion = TkinterDnD._require(self)
                self.drop_target_register(DND_FILES)
                self.dnd_bind("<<Drop>>", self._on_file_drop)
            except Exception as e:
                print(f"[Warning] TkinterDnD init error: {e}")

        # Window Setup
        self.title("Costa Cruises — Schedule Exporter")
        self.geometry("1120x820")
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
        self._cached_crew_count = 0
        self._cached_section_count = 0
        self._qr_a_ref = None
        self._qr_b_ref = None

        # Logo
        self.logo_image = self._load_logo_image()

        # Build UI Sections
        self._build_top_bar()
        self._build_control_strip()
        self._build_content_area()
        self._build_bottom_bar()

        # Auto-parse default sample on startup
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
                return ctk.CTkImage(light_image=pil, dark_image=pil, size=(34, 40))
            except Exception:
                pass
        return None

    # ─────────────────────────────────────────────────────────
    # TOP BAR (Newspaper Masthead with Orange Dot Title & Telemetry)
    # ─────────────────────────────────────────────────────────
    def _build_top_bar(self):
        bar = ctk.CTkFrame(
            self, height=60, corner_radius=0,
            fg_color=TK["bg_base"],
            border_width=0
        )
        bar.pack(fill="x")
        bar.pack_propagate(False)

        # 3px Costa Blue Accent Line at Top
        accent_line = ctk.CTkFrame(bar, height=3, fg_color=TK["accent"], corner_radius=0)
        accent_line.pack(fill="x", side="top")

        inner = ctk.CTkFrame(bar, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=20)

        # Left: Official Costa Logo + Masthead Title
        brand = ctk.CTkFrame(inner, fg_color="transparent")
        brand.pack(side="left", fill="y")

        if self.logo_image:
            ctk.CTkLabel(brand, image=self.logo_image, text="").pack(side="left", padx=(0, 10))

        title_box = ctk.CTkFrame(brand, fg_color="transparent")
        title_box.pack(side="left", fill="y", pady=6)

        # "COSTA SMERALDA." with +20% Yellow Dot aligned to text baseline
        title_frame = ctk.CTkFrame(title_box, fg_color="transparent")
        title_frame.pack(anchor="w")
        
        self.lbl_brand_title = ctk.CTkLabel(
            title_frame, text="COSTA SMERALDA",
            font=Fonts.get("brand_title"), text_color=TK["fg_primary"]
        )
        self.lbl_brand_title.pack(side="left")
        
        # Perfect circular yellow dot resting strictly on text baseline (per costaassets/text guidelines.png)
        dot_cv = tk.Canvas(title_frame, width=8, height=28, bg=TK["bg_base"], highlightthickness=0)
        dot_cv.pack(side="left", padx=(1, 0))
        dot_cv.create_oval(0, 15, 7, 22, fill=TK["gold_accent"], outline="")

        ctk.CTkLabel(
            title_box, text="RESTAURANT SCHEDULE EXPORTER",
            font=Fonts.get("brand_sub"), text_color=TK["fg_secondary"], anchor="w"
        ).pack(anchor="w")

        # Right: Telemetry Badges with Clean Vector Icons
        badge_box = ctk.CTkFrame(inner, fg_color="transparent")
        badge_box.pack(side="right", fill="y")

        self.badge_date = self._make_telemetry_badge(
            badge_box, "calendar", "August 23, 2026",
            text_color=TK["fg_secondary"],
            bg_color=TK["surface_inner"],
            border_color=TK["border_card"]
        )
        self.badge_port = self._make_telemetry_badge(
            badge_box, "map_pin", "KAOHSIUNG",
            text_color=TK["fg_accent"],
            bg_color=TK["accent_dim"],
            border_color=TK["accent_border"]
        )

        # Hairline Bottom Border
        ctk.CTkFrame(self, height=1, fg_color=TK["border_inner"], corner_radius=0).pack(fill="x")

    def _make_telemetry_badge(self, parent, icon_name, text, text_color, bg_color=None, border_color=None):
        pill = ctk.CTkFrame(
            parent,
            height=32,
            corner_radius=16,
            fg_color=bg_color or TK["surface_inner"],
            border_width=1,
            border_color=border_color or TK["border_card"]
        )
        pill.pack(side="left", padx=4, pady=12)

        icon_img = VectorIcons.get(icon_name, size=14, color=text_color)
        lbl = ctk.CTkLabel(
            pill,
            image=icon_img,
            text=f"  {text}",
            compound="left",
            font=Fonts.get("small_bold"),
            text_color=text_color,
            height=30
        )
        lbl.pack(padx=12, pady=1)

        # Ensure future .configure(text=...) calls preserve leading space
        orig_configure = lbl.configure
        def _safe_configure(**kwargs):
            if "text" in kwargs:
                t = str(kwargs["text"])
                if not t.startswith("  "):
                    kwargs["text"] = f"  {t}"
            return orig_configure(**kwargs)
        lbl.configure = _safe_configure

        return lbl

    # ─────────────────────────────────────────────────────────
    # CONTROL STRIP  (Source File + Meal Shift + Search + Filter Pills)
    # ─────────────────────────────────────────────────────────
    def _build_control_strip(self):
        strip = ctk.CTkFrame(self, fg_color=TK["surface_inner"], corner_radius=0)
        strip.pack(fill="x")

        inner = ctk.CTkFrame(strip, fg_color="transparent")
        inner.pack(fill="x", padx=20, pady=10)

        # Row 1: Source File + Meal Shift Switcher
        r1 = ctk.CTkFrame(inner, fg_color="transparent")
        r1.pack(fill="x", pady=(0, 8))

        # File box
        file_box = ctk.CTkFrame(r1, fg_color="transparent")
        file_box.pack(side="left", fill="x", expand=True, padx=(0, 14))

        ctk.CTkLabel(
            file_box, text="SOURCE ROSTER (.XLSX)",
            font=Fonts.get("tiny"), text_color=TK["fg_subtle"]
        ).pack(anchor="w")

        file_pill = ctk.CTkFrame(
            file_box, fg_color=TK["bg_base"], corner_radius=16,
            border_width=1, border_color=TK["border_card"], height=36
        )
        file_pill.pack(fill="x", pady=(3, 0))
        file_pill.pack_propagate(False)

        # File vector icon
        ctk.CTkLabel(
            file_pill, text="",
            image=VectorIcons.get("folder", size=16, color=TK["fg_secondary"]),
            width=16
        ).pack(side="left", padx=(12, 6), pady=3)

        self.lbl_file = ctk.CTkLabel(
            file_pill, text=self._file_display_text(),
            font=Fonts.get("body"), text_color=TK["fg_secondary"], anchor="w"
        )
        self.lbl_file.pack(side="left", fill="x", expand=True, pady=3)

        # Browse Button (Outline Pill)
        btn_browse = ctk.CTkButton(
            file_pill, text=" Browse", compound="left",
            image=VectorIcons.get("folder", size=14, color=TK["fg_primary"]),
            font=Fonts.get("btn_sm"),
            fg_color=TK["surface_hover"], hover_color=TK["surface_active"],
            border_width=1, border_color=TK["border_card"],
            text_color=TK["fg_primary"], width=90, height=26, corner_radius=13,
            command=self.browse_file
        )
        btn_browse.pack(side="right", padx=5, pady=4)

        # Reload Button (Outline Pill)
        btn_reload = ctk.CTkButton(
            file_pill, text=" Reload", compound="left",
            image=VectorIcons.get("refresh", size=14, color=TK["fg_secondary"]),
            font=Fonts.get("btn_sm"),
            fg_color=TK["surface_hover"], hover_color=TK["surface_active"],
            border_width=1, border_color=TK["border_card"],
            text_color=TK["fg_secondary"], width=80, height=26, corner_radius=13,
            command=self.process_schedule
        )
        btn_reload.pack(side="right", padx=(0, 3), pady=4)

        # Meal Shift Selector (HTML/APK Outline Pill Style)
        shift_box = ctk.CTkFrame(r1, fg_color="transparent")
        shift_box.pack(side="right")

        ctk.CTkLabel(
            shift_box, text="MEAL SHIFT",
            font=Fonts.get("tiny"), text_color=TK["fg_subtle"]
        ).pack(anchor="w")

        self.shift_pills = OutlinePillGroup(
            shift_box,
            values=["Breakfast", "Lunch", "Dinner"],
            initial_value="Lunch",
            command=self._on_shift_pill_selected,
            height=34,
            corner_radius=17
        )
        self.shift_pills.pack(pady=(3, 0))

        # Row 2: Search Entry + Filter Pills
        r2 = ctk.CTkFrame(inner, fg_color="transparent")
        r2.pack(fill="x")

        # Search Bar
        search_wrap = ctk.CTkFrame(
            r2, fg_color=TK["bg_base"], corner_radius=16,
            border_width=1, border_color=TK["border_card"], height=34
        )
        search_wrap.pack(side="left", fill="x", expand=True, padx=(0, 12))
        search_wrap.pack_propagate(False)

        ctk.CTkLabel(
            search_wrap, text="",
            image=VectorIcons.get("search", size=16, color=TK["fg_subtle"]),
            width=16
        ).pack(side="left", padx=(12, 6), pady=3)

        self.search_entry = ctk.CTkEntry(
            search_wrap,
            placeholder_text="Search crew name, station, table, duty...",
            placeholder_text_color=TK["fg_subtle"],
            fg_color="transparent", border_width=0,
            font=Fonts.get("body"), text_color=TK["fg_primary"], height=24
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=4, pady=3)
        self.search_entry.bind("<KeyRelease>", self._on_search_key)

        btn_clear = ctk.CTkButton(
            search_wrap, text="", width=22, height=22, corner_radius=11,
            image=VectorIcons.get("clear", size=12, color=TK["fg_subtle"]),
            fg_color="transparent", hover_color=TK["surface_hover"],
            command=self._clear_search
        )
        btn_clear.pack(side="right", padx=6, pady=4)

        # Filter Pills (HTML/APK Outline Pill Style)
        self.filter_pills = OutlinePillGroup(
            r2,
            values=["All", "Main Dining", "Buffet & Outlets", "Side Duties"],
            initial_value="All",
            command=self._on_filter_pill_changed,
            height=32,
            corner_radius=16
        )
        self.filter_pills.pack(side="right")

        # Hairline Bottom Divider
        ctk.CTkFrame(self, height=1, fg_color=TK["border_inner"], corner_radius=0).pack(fill="x")

    def _file_display_text(self):
        if not self.current_file:
            return "No file loaded — Click Browse to select roster (.xlsx)"
        return os.path.basename(self.current_file)

    def _on_shift_pill_selected(self, value):
        self.meal_shift = value.upper()
        if self.current_file:
            self.process_schedule()

    def _on_filter_pill_changed(self, value):
        self.active_filter = value.upper()
        self._render_cards()

    # ─────────────────────────────────────────────────────────
    # CONTENT SCROLL AREA (Stats + Airgap QR Section + Roster Cards)
    # ─────────────────────────────────────────────────────────
    def _build_content_area(self):
        self.content_scroll = ctk.CTkScrollableFrame(
            self, fg_color=TK["bg_base"], corner_radius=0
        )
        self.content_scroll.pack(fill="both", expand=True, padx=0, pady=0)

        # Inner container with standard width
        self.content_inner = ctk.CTkFrame(self.content_scroll, fg_color="transparent")
        self.content_inner.pack(fill="x", expand=True, padx=24, pady=16)

        # ── 1. Telemetry Stats Row ──
        self.stats_frame = ctk.CTkFrame(self.content_inner, fg_color="transparent")
        self.stats_frame.pack(fill="x", pady=(0, 16))
        self.stats_frame.columnconfigure((0, 1, 2, 3), weight=1, uniform="stat")

        self.stat_port = self._make_stat_card(self.stats_frame, 0, "map_pin", "PORT & MEAL", "—", "—")
        self.stat_crew = self._make_stat_card(self.stats_frame, 1, "users", "ACTIVE ROSTER", "0 Crew", "0 Sections")
        self.stat_stations = self._make_stat_card(self.stats_frame, 2, "utensils", "DINING STATIONS", "0 Tables", "0 Venues")
        self.stat_payload = self._make_stat_card(self.stats_frame, 3, "qr", "ENCODED STREAM", "0 Chars", "0 Bytes")

        # ── 2. Airgap QR Section (Dual-Mode & Perfectly Sized Side-by-Side QRs) ──
        self.qr_section = ctk.CTkFrame(
            self.content_inner, fg_color=TK["bg_base"],
            corner_radius=12, border_width=1, border_color=TK["border_card"]
        )
        self.qr_section.pack(fill="x", pady=(0, 16))

        qr_inner = ctk.CTkFrame(self.qr_section, fg_color="transparent")
        qr_inner.pack(fill="x", padx=20, pady=16)

        # ── Left Column: Instructions & Actions ──
        qr_info = ctk.CTkFrame(qr_inner, fg_color="transparent")
        qr_info.pack(side="left", fill="both", expand=True, padx=(0, 16))

        # Category Tag with Dot
        tag_row = ctk.CTkFrame(qr_info, fg_color="transparent")
        tag_row.pack(anchor="w")
        dot = ctk.CTkFrame(tag_row, width=6, height=6, corner_radius=3, fg_color=TK["accent"])
        dot.pack(side="left", padx=(0, 6))
        ctk.CTkLabel(
            tag_row, text="OFFLINE AIRGAP SYSTEM • SHIP IT COMPLIANT",
            font=Fonts.get("tiny"), text_color=TK["fg_subtle"]
        ).pack(side="left")

        ctk.CTkLabel(
            qr_info, text="Send Schedule via WhatsApp (2 Scans)",
            font=Fonts.get("h2"), text_color=TK["fg_primary"], anchor="w"
        ).pack(anchor="w", pady=(4, 4))

        self.airgap_status_label = ctk.CTkLabel(
            qr_info,
            text="1. Point phone camera at QR preview or click 'ENLARGE QR CODE'.\n"
                 "2. Tap 'Copy text' on phone, then paste into WhatsApp.\n"
                 "3. Repeat for Part 2 to transfer complete encrypted roster.",
            font=Fonts.get("body"), text_color=TK["fg_secondary"],
            anchor="w", justify="left"
        )
        self.airgap_status_label.pack(anchor="w", pady=(0, 12))

        airgap_btns = ctk.CTkFrame(qr_info, fg_color="transparent")
        airgap_btns.pack(anchor="w")

        # One Primary Yellow Action Button
        self.btn_enlarge_qr = ctk.CTkButton(
            airgap_btns, text=" ENLARGE QR CODE (FULL SCREEN)", compound="left",
            image=VectorIcons.get("zoom", size=16, color=TK["fg_primary"]),
            font=Fonts.get("btn"),
            fg_color=TK["gold_accent"], hover_color=TK["gold_hover"],
            text_color=TK["fg_primary"], height=38, corner_radius=19,
            command=lambda: self.open_qr_modal(0)
        )
        self.btn_enlarge_qr.pack(side="left", padx=(0, 8))

        # Secondary Outline Action Buttons
        self.btn_quick_save = ctk.CTkButton(
            airgap_btns, text=" Quick Save", compound="left",
            image=VectorIcons.get("save", size=15, color=TK["fg_secondary"]),
            font=Fonts.get("btn_sm"),
            fg_color=TK["bg_base"], hover_color=TK["surface_hover"],
            border_width=1, border_color=TK["border_card"],
            text_color=TK["fg_secondary"], height=38, corner_radius=19,
            command=self.save_json_backup_action
        )
        self.btn_quick_save.pack(side="left", padx=(0, 6))

        self.btn_save_as = ctk.CTkButton(
            airgap_btns, text=" Save As", compound="left",
            image=VectorIcons.get("export", size=15, color=TK["fg_secondary"]),
            font=Fonts.get("btn_sm"),
            fg_color=TK["bg_base"], hover_color=TK["surface_hover"],
            border_width=1, border_color=TK["border_card"],
            text_color=TK["fg_secondary"], height=38, corner_radius=19,
            command=self.export_json_action
        )
        self.btn_save_as.pack(side="left")

        # ── Right Column: Dual QR Code Preview Cards (Fixed Width ~290px, No Cutoff!) ──
        self.qr_preview_container = ctk.CTkFrame(qr_inner, fg_color="transparent")
        self.qr_preview_container.pack(side="right", padx=(10, 0))

        # QR Part 1 Card
        self.qr_a_sub = ctk.CTkFrame(
            self.qr_preview_container, fg_color=TK["surface_inner"],
            corner_radius=10, border_width=1, border_color=TK["border_inner"],
            width=134, height=182, cursor="pointinghand"
        )
        self.qr_a_sub.pack(side="left", padx=(0, 10))
        self.qr_a_sub.pack_propagate(False)

        ctk.CTkLabel(
            self.qr_a_sub, text="PART 1 OF 2",
            font=Fonts.get("small_bold"), text_color=TK["accent"]
        ).pack(pady=(8, 4))

        self.qr_a_box = ctk.CTkFrame(
            self.qr_a_sub, width=116, height=116,
            fg_color="#FFFFFF", corner_radius=6,
            border_width=1, border_color=TK["border_card"]
        )
        self.qr_a_box.pack(pady=0)
        self.qr_a_box.pack_propagate(False)

        self.qr_a_label = ctk.CTkLabel(
            self.qr_a_box, text="Part 1\n(Click to zoom)",
            font=Fonts.get("small"), text_color=TK["fg_subtle"]
        )
        self.qr_a_label.pack(expand=True)

        self.lbl_zoom_a = ctk.CTkLabel(
            self.qr_a_sub, text=" Click to enlarge",
            image=VectorIcons.get("zoom", size=11, color=TK["fg_secondary"]),
            compound="left",
            font=Fonts.get("qr_label"), text_color=TK["fg_secondary"]
        )
        self.lbl_zoom_a.pack(pady=(4, 6))

        for w in (self.qr_a_sub, self.qr_a_box, self.qr_a_label, self.lbl_zoom_a):
            w.bind("<Button-1>", lambda e: self.open_qr_modal(0))

        # QR Part 2 Card
        self.qr_b_sub = ctk.CTkFrame(
            self.qr_preview_container, fg_color=TK["surface_inner"],
            corner_radius=10, border_width=1, border_color=TK["border_inner"],
            width=134, height=182, cursor="pointinghand"
        )
        self.qr_b_sub.pack(side="left")
        self.qr_b_sub.pack_propagate(False)

        ctk.CTkLabel(
            self.qr_b_sub, text="PART 2 OF 2",
            font=Fonts.get("small_bold"), text_color=TK["accent"]
        ).pack(pady=(8, 4))

        self.qr_b_box = ctk.CTkFrame(
            self.qr_b_sub, width=116, height=116,
            fg_color="#FFFFFF", corner_radius=6,
            border_width=1, border_color=TK["border_card"]
        )
        self.qr_b_box.pack(pady=0)
        self.qr_b_box.pack_propagate(False)

        self.qr_b_label = ctk.CTkLabel(
            self.qr_b_box, text="Part 2\n(Click to zoom)",
            font=Fonts.get("small"), text_color=TK["fg_subtle"]
        )
        self.qr_b_label.pack(expand=True)

        self.lbl_zoom_b = ctk.CTkLabel(
            self.qr_b_sub, text=" Click to enlarge",
            image=VectorIcons.get("zoom", size=11, color=TK["fg_secondary"]),
            compound="left",
            font=Fonts.get("qr_label"), text_color=TK["fg_secondary"]
        )
        self.lbl_zoom_b.pack(pady=(4, 6))

        for w in (self.qr_b_sub, self.qr_b_box, self.qr_b_label, self.lbl_zoom_b):
            w.bind("<Button-1>", lambda e: self.open_qr_modal(1))

        # ── 3. Cards container ──
        self.cards_frame = ctk.CTkFrame(self.content_inner, fg_color="transparent")
        self.cards_frame.pack(fill="x", pady=(0, 8))

        self.empty_label = ctk.CTkLabel(
            self.cards_frame,
            text="No schedule loaded. Click Browse to select an Excel roster file.",
            font=Fonts.get("body"), text_color=TK["fg_secondary"], pady=40
        )
        self.empty_label.pack(expand=True)

    def _make_stat_card(self, parent, col, icon_name, tag, title, subtitle):
        card = ctk.CTkFrame(
            parent, fg_color=TK["surface_card"], corner_radius=10,
            border_width=1, border_color=TK["border_card"]
        )
        card.grid(row=0, column=col, padx=4, pady=2, sticky="nsew")

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=14, pady=12)

        # Tag with vector icon
        ctk.CTkLabel(
            inner, text=f"  {tag}",
            image=VectorIcons.get(icon_name, size=15, color=TK["accent"]),
            compound="left",
            font=Fonts.get("tiny"), text_color=TK["fg_subtle"], anchor="w"
        ).pack(fill="x")

        title_lbl = ctk.CTkLabel(
            inner, text=title, font=Fonts.get("stat_val"),
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
    # BOTTOM BAR  (Primary yellow action + Open WebApp + Status)
    # ─────────────────────────────────────────────────────────
    def _build_bottom_bar(self):
        # Top hairline
        ctk.CTkFrame(self, height=1, fg_color=TK["border_card"], corner_radius=0).pack(fill="x")

        bar = ctk.CTkFrame(self, height=58, fg_color=TK["bg_base"], corner_radius=0)
        bar.pack(fill="x")
        bar.pack_propagate(False)

        inner = ctk.CTkFrame(bar, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=20)

        # Primary Action CTA — Costa Yellow (One Yellow Button Rule)
        self.btn_primary = ctk.CTkButton(
            inner, text=" COPY SCHEDULE TO CLIPBOARD", compound="left",
            image=VectorIcons.get("copy", size=16, color=TK["fg_primary"]),
            font=Fonts.get("btn"),
            fg_color=TK["gold_accent"], hover_color=TK["gold_hover"],
            text_color=TK["fg_primary"],  # Dark text on yellow (8:1 contrast)
            height=42, corner_radius=21,
            command=self._primary_action
        )
        self.btn_primary.pack(side="left", fill="x", expand=True, padx=(0, 12))

        # Secondary Outline: Open WebApp
        self.btn_open_web = ctk.CTkButton(
            inner, text=" Open WebApp", compound="left",
            image=VectorIcons.get("external", size=15, color=TK["fg_secondary"]),
            font=Fonts.get("btn_sm"),
            fg_color=TK["bg_base"], hover_color=TK["surface_hover"],
            border_width=1, border_color=TK["border_card"],
            text_color=TK["fg_secondary"], height=42, corner_radius=21,
            command=self.open_webapp
        )
        self.btn_open_web.pack(side="right")

        # Live Status Label
        self.lbl_status = ctk.CTkLabel(
            inner, text="Ready",
            font=Fonts.get("small_bold"), text_color=TK["good_ink"]
        )
        self.lbl_status.pack(side="right", padx=16)

    # ─────────────────────────────────────────────────────────
    # QR CODE GENERATION & MODAL ACTIONS
    # ─────────────────────────────────────────────────────────
    def open_qr_modal(self, initial_idx=0):
        if not self.qr_segments:
            messagebox.showinfo("No Schedule", "Please load an Excel roster file first.")
            return
        meta = {
            "ship": self.schedule_data.get("ship", "COSTA SMERALDA") if self.schedule_data else "COSTA SMERALDA",
            "shift": self.schedule_data.get("shift", "LUNCH") if self.schedule_data else "LUNCH",
            "date": self.schedule_data.get("date", "Today") if self.schedule_data else "Today",
            "crew": self._cached_crew_count,
        }
        QRModal(self, self.qr_segments, meta, initial_idx=initial_idx)

    def _make_qr_image(self, data, size=110, box_size=3):
        """Generate a crisp QR code CTkImage with high contrast and proper quiet zone."""
        qr = qrcode.QRCode(
            version=None,
            error_correction=ERROR_CORRECT_L,
            box_size=box_size,
            border=2,
        )
        qr.add_data(data)
        qr.make(fit=True)
        pil = qr.make_image(fill_color="#000000", back_color="#FFFFFF").convert("RGB")
        if size:
            pil = pil.resize((size * 2, size * 2), PILImage.NEAREST)

        return ctk.CTkImage(
            light_image=pil, dark_image=pil,
            size=(size or pil.size[0], size or pil.size[1])
        )

    def _generate_qr(self):
        """Generate 2-part Airgap QR codes from schedule data."""
        if not self.schedule_data:
            return

        try:
            # Generate exactly 2 Airgap Segments with [COSTA-PART 1/2] and [COSTA-PART 2/2]
            self.qr_segments, self.qr_compressed_b64 = generate_compressed_payload(
                self.schedule_data, num_segments=2
            )

            if len(self.qr_segments) >= 1:
                qr_a_img = self._make_qr_image(self.qr_segments[0], size=110, box_size=3)
                self.qr_a_label.configure(image=qr_a_img, text="")
                self._qr_a_ref = qr_a_img

            if len(self.qr_segments) >= 2:
                qr_b_img = self._make_qr_image(self.qr_segments[1], size=110, box_size=3)
                self.qr_b_label.configure(image=qr_b_img, text="")
                self._qr_b_ref = qr_b_img

            self.airgap_status_label.configure(
                text="1. Point phone camera at QR preview or click 'ENLARGE QR CODE'.\n"
                     "2. Tap 'Copy text' on phone, then paste into WhatsApp.\n"
                     "3. Repeat for Part 2 to transfer complete encrypted roster."
            )
        except Exception as e:
            print(f"[Error] QR Generation failed: {e}")

    # ─────────────────────────────────────────────────────────
    # CARD RENDERING  (Newspaper Editorial Style, Zero Emojis)
    # ─────────────────────────────────────────────────────────
    def _render_cards(self):
        """Render schedule data as clean newspaper-style cards."""
        for w in self.cards_frame.winfo_children():
            w.destroy()

        d = self.schedule_data
        if not d:
            self.empty_label = ctk.CTkLabel(
                self.cards_frame,
                text="No schedule loaded. Click Browse to select an Excel roster file.",
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
            hdr, text=f"Report: {report_time}  •  {len(assignments)} stations",
            font=Fonts.get("small_bold"), text_color=TK["accent"]
        ).pack(side="right")

        # Thin divider
        ctk.CTkFrame(card, height=1, fg_color=TK["border_subtle"]).pack(fill="x", padx=16)

        body = tk.Frame(card, bg=TK["surface_card"])
        body.pack(fill="x", padx=12, pady=(4, 10))

        for idx, a in enumerate(assignments):
            bg = TK["surface_inner"] if idx % 2 == 0 else TK["surface_card"]
            row = tk.Frame(body, bg=bg)
            row.pack(fill="x", pady=1, padx=4)

            # Station badge
            tk.Label(
                row, text=a.get("station", "—"),
                font=Fonts.get("small_bold"), fg=TK["accent"], bg=bg,
                width=8, anchor="center"
            ).pack(side="left", padx=(8, 4), pady=5)

            # Waiter
            tk.Label(
                row, text=a.get("waiterName", "—"),
                font=Fonts.get("body_bold"), fg=TK["fg_primary"], bg=bg,
                anchor="w"
            ).pack(side="left", padx=6)

            # Attendant
            if a.get("attendantName"):
                tk.Label(
                    row, text=f"/ {a['attendantName']}",
                    font=Fonts.get("body"), fg=TK["fg_secondary"], bg=bg,
                    anchor="w"
                ).pack(side="left", padx=4)

            # Tables in clean monospace
            if a.get("tables"):
                tk.Label(
                    row, text=a["tables"],
                    font=Fonts.get("mono_sm"), fg=TK["fg_primary"], bg=bg,
                    anchor="e"
                ).pack(side="right", padx=8, pady=5)

    def _card_buffet(self, name, timing, lead, crew):
        card = self._card_shell(self.cards_frame)

        hdr = ctk.CTkFrame(card, fg_color="transparent")
        hdr.pack(fill="x", padx=16, pady=(12, 8))

        ctk.CTkLabel(
            hdr, text=name,
            font=Fonts.get("h3"), text_color=TK["fg_primary"]
        ).pack(side="left")

        right_text = f"{timing}  •  {len(crew)} crew"
        if lead:
            right_text = f"Lead: {lead}  •  " + right_text
        ctk.CTkLabel(
            hdr, text=right_text,
            font=Fonts.get("small_bold"), text_color=TK["fg_secondary"]
        ).pack(side="right")

        ctk.CTkFrame(card, height=1, fg_color=TK["border_subtle"]).pack(fill="x", padx=16)

        body = tk.Frame(card, bg=TK["surface_card"])
        body.pack(fill="x", padx=12, pady=(4, 10))

        chip_row = tk.Frame(body, bg=TK["surface_card"])
        chip_row.pack(fill="x")

        for c in crew:
            role = f" — {c['role']}" if c.get("role") else ""
            tk.Label(
                chip_row, text=f"  {c.get('name', '')}{role}  ",
                font=Fonts.get("small"), fg=TK["fg_primary"], bg=TK["surface_inner"],
                highlightthickness=1, highlightbackground=TK["border_subtle"],
                pady=2
            ).pack(side="left", padx=3, pady=3)

    def _card_side_duty(self, name, timing, crew):
        card = self._card_shell(self.cards_frame)

        hdr = ctk.CTkFrame(card, fg_color="transparent")
        hdr.pack(fill="x", padx=16, pady=(10, 6))

        ctk.CTkLabel(
            hdr, text=name,
            font=Fonts.get("h3"), text_color=TK["fg_primary"]
        ).pack(side="left")

        ctk.CTkLabel(
            hdr, text=f"{timing}  •  {len(crew)} crew",
            font=Fonts.get("small_bold"), text_color=TK["fg_subtle"]
        ).pack(side="right")

        ctk.CTkFrame(card, height=1, fg_color=TK["border_subtle"]).pack(fill="x", padx=16)

        body = tk.Frame(card, bg=TK["surface_card"])
        body.pack(fill="x", padx=12, pady=(4, 8))

        chip_row = tk.Frame(body, bg=TK["surface_card"])
        chip_row.pack(fill="x")

        for c in crew:
            tk.Label(
                chip_row, text=f"  {c.get('name', '')}  ",
                font=Fonts.get("small"), fg=TK["fg_secondary"], bg=TK["surface_inner"],
                highlightthickness=1, highlightbackground=TK["border_subtle"],
                pady=2
            ).pack(side="left", padx=3, pady=2)

    def _card_special_events(self, events):
        card = self._card_shell(self.cards_frame)

        ctk.CTkLabel(
            card, text="SPECIAL EVENTS & TRAVEL TALK",
            font=Fonts.get("h3"), text_color=TK["accent"]
        ).pack(anchor="w", padx=16, pady=(12, 6))

        ctk.CTkFrame(card, height=1, fg_color=TK["border_subtle"]).pack(fill="x", padx=16)

        body = tk.Frame(card, bg=TK["surface_card"])
        body.pack(fill="x", padx=12, pady=(4, 10))

        for ev in events:
            ev_box = tk.Frame(
                body, bg=TK["surface_inner"],
                highlightthickness=1, highlightbackground=TK["border_subtle"]
            )
            ev_box.pack(fill="x", pady=3)

            tk.Label(
                ev_box,
                text=f"{ev.get('title')}  —  {ev.get('location')}",
                font=Fonts.get("body_bold"), fg=TK["fg_primary"], bg=TK["surface_inner"], anchor="w"
            ).pack(fill="x", padx=10, pady=(6, 4))

            p_frame = tk.Frame(ev_box, bg=TK["surface_inner"])
            p_frame.pack(fill="x", padx=8, pady=(0, 6))
            for p in ev.get("participants", []):
                tk.Label(
                    p_frame,
                    text=f"  {p.get('name')} [{p.get('uniform')}]  ",
                    font=Fonts.get("mono_sm"), fg=TK["fg_secondary"], bg=TK["surface_card"],
                    highlightthickness=1, highlightbackground=TK["border_card"],
                    pady=2
                ).pack(side="left", padx=2, pady=2)

    def _card_sick_leave(self, sick_list):
        card = self._card_shell(self.cards_frame)

        ctk.CTkLabel(
            card, text="SICK LEAVE / OFF DUTY",
            font=Fonts.get("h3"), text_color=TK["bad_ink"]
        ).pack(anchor="w", padx=16, pady=(12, 6))

        ctk.CTkFrame(card, height=1, fg_color=TK["border_subtle"]).pack(fill="x", padx=16)

        body = tk.Frame(card, bg=TK["surface_card"])
        body.pack(fill="x", padx=12, pady=(4, 8))

        chip_row = tk.Frame(body, bg=TK["surface_card"])
        chip_row.pack(fill="x")

        for sk in sick_list:
            tk.Label(
                chip_row, text=f"  {sk.get('name', '')}  ",
                font=Fonts.get("small_bold"), fg=TK["bad_ink"], bg=TK["bad_bg"],
                highlightthickness=1, highlightbackground=TK["bad_border"],
                pady=2
            ).pack(side="left", padx=3, pady=2)

    def _card_shell(self, parent):
        """Create an editorial newspaper card frame."""
        card = ctk.CTkFrame(
            parent, fg_color=TK["surface_card"], corner_radius=10,
            border_width=1, border_color=TK["border_card"]
        )
        card.pack(fill="x", pady=5)
        return card

    # ─────────────────────────────────────────────────────────
    # BUSINESS LOGIC & ACTIONS
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
        if raw.startswith("{") and raw.endswith("}"):
            raw = raw[1:-1]
        elif raw.startswith('"') and raw.endswith('"'):
            raw = raw[1:-1]
        path = raw.strip()
        if path.lower().endswith((".xlsx", ".xls")) and os.path.exists(path):
            self.current_file = path
            self.lbl_file.configure(text=self._file_display_text())
            self.process_schedule()
            self._show_status("Roster loaded via drag & drop", TK["good_ink"])
        else:
            self._show_status("Drop a valid Excel file (.xlsx)", TK["warn_ink"])

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

    def process_schedule(self):
        """Parse Excel and generate payload + QR codes."""
        if not self.current_file or not os.path.exists(self.current_file):
            return

        self._show_status("Parsing roster...", TK["fg_accent"])
        self.update_idletasks()

        try:
            self.schedule_data = parse_schedule_excel(self.current_file, self.meal_shift)
            self.payload, self.b64_data = generate_payload(self.schedule_data)

            # Count crew once
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

        # Update Masthead Brand Title if available
        ship_name = d.get("ship", "COSTA SMERALDA")
        self.lbl_brand_title.configure(text=ship_name)

        # Update Badges
        self.badge_date.configure(text=d.get("date", "—"))
        self.badge_port.configure(text=d.get("port", "—"))

        # Update Stat Cards
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

        # Render Cards
        self._render_cards()

    def _primary_action(self):
        """Primary Action CTA: copy payload + ensure QR generated."""
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
            text=" COPIED — READY TO PASTE ON WHATSAPP",
            image=VectorIcons.get("check", size=16, color="#FFFFFF"),
            fg_color=TK["good_ink"],
            hover_color=TK["good_ink"],
            text_color="#FFFFFF"
        )
        self._toast_job = self.after(2400, self._restore_primary_btn)

    def _restore_primary_btn(self):
        self.btn_primary.configure(
            text=" COPY SCHEDULE TO CLIPBOARD",
            image=VectorIcons.get("copy", size=16, color=TK["fg_primary"]),
            fg_color=TK["gold_accent"],
            hover_color=TK["gold_hover"],
            text_color=TK["fg_primary"]
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
            messagebox.showinfo("Quick Save", f"Schedule saved to internal backup:\n{fname}")
        except Exception as err:
            messagebox.showerror("Save Failed", f"Failed:\n{err}")

    def export_json_action(self):
        if not self.schedule_data:
            messagebox.showwarning("No Data", "Load a schedule first.")
            return
        out = filedialog.asksaveasfilename(
            parent=self, title="Save Schedule As",
            defaultextension=".json", filetypes=[("JSON", "*.json")]
        )
        if out:
            with open(out, "w", encoding="utf-8") as f:
                json.dump(self.schedule_data, f, indent=2, ensure_ascii=False)
            messagebox.showinfo("Save As", f"Saved successfully to:\n{out}")

    def open_webapp(self):
        import subprocess
        from pathlib import Path
        base = os.path.dirname(os.path.abspath(__file__))
        html = os.path.join(base, "CostaSchedule.html")
        build_script = os.path.join(base, "build_single_html.py")
        web_index = os.path.join(base, "web", "index.html")

        # Automatically re-bundle if web sources are newer than single-file html
        if os.path.exists(build_script) and os.path.exists(web_index) and os.path.exists(html):
            try:
                if os.path.getmtime(web_index) > os.path.getmtime(html):
                    subprocess.run([sys.executable, build_script], cwd=base, timeout=5)
            except Exception:
                pass

        if os.path.exists(html):
            if sys.platform == "darwin":
                subprocess.Popen(["open", html])
            elif sys.platform == "win32":
                os.startfile(html)
            else:
                try:
                    subprocess.Popen(["xdg-open", html])
                except Exception:
                    webbrowser.open(Path(html).resolve().as_uri())
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
