import os
import requests
import shutil

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
    print(f"Notion API 回應狀態碼: {response.status_code}")
    if response.status_code != 200:
        print(f"錯誤訊息: {response.text}")
        return []
    results = response.json().get("results", [])
    print(f"總共抓到 {len(results)} 筆資料")
    return results

def download_image(url, save_path):
    if not url or url == "#": return False
    try:
        res = requests.get(url, stream=True, timeout=10)
        if res.status_code == 200:
            with open(save_path, 'wb') as f:
                shutil.copyfileobj(res.raw, f)
            return True
    except: return False
    return False

def main():
    projects = get_projects()
    if not os.path.exists('images'): os.makedirs('images')
    
    content = "# 我的 AI Studio 專案\n\n這裡記錄了近期透過 AI 輔助開發的應用服務與練習。\n\n<table border='0'><tr>"
    
    valid_count = 0
    for i, p in enumerate(projects):
        props = p.get('properties', {})
        
        try:
            # 1. 名稱 (標題)
            name = props['名稱']['title'][0]['plain_text'] if props.get('名稱') and props['名稱']['title'] else "未命名"
            
            # 2. 描述
            desc = props['描述']['rich_text'][0]['plain_text'] if props.get('描述') and props['描述']['rich_text'] else ""
            
            # 3. 分享連結
            link = props['分享連結']['url'] if props.get('分享連結') else "#"
            
            # 4. 分類 (改用更強壯的解析方式)
            tag = ""
            if '分類' in props:
                c_prop = props['分類']
                p_type = c_prop.get('type')
                if p_type == 'select' and c_prop.get('select'):
                    tag = c_prop['select']['name']
                elif p_type == 'multi_select' and c_prop.get('multi_select'):
                    tag = ", ".join([t['name'] for t in c_prop['multi_select']])

            # 5. 圖片下載處理
            page_id = p.get('id')
            local_img_path = f"images/{page_id}.png"
            img_src = f"./images/{page_id}.png"
            
            notion_img_url = None
            if p.get('cover'):
                notion_img_url = p['cover'].get('external', {}).get('url') or p['cover'].get('file', {}).get('url')
            
            # 執行下載
            if notion_img_url:
                success = download_image(notion_img_url, local_img_path)
                if not success: img_src = "https://via.placeholder.com/600x400?text=Download+Failed"
            else:
                img_src = "https://via.placeholder.com/600x400?text=No+Cover"

            # 每 3 個換行
            if valid_count % 3 == 0 and valid_count != 0:
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
            valid_count += 1
            
        except Exception as e:
            print(f"解析第 {i+1} 筆資料出錯: {str(e)}")
            continue

    content += "</tr></table>\n\n---\n*最後更新時間：自動同步自 Notion 資料庫*"
    
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(content)
    print("README 更新完成，共處理了", valid_count, "筆資料")

if __name__ == "__main__":
    main()
