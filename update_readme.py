import os
import requests

# 取得保險箱裡的資訊
NOTION_TOKEN = os.environ['NOTION_TOKEN']
DATABASE_ID = os.environ['NOTION_DATABASE_ID']

headers = {
    "Authorization": "Bearer " + NOTION_TOKEN,
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

def get_projects():
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    response = requests.post(url, headers=headers)
    return response.json().get("results", [])

def main():
    projects = get_projects()
    # 這裡開始構建你的 HTML 網格，格式就如你之前截圖的 Gallery View
    content = "# 我的 AI Studio 專案\n\n<table border='0'><tr>"
    
    for i, p in enumerate(projects):
        props = p['properties']
        # 根據你的 Notion 欄位名稱修改這裡
        name = props['名稱']['title'][0]['text']['content']
        desc = props['描述']['rich_text'][0]['text']['content']
        img = props['圖片網址']['url']
        link = props['專案連結']['url']

        if i % 3 == 0 and i != 0: content += "</tr><tr>"
        
        content += f"""
        <td width="33%" valign="top">
          <img src="{img}" width="100%"><br>
          <b>{name}</b><br>
          <font size="2">{desc}</font><br>
          <a href="{link}">🚀 啟動專案</a>
        </td>"""
    
    content += "</tr></table>"
    
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    main()
