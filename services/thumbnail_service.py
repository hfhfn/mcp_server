from starlette.responses import Response
from io import BytesIO
import requests
from PIL import Image as PILImage
from mcp.server.fastmcp import FastMCP, Image

# 步骤 1: 创建 MCP 服务器实例，名为 "My App"
mcp = FastMCP("My App")


# 步骤 2: 定义缩略图生成工具
@mcp.tool()
def create_thumbnail(image_path: str) -> Response:
    """Create a thumbnail from an image and return it as a Starlette Response"""
    
    # 步骤 3: 获取图像数据 (支持网络 URL 和本地路径)
    if image_path.startswith("http://") or image_path.startswith("https://"):
        response = requests.get(image_path)
        img = PILImage.open(BytesIO(response.content))
    else:
        img = PILImage.open(image_path)

    # 步骤 4: 调整图像尺寸，保持纵横比
    img.thumbnail((100, 100))

    # 步骤 5: 将 PIL 图像对象转换为字节流 (PNG 格式)
    img_bytes = BytesIO()
    img.save(img_bytes, format="PNG")
    img_bytes.seek(0)

    # 步骤 6: 返回 Starlette Response，包含二进制图像数据和相应的 MIME 类型
    # return Image(data=img_bytes.getvalue(), format="png")
    # Return a Starlette Response with the binary image data
    return Response(
        content=img_bytes.getvalue(),
        media_type="image/png",
        headers={"Content-Disposition": "inline; filename=thumbnail.png"}
    )


# 下面是备用的实现示例 (已注释)
# @mcp.tool()
# def create_thumbnail(image_path: str):
#     """Create a thumbnail from an image"""
#     if image_path.startswith("http://") or image_path.startswith("https://"):
#         response = requests.get(image_path)
#         img = PILImage.open(BytesIO(response.content))
#     else:
#         img = PILImage.open(image_path)
#     img.thumbnail((100, 100))
#
#     # return Image(data=img.tobytes(), format="png")
#     image = Image(data=img.tobytes(), format="png")
#     return Response(
#         content=image.data,
#         media_type=image._mime_type
#     )
