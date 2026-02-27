import asyncio
import os
from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from dotenv import load_dotenv

load_dotenv()

# === 1) 配置 DeepSeek 模型 ===
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "sk-a3a79242b87a45")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")

model = ChatOpenAI(
    base_url=DEEPSEEK_BASE_URL,
    api_key=DEEPSEEK_API_KEY,
    model="deepseek-chat",
)

async def main():
    print("--- 正在连接 MCP 聚合服务器 ---")
    
    # 3) 连接到聚合服务的 SSE 多个端点
    # 注意：这里我们可以一次性连接多个端点
    client = MultiServerMCPClient(
        {
            "math": {"url": "http://127.0.0.1:8888/math/sse", "transport": "sse"},
            "weather": {"url": "http://127.0.0.1:8888/weather/sse", "transport": "sse"},
            "file": {"url": "http://127.0.0.1:8888/file/sse", "transport": "sse"},
            "news": {"url": "http://127.0.0.1:8888/newsnow/sse", "transport": "sse"},
            "love": {"url": "http://127.0.0.1:8888/love/sse", "transport": "sse"},
        }
    )

    # 4) 获取所有工具并交给 Agent
    try:
        tools = await client.get_tools()
        print(f"成功获取工具: {[tool.name for tool in tools]}")
    except Exception as e:
        print(f"获取工具失败 (请确保 main.py 已启动): {e}")
        return

    agent = create_react_agent(model, tools)

    print("\n--- MCP 交互终端 (输入 'q' 退出) ---")
    while True:
        my_input = input("请输入指令 (例如: '帮我写封情书给小美并发送到 test@qq.com'): ")
        if my_input.lower() == "q":
            break
        
        try:
            # 使用流式或同步调用
            out = await agent.ainvoke({"messages": [{"role": "user", "content": my_input}]})
            print("\n[AI]:", out['messages'][-1].content)
            print("-" * 50)
        except Exception as e:
            print(f"执行出错: {e}")

if __name__ == "__main__":
    asyncio.run(main())
