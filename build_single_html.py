#!/usr/bin/env python3
"""
Bundle web/ folder assets into a single-file portable CostaSchedule.html
and sync assets to android/app/src/main/assets/
"""
import os
import shutil
import base64

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
    print(f"✅ Synced web assets to {ANDROID_ASSETS}")

def build_single_html():
    sync_assets_to_android()

    index_path = os.path.join(WEB_DIR, "index.html")
    css_path = os.path.join(WEB_DIR, "style.css")
    js_path = os.path.join(WEB_DIR, "app.js")
    logo_path = os.path.join(WEB_DIR, "logo.png")

    with open(index_path, "r", encoding="utf-8") as f:
        html = f.read()

    with open(css_path, "r", encoding="utf-8") as f:
        css = f.read()

    with open(js_path, "r", encoding="utf-8") as f:
        js = f.read()

    with open(logo_path, "rb") as f:
        logo_b64 = base64.b64encode(f.read()).decode("utf-8")
        logo_data_uri = f"data:image/png;base64,{logo_b64}"

    # Replace CSS
    html = html.replace('<link rel="stylesheet" href="style.css">', f'<style>\n{css}\n</style>')
    
    # Replace logo image
    html = html.replace('src="logo.png"', f'src="{logo_data_uri}"')

    # Replace JS script
    html = html.replace('<script src="app.js"></script>', f'<script>\n{js}\n</script>')

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✅ Successfully generated standalone {OUTPUT_FILE} ({os.path.getsize(OUTPUT_FILE)} bytes)")

if __name__ == "__main__":
    build_single_html()
