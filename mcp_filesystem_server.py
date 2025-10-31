#!/usr/bin/env python3
"""
🏴 MCP Filesystem Server for Sovereign Shadow
Provides file system access for Claude Desktop
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp import types
except ImportError:
    print("Error: mcp package not installed. Run: pip install mcp", file=sys.stderr)
    sys.exit(1)

# Initialize MCP server
app = Server("sovereign-shadow-filesystem")

@app.list_tools()
async def list_tools() -> List[types.Tool]:
    """List available filesystem tools"""
    return [
        types.Tool(
            name="read_file",
            description="Read contents of a file",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the file to read"
                    }
                },
                "required": ["file_path"]
            }
        ),
        types.Tool(
            name="write_file",
            description="Write contents to a file",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the file to write"
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to write to the file"
                    }
                },
                "required": ["file_path", "content"]
            }
        ),
        types.Tool(
            name="list_directory",
            description="List contents of a directory",
            inputSchema={
                "type": "object",
                "properties": {
                    "directory_path": {
                        "type": "string",
                        "description": "Path to the directory to list"
                    }
                },
                "required": ["directory_path"]
            }
        ),
        types.Tool(
            name="create_directory",
            description="Create a new directory",
            inputSchema={
                "type": "object",
                "properties": {
                    "directory_path": {
                        "type": "string",
                        "description": "Path of the directory to create"
                    }
                },
                "required": ["directory_path"]
            }
        ),
        types.Tool(
            name="delete_file",
            description="Delete a file",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the file to delete"
                    }
                },
                "required": ["file_path"]
            }
        ),
        types.Tool(
            name="get_file_info",
            description="Get information about a file or directory",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the file or directory"
                    }
                },
                "required": ["path"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: Any) -> List[types.TextContent]:
    """Handle filesystem tool calls"""
    
    if name == "read_file":
        file_path = arguments.get("file_path")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            result = {
                "status": "success",
                "file_path": file_path,
                "content": content,
                "size": len(content)
            }
        except Exception as e:
            result = {
                "status": "error",
                "file_path": file_path,
                "error": str(e)
            }
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "write_file":
        file_path = arguments.get("file_path")
        content = arguments.get("content")
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            result = {
                "status": "success",
                "file_path": file_path,
                "size": len(content)
            }
        except Exception as e:
            result = {
                "status": "error",
                "file_path": file_path,
                "error": str(e)
            }
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "list_directory":
        directory_path = arguments.get("directory_path")
        try:
            items = []
            for item in os.listdir(directory_path):
                item_path = os.path.join(directory_path, item)
                is_dir = os.path.isdir(item_path)
                size = os.path.getsize(item_path) if not is_dir else None
                items.append({
                    "name": item,
                    "type": "directory" if is_dir else "file",
                    "size": size
                })
            result = {
                "status": "success",
                "directory_path": directory_path,
                "items": items
            }
        except Exception as e:
            result = {
                "status": "error",
                "directory_path": directory_path,
                "error": str(e)
            }
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "create_directory":
        directory_path = arguments.get("directory_path")
        try:
            os.makedirs(directory_path, exist_ok=True)
            result = {
                "status": "success",
                "directory_path": directory_path,
                "created": True
            }
        except Exception as e:
            result = {
                "status": "error",
                "directory_path": directory_path,
                "error": str(e)
            }
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "delete_file":
        file_path = arguments.get("file_path")
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                result = {
                    "status": "success",
                    "file_path": file_path,
                    "deleted": True
                }
            else:
                result = {
                    "status": "error",
                    "file_path": file_path,
                    "error": "File not found"
                }
        except Exception as e:
            result = {
                "status": "error",
                "file_path": file_path,
                "error": str(e)
            }
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "get_file_info":
        path = arguments.get("path")
        try:
            if os.path.exists(path):
                stat = os.stat(path)
                result = {
                    "status": "success",
                    "path": path,
                    "exists": True,
                    "is_file": os.path.isfile(path),
                    "is_directory": os.path.isdir(path),
                    "size": stat.st_size,
                    "modified": stat.st_mtime
                }
            else:
                result = {
                    "status": "error",
                    "path": path,
                    "error": "Path not found"
                }
        except Exception as e:
            result = {
                "status": "error",
                "path": path,
                "error": str(e)
            }
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
    
    else:
        return [types.TextContent(type="text", text=f"Unknown tool: {name}")]

async def main():
    """Run the MCP filesystem server"""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())

