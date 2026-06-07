"""
MCP 服务器 - 将 tools.py 中的 Function Calling 工具暴露给 VS Code Copilot

启动方式:
    python mcp_server.py

配置 VS Code (settings.json):
    "github.copilot.mcp.agent": {
        "servers": {
            "aitools": {
                "command": "python",
                "args": ["e:\\Docs\\Aitools\\mcp_server.py"]
            }
        }
    }
"""

import json
import sys
import os
from typing import Any, Dict

# 确保能找到 tools.py
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

from tools import registry

# 创建 MCP 服务器实例
server = Server("aitools")


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """列出所有可用工具"""
    return [
        types.Tool(
            name="save_data_to_log",
            description="将指定的数据保存到本地日志文件中，用于记录模型调用过程中的关键信息",
            inputSchema={
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "数据分类，如 'user_input', 'model_response', 'system_event' 等"
                    },
                    "data": {
                        "type": "object",
                        "description": "要保存的数据内容，可以是任意键值对"
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high"],
                        "description": "数据优先级，默认为 medium"
                    }
                },
                "required": ["category", "data"]
            }
        ),
        types.Tool(
            name="query_logs",
            description="查询已保存的日志数据，支持按分类筛选",
            inputSchema={
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "要查询的数据分类，如果不指定则查询所有"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "返回记录的数量限制，默认为 10"
                    }
                },
                "required": []
            }
        ),
        types.Tool(
            name="get_test_statistics",
            description="获取工具调用的统计信息，包括调用次数、分类分布等",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        types.Tool(
            name="show_popup",
            description="弹出一个 Windows 消息框，支持自定义标题、内容和图标",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "弹窗标题"
                    },
                    "content": {
                        "type": "string",
                        "description": "弹窗显示的内容文本"
                    },
                    "icon": {
                        "type": "string",
                        "enum": ["info", "warning", "error", "question"],
                        "description": "弹窗图标类型，默认为 info"
                    }
                },
                "required": ["title", "content"]
            }
        ),
        types.Tool(
            name="test_recall",
            description="弹出一个窗口显示最近一次工具调用的记录，用于验证 Function Calling 功能",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        types.Tool(
            name="calculate",
            description="执行精确的数学计算。支持加减乘除、括号和小数",
            inputSchema={
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "数学表达式字符串，如 '5*9+10-3/2'"
                    }
                },
                "required": ["expression"]
            }
        ),
        types.Tool(
            name="get_local_time",
            description="获取当前系统的本地时间，返回 ISO 格式的时间字符串",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        types.Tool(
            name="get_self_info",
            description="获取当前使用的模型信息，包括模型名称、API 地址、提供商等配置详情",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any] | None) -> list[types.TextContent]:
    """处理工具调用请求"""
    if arguments is None:
        arguments = {}

    try:
        # 根据工具名称路由到对应的 registry 方法
        tool_func = getattr(registry, name, None)
        if tool_func is None:
            return [types.TextContent(
                type="text",
                text=json.dumps({"status": "error", "message": f"未知工具: {name}"}, ensure_ascii=False)
            )]

        result = tool_func(**arguments)

        return [types.TextContent(
            type="text",
            text=json.dumps(result, ensure_ascii=False, indent=2)
        )]

    except Exception as e:
        return [types.TextContent(
            type="text",
            text=json.dumps({"status": "error", "message": f"{type(e).__name__}: {str(e)}"}, ensure_ascii=False)
        )]


async def main():
    """运行 MCP 服务器"""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="aitools",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
