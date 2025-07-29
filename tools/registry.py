"""
工具注册表
管理所有Function Call工具的注册、发现和调用
"""

import logging
from typing import Dict, List, Any, Optional
from .base import BaseTool

logger = logging.getLogger(__name__)


class ToolRegistry:
    """工具注册表"""
    
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
    
    def register(self, tool: BaseTool) -> None:
        """注册一个工具"""
        if not isinstance(tool, BaseTool):
            raise TypeError(f"工具必须继承自BaseTool: {type(tool)}")
        
        if tool.name in self._tools:
            logger.warning(f"⚠️ 工具 {tool.name} 已存在，将被覆盖")
        
        self._tools[tool.name] = tool
        logger.info(f"📝 注册工具: {tool.name}")
    
    def unregister(self, tool_name: str) -> bool:
        """注销一个工具"""
        if tool_name in self._tools:
            del self._tools[tool_name]
            logger.info(f"🗑️ 注销工具: {tool_name}")
            return True
        return False
    
    def get_tool(self, tool_name: str) -> Optional[BaseTool]:
        """获取指定工具"""
        return self._tools.get(tool_name)
    
    def get_all_tools(self) -> Dict[str, BaseTool]:
        """获取所有工具"""
        return self._tools.copy()
    
    def get_tool_names(self) -> List[str]:
        """获取所有工具名称"""
        return list(self._tools.keys())
    
    def get_function_definitions(self) -> List[Dict[str, Any]]:
        """获取所有工具的函数定义（用于LLM）"""
        return [tool.get_function_definition() for tool in self._tools.values()]
    
    def call_tool(self, tool_name: str, **kwargs) -> str:
        """调用指定工具"""
        tool = self.get_tool(tool_name)
        if tool is None:
            error_msg = f"未找到工具: {tool_name}"
            logger.error(f"❌ {error_msg}")
            return f'{{"error": "{error_msg}"}}'
        
        return tool.call(**kwargs)
    
    def list_tools(self) -> str:
        """列出所有工具信息"""
        if not self._tools:
            return "当前没有注册任何工具"
        
        tool_info = []
        for tool in self._tools.values():
            tool_info.append(f"- {tool.name}: {tool.description}")
        
        return "可用工具:\n" + "\n".join(tool_info)
    
    def __len__(self):
        return len(self._tools)
    
    def __contains__(self, tool_name: str):
        return tool_name in self._tools
    
    def __str__(self):
        return f"ToolRegistry({len(self._tools)} tools: {list(self._tools.keys())})" 