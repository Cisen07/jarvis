"""
计算器工具
执行数学计算
"""

import json
import math
import re
from typing import Dict, Any

from .base import BaseTool


class CalculatorTool(BaseTool):
    """计算器工具"""
    
    def get_name(self) -> str:
        return "calculator"
    
    def get_description(self) -> str:
        return "执行数学计算，支持基本运算和数学函数"
    
    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "要计算的数学表达式，如 '2+3*4' 或 'sqrt(16)' 或 'sin(3.14159/2)'"
                }
            },
            "required": ["expression"]
        }
    
    def execute(self, expression: str) -> str:
        """执行数学计算"""
        try:
            # 安全的数学表达式环境
            allowed_names = {
                k: v for k, v in math.__dict__.items() if not k.startswith("__")
            }
            allowed_names.update({
                "abs": abs, 
                "round": round,
                "min": min,
                "max": max,
                "sum": sum,
                "pow": pow
            })
            
            # 基本的表达式清理（保留更多有效字符）
            # 允许数字、运算符、小数点、括号、字母（用于函数名）和空格
            cleaned_expression = re.sub(r'[^\w\d+\-*/().,\s]', '', expression)
            
            # 安全计算
            result = eval(cleaned_expression, {"__builtins__": {}}, allowed_names)
            
            return json.dumps({
                'result': result,
                'expression': expression,
                'type': type(result).__name__
            }, ensure_ascii=False)
            
        except Exception as e:
            raise Exception(f'计算失败: {str(e)}，表达式: {expression}') 