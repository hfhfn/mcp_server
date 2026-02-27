# server.py
from mcp.server.fastmcp import FastMCP

# 步骤 1: 创建一个名为 "Demo" 的 MCP 服务器实例
mcp = FastMCP("Demo")


# 步骤 2: 添加一个加法工具工具
# @mcp.tool() 装饰器将普通 Python 函数转换为可供 LLM 调用的工具
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""  # 这里的 Docstring 会被 LLM 读取，帮助它理解工具用途
    return a + b


# 步骤 3: 添加一个动态欢迎语资源
# 资源允许 LLM 读取特定的数据，支持带参数的 URI 格式
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"


# 步骤 4: 独立运行配置（用于调试）
if __name__ == '__main__':
    # 设置 SSE 服务端口
    mcp.settings.port = 8880
    # 以 SSE 传输协议启动服务
    mcp.run(transport="sse")
    # 以标准输入输出协议启动服务
    # mcp.run("stdio")
