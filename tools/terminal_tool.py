"""
终端命令工具
执行终端/命令行命令
"""

import json
import subprocess
import os
import shlex
from typing import Dict, Any

from .base import BaseTool


class TerminalTool(BaseTool):
    """终端命令执行工具"""
    
    def get_name(self) -> str:
        return "execute_terminal_command"
    
    def get_description(self) -> str:
        return "执行终端命令并返回结果。支持大部分常见的命令行操作，如ls、pwd、echo、cat等"
    
    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "要执行的终端命令，如 'ls -la'、'pwd'、'echo hello world'、'cat file.txt' 等"
                },
                "working_directory": {
                    "type": "string",
                    "description": "可选：命令执行的工作目录，默认为当前目录"
                }
            },
            "required": ["command"]
        }
    
    def execute(self, command: str, working_directory: str = None) -> str:
        """执行终端命令"""
        try:
            # 安全检查：禁止一些危险的命令
            dangerous_commands = [
                'rm -rf /', 'format', 'del /f /s /q', 'shutdown', 'reboot',
                'mkfs', 'dd if=', ':(){ :|:& };:', 'chmod 000', 'sudo rm'
            ]
            
            # 检查是否包含危险命令
            command_lower = command.lower()
            for dangerous in dangerous_commands:
                if dangerous in command_lower:
                    raise Exception(f"出于安全考虑，不允许执行包含 '{dangerous}' 的命令")
            
            # 设置工作目录
            if working_directory and os.path.exists(working_directory):
                cwd = working_directory
            else:
                cwd = os.getcwd()
            
            # 使用shlex.split来安全地分割命令
            try:
                cmd_args = shlex.split(command)
            except ValueError as e:
                raise Exception(f"命令格式错误: {str(e)}")
            
            # 执行命令
            result = subprocess.run(
                cmd_args,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=30,  # 30秒超时
                shell=False  # 不使用shell模式，更安全
            )
            
            # 准备返回结果
            response_data = {
                'command': command,
                'working_directory': cwd,
                'return_code': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'success': result.returncode == 0
            }
            
            # 如果命令失败，添加错误说明
            if result.returncode != 0:
                response_data['error_message'] = f"命令执行失败，返回码: {result.returncode}"
            
            return json.dumps(response_data, ensure_ascii=False, indent=2)
            
        except subprocess.TimeoutExpired:
            raise Exception(f"命令执行超时（30秒）: {command}")
        except FileNotFoundError:
            raise Exception(f"命令未找到: {command.split()[0] if command else 'unknown'}")
        except PermissionError:
            raise Exception(f"权限不足，无法执行命令: {command}")
        except Exception as e:
            if "出于安全考虑" in str(e):
                raise e  # 重新抛出安全检查的异常
            raise Exception(f'执行终端命令失败: {str(e)}，命令: {command}') 