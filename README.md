#### 使用uv管理python环境
- uv启动mcp服务的python脚本
```python
uv run --with mcp[cli] mcp run path/to/mcp.py
```
- uvx启动mcp服务的python脚本
```python
uvx --with pillow --with mcp[cli] fastmcp run path/to/mcp.py
```