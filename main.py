
import uvicorn
from starlette.applications import Starlette
from starlette.routing import Mount
import math_mcp, thumbnail_mcp, weather_mcp, filesystem_mcp


server = filesystem_mcp.FileSystemMCPServer(["C:\\Users\\hfhfn\\Desktop\\dify"])

math_mcp.mcp.settings.mount_path = "/math"
thumbnail_mcp.mcp.settings.mount_path = "/thumbnail"
weather_mcp.mcp.settings.mount_path = "/weather"
server.mcp.settings.mount_path = "/file"
# thumbnail_mcp.mcp.settings.streamable_http_path = "/mcp"
# math_mcp.mcp.settings.streamable_http_path = "/math"

# Create Starlette app with multiple mounted servers
app = Starlette(
    routes=[
        # # Using settings-based configuration
        # Mount("/math", app=math_mcp.mcp.streamable_http_app()),
        # Mount("/thumbnail", app=thumbnail_mcp.mcp.streamable_http_app()),
        # Mount("/weather", app=weather_mcp.mcp.streamable_http_app()),
        Mount("/math", app=math_mcp.mcp.sse_app()),
        Mount("/thumbnail", app=thumbnail_mcp.mcp.sse_app()),
        Mount("/weather", app=weather_mcp.mcp.sse_app()),
        Mount("/file", app=server.mcp.sse_app()),
    ]
)

# Method 3: For direct execution, you can also pass the mount path to run()
if __name__ == "__main__":
    # weather_mcp.mcp.settings.port = 8888
    # weather_mcp.mcp.run(transport="sse", mount_path="/search")
    uvicorn.run(app, host="0.0.0.0", port=8888)