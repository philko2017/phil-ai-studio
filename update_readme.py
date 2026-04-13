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
    response = requests.post(url, headers=headers)
    if response.status_code != 200:
        print(f"❌ 無法讀取 Notion 資料庫: {response.text}")
        return []
    results = response.json().get("results", [])
    print(f"✅ 成功抓取到 {len(results)} 筆資料")
    return results

def main():
    projects = get_projects()
    content = "# 我的 AI Studio 專案\n\n這裡記錄了近期透過 AI 輔助開發的應用服務與練習。\n\n"
    
    if not projects:
        content += "> 目前資料庫中沒有可顯示的資料，請確認 Notion 頁面是否已分享給 Integration。\n"
    else:
        content += "<table border='0'><tr>"
        for i, p in enumerate(projects):
            props = p.get('properties', {})
            
            # --- 強化版欄位解析 ---
            try:
                # 名稱：處理標題
                name_list = props.get('名稱', {}).get('title', [])
                name = name_list[0]['plain_text'] if name_list else "未命名專案"
                
                # 描述：處理富文本，若空則顯示空白
                desc_list = props.get('描述', {}).get('rich_text', [])
                desc = desc_list[0]['plain_text'] if desc_list else "暫無描述"
                
                # 分享連結
                link = props.get('分享連結', {}).get('url') or "#"
                
                # 分類：處理 Select 或 Multi-select
                cat_data = props.get('分類', {})
                tag = ""
                if cat_data.get('select'):
                    tag = cat_data['select']['name']
                elif cat_data.get('multi_select'):
                    tag = ", ".join([m['name'] for m in cat_data['multi_select']])

                # 封面圖：抓取頁面 Cover
                img_url = "https://via.placeholder.com/600x400?text=No+Image" # 預設圖
                if p.get('cover'):
                    img_url = p['cover'].get('external', {}).get('url') or p['cover'].get('file', {}).get('url')

                # 生成 HTML
                if i % 3 == 0 and i != 0:
                    content += "</tr><tr>"
                
                content += f"""
<td width="33%" valign="top">
  <img src="{img_url}" width="100%" style="border-radius:10px; border:1px solid #eee;">
  <br>
  <div style="padding:10px 0;">
    <span style="font-size:0.8em; background:#f0f0f0; padding:2px 6px; border-radius:4px;">{tag}</span><br>
    <strong style="font-size:1.1em; display:block; margin-top:5px;">{name}</strong>
    <p style="font-size:0.9em; color:#666;">{desc}</p>
    <a href="{link}" target="_blank" style="text-decoration:none; color:#0366d6;">🚀 啟動專案</a>
  </div>
</td>"""
                print(f"✔️ 已成功解析: {name}")

            except Exception as e:
                print(f"⚠️ 解析第 {i+1} 筆資料時發生錯誤: {e}")
                continue

        content += "</tr></table>\n\n"

    content += "---\n最後更新時間：自動同步自 Notion 資料庫"

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    main()
