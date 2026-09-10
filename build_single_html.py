#!/usr/bin/env python3
"""
Bundle web/ folder assets into a single-file portable CostaSchedule.html
and sync assets to android/app/src/main/assets/
"""
import os
import re
import shutil
import base64
import subprocess
import sys
import tempfile

ROOT_DIR = "/Users/dianjulie/Documents/Schedule Costa"
WEB_DIR = os.path.join(ROOT_DIR, "web")
ANDROID_ASSETS = os.path.join(ROOT_DIR, "android/app/src/main/assets")
OUTPUT_FILE = os.path.join(ROOT_DIR, "CostaSchedule.html")


def sync_assets_to_android():
    os.makedirs(ANDROID_ASSETS, exist_ok=True)
    for item in os.listdir(WEB_DIR):
        s = os.path.join(WEB_DIR, item)
        d = os.path.join(ANDROID_ASSETS, item)
        if os.path.isfile(s):
            shutil.copy2(s, d)
    print(f"Synced web assets to {ANDROID_ASSETS}")


def minify_js(js_code):
    """Minify JavaScript via terser (industry-standard, reversible with any beautifier)."""
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False, encoding='utf-8') as tmp:
            tmp.write(js_code)
            tmp_path = tmp.name

        result = subprocess.run(
            ['npx', 'terser', tmp_path,
             '--compress', 'passes=2,dead_code=true,drop_console=false',
             '--mangle', '--toplevel',
             '--output', tmp_path + '.min'],
            capture_output=True, text=True, timeout=30
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
            os.unlink(tmp_path)
            return js_code
    except Exception as e:
        print(f"  [Warning] JS minification skipped: {e}")
        return js_code


def minify_css(css_code):
    """Minify CSS via regex transforms (lightweight, no external dependency)."""
    original_len = len(css_code)
    s = css_code

    # Remove CSS comments (preserve license/copyright blocks)
    s = re.sub(r'/\*(?!\!)[^*]*\*+(?:[^/*][^*]*\*+)*/', '', s)

    # Collapse whitespace around selectors and properties
    s = re.sub(r'\s+', ' ', s)
    s = re.sub(r'\s*{\s*', '{', s)
    s = re.sub(r'\s*}\s*', '}', s)
    s = re.sub(r'\s*;\s*', ';', s)
    s = re.sub(r'\s*:\s*', ':', s)
    s = re.sub(r'\s*,\s*', ',', s)

    # Remove trailing semicolons before closing braces
    s = s.replace(';}', '}')

    # Remove leading/trailing whitespace
    s = s.strip()

    ratio = (1 - len(s) / original_len) * 100
    print(f"  CSS minified: {original_len:,} -> {len(s):,} bytes ({ratio:.1f}% reduction)")
    return s


def strip_html_comments(html_code):
    """Remove HTML comments (<!-- ... -->) except conditional/IE comments."""
    return re.sub(r'<!--(?!\[)(?!.*?-->\s*\n\s*<script).*?-->', '', html_code, flags=re.DOTALL)


def build_single_html():
    sync_assets_to_android()

    fonts_path = os.path.join(WEB_DIR, "fonts.css")
    index_path = os.path.join(WEB_DIR, "index.html")
    css_path = os.path.join(WEB_DIR, "style.css")
    js_path = os.path.join(WEB_DIR, "app.js")
    logo_path = os.path.join(WEB_DIR, "logo.png")

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

    with open(logo_path, "rb") as f:
        logo_b64 = base64.b64encode(f.read()).decode("utf-8")
        logo_data_uri = f"data:image/png;base64,{logo_b64}"

    # Production minification
    print("Building production bundle...")
    print("  Minifying JavaScript...")
    js = minify_js(js)

    print("  Minifying CSS...")
    css = minify_css(css)
    if fonts_css:
        fonts_css = minify_css(fonts_css)

    # Inline assets
    if fonts_css:
        html = html.replace('<link rel="stylesheet" href="fonts.css">', f'<style>{fonts_css}</style>')
    html = html.replace('<link rel="stylesheet" href="style.css">', f'<style>{css}</style>')
    html = html.replace('src="logo.png"', f'src="{logo_data_uri}"')
    html = html.replace('<script src="app.js"></script>', f'<script>{js}</script>')

    # Strip HTML comments for clean output
    html = strip_html_comments(html)

    # Collapse excessive blank lines
    html = re.sub(r'\n{3,}', '\n\n', html)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html)

    size_kb = os.path.getsize(OUTPUT_FILE) / 1024
    print(f"Production build complete: {OUTPUT_FILE} ({size_kb:.0f} KB)")


if __name__ == "__main__":
    build_single_html()
