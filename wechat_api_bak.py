import time
import threading
from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
from wxauto import WeChat
import os
import uvicorn

app = FastAPI(title="WeChat Automation Service")
wx = WeChat()


# 消息状态跟踪
class MessageTracker:
    def __init__(self):
        self.last_msg_content = ""
        self.current_chat = None


tracker = MessageTracker()


# 数据模型（严格使用文档参数名）
class SendTextRequest(BaseModel):
    who: str  # 文档指定参数名
    message: str


class SendFileRequest(BaseModel):
    who: str
    filepath: str


# 核心消息功能（严格遵循文档用法）
def get_recent_messages():
    """正确调用GetAllMessage()获取消息"""
    try:
        # 注意：必须加括号调用方法
        messages = wx.GetAllMessage()  # 返回最后20条消息

        if not messages:
            return None

        # 文档说明：每条消息格式为 (sender, content, time)
        latest_msg = messages[-1]

        # 简单去重（可根据需要改为msg_id = f"{sender}_{time}"）
        if latest_msg[1] != tracker.last_msg_content:
            tracker.last_msg_content = latest_msg[1]
            return {
                "who": latest_msg[0],
                "message": latest_msg[1],
                "time": latest_msg[2]
            }
        return None
    except Exception as e:
        print(f"[ERROR] 获取消息失败（正确用法）: {e}")
        return None


def switch_to_chat(who: str):
    """切换聊天窗口（文档标准做法）"""
    if who != tracker.current_chat:
        wx.ChatWith(who)  # 先切换到目标聊天
        tracker.current_chat = who
        time.sleep(0.3)  # 等待窗口切换完成


# 消息监听服务
def message_monitor():
    while True:
        try:
            msg = get_recent_messages()
            if msg:
                handle_message(msg)
        except Exception as e:
            print(f"[ERROR] 监听服务异常: {e}")
        time.sleep(1)


def handle_message(msg: dict):
    """处理消息（示例逻辑）"""
    print(f"新消息来自 {msg['who']}: {msg['message']}")

    # 示例回复逻辑
    reply = None
    content = msg["message"].lower()

    if "hello" in content or "你好" in content:
        reply = f"{msg['who']}你好！我是自动回复"
    elif "时间" in content:
        reply = time.strftime("现在是%H:%M:%S")

    if reply:
        send_text(msg["who"], reply)


# 文档标准消息发送
def send_text(who: str, message: str):
    try:
        switch_to_chat(who)
        wx.SendMsg(message)  # 文档标准发送方法
        print(f"已回复 {who}: {message}")
    except Exception as e:
        print(f"[ERROR] 发送失败: {e}")


def send_file(who: str, filepath: str):
    try:
        switch_to_chat(who)
        wx.SendFiles(filepath)  # 文档标准文件发送
    except Exception as e:
        print(f"[ERROR] 文件发送失败: {e}")


# FastAPI接口
@app.post("/send/text")
async def api_send_text(req: SendTextRequest):
    """文档标准文本接口"""
    try:
        send_text(req.who, req.message)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(500, str(e))
@app.post("/send/file")


async def api_send_file(req: SendFileRequest):
    """文档标准文件接口"""
    try:
        if not os.path.exists(req.filepath):
            raise HTTPException(404, "文件不存在")
        send_file(req.who, req.filepath)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(500, str(e))


@app.post("/upload")
async def api_upload(who: str, file: UploadFile = File(...)):
    """上传+发送文件"""
    try:
        save_path = f"./uploads/{file.filename}"
        with open(save_path, "wb") as f:
            f.write(await file.read())

        send_file(who, save_path)
        return {"status": "success", "saved_path": save_path}
    except Exception as e:
        raise HTTPException(500, str(e))


if __name__ == "__main__":
    # 初始化
    os.makedirs("./uploads", exist_ok=True)

    # 启动监听线程
    threading.Thread(
        target=message_monitor,
        daemon=True,
        name="WeChatListener"
    ).start()

    # 启动服务
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8888,
        log_level="info"
    )