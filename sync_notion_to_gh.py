import os
import requests
import shutil
from datetime import datetime

# ==========================================
# 1. 設定區 (從 GitHub Secrets 讀取)
# ==========================================
NOTION_TOKEN = os.environ.get('NOTION_TOKEN')
DATABASE_ID = os.environ.get('NOTION_DATABASE_ID')
IMAGE_DIR = 'images'

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

# ==========================================
# 2. HTML 模板 (Mobile-First 沉浸式視覺)
# ==========================================
HTML_TEMPLATE_START = """<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Phil AI Studio | Mobile</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body, html { height: 100%; overflow: hidden; background: #000; font-family: -apple-system, sans-serif; }
        .container { height: 100vh; overflow-y: scroll; scroll-snap-type: y mandatory; scroll-behavior: smooth; -webkit-overflow-scrolling: touch; }
        .container::-webkit-scrollbar { display: none; }
        section { position: relative; height: 100vh; width: 100%; display: flex; flex-direction: column; align-items: center; justify-content: center; scroll-snap-align: start; overflow: hidden; }
        .bg-bleed { position: absolute; top: -10%; left: -10%; width: 120%; height: 120%; background-size: cover; background-position: center; filter: blur(35px) brightness(0.4); z-index: -1; }
        .img-box { width: 85%; height: 45vh; display: flex; align-items: center; justify-content: center; z-index: 1; }
        .img-box img { max-width: 100%; max-height: 100%; object-fit: contain; border-radius: 12px; box-shadow: 0 15px 35px rgba(0,0,0,0.6); }
        .info { z-index: 2; width: 85%; margin-top: 2.5rem; text-align: center; color: white; }
        .info .tag { display: inline-block; font-size: 0.75rem; background: rgba(255,255,255,0.2); padding: 3px 10px; border-radius: 4px; margin-bottom: 10px; }
        .info h2 { font-size: 1.6rem; margin-bottom: 0.8rem; text-shadow: 0 2px 4px rgba(0,0,0,0.5); }
        .info p { font-size: 0.95rem; color: rgba(255,255,255,0.7); line-height: 1.5; margin-bottom: 2rem; }
        .cta { display: inline-block; padding: 14px 40px; background: #fff; color: #000; text-decoration: none; border-radius: 50px; font-weight: bold; }
    </style>
</head>
<body><div class="container">
"""
HTML_TEMPLATE_END = "</div></body></html>"

# ==========================================
# 3. 工具函式
# ==========================================
def download_image(url, save_path):
    if not url or url == "#": return False
    try:
        res = requests.get(url, stream=True, timeout=15)
        if res.status_code == 200:
            with open(save_path, 'wb') as f:
                shutil.copyfileobj(res.raw, f)
            return True
    except: return False
    return False

def get_projects():
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    res = requests.post(url, headers=HEADERS)
    if res.status_code != 200:
        print(f"[Error] Notion API 失敗: {res.text}")
        return []
    return res.json().get("results", [])

# ==========================================
# 4. 主程式
# ==========================================
def main():
    projects = get_projects()
    if not os.path.exists(IMAGE_DIR): os.makedirs(IMAGE_DIR)
    
    # README 標題與網格開頭
    readme_content = "## Phil AI Studio 專案\n\n ### 這裡主要是我透過 AI Studio 以及 Gemini Canvas，透過對話的方式創造的一些生活小工具。\n\n ### 我主要在 Notion 使用圖庫的瀏覽模式排版好，再透過同步按鈕送到 GitHub \n\n ### 歡迎自由取用與交流 \n\n<table border='0'><tr>"
    
    html_items = ""
    valid_count = 0

    for i, p in enumerate(projects):
        props = p.get('properties', {})
        try:
            # 依據您的舊代碼邏輯擷取欄位
            name = props['名稱']['title'][0]['plain_text'] if props.get('名稱') and props['名稱']['title'] else "未命名"
            desc = props['描述']['rich_text'][0]['plain_text'] if props.get('描述') and props['描述']['rich_text'] else ""
            link = props['分享連結']['url'] if props.get('分享連結') else "#"
            
            # 分類解析
            tag = ""
            if '分類' in props:
                c_prop = props['分類']
                p_type = c_prop.get('type')
                if p_type == 'select' and c_prop.get('select'):
                    tag = c_prop['select']['name']
                elif p_type == 'multi_select' and c_prop.get('multi_select'):
                    tag = ", ".join([t['name'] for t in c_prop['multi_select']])

            # 圖片下載
            page_id = p.get('id')
            local_img_path = f"{IMAGE_DIR}/{page_id}.png"
            img_src = f"./{IMAGE_DIR}/{page_id}.png"
            
            notion_img_url = None
            if p.get('cover'):
                notion_img_url = p['cover'].get('external', {}).get('url') or p['cover'].get('file', {}).get('url')
            
            if notion_img_url:
                success = download_image(notion_img_url, local_img_path)
                if not success: img_src = "https://via.placeholder.com/600x400?text=Download+Failed"
            else:
                img_src = "https://via.placeholder.com/600x400?text=No+Cover"

            # --- 生成 README 網格 (每 3 個換行) ---
            if valid_count % 3 == 0 and valid_count != 0:
                readme_content += "</tr><tr>"
            
            readme_content += f"""
<td width="33%" valign="top">
  <img src="{img_src}" width="100%" style="border-radius:10px; border: 1px solid #eee;">
  <br>
  <div style="padding: 10px 0;">
    <span style="font-size: 0.8em; background: #f0f0f0; padding: 2px 6px; border-radius: 4px;">{tag}</span><br>
    <strong style="font-size: 1.1em; display: block; margin-top: 5px;">{name}</strong>
    <p style="font-size: 0.9em; color: #666; line-height: 1.4;">{desc}</p>
    <a href="{link}" target="_blank" style="text-decoration: none; color: #0366d6;">🚀 啟動專案</a>
  </div>
</td>"""

            # --- 生成 Mobile Landing Page HTML ---
            html_items += f"""
        <section>
            <div class="bg-bleed" style="background-image: url('{img_src}');"></div>
            <div class="img-box"><img src="{img_src}"></div>
            <div class="info">
                {f'<span class="tag">{tag}</span>' if tag else ''}
                <h2>{name}</h2>
                <p>{desc}</p>
                <a href="{link}" class="cta">🚀 啟動專案</a>
            </div>
        </section>"""

            valid_count += 1
            
        except Exception as e:
            print(f"解析第 {i+1} 筆資料出錯: {str(e)}")
            continue

    # 結尾處理
    readme_content += f"</tr></table>\n\n---\n*最後更新時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"
    
    # 寫入 README.md
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    # 寫入 index.html
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(HTML_TEMPLATE_START + html_items + HTML_TEMPLATE_END)

    print(f"同步完成！共處理 {valid_count} 筆專案。README 與 index.html 已更新。")

if __name__ == "__main__":
    main()
