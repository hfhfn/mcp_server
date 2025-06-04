import asyncio
import uvicorn # uvicorn might not be strictly needed if fastmcp handles its own serving via app.run
import httpx
from fastmcp import FastMCP, Context # Changed imports for FastMCP and Context

# 1. Define your MCP application
app = FastMCP(
    name="NewsNowMcpService",
    instructions="A simple MCP service using FastMcp and SSE transport that can fetch news. Version 0.1.0."
)


@app.prompt(
    name="guide_get_hotest_latest_news",
    description="Provides instructions and a list of valid source IDs for the get_hotest_latest_news tool."
)
async def get_news_tool_usage_prompt(context: Context) -> str:
    """
    Provides guidance to an LLM on how to correctly use the
    'get_hotest_latest_news' tool, including a list of valid source IDs.
    """
    # This multi-line string contains the pre-formatted list of IDs.
    # Ensure this block is correctly indented in the actual file.
    id_list_str = '''
            v2ex-share (V2EX - 最新分享)
            zhihu (知乎)
            weibo (微博 - 实时热搜)
            zaobao (联合早报)
            coolapk (酷安 - 今日最热)
            wallstreetcn-quick (华尔街见闻 - 实时快讯)
            wallstreetcn-news (华尔街见闻 - 最新资讯)
            wallstreetcn-hot (华尔街见闻 - 最热文章)
            36kr-quick (36氪 - 快讯)
            douyin (抖音)
            hupu (虎扑 - 主干道热帖)
            tieba (百度贴吧 - 热议)
            toutiao (今日头条)
            ithome (IT之家)
            thepaper (澎湃新闻 - 热榜)
            sputniknewscn (卫星通讯社)
            cankaoxiaoxi (参考消息)
            pcbeta-windows11 (远景论坛 - Windows 11)
            pcbeta-windows (远景论坛 - Windows 资源)
            cls-telegraph (财联社 - 电报)
            cls-depth (财联社 - 深度)
            cls-hot (财联社 - 热门)
            xueqiu-hotstock (雪球 - 热门股票)
            gelonghui (格隆汇 - 事件)
            fastbull-express (法布财经 - 快讯)
            fastbull-news (法布财经 - 头条)
            solidot (Solidot)
            hackernews (Hacker News)
            producthunt (Product Hunt)
            github-trending-today (Github - Today)
            bilibili-hot-search (哔哩哔哩 - 热搜)
            bilibili-hot-video (哔哩哔哩 - 热门视频)
            bilibili-ranking (哔哩哔哩 - 排行榜)
            kuaishou (快手)
            kaopu (靠谱新闻)
            jin10 (金十数据)
            baidu (百度热搜)
            linuxdo-latest (LINUX DO - 最新)
            linuxdo-hot (LINUX DO - 今日最热)
            ghxi (果核剥壳)
            smzdm (什么值得买)
            nowcoder (牛客)
            sspai (少数派)
            juejin (稀土掘金)
            ifeng (凤凰网 - 热点资讯)
            chongbuluo-latest (虫部落 - 最新)
            chongbuluo-hot (虫部落 - 最热)
            '''.strip() # strip() to manage whitespace from the triple-quote block

    prompt_message = f"""
        You can use the 'get_hotest_latest_news' tool to fetch news articles.
        This tool requires a specific 'id' for the news source and optionally accepts a 'count' for the number of articles (default is 10).
        
        To use this tool, you MUST choose an 'id' from the following list of valid news sources:
        {id_list_str}
        
        When calling the tool, provide the chosen 'id' and, if desired, a 'count'.
        For example, to get 5 news items from Zhihu, you would specify:
        Tool Name: get_hotest_latest_news
        Inputs:
          id: "zhihu"
          count: 5
        
        Please select an 'id' from the list above and specify it correctly when you request to call the 'get_hotest_latest_news' tool.
        """
    return prompt_message.strip()

