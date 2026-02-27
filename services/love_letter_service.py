from mcp.server.fastmcp import FastMCP
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 创建一个 FastMCP 实例
mcp = FastMCP("LoveLetterService")

# ========== 1) 配置 LLM ==========
# 优先从环境变量读取，否则使用提供的默认值
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "sk-a3a7924")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")

llm = ChatOpenAI(
    model="deepseek-chat",
    base_url=DEEPSEEK_BASE_URL,
    api_key=DEEPSEEK_API_KEY
)

@mcp.tool()
def write_love_letter(name: str) -> str:
    """
    写情书的工具，调用该工具可以根据对方名字生成一封深情的情书。
    :param name: 对方的名字
    :return: 情书内容
    """
    print(f"正在为 {name} 创作情书...")
    messages = [
        SystemMessage(content=(
            "你是一位深情的中文情书作家，擅长用优美典雅的中文表达真挚的情感。"
            "请遵循以下创作原则："
            "1. 使用纯中文写作，避免使用任何英文单词或短语"
            "2. 情感真挚自然，避免陈词滥调"
            "3. 融入诗意的比喻和生动的意象"
            "4. 根据收信人名字个性化内容"
            "5. 保持适当的长度（约150-200字）"
            "6. 结尾要有合适的落款格式"
            "7. 语气温柔深情，含蓄而动人"
            "8. 结构完整：开头问候、主体情感表达、结尾承诺"
        )),
        HumanMessage(content=f"写一封情书给{name}，内容核心是：我爱你，你是我心中的唯一。")
    ]

    try:
        response = llm.invoke(messages).content.strip()
        return response
    except Exception as e:
        return f"书写失败: {str(e)}"

@mcp.tool()
def send_love_email(receiver_email: str, subject: str, message: str):
    """
    通过邮件发送内容的工具。
    :param receiver_email: 邮件接收者邮箱 (如: example@qq.com)
    :param subject: 邮件主题
    :param message: 邮件内容
    :return: 发送状态描述
    """
    print(f"正在向 {receiver_email} 发送内容...")

    # 邮箱配置 (优先从环境变量读取)
    sender_email = os.getenv("SENDER_EMAIL", "1074@qq.com")
    sender_password = os.getenv("SENDER_PASSWORD", "lxppti") # 注意：这里通常应是授权码

    # 设置邮件内容
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'plain'))

    try:
        smtp_server = "smtp.qq.com"
        smtp_port = 465  # 使用 SSL 加密

        # 建立与 SMTP 服务器的连接并登录
        server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        server.login(sender_email, sender_password)

        # 发送邮件
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        return "邮件发送成功!"

    except Exception as e:
        return f"邮件发送失败: {str(e)}"

if __name__ == "__main__":
    # 以 SSE 模式独立运行
    mcp.run("sse")
