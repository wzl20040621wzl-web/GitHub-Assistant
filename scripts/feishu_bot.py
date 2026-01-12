import os
import requests
import json
import sys

# 1. 加载环境变量
APP_ID = os.environ["FEISHU_APP_ID"]
APP_SECRET = os.environ["FEISHU_APP_SECRET"]
APP_TOKEN = os.environ["FEISHU_APP_TOKEN"]
TABLE_ID = os.environ["FEISHU_TABLE_ID"]
CHAT_ID = os.environ["FEISHU_CHAT_ID"]

COMMIT_MSG = os.environ.get("COMMIT_MESSAGE", "Test Message")
COMMIT_AUTHOR = os.environ.get("COMMIT_AUTHOR", "Test User")
COMMIT_URL = os.environ.get("COMMIT_URL", "http://github.com")

def get_token():
    print(f"🔍 1. 正在尝试登录飞书...")
    print(f"   使用的 App ID: {APP_ID[:5]}****** (检查是否以 cli_ 开头)")
    
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    resp = requests.post(url, json={"app_id": APP_ID, "app_secret": APP_SECRET})
    
    # 【关键】打印飞书返回的具体错误
    print(f"   📩 飞书接口返回: {resp.text}")
    
    if "tenant_access_token" not in resp.json():
        print("❌ 登录失败！请检查 Secrets 里的 APP_ID 和 SECRET 是否正确！")
        return None
    
    print("✅ 登录成功！")
    return resp.json().get("tenant_access_token")

def add_task(token):
    print("📝 2. 正在写入多维表格...")
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    fields = {"任务描述": f"【Code】{COMMIT_MSG} -- {COMMIT_AUTHOR}"}
    
    resp = requests.post(url, headers=headers, json={"fields": fields})
    print(f"   📩 表格接口返回: {resp.text}")

def send_msg(token):
    print("📢 3. 正在发送群消息...")
    url = "https://open.feishu.cn/open-apis/im/v1/messages"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    content = {
        "config": {"wide_screen_mode": True},
        "header": {"template": "blue", "title": {"content": "🚀 代码调试消息", "tag": "plain_text"}},
        "elements": [
            {"tag": "div", "text": {"tag": "lark_md", "content": f"**提交人:** {COMMIT_AUTHOR}\n**状态:** 调试成功"}},
            {"tag": "action", "actions": [{"tag": "button", "text": {"tag": "plain_text", "content": "查看代码"}, "url": COMMIT_URL, "type": "primary"}]}
        ]
    }
    body = {"receive_id": CHAT_ID, "msg_type": "interactive", "content": json.dumps(content)}
    resp = requests.post(url, params={"receive_id_type": "chat_id"}, headers=headers, json=body)
    print(f"   📩 消息接口返回: {resp.text}")

if __name__ == "__main__":
    print("--- 🤖 脚本开始运行 ---")
    token = get_token()
    if token:
        add_task(token)
        send_msg(token)
    else:
        print("--- ❌ 运行因登录失败而终止 ---")
        # 强制报错，让 GitHub 显示红色叉叉
        sys.exit(1)
