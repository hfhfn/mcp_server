import asyncio
from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent

# 1) 初始化大模型 (示例使用 DeepSeek)
model = ChatOpenAI(model="deepseek-chat",
                   openai_api_base="https://api.deepseek.com",
                   openai_api_key="sk-你的KEY")

async def get_agent(transport_type="stdio"):
    """
    获取 Agent，支持三种传输方式: stdio, sse, streamable_http
    """
    
    if transport_type == "stdio":
        # STDIO 模式启动参数
        args = ["--directory", "/Users/hfhfn/charmProjects/mcp_server/", "run", "main.py"]
        config = {
            "demo": {
                "command": "uv",
                "args": args,
                "transport": "stdio",
            }
        }
    elif transport_type == "sse":
        # SSE 模式建议配置 (需先启动 main.py)
        config = {
            "demo": {
                "url": "http://127.0.0.1:8888/math/sse",
                "transport": "sse",
            }
        }
    elif transport_type == "streamable_http":
        # Streamable HTTP 模式建议配置 (需先启动 main.py)
        config = {
            "demo": {
                "url": "http://127.0.0.1:8888/math/mcp",
                "transport": "streamable_http",
            }
        }
    else:
        raise ValueError(f"不支持的传输类型: {transport_type}")

    # 连接 MCP 服务器
    client = MultiServerMCPClient(config)

    # 获取工具列表
    tools = await client.get_tools()
    print(f"[{transport_type}] 可用工具:", [tool.name for tool in tools])

    # 创建 React Agent
    agent = create_react_agent(model, tools)
    return agent

async def run_mcp(user_input, transport_type="stdio"):
    agent = await get_agent(transport_type)
    result_content = ""
    async for state in agent.astream(input={"messages": [{"role": "user", "content": user_input}]},
                                     stream_mode="values"):

        msg = state["messages"][-1]
        role = msg.type
        content = msg.content
        print(f"{role}: {content}")

        if hasattr(msg, 'tool_calls'):
            for tool_call in msg.tool_calls:
                print("调用的函数：", tool_call["name"])
                print("函数参数：", tool_call["args"])

        result_content = content
        print("*" * 100, "\n\n")
    return result_content

if __name__ == '__main__':
    user_query = "我买了3个鸡蛋，又买了5个鸡蛋，又买了7个鸡蛋，一共买了多少个鸡蛋？"
    
    # 演示 stdio 模式调用 (默认)
    print("--- 正在使用 stdio 模式运行 ---")
    print(asyncio.run(run_mcp(user_query, transport_type="stdio")))
    
    # 注意：sse 和 streamable_http 模式需要主服务器已在 8888 端口运行
    # print("--- 正在使用 sse 模式运行 ---")
    # asyncio.run(run_mcp(user_query, transport_type="sse"))
