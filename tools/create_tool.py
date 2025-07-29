#!/usr/bin/env python3
"""
工具创建脚本
帮助快速创建新的Function Call工具
"""

import os
import sys

def create_tool_template(tool_name: str, description: str, class_name: str):
    """创建工具模板代码"""
    
    template = f'''"""
{description}
"""

import json
from typing import Dict, Any

from .base import BaseTool


class {class_name}(BaseTool):
    """{description}"""
    
    def get_name(self) -> str:
        return "{tool_name}"
    
    def get_description(self) -> str:
        return "{description}"
    
    def get_parameters(self) -> Dict[str, Any]:
        return {{
            "type": "object",
            "properties": {{
                "param1": {{
                    "type": "string",
                    "description": "参数1的描述"
                }}
            }},
            "required": ["param1"]
        }}
    
    def execute(self, param1: str) -> str:
        """执行工具逻辑"""
        try:
            # 在这里实现你的工具逻辑
            result = {{
                "input_param1": param1,
                "result": f"处理结果: {{param1}}",
                "status": "success"
            }}
            
            return json.dumps(result, ensure_ascii=False)
            
        except Exception as e:
            raise Exception(f'{{self.get_description()}}执行失败: {{str(e)}}')
'''
    
    return template

def main():
    """主函数"""
    if len(sys.argv) != 4:
        print("使用方法: python create_tool.py <tool_name> <class_name> <description>")
        print("示例: python create_tool.py translate TranslateTool '文本翻译工具'")
        sys.exit(1)
    
    tool_name = sys.argv[1]
    class_name = sys.argv[2] 
    description = sys.argv[3]
    
    # 生成文件名
    file_name = f"{tool_name}_tool.py"
    file_path = os.path.join(os.path.dirname(__file__), file_name)
    
    # 检查文件是否已存在
    if os.path.exists(file_path):
        print(f"❌ 文件 {file_name} 已存在!")
        sys.exit(1)
    
    # 创建工具文件
    template_code = create_tool_template(tool_name, description, class_name)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(template_code)
    
    print(f"✅ 成功创建工具文件: {file_name}")
    print(f"📝 工具名称: {tool_name}")
    print(f"📝 类名: {class_name}")
    print(f"📝 描述: {description}")
    print()
    print("📋 下一步:")
    print(f"1. 编辑 {file_name} 文件，实现具体的工具逻辑")
    print("2. 在 tools/__init__.py 中导入并注册新工具:")
    print(f"   from .{tool_name}_tool import {class_name}")
    print(f"   tool_registry.register({class_name}())")
    print("3. 重启Jarvis即可使用新工具")

if __name__ == "__main__":
    main() 