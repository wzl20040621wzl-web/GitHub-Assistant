import os
import requests
import json

# 环境变量
APP_ID = os.environ["FEISHU_APP_ID"]
APP_SECRET = os.environ["FEISHU_APP_SECRET"]
APP_TOKEN = os.environ["FEISHU_APP_TOKEN"]
TABLE_ID = os.environ["FEISHU_TABLE_ID"]
CHAT_ID = os.environ["FEISHU_CHAT_ID"]

COMMIT_MSG = os.environ.get("COMMIT_MESSAGE", "Update")
COMMIT_AUTHOR = os.environ.get("COMMIT_AUTHOR", "Unknown")
COMMIT_URL = os.environ.get("COMMIT_URL", "")
REPO_NAME = os.environ.get("GITHUB_REPOSITORY", "")

def get_token():
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    try:
        resp = requests.post(url, json={"app_id": APP_ID, "app_secret": APP_SECRET})
        return resp.json().get("tenant_access_token")
    except:
        return None

def add_task(token):
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    fields = {"任务描述": f"【Code】{COMMIT_MSG} -- {COMMIT_AUTHOR}"}
    requests.post(url, headers=headers, json={"fields": fields})

def send_msg(token):
    url = "https://open.feishu.cn/open-apis/im/v1/messages"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    content = {
        "config": {"wide_screen_mode": True},
        "header": {"template": "blue", "title": {"content": "🚀 代码提交", "tag": "plain_text"}},
        "elements": [
            {"tag": "div", "text": {"tag": "lark_md", "content": f"**提交人:** {COMMIT_AUTHOR}\n**内容:** {COMMIT_MSG}"}},
            {"tag": "action", "actions": [{"tag": "button", "text": {"tag": "plain_text", "content": "查看代码"}, "url": COMMIT_URL, "type": "primary"}]}
        ]
    }
    body = {"receive_id": CHAT_ID, "msg_type": "interactive", "content": json.dumps(content)}
    requests.post(url, params={"receive_id_type": "chat_id"}, headers=headers, json=body)

if __name__ == "__main__":
    token = get_token()
    if token:
        add_task(token)
        send_msg(token)
