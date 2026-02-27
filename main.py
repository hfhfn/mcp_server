import uvicorn
import logging
from starlette.applications import Starlette
from starlette.routing import Mount
from services import math_service, thumbnail_service, weather_service, filesystem_service, newsnow_service, love_letter_service

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-aggregator")

# 步骤 1: 初始化文件系统服务 (带目录白名单)
fs_server = filesystem_service.FileSystemMCPServer(["C:\\Users\\hfhfn\\Desktop\\mcp_server"])

# 步骤 2: 为各个模块配置挂载路径
math_service.mcp.settings.mount_path = "/math"
thumbnail_service.mcp.settings.mount_path = "/thumbnail"
weather_service.mcp.settings.mount_path = "/weather"
fs_server.mcp.settings.mount_path = "/file"
newsnow_service.app.settings.mount_path = "/newsnow"
love_letter_service.mcp.settings.mount_path = "/love"

# 步骤 3: 创建聚合的 Starlette 应用
app = Starlette(
    routes=[
        # # 使用基于设置的配置 (注释备用)
        # Mount("/math", app=math_mcp.mcp.streamable_http_app()),
        # Mount("/thumbnail", app=thumbnail_mcp.mcp.streamable_http_app()),
        # Mount("/weather", app=weather_mcp.mcp.streamable_http_app()),
        
        # 挂载各个服务的 SSE 端点
        Mount("/math", app=math_service.mcp.sse_app()),
        Mount("/thumbnail", app=thumbnail_service.mcp.sse_app()),
        Mount("/weather", app=weather_service.mcp.sse_app()),
        Mount("/file", app=fs_server.mcp.sse_app()),
        Mount("/newsnow", app=newsnow_service.app.sse_app()),
        Mount("/love", app=love_letter_service.mcp.sse_app()),
    ]
)

# 步骤 4: 程序运行入口
if __name__ == "__main__":
    # 也可以在运行脚本时直接传递挂载路径 (注释备用示例)
    # weather_mcp.mcp.settings.port = 8888
    # weather_mcp.mcp.run(transport="sse", mount_path="/search")
    
    # 启动应用，监听所有网卡 (0.0.0.0)，通过 8888 端口对外提供服务
    uvicorn.run(app, host="0.0.0.0", port=8888)