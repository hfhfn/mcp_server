from mcp.server.fastmcp import FastMCP
from wxauto import WeChat

# Initialize FastMCP server
mcp = FastMCP(port=8888)  # 默认8000
wx = WeChat()


@mcp.tool()
async def send_wechat_msg(msg: str, who: str=None) -> str:
    """send wechat text message"""
    wx.ChatWith(who)
    wx.SendMsg(msg, who)
    return "success"


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport="sse")