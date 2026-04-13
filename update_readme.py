import os
import requests

# 從 GitHub Secrets 讀取金鑰
NOTION_TOKEN = os.environ.get('NOTION_TOKEN')
DATABASE_ID = os.environ.get('NOTION_DATABASE_ID')

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

def get_projects():
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    # 這裡預設抓取前 12 筆，你可以根據需要調整
    response = requests.post(url, headers=headers)
    if response.status_code != 200:
        return []
    return response.json().get("results", [])

def main():
    projects = get_projects()
    
    content = "# 我的 AI Studio 專案\n\n"
    content += "這裡記錄了近期透過 AI 輔助開發的應用服務與練習。\n\n"
    content += "<table border='0'><tr>"
    
    for i, p in enumerate(projects):
        props = p.get('properties', {})
        
        # --- 欄位對應開始 ---
        try:
            # 1. 名稱 (標題類型)
            name = props['名稱']['title'][0]['plain_text'] if props.get('名稱') and props['名稱']['title'] else "未命名"
            
            # 2. 描述 (文字類型)
            desc = props['描述']['rich_text'][0]['plain_text'] if props.get('描述') and props['描述']['rich_text'] else ""
            
            # 3. 分享連結 (URL 類型)
            link = props['分享連結']['url'] if props.get('分享連結') else "#"
            
            # 4. 分類 (選擇類型 - 這裡我們用來當標籤顯示)
            tag = props['分類']['select']['name'] if props.get('分類') and props['分類']['select'] else ""

            # 5. 圖片處理：優先抓取 Notion 頁面的「封面圖 (Cover)」
            if p.get('cover'):
                img_url = p['cover'].get('external', {}).get('url') or p['cover'].get('file', {}).get('url')
            else:
                # 如果沒有封面圖，顯示一張預設的占位圖（你可以換成你喜歡的網址）
                img_url = "https://via.placeholder.com/600x400?text=AI+Studio"

        except Exception as e:
            print(f"解析資料出錯: {e}")
            continue
        # --- 欄位對應結束 ---

        # 每 3 個專案換一行
        if i % 3 == 0 and i != 0:
            content += "</tr><tr>"
        
        # 構建 HTML 卡片
        content += f"""
<td width="33%" valign="top">
  <img src="{img_url}" width="100%" style="border-radius:10px; border: 1px solid #eee;">
  <br>
  <div style="padding: 10px 0;">
    <span style="font-size: 0.8em; background: #f0f0f0; padding: 2px 6px; border-radius: 4px;">{tag}</span><br>
    <strong style="font-size: 1.1em; display: block; margin-top: 5px;">{name}</strong>
    <p style="font-size: 0.9em; color: #666; line-height: 1.4;">{desc}</p>
    <a href="{link}" target="_blank" style="text-decoration: none; color: #0366d6;">🚀 啟動專案</a>
  </div>
</td>"""

    content += "</tr></table>\n\n"
    content += "---\n*最後更新時間：自動同步自 Notion 資料庫*"

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    main()
