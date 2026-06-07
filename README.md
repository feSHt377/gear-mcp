# AI 模型 Function Calling 测试工具

测试 AI 模型的**工具调用（Function Calling）能力**，验证模型能否正确识别并调用定义的工具函数，同时将调用数据保存到本地日志文件。

## 项目结构

```
Aitools/
├── test_function_calling.py   # 主入口：Function Calling 测试脚本
├── tools.py                   # 工具定义（JSON Schema）和实现
├── config/
│   └── config.json           # 配置文件（模型地址、参数等）
├── logs/                      # 日志输出目录（运行时自动生成）
│   ├── tool_calls.log        # 工具调用日志
│   └── tool_call_history.json # 工具调用数据记录
├── requirements.txt           # Python 依赖
└── README.md                  # 项目说明
```

## 安装

```bash
pip install -r requirements.txt
```

## 配置

编辑 `config/config.json`：

```json
{
  "models": {
    "local": {
      "api_url": "http://100.64.0.13:11438",
      "default_model": "qwen3.6:27b"
    }
  }
}
```

## 使用方法

### 运行完整测试套件

```bash
python test_function_calling.py
```

### 自定义测试提示词

```bash
python test_function_calling.py -p "保存一条测试数据到日志，分类是test，数据包含key是hello值是world"
```

### 指定配置文件

```bash
python test_function_calling.py -c config/config.json
```

## 定义的工具

| 工具名称 | 功能 | 参数 |
|---------|------|------|
| `save_data_to_log` | 保存数据到本地日志文件 | `category`(分类), `data`(数据), `priority`(优先级) |
| `query_logs` | 查询已保存的日志数据 | `category`(分类筛选), `limit`(数量限制) |
| `get_test_statistics` | 获取工具调用统计信息 | 无 |

## 测试示例

### 测试保存数据
```
提示词: 请保存以下数据到日志：用户ID为12345，操作类型为'登录'。
分类为'user_action'，优先级为'high'。

模型行为: ✅ 调用 save_data_to_log(category='user_action', data={...}, priority='high')
```

### 测试查询日志
```
提示词: 查询一下最近保存的日志数据，限制返回5条记录。

模型行为: ✅ 调用 query_logs(limit=5)
```

### 测试多工具调用
```
提示词: 先保存一条系统事件日志，然后查询所有日志，最后获取统计信息。

模型行为: ✅ 连续调用 3 个工具
```

## 输出文件

| 文件 | 说明 |
|------|------|
| `logs/tool_calls.log` | 工具调用的详细日志（时间戳、参数、结果） |
| `logs/tool_call_history.json` | 所有工具调用的结构化数据记录 |

## 测试结果示例

```
==================================================
开始 Function Calling 测试
==================================================

测试 1/5: 测试保存用户输入
✅ 模型决定调用 1 个工具
   调用工具: save_data_to_log
   参数: {"category": "user_action", "data": {...}, "priority": "high"}
   ✅ 工具执行成功

测试汇总:
  总测试数: 5
  工具调用总数: 5
  成功调用数: 5
  成功率: 100.0%
```
