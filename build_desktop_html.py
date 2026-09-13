#!/usr/bin/env python3
"""
Bundle desktop_web/ folder assets into a single-file portable CostaExporter.html.
Stand-alone, zero-installation offline Desktop Schedule Exporter for Windows/Mac.
"""
import os
import re
import base64
import subprocess
import sys
import tempfile

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DESKTOP_WEB_DIR = os.path.join(BASE_DIR, "desktop_web")
OUTPUT_FILE = os.path.join(BASE_DIR, "CostaExporter.html")


def minify_js(js_code):
    """Minify JavaScript via terser."""
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False, encoding='utf-8') as tmp:
            tmp.write(js_code)
            tmp_path = tmp.name

        result = subprocess.run(
            ['npx', 'terser', tmp_path,
             '--compress', 'passes=2,dead_code=true,drop_console=false',
             '--mangle',
             '--output', tmp_path + '.min'],
            capture_output=True, text=True, timeout=45
        )

        if result.returncode == 0:
            with open(tmp_path + '.min', 'r', encoding='utf-8') as f:
                minified = f.read()
            os.unlink(tmp_path)
            os.unlink(tmp_path + '.min')
            ratio = (1 - len(minified) / len(js_code)) * 100
            print(f"  JS minified: {len(js_code):,} -> {len(minified):,} bytes ({ratio:.1f}% reduction)")
            return minified
        else:
            print(f"  [Warning] terser failed, using original JS: {result.stderr[:200]}")
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            if os.path.exists(tmp_path + '.min'):
                os.unlink(tmp_path + '.min')
            return js_code
    except Exception as e:
        print(f"  [Warning] JS minification skipped: {e}")
        return js_code


def minify_css(css_code):
    """Minify CSS via regex transforms."""
    original_len = len(css_code)
    s = css_code
    s = re.sub(r'/\*(?!\!)[^*]*\*+(?:[^/*][^*]*\*+)*/', '', s)
    s = re.sub(r'\s+', ' ', s)
    s = re.sub(r'\s*{\s*', '{', s)
    s = re.sub(r'\s*}\s*', '}', s)
    s = re.sub(r'\s*;\s*', ';', s)
    s = re.sub(r'\s*:\s*', ':', s)
    s = re.sub(r'\s*,\s*', ',', s)
    s = s.replace(';}', '}')
    s = s.strip()
    ratio = (1 - len(s) / original_len) * 100
    print(f"  CSS minified: {original_len:,} -> {len(s):,} bytes ({ratio:.1f}% reduction)")
    return s


def strip_html_comments(html_code):
    """Remove HTML comments."""
    return re.sub(r'<!--(?!\[)(?!.*?-->\s*\n\s*<script).*?-->', '', html_code, flags=re.DOTALL)


def build_desktop_html():
    fonts_path = os.path.join(DESKTOP_WEB_DIR, "fonts.css")
    index_path = os.path.join(DESKTOP_WEB_DIR, "index.html")
    css_path = os.path.join(DESKTOP_WEB_DIR, "style.css")
    js_path = os.path.join(DESKTOP_WEB_DIR, "app.js")
    logo_path = os.path.join(DESKTOP_WEB_DIR, "logo.png")

    vendor_xlsx = os.path.join(DESKTOP_WEB_DIR, "vendor", "xlsx.full.min.js")
    vendor_pako = os.path.join(DESKTOP_WEB_DIR, "vendor", "pako_deflate.min.js")
    vendor_qrcode = os.path.join(DESKTOP_WEB_DIR, "vendor", "qrcode.min.js")

    with open(index_path, "r", encoding="utf-8") as f:
        html = f.read()

    fonts_css = ""
    if os.path.exists(fonts_path):
        with open(fonts_path, "r", encoding="utf-8") as f:
            fonts_css = f.read()

    with open(css_path, "r", encoding="utf-8") as f:
        css = f.read()

    with open(js_path, "r", encoding="utf-8") as f:
        js = f.read()

    with open(vendor_xlsx, "r", encoding="utf-8") as f:
        xlsx_code = f.read()

    with open(vendor_pako, "r", encoding="utf-8") as f:
        pako_code = f.read()

    with open(vendor_qrcode, "r", encoding="utf-8") as f:
        qrcode_code = f.read()

    with open(logo_path, "rb") as f:
        logo_b64 = base64.b64encode(f.read()).decode("utf-8")
        logo_data_uri = f"data:image/png;base64,{logo_b64}"

    print("Building CostaExporter production bundle...")
    print("  Minifying Application JS...")
    js = minify_js(js)

    print("  Minifying CSS...")
    css = minify_css(css)
    if fonts_css:
        fonts_css = minify_css(fonts_css)

    # Inline Fonts & CSS
    if fonts_css:
        html = html.replace('<link rel="stylesheet" href="fonts.css">', f'<style>{fonts_css}</style>')
    html = html.replace('<link rel="stylesheet" href="style.css">', f'<style>{css}</style>')
    html = html.replace('src="logo.png"', f'src="{logo_data_uri}"')

    # Inline Vendor Libraries
    html = html.replace('<script src="vendor/xlsx.full.min.js"></script>', f'<script>{xlsx_code}</script>')
    html = html.replace('<script src="vendor/pako_deflate.min.js"></script>', f'<script>{pako_code}</script>')
    html = html.replace('<script src="vendor/qrcode.min.js"></script>', f'<script>{qrcode_code}</script>')

    # Inline App Script
    html = html.replace('<script src="app.js"></script>', f'<script>{js}</script>')

    # Strip HTML comments & excessive blank lines
    html = strip_html_comments(html)
    html = re.sub(r'\n{3,}', '\n\n', html)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html)

    size_mb = os.path.getsize(OUTPUT_FILE) / (1024 * 1024)
    print(f"Production build complete: {OUTPUT_FILE} ({size_mb:.2f} MB)")


if __name__ == "__main__":
    build_desktop_html()
