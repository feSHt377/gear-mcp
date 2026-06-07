"""
工具定义模块
定义可以被大模型通过 Function Calling 调用的工具
"""

import os
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Callable
import re


# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='logs/tool_calls.log',
    filemode='a',
    encoding='utf-8'
)
logger = logging.getLogger("ToolFunctions")


# ==================== 工具实现 ====================

class ToolRegistry:
    """工具注册中心，存储和管理工具调用记录"""
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = log_dir
        self.ensure_log_dir()
        self.call_history = self._load_history()
        
    def ensure_log_dir(self):
        """确保日志目录存在"""
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
            
    def _load_history(self) -> List[Dict]:
        """加载历史调用记录"""
        history_file = os.path.join(self.log_dir, "tool_call_history.json")
        if os.path.exists(history_file):
            try:
                with open(history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
        
    def _save_history(self):
        """保存调用历史"""
        history_file = os.path.join(self.log_dir, "tool_call_history.json")
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(self.call_history, f, ensure_ascii=False, indent=2)
    
    def save_data_to_log(self, category: str, data: Dict[str, Any], 
                        priority: str = "medium") -> Dict:
        """保存数据到日志文件"""
        timestamp = datetime.now().isoformat()
        record = {
            "timestamp": timestamp,
            "category": category,
            "data": data,
            "priority": priority
        }
        
        self.call_history.append(record)
        self._save_history()
        logger.info(f"[{priority.upper()}] {category}: {json.dumps(data, ensure_ascii=False)}")
        
        return {
            "status": "success",
            "message": f"数据已保存到 {self.log_dir}/tool_call_history.json",
            "record_id": len(self.call_history)
        }
    
    def query_logs(self, category: Optional[str] = None, limit: int = 10) -> Dict:
        """查询日志数据"""
        records = self.call_history
        
        if category:
            records = [r for r in records if r["category"] == category]
        
        records = records[-limit:]
        
        return {
            "status": "success",
            "total_records": len(self.call_history),
            "filtered_records": len(records),
            "records": records
        }
    
    def get_test_statistics(self) -> Dict:
        """获取测试统计信息"""
        total_calls = len(self.call_history)
        
        category_counts = {}
        for record in self.call_history:
            cat = record["category"]
            category_counts[cat] = category_counts.get(cat, 0) + 1
            
        priority_counts = {}
        for record in self.call_history:
            pri = record["priority"]
            priority_counts[pri] = priority_counts.get(pri, 0) + 1
            
        return {
            "status": "success",
            "statistics": {
                "total_calls": total_calls,
                "by_category": category_counts,
                "by_priority": priority_counts
            }
        }
    
    def show_popup(self, title: str, content: str, icon: str = "info") -> Dict:
        """弹出 Windows 消息框（非阻塞，独立子进程）
        
        Args:
            title: 弹窗标题
            content: 弹窗内容
            icon: 图标类型 - "info", "warning", "error", "question"
        """
        import subprocess
        import sys
        
        icon_map = {
            "info": 0x40,      # MB_ICONINFORMATION
            "warning": 0x30,   # MB_ICONWARNING
            "error": 0x10,     # MB_ICONERROR
            "question": 0x20,  # MB_ICONQUESTION
        }
        icon_flag = icon_map.get(icon, 0x40)
        
        # 通过子进程调用 Windows 原生弹窗，不阻塞主流程
        popup_code = (
            "import ctypes;"
            "ctypes.windll.user32.MessageBoxW(0,"
            + repr(content) + ","
            + repr(title) + ","
            f"{icon_flag}|0x1000)"  # MB_SYSTEMMODAL 置顶显示
        )
        
        subprocess.Popen([sys.executable, "-c", popup_code])
        
        return {
            "status": "success",
            "message": f"弹窗已打开: {title}"
        }
    
    def calculate(self, expression: str) -> Dict:
        """执行简单的加减乘除数学计算
        
        Args:
            expression: 数学表达式，如 "5*9+10-3/2"
        """
        # 安全检查：只允许数字、运算符、空格、小数点
        allowed_pattern = re.compile(r'^[\d\s\+\-\*\/\.\(\)]+$')
        if not allowed_pattern.match(expression):
            return {
                "status": "error",
                "message": f"表达式包含非法字符: {expression}"
            }
        
        try:
            # 使用 eval 计算表达式（已做安全过滤）
            result = eval(expression)
            return {
                "status": "success",
                "expression": expression,
                "result": result
            }
        except ZeroDivisionError:
            return {
                "status": "error",
                "message": "除数不能为零"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"计算失败: {str(e)}"
            }
    
    def test_recall(self) -> Dict:
        """测试模型调用 - 弹出窗口显示调用信息（非阻塞）"""
        import json
        
        # 获取最近一条记录
        if not self.call_history:
            last_record = {"info": "暂无历史记录"}
        else:
            last_record = self.call_history[-1]
        
        record_json = json.dumps(last_record, ensure_ascii=False)
        content = f"模型成功调用了 test_recall 工具！\n\n最近一条记录:\n{record_json}"
        
        # 复用 show_popup
        return self.show_popup(
            title="Function Calling 测试",
            content=content,
            icon="info"
        )
    
    def get_local_time(self) -> Dict:
        """获取当前系统的本地时间，返回 ISO 格式的时间字符串"""
        local_time = datetime.now().isoformat()
        return {
            "status": "success",
            "local_time": local_time
        }
    def get_self_info(self) -> Dict:
        """获取当前使用模型的数据"""
        config_path = os.path.join("config", "config.json")
        if not os.path.exists(config_path):
            return {
                "status": "error",
                "message": "配置文件不存在"
            }
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except Exception as e:
            return {
                "status": "error",
                "message": f"读取配置失败: {str(e)}"
            }
        
        # 查找第一个未禁用的模型配置
        models_config = config.get("models", {})
        active_model_name = None
        active_model_config = None
        
        for model_name, cfg in models_config.items():
            if not cfg.get("disable", False):
                active_model_name = model_name
                active_model_config = cfg
                break
        
        if active_model_config is None:
            return {
                "status": "error",
                "message": "未找到启用的模型配置"
            }
        
        return {
            "status": "success",
            "model_info": {
                "name": active_model_name,
                "api_url": active_model_config.get("api_url", ""),
                "default_model": active_model_config.get("default_model", ""),
                "provider": "ollama"
            },
            "config_path": config_path
        }



# 创建全局实例
registry = ToolRegistry()


# ==================== 工具定义 ====================
# 定义在类之后，这样可以直接引用方法

# 工具1: 保存数据到日志文件
TOOL_SAVE_DATA = {
    "type": "function",
    "function": {
        "name": "save_data_to_log",
        "point": registry.save_data_to_log,
        "description": "将指定的数据保存到本地日志文件中，用于记录模型调用过程中的关键信息",
        "parameters": {
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
    }
}

# 工具2: 查询日志数据
TOOL_QUERY_LOGS = {
    "type": "function",
    "function": {
        "name": "query_logs",
        "point": registry.query_logs,
        "description": "查询已保存的日志数据，支持按分类和时间范围筛选",
        "parameters": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "description": "要查询的数据分类，如果不指定则查询所有"
                },
                "limit": {
                    "type": "integer",
                    "description": "返回记录的数量限制，默认为10"
                }
            },
            "required": []
        }
    }
}

