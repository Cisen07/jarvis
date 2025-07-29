"""
天气查询工具 (示例)
注意：这是一个示例工具，实际使用需要接入真实的天气API
"""

import json
import random
from typing import Dict, Any

from .base import BaseTool


class WeatherTool(BaseTool):
    """天气查询工具"""
    
    def get_name(self) -> str:
        return "get_weather"
    
    def get_description(self) -> str:
        return "获取指定城市的天气信息"
    
    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "城市名称，如：北京、上海、广州"
                },
                "days": {
                    "type": "integer", 
                    "description": "查询天数，1-7天",
                    "default": 1,
                    "minimum": 1,
                    "maximum": 7
                }
            },
            "required": ["city"]
        }
    
    def execute(self, city: str, days: int = 1) -> str:
        """执行天气查询（模拟数据）"""
        # 注意：这里使用模拟数据，实际应该调用天气API
        
        # 模拟天气数据
        weather_conditions = ["晴", "多云", "阴", "小雨", "中雨", "雪"]
        temperatures = list(range(-10, 35))
        
        forecast = []
        for i in range(days):
            day_weather = {
                "date": f"2025-07-{29+i:02d}",
                "condition": random.choice(weather_conditions),
                "temperature": {
                    "high": random.choice(temperatures),
                    "low": random.choice(temperatures[:-10])
                },
                "humidity": random.randint(30, 90),
                "wind": f"{random.choice(['东', '南', '西', '北'])}风 {random.randint(1, 5)}级"
            }
            forecast.append(day_weather)
        
        result = {
            "city": city,
            "forecast": forecast,
            "note": "这是模拟数据，实际使用请接入真实天气API"
        }
        
        return json.dumps(result, ensure_ascii=False) 