"""
工具基类
定义所有Function Call工具的统一接口
"""

import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class BaseTool(ABC):
    """工具基类"""
    
    def __init__(self):
        self.name = self.get_name()
        self.description = self.get_description()
        self.parameters = self.get_parameters()
    
    @abstractmethod
    def get_name(self) -> str:
        """获取工具名称"""
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """获取工具描述"""
        pass
    
    @abstractmethod
    def get_parameters(self) -> Dict[str, Any]:
        """获取参数定义（JSON Schema格式）"""
        pass
    
    @abstractmethod
    def execute(self, **kwargs) -> str:
        """执行工具逻辑，返回JSON格式字符串"""
        pass
    
    def get_function_definition(self) -> Dict[str, Any]:
        """获取完整的函数定义（用于LLM）"""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters
        }
    
    def call(self, **kwargs) -> str:
        """调用工具（包含日志和错误处理）"""
        logger.info(f"🔧 调用工具: {self.name}，参数: {kwargs}")
        
        try:
            result = self.execute(**kwargs)
            logger.info(f"✅ {self.name} 执行成功")
            return result
        except Exception as e:
            error_msg = f"工具 {self.name} 执行失败: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return json.dumps({'error': error_msg}, ensure_ascii=False)
    
    def __str__(self):
        return f"Tool({self.name})"
    
    def __repr__(self):
        return f"Tool(name='{self.name}', description='{self.description}')" 