import os
import requests

NOTION_TOKEN = os.environ.get('NOTION_TOKEN')
DATABASE_ID = os.environ.get('NOTION_DATABASE_ID')

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

def get_projects():
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    # 你可以在 Notion 裡設定排序，或這裡預設抓取
    response = requests.post(url, headers=headers)
    if response.status_code != 200:
        return []
    return response.json().get("results", [])

def main():
    projects = get_projects()
    content = "# 我的 AI Studio 專案\n\n這裡記錄了近期透過 AI 輔助開發的應用服務與練習。\n\n"
    
    if not projects:
        content += "> ⚠️ 目前資料庫中沒有可顯示的資料。\n"
    else:
        content += "<table border='0'><tr>"
        count = 0
        for p in projects:
            props = p.get('properties', {})
            
            try:
                # 1. 抓取名稱 (Title)
                name = "未命名專案"
                for k, v in props.items():
                    if v['type'] == 'title' and v['title']:
                        name = v['title'][0]['plain_text']
                        break
                
                # 2. 抓取描述
                desc = ""
                desc_obj = props.get('描述') or props.get('Description')
                if desc_obj and desc_obj.get('rich_text'):
                    desc = desc_obj['rich_text'][0]['plain_text']
                
                # 3. 抓取連結
                link = "#"
                link_obj = props.get('分享連結') or props.get('URL')
                if link_obj:
                    link = link_obj.get('url') or "#"

                # 4. 抓取封面圖 (Cover)
                img_url = "https://via.placeholder.com/600x400?text=AI+Studio"
                if p.get('cover'):
                    img_url = p['cover'].get('external', {}).get('url') or p['cover'].get('file', {}).get('url')

                # --- 核心邏輯修改：一排 3 個 ---
                if count % 3 == 0 and count != 0:
                    content += "</tr><tr>"
                
                # 移除 tag 顯示，優化卡片間距
                content += f"""
<td width="20%" valign="top">
  <img src="{img_url}" width="100%" style="border-radius:8px; border:1px solid #eee;">
  <br>
  <div style="padding:8px 0;">
    <strong style="font-size:1.0em; display:block; margin-top:5px; line-height:1.2;">{name}</strong>
    <p style="font-size:0.8em; color:#666; margin:5px 0; line-height:1.4;">{desc}</p>
    <a href="{link}" target="_blank" style="text-decoration:none; color:#0366d6; font-size:0.85em;">🚀 啟動專案</a>
  </div>
</td>"""
                count += 1

            except Exception as e:
                continue

        content += "</tr></table>\n\n"

    content += "---\n*最後更新時間：自動同步自 Notion 資料庫*"

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    main()