# 2. Define the get_hotest_latest_news tool
@app.tool(
    name="get_hotest_latest_news",
    description="Gets hottest or latest news from a specified source by id. Fetches data from an internal API."
)
async def get_hotest_latest_news_tool(context: Context, id: str, count: int = 10) -> dict: # Changed ToolContext to Context
    """Fetches the hottest or latest news items for a given source ID.

    This tool queries an internal API to retrieve news data based on the
    provided source identifier and desired count.

    Args:
        context: The MCP Context, providing access to logging and other features.
        id: The unique identifier for the news source. Examples include:
            v2ex-share (V2EX - 最新分享)
            zhihu (知乎)
            weibo (微博 - 实时热搜)
            zaobao (联合早报)
            coolapk (酷安 - 今日最热)
            wallstreetcn-quick (华尔街见闻 - 实时快讯)
            wallstreetcn-news (华尔街见闻 - 最新资讯)
            wallstreetcn-hot (华尔街见闻 - 最热文章)
            36kr-quick (36氪 - 快讯)
            douyin (抖音)
            hupu (虎扑 - 主干道热帖)
            tieba (百度贴吧 - 热议)
            toutiao (今日头条)
            ithome (IT之家)
            thepaper (澎湃新闻 - 热榜)
            sputniknewscn (卫星通讯社)
            cankaoxiaoxi (参考消息)
            pcbeta-windows11 (远景论坛 - Windows 11)
            pcbeta-windows (远景论坛 - Windows 资源)
            cls-telegraph (财联社 - 电报)
            cls-depth (财联社 - 深度)
            cls-hot (财联社 - 热门)
            xueqiu-hotstock (雪球 - 热门股票)
            gelonghui (格隆汇 - 事件)
            fastbull-express (法布财经 - 快讯)
            fastbull-news (法布财经 - 头条)
            solidot (Solidot)
            hackernews (Hacker News)
            producthunt (Product Hunt)
            github-trending-today (Github - Today)
            bilibili-hot-search (哔哩哔哩 - 热搜)
            bilibili-hot-video (哔哩哔哩 - 热门视频)
            bilibili-ranking (哔哩哔哩 - 排行榜)
            kuaishou (快手)
            kaopu (靠谱新闻)
            jin10 (金十数据)
            baidu (百度热搜)
            linuxdo-latest (LINUX DO - 最新)
            linuxdo-hot (LINUX DO - 今日最热)
            ghxi (果核剥壳)
            smzdm (什么值得买)
            nowcoder (牛客)
            sspai (少数派)
            juejin (稀土掘金)
            ifeng (凤凰网 - 热点资讯)
            chongbuluo-latest (虫部落 - 最新)
            chongbuluo-hot (虫部落 - 最热)
        count: The maximum number of news items to return. Defaults to 10.

    Returns:
        A dictionary containing a list of news items under the 'content' key,
        or an 'error' key if fetching fails. Each news item is a dictionary
        with 'type': 'text' and 'text': '[Title](URL)'.
    """
    if not isinstance(count, int) or count <= 0:
        print(f"Invalid count '{count}' received, defaulting to 10.")
        count = 10

    # Port 4444 is the Node.js service internal port as per instructions
    # url = f"http://localhost:4444/api/s?id={id}&count={count}"
    url = f"https://newsnow.busiyi.world/api/s?id={id}&count={count}"


    print(f"Executing get_hotest_latest_news_tool: Fetching news from: {url}")

    try:
        async with httpx.AsyncClient() as client:
            # Standard timeout for the request
            response = await client.get(url, timeout=10.0)
            # Raise an exception for HTTP 4xx or 5xx status codes
            response.raise_for_status()

            data = response.json()

            # Validate the structure of the data received from the API
            if not isinstance(data, dict) or "items" not in data or not isinstance(data["items"], list):
                print(f"Unexpected data format from upstream API. URL: {url}, Data: {data}")
                # Return a structured error that MCP can understand
                return {"error": {"message": "Unexpected data format from upstream API."}}

            news_items_content = []
            for item in data.get("items", []):
                # Ensure each item is a dictionary and has title and url
                if isinstance(item, dict) and "title" in item and "url" in item:
                    news_items_content.append({
                        "type": "text", # Conforming to TextContent structure
                        "text": f"[{item.get('title', 'N/A')}]({item.get('url', '#')})"
                    })
                else:
                    # Log if an item is malformed but continue processing others
                    print(f"Skipping malformed news item: {item}")

            # Return the list of TextContent objects as the 'content' field of the CallToolResult
            return {"content": news_items_content}

    except httpx.HTTPStatusError as e:
        # Handle HTTP errors from the upstream API (e.g., 404, 500)
        print(f"HTTP error occurred while fetching news from {url}: {e.response.status_code} - {e.response.text}")
        return {"error": {"message": f"Upstream API error: Status {e.response.status_code}"}}
    except httpx.RequestError as e:
        # Handle network errors (e.g., connection refused, timeout)
        print(f"Request error occurred while fetching news from {url}: {e}")
        return {"error": {"message": f"Failed to connect to upstream API: {type(e).__name__}"}}
    except Exception as e:
        # Catch any other unexpected errors
        print(f"An unexpected error occurred in get_hotest_latest_news_tool: {e}")
        import traceback
        traceback.print_exc()
        return {"error": {"message": "An internal error occurred while processing the news request."}}

# 3. Main function to start the server
async def main():
    # SSETransport instantiation is removed.
    # app.serve(transport, ...) is changed to app.run(transport="sse", ...)

    print("Starting FastMCP Server (SSE)...") # Updated print message

    # FastMCP's run method is used with transport specified as an argument
    await app.run_async(transport="sse", host="0.0.0.0",
                        port=8888)  # Changed to run_async
    print("FastMCP Server (SSE) is running on http://0.0.0.0:8888") # Updated print message

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Server shutting down gracefully.")
    except Exception as e:
        # Basic error logging to stdout
        print(f"An error occurred during server execution: {e}")
        # In a real application, you might use a more robust logging framework here.
        import traceback
        traceback.print_exc()