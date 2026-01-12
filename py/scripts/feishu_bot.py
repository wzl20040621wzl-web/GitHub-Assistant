import os
import requests
import json
import sys

# 1. 接收 GitHub Secrets
APP_ID = os.environ["FEISHU_APP_ID"]
APP_SECRET = os.environ["FEISHU_APP_SECRET"]
APP_TOKEN = os.environ["FEISHU_APP_TOKEN"]
TABLE_ID = os.environ["FEISHU_TABLE_ID"]
CHAT_ID = os.environ["FEISHU_CHAT_ID"]

# 2. 接收 GitHub 提交信息
COMMIT_MSG = os.environ.get("COMMIT_MESSAGE", "No message")
COMMIT_AUTHOR = os.environ.get("COMMIT_AUTHOR", "Unknown")
COMMIT_URL = os.environ.get("COMMIT_URL", "")
REPO_NAME = os.environ.get("GITHUB_REPOSITORY", "")

def get_token():
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    try:
        resp = requests.post(url, json={"app_id": APP_ID, "app_secret": APP_SECRET})
        if resp.status_code != 200:
            print(f"❌ Token 获取失败: {resp.text}")
            return None
        return resp.json().get("tenant_access_token")
    except Exception as e:
        print(f"❌ 网络请求出错: {e}")
        return None

def add_task(token):
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    # ⚠️ 这里的"任务描述"必须和飞书表格里的字段名一模一样
    fields = {"任务描述": f"【代码提交】{COMMIT_MSG} -- {COMMIT_AUTHOR}"}

    try:
        resp = requests.post(url, headers=headers, json={"fields": fields})
        if resp.status_code == 200:
            print("✅ 已写入多维表格")
        else:
            print(f"❌ 写入表格失败: {resp.text}")
    except Exception as e:
        print(f"❌ 写入表格出错: {e}")

def send_msg(token):
    url = "https://open.feishu.cn/open-apis/im/v1/messages"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    content = {
        "config": {"wide_screen_mode": True},
        "header": {"template": "blue", "title": {"content": "🚀 代码提交通知", "tag": "plain_text"}},
        "elements": [
            {"tag": "div", "text": {"tag": "lark_md", "content": f"**提交人:** {COMMIT_AUTHOR}\n**项目:** {REPO_NAME}"}},
            {"tag": "div", "text": {"tag": "lark_md", "content": f"**内容:** {COMMIT_MSG}"}},
            {"tag": "action", "actions": [{"tag": "button", "text": {"tag": "plain_text", "content": "查看代码详情"}, "url": COMMIT_URL, "type": "primary"}]}
        ]
    }
    body = {"receive_id": CHAT_ID, "msg_type": "interactive", "content": json.dumps(content)}
    try:
        requests.post(url, params={"receive_id_type": "chat_id"}, headers=headers, json=body)
        print("✅ 已发送群通知")
    except Exception as e:
        print(f"❌ 发送消息出错: {e}")

if __name__ == "__main__":
    print("开始运行同步脚本...")
    token = get_token()
    if token:
        add_task(token)
        send_msg(token)