# 工具3: 获取测试统计信息
TOOL_GET_STATS = {
    "type": "function",
    "function": {
        "name": "get_test_statistics",
        "point": registry.get_test_statistics,
        "description": "获取工具调用的统计信息，包括调用次数、分类分布等",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
}

# 工具4: 通用弹窗工具（完全解耦，支持自定义内容）
TOOL_SHOW_POPUP = {
    "type": "function",
    "function": {
        "name": "show_popup",
        "point": registry.show_popup,
        "description": "弹出一个 Windows 消息框，支持自定义标题、内容和图标。可用于测试提醒、通知或验证 Function Calling 功能",
        "parameters": {
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
    }
}

TOOL_TEST_RECALL = {
    "type": "function",
    "function": {
        "name": "test_recall",
        "point": registry.test_recall,
        "description": "弹出一个窗口显示最近一次工具调用的记录，用于验证模型的 Function Calling 功能是否正常工作",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
}

# 工具6: 数学计算工具
TOOL_CALCULATE = {
    "type": "function",
    "function": {
        "name": "calculate",
        "point": registry.calculate,
        "description": "执行精确的数学计算。当用户要求计算数学表达式、做加减乘除运算、或需要数值结果时，必须使用此工具而不是自己心算。支持括号、小数点等复杂表达式。例如：'5*9*1021-213+3241/221341'",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "要计算的数学表达式字符串，如 '5*9+10-3/2' 或 '5*9*1021-213+3241/221341'。支持加减乘除、括号和小数"
                }
            },
            "required": ["expression"]
        }
    }
}

TOOL_GET_LOCAL_TIME = {
    "type": "function",
    "function": {
        "name": "get_local_time",
        "point": registry.get_local_time,
        "description": "获取当前系统的本地时间，返回 ISO 格式的时间字符串",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
}

# 工具8: 获取当前模型信息
TOOL_GET_SELF_INFO = {
    "type": "function",
    "function": {
        "name": "get_self_info",
        "point": registry.get_self_info,
        "description": "获取当前使用的模型信息，包括模型名称、API 地址、提供商等配置详情",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
}


# 所有工具列表
ALL_TOOLS = [TOOL_SAVE_DATA, TOOL_QUERY_LOGS, TOOL_GET_STATS, TOOL_SHOW_POPUP, TOOL_TEST_RECALL, TOOL_CALCULATE, TOOL_GET_LOCAL_TIME, TOOL_GET_SELF_INFO]


def get_tool_schema(tool: Dict) -> Dict:
    """获取工具的 JSON Schema（过滤掉 point 字段，因为函数引用不可序列化）"""
    schema = tool.copy()
    func = schema["function"].copy()
    func.pop("point", None)  # 移除 point 字段
    schema["function"] = func
    return schema


def get_tool_schema_list(tools: List[Dict]) -> List[Dict]:
    """获取所有工具的 JSON Schema 列表"""
    return [get_tool_schema(t) for t in tools]


def execute_tool(tool: Dict, arguments: Dict) -> Dict:
    """执行工具调用"""
    point = tool["function"].get("point")
    if not callable(point):
        return {"status": "error", "message": f"工具 {tool['function']['name']} 未绑定实现"}
    
    try:
        result = point(**arguments)
        return {"status": "success", "result": result}
    except Exception as e:
        return {"status": "error", "message": f"{type(e).__name__}: {str(e)}"}
