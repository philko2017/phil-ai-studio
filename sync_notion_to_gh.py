import os
import requests
import json
from datetime import datetime

# 環境變數
NOTION_TOKEN = os.getenv('NOTION_TOKEN')
DATABASE_ID = os.getenv('NOTION_DATABASE_ID')
IMAGE_DIR = "assets/projects"

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

# HTML 模板：沉浸式視覺 (出血模糊 + 完整主圖)
HTML_TEMPLATE_START = """<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Showcase | Mobile Landing Page</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body, html { height: 100%; overflow: hidden; background: #000; font-family: sans-serif; }
        .container { height: 100vh; overflow-y: scroll; scroll-snap-type: y mandatory; scroll-behavior: smooth; -webkit-overflow-scrolling: touch; }
        .container::-webkit-scrollbar { display: none; }
        
        section {
            position: relative; height: 100vh; width: 100%;
            display: flex; flex-direction: column; align-items: center; justify-content: center;
            scroll-snap-align: start; overflow: hidden;
        }

        /* 1. 出血模糊背景 */
        .bg-bleed {
            position: absolute; top: -10%; left: -10%; width: 120%; height: 120%;
            background-size: cover; background-position: center;
            filter: blur(40px) brightness(0.4); z-index: -1;
        }

        /* 2. 完整主圖容器 (維持比例) */
        .img-box {
            width: 85%; height: 50vh;
            display: flex; align-items: center; justify-content: center;
            z-index: 1;
        }
        .img-box img {
            max-width: 100%; max-height: 100%;
            object-fit: contain; border-radius: 8px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.6);
        }

        /* 3. 資訊層 */
        .info { z-index: 2; width: 85%; margin-top: 2rem; text-align: center; color: white; }
        .info h2 { font-size: 1.6rem; margin-bottom: 0.8rem; letter-spacing: 1px; }
        .info p { font-size: 0.95rem; color: rgba(255,255,255,0.7); line-height: 1.6; margin-bottom: 2rem; }
        
        /* 超連結按鈕 */
        .cta {
            display: inline-block; padding: 12px 35px;
            background: rgba(255,255,255,0.9); color: #000;
            text-decoration: none; border-radius: 50px; font-weight: bold;
        }
    </style>
</head>
<body><div class="container">
"""

HTML_TEMPLATE_END = "</div></body></html>"

def download_img(url, name):
    if not os.path.exists(IMAGE_DIR): os.makedirs(IMAGE_DIR)
    path = os.path.join(IMAGE_DIR, f"{name}.png")
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            with open(path, 'wb') as f: f.write(r.content)
            return path
    except: pass
    return None

def run():
    print(f"[{datetime.now()}] Starting...")
    res = requests.post(f"https://api.notion.com/v1/databases/{DATABASE_ID}/query", headers=HEADERS)
    if res.status_code != 200: return print("Error fetching Notion data")
    
    pages = res.json().get("results", [])
    html_items = ""
    readme_table = "<table><tr>"

    for i, page in enumerate(pages):
        props = page["properties"]
        name = props["Name"]["title"][0]["plain_text"]
        desc = props["Description"]["rich_text"][0]["plain_text"] if props["Description"]["rich_text"] else ""
        link = props["URL"]["url"] or "#"
        
        # 抓取封面圖
        img_url = ""
        if page.get("cover"):
            img_url = page["cover"].get("external", {}).get("url") or page["cover"].get("file", {}).get("url")
        
        local_img = download_img(img_url, f"p_{i}") if img_url else ""

        # 生成手機頁面 HTML
        html_items += f"""
        <section>
            <div class="bg-bleed" style="background-image: url('{local_img}')"></div>
            <div class="img-box"><img src="{local_img}"></div>
            <div class="info">
                <h2>{name}</h2>
                <p>{desc}</p>
                <a href="{link}" class="cta">Explore</a>
            </div>
        </section>"""

        # 生成 README 網格
        if i > 0 and i % 5 == 0: readme_table += "</tr><tr>"
        readme_table += f'<td align="center"><a href="{link}"><img src="{local_img}" width="180"/><br/>{name}</a></td>'

    # 寫入檔案
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(HTML_TEMPLATE_START + html_items + HTML_TEMPLATE_END)
    
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(f"# Portfolio\\n\\n{readme_table}</tr></table>\\n\\nUpdated: {datetime.now()}")

if __name__ == "__main__":
    run()
