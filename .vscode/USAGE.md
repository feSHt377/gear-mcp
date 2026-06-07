# MCP 服务器使用说明

## 什么是 MCP？

MCP (Model Context Protocol) 是 VS Code Copilot 的扩展协议，允许 Copilot 在对话中
调用自定义工具，就像 Function Calling 一样。

## 已注册的工具

| 工具名 | 功能 |
|--------|------|
| `save_data_to_log` | 保存数据到本地日志 |
| `query_logs` | 查询已有日志 |
| `get_test_statistics` | 获取调用统计 |
| `show_popup` | 弹出 Windows 消息框 |
| `test_recall` | 测试弹窗（显示最近记录） |
| `calculate` | 数学计算 |
| `get_local_time` | 获取当前时间 |
| `get_self_info` | 获取当前模型配置 |

## 使用方法

### 方式一：工作区级别（已配置）

1. 文件 `.vscode/settings.json` 已写入配置
2. **重启 VS Code**
3. 打开 Copilot Chat，直接提问，Copilot 会自动决定何时调用这些工具

例如：
- "帮我保存一条日志，分类是 test，数据是 {'msg': 'hello'}"
- "弹出消息框，标题是通知，内容是测试成功"
- "当前用的什么模型？"

### 方式二：用户全局级别

如果你想在所有项目中使用，按 `Ctrl+Shift+P` → "打开用户设置 (JSON)"，
加入：

```json
"github.copilot.mcp.agent": {
    "servers": {
        "aitools": {
            "command": "e:/Docs/Aitools/.venv/Scripts/python.exe",
            "args": [
                "e:\\Docs\\Aitools\\mcp_server.py"
            ]
        }
    }
}
```

## 验证是否生效

在 Copilot Chat 中输入：
> 获取当前模型信息

如果 Copilot 回复了模型名称和 API 地址，说明 MCP 连接成功。
