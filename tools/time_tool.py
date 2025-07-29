"""
时间查询工具
获取当前时间和日期信息
"""

import json
from datetime import datetime
from typing import Dict, Any
import pytz

from .base import BaseTool


class TimeTool(BaseTool):
    """时间查询工具"""
    
    def get_name(self) -> str:
        return "get_current_time"
    
    def get_description(self) -> str:
        return "获取当前时间和日期信息"
    
    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "timezone": {
                    "type": "string",
                    "description": "时区，例如: Asia/Shanghai, UTC, America/New_York",
                    "default": "Asia/Shanghai"
                }
            },
            "required": []
        }
    
    def execute(self, timezone: str = "Asia/Shanghai") -> str:
        """执行时间查询"""
        try:
            if timezone == 'UTC':
                tz = pytz.UTC
            else:
                tz = pytz.timezone(timezone)
            
            current_time = datetime.now(tz)
            
            result = {
                'current_time': current_time.strftime('%Y-%m-%d %H:%M:%S %Z'),
                'timezone': timezone,
                'weekday': current_time.strftime('%A'),
                'date_info': {
                    'year': current_time.year,
                    'month': current_time.month,
                    'day': current_time.day,
                    'hour': current_time.hour,
                    'minute': current_time.minute,
                    'second': current_time.second
                }
            }
            
            return json.dumps(result, ensure_ascii=False)
            
        except Exception as e:
            raise Exception(f'获取时间失败: {str(e)}') 