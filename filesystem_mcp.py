#!/usr/bin/env python3
from mcp.server.fastmcp import FastMCP
from pathlib import Path
from typing import List, Dict, Any, Optional, Literal
import difflib
import fnmatch
import json
import os
from datetime import datetime


class FileSystemMCPServer:
    def __init__(self, allowed_directories: List[str]):
        self.mcp = FastMCP("FileSystemServer")
        self.allowed_directories = [Path(d).expanduser().resolve() for d in allowed_directories]
        self._validate_directories()
        self._register_tools()

    def _validate_directories(self):
        """Verify all allowed directories exist and are accessible"""
        for dir_path in self.allowed_directories:
            if not dir_path.is_dir():
                raise ValueError(f"{dir_path} is not a directory")

    def _validate_path(self, requested_path: str) -> Path:
        """Ensure a path is within allowed directories"""
        requested = Path(requested_path).expanduser()
        if not requested.is_absolute():
            requested = Path.cwd() / requested

        normalized = requested.resolve()

        # Check if path is within allowed directories
        if not any(str(normalized).startswith(str(allowed))
                   for allowed in self.allowed_directories):
            raise PermissionError(f"Access denied - path outside allowed directories: {requested}")

        return normalized

    def _register_tools(self):
        """Register all filesystem tools with the MCP server"""

        @self.mcp.tool()
        def read_file(path: str) -> str:
            """Read the complete contents of a file"""
            valid_path = self._validate_path(path)
            return valid_path.read_text(encoding='utf-8')

        @self.mcp.tool()
        def read_multiple_files(paths: List[str]) -> Dict[str, str]:
            """Read multiple files simultaneously"""
            results = {}
            for file_path in paths:
                try:
                    valid_path = self._validate_path(file_path)
                    results[file_path] = valid_path.read_text(encoding='utf-8')
                except Exception as e:
                    results[file_path] = f"Error: {str(e)}"
            return results

        @self.mcp.tool()
        def write_file(path: str, content: str) -> str:
            """Write content to a file (overwrites existing)"""
            valid_path = self._validate_path(path)
            valid_path.write_text(content, encoding='utf-8')
            return f"Successfully wrote to {path}"

        @self.mcp.tool()
        def edit_file(path: str, edits: List[Dict[str, str]], dry_run: bool = False) -> str:
            """Make edits to a file with diff output"""
            valid_path = self._validate_path(path)
            original = valid_path.read_text(encoding='utf-8')
            modified = original

            for edit in edits:
                old_text = edit['oldText']
                new_text = edit['newText']

                if old_text in modified:
                    modified = modified.replace(old_text, new_text)
                else:
                    # Try line-by-line matching with whitespace flexibility
                    old_lines = old_text.splitlines()
                    modified_lines = modified.splitlines()
                    match_found = False

                    for i in range(len(modified_lines) - len(old_lines) + 1):
                        window = modified_lines[i:i + len(old_lines)]

                        if all(o.strip() == m.strip() for o, m in zip(old_lines, window)):
                            indent = len(modified_lines[i]) - len(modified_lines[i].lstrip())
                            new_lines = []

                            for j, line in enumerate(new_text.splitlines()):
                                if j == 0:
                                    new_lines.append((' ' * indent) + line.lstrip())
                                else:
                                    new_lines.append(line)

                            modified_lines[i:i + len(old_lines)] = new_lines
                            modified = '\n'.join(modified_lines)
                            match_found = True
                            break

                    if not match_found:
                        raise ValueError(f"Could not find exact match for edit:\n{old_text}")

            # Generate unified diff
            diff = difflib.unified_diff(
                original.splitlines(),
                modified.splitlines(),
                fromfile=str(valid_path),
                tofile=str(valid_path),
                lineterm=''
            )
            diff_output = '\n'.join(diff)

            if not dry_run:
                valid_path.write_text(modified, encoding='utf-8')

            return diff_output

        @self.mcp.tool()
        def create_directory(path: str) -> str:
            """Create directory (and parents if needed)"""
            valid_path = self._validate_path(path)
            valid_path.mkdir(parents=True, exist_ok=True)
            return f"Successfully created directory {path}"

        @self.mcp.tool()
        def list_directory(path: str) -> List[Dict[str, str]]:
            """List directory contents with type info"""
            valid_path = self._validate_path(path)
            return [
                {
                    'name': entry.name,
                    'type': 'directory' if entry.is_dir() else 'file'
                }
                for entry in valid_path.iterdir()
            ]

        @self.mcp.tool()
        def directory_tree(path: str) -> Dict[str, Any]:
            """Generate recursive directory tree"""
            valid_path = self._validate_path(path)

            def build_tree(current_path: Path) -> Dict[str, Any]:
                return {
                    'name': current_path.name,
                    'type': 'directory',
                    'children': [
                        build_tree(entry) if entry.is_dir() else {
                            'name': entry.name,
                            'type': 'file'
                        }
                        for entry in current_path.iterdir()
                    ]
                }

            return build_tree(valid_path)

        @self.mcp.tool()
        def move_file(source: str, destination: str) -> str:
            """Move or rename a file/directory"""
            valid_source = self._validate_path(source)
            valid_dest = self._validate_path(destination)
            valid_source.rename(valid_dest)
            return f"Successfully moved {source} to {destination}"

        @self.mcp.tool()
        def search_files(root_path: str, pattern: str, exclude_patterns: Optional[List[str]] = None) -> List[str]:
            """Recursively search for files matching pattern"""
            if exclude_patterns is None:
                exclude_patterns = []

            valid_root = self._validate_path(root_path)
            results = []

            for entry in valid_root.rglob('*'):
                try:
                    self._validate_path(entry)
                    relative_path = str(entry.relative_to(valid_root))

                    if any(fnmatch.fnmatch(relative_path, pat) for pat in exclude_patterns):
                        continue

                    if pattern.lower() in entry.name.lower():
                        results.append(str(entry))
                except (PermissionError, ValueError):
                    continue

            return results

        @self.mcp.tool()
        def get_file_info(path: str) -> Dict[str, Any]:
            """Get file metadata"""
            valid_path = self._validate_path(path)
            stat = valid_path.stat()

            return {
                'size': stat.st_size,
                'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'accessed': datetime.fromtimestamp(stat.st_atime).isoformat(),
                'isDirectory': valid_path.is_dir(),
                'isFile': valid_path.is_file(),
                'permissions': oct(stat.st_mode)[-3:]
            }

        @self.mcp.tool()
        def list_allowed_directories() -> List[str]:
            """List allowed directories"""
            return [str(d) for d in self.allowed_directories]

    def run(self, transport: Literal["stdio", "sse", "streamable-http"] = "stdio", port: int = None):
        """Run the MCP server"""
        if port:
            self.mcp.settings.port = port
        self.mcp.run(transport=transport)


if __name__ == '__main__':
    # import sys
    #
    # if len(sys.argv) < 2:
    #     print("Usage: mcp-server-filesystem <allowed-directory> [additional-directories...]", file=sys.stderr)
    #     sys.exit(1)
    #
    # server = FileSystemMCPServer(sys.argv[1:])
    server = FileSystemMCPServer(["C:\\Users\\hfhfn\\Desktop\\dify"])
    server.run(transport="sse", port=8888)