"""
Jarvis Tools Package
管理所有的Function Call工具
"""

from .registry import ToolRegistry
from .time_tool import TimeTool
from .calculator_tool import CalculatorTool
from .terminal_tool import TerminalTool

# 创建全局工具注册表
tool_registry = ToolRegistry()

# 注册所有工具
tool_registry.register(TimeTool())
tool_registry.register(CalculatorTool())
tool_registry.register(TerminalTool())

# 导出接口
__all__ = [
    'tool_registry',
    'ToolRegistry',
    'TimeTool', 
    'CalculatorTool',
    'TerminalTool',
] 