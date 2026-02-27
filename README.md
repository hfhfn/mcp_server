### 使用uv管理python环境

- uv启动mcp服务的python脚本

```shell
uv run --with mcp[cli] mcp run path/to/mcp.py
```

- uvx启动mcp服务的python脚本

```shell
uvx --with pillow --with mcp[cli] fastmcp run path/to/mcp.py
```

### 启动单个mcp服务 sse和streamable-http两种模式的URL路径

```shell
# sse 模式
http://127.0.0.1:8000/sse  # 默认8000端口
http://host.docker.internal:8000/sse  # docker容器内访问
# streamable-http 模式
http://127.0.0.1:8000/mcp  # 默认8000端口
http://host.docker.internal:8000/mcp  # docker容器内访问
```

### 使用mcp工具的多种基本配置示例参考：

```json5
// 涉及3种模式：stdio，sse，streamable_http
{
  // streamable_http模式
  "mcpServers": {
    "math": {
      "transport": "streamable_http",
      "url": "http://127.0.0.1:8000/mcp"
    },
    // sse模式
    "weather": {
      "transport": "sse",
      "url": "http://127.0.0.1:8000/sse"
    },
    "12306-mcp": {
      "type": "sse",
      "url": "https://mcp.api-inference.modelscope.cn/sse/76ee2dbba8d74f"
    },
    "sequentialthinking": {
      "headers": {
        "Accept": "application/json, text/event-stream",
        "Authorization": "Bearer 0e51a8cd-e77f-072ec3f3d161"
      },
      "url": "https://mcp.api-inference.modelscope.cn/sse/bb19488b5bc049"
    },
    // 本地服务 stdio模式
    "quickchart-server": {
      "isActive": true,
      "command": "cmd",
      "args": [
        "/c",
        "npx",
        "-y",
        "@gongrzhe/quickchart-mcp-server"
      ],
      "name": "quickchart-server"
    },
    "excel-mcp-server": {
      "isActive": true,
      "command": "cmd",
      "args": [
        "/c",
        "npx",
        "--yes",
        "@zhiweixu/excel-mcp-server"
      ],
      "env": {
        "LOG_PATH": "C:\\Users\\username\\Desktop\\temp",
        "CACHE_MAX_AGE": "1",
        "CACHE_CLEANUP_INTERVAL": "4",
        "LOG_RETENTION_DAYS": "7",
        "LOG_CLEANUP_INTERVAL": "24"
      },
      "name": "excel-mcp-server"
    }
  }
}
```
---

### STDIO 模式启动说明

如果需要在客户端以 **stdio** 模式启动本项目：

1.  **环境准备**：
    在项目根目录下运行以下命令，安装 MCP 命令行工具：

```bash
uv add "mcp[cli]"
```

2.  **启动配置**：
    在配置客户端时，使用 `uv` 作为命令，并配合 `--directory` 参数指定项目路径。
    - **命令**: `uv`
    - **参数**: `["--directory", "/Users/hfhfn/charmProjects/mcp_server/", "run", "main.py"]`
