from starlette.responses import Response
from io import BytesIO
import requests
from PIL import Image as PILImage
from mcp.server.fastmcp import FastMCP, Image

mcp = FastMCP("My App")


@mcp.tool()
def create_thumbnail(image_path: str) -> Response:
    """Create a thumbnail from an image and return it as a Starlette Response"""
    if image_path.startswith("http://") or image_path.startswith("https://"):
        response = requests.get(image_path)
        img = PILImage.open(BytesIO(response.content))
    else:
        img = PILImage.open(image_path)

    img.thumbnail((100, 100))

    # Convert PIL Image to bytes
    img_bytes = BytesIO()
    img.save(img_bytes, format="PNG")
    img_bytes.seek(0)

    # return Image(data=img_bytes.getvalue(), format="png")
    # Return a Starlette Response with the binary image data
    return Response(
        content=img_bytes.getvalue(),
        media_type="image/png",
        headers={"Content-Disposition": "inline; filename=thumbnail.png"}
    )


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
