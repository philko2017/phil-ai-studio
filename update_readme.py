import os
import requests
import shutil

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
    response = requests.post(url, headers=headers)
    if response.status_code != 200:
        return []
    return response.json().get("results", [])

def download_image(url, save_path):
    """將圖片下載到本地路徑"""
    if not url or url == "#":
        return None
    try:
        res = requests.get(url, stream=True)
        if res.status_code == 200:
            with open(save_path, 'wb') as f:
                shutil.copyfileobj(res.raw, f)
            return True
    except Exception as e:
        print(f"下載圖片失敗: {e}")
    return False

def main():
    projects = get_projects()
    
    # 建立存放圖片的資料夾
    if not os.path.exists('images'):
        os.makedirs('images')
    
    content = "# 我的 AI Studio 專案\n\n"
    content += "這裡記錄了近期透過 AI 輔助開發的應用服務與練習。\n\n"
    content += "<table border='0'><tr>"
    
    for i, p in enumerate(projects):
        props = p.get('properties', {})
        page_id = p.get('id') # 用 Notion Page ID 當作檔名，避免重複
        
        try:
            name = props['名稱']['title'][0]['plain_text'] if props.get('名稱') and props['名稱']['title'] else "未命名"
            desc = props['描述']['rich_text'][0]['plain_text'] if props.get('描述') and props['描述']['rich_text'] else ""
            link = props['分享連結']['url'] if props.get('分享連結') else "#"
            tag = props['分類']['select']['name'] if props.get('分類') and props['分類']['select'] else ""

            # 處理圖片：抓取封面並下載到本地
            local_img_path = f"images/{page_id}.png"
            img_src = f"./images/{page_id}.png" # README 裡面使用的路徑
            
            notion_img_url = None
            if p.get('cover'):
                notion_img_url = p['cover'].get('external', {}).get('url') or p['cover'].get('file', {}).get('url')
            
            if notion_img_url:
                success = download_image(notion_img_url, local_img_path)
                if not success:
                    img_src = "https://via.placeholder.com/600x400?text=No+Image"
            else:
                img_src = "https://via.placeholder.com/600x400?text=AI+Studio"

        except Exception as e:
            print(f"解析資料出錯: {e}")
            continue

        if i % 3 == 0 and i != 0:
            content += "</tr><tr>"
        
        content += f"""
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

    content += "</tr></table>\n\n---\n*最後更新時間：自動同步自 Notion 資料庫*"

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    main()
