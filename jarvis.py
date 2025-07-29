#!/usr/bin/env python3
"""
Jarvis - 基于Qwen-Agent的本地AI助手 (重构版)
使用模块化的工具管理架构
"""

import os
import json
import logging
import traceback
from dotenv import load_dotenv
from qwen_agent.llm import get_chat_model

# 导入工具管理
from tools import tool_registry

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class JarvisAgent:
    """Jarvis AI助手主类"""
    
    def __init__(self, llm_config: dict):
        """初始化Jarvis"""
        self.llm_config = llm_config
        self.llm = None
        self.tool_registry = tool_registry
        self._initialize_llm()
    
    def _initialize_llm(self):
        """初始化LLM"""
        try:
            logger.info("🚀 创建LLM实例...")
            self.llm = get_chat_model(self.llm_config)
            logger.info("✅ LLM创建成功!")
        except Exception as e:
            logger.error(f"❌ LLM初始化失败: {e}")
            raise
    
    def get_available_tools(self) -> list:
        """获取可用工具列表"""
        return self.tool_registry.get_function_definitions()
    
    def process_message(self, user_input: str, system_message: str = None) -> str:
        """处理用户消息"""
        logger.info(f"📝 用户输入: {user_input}")
        
        # 默认系统提示
        if system_message is None:
            system_message = """你是一个智能助手Jarvis。你可以使用以下工具来帮助用户：
- get_current_time: 获取当前时间和日期信息
- calculator: 执行数学计算

请根据用户的需求选择合适的工具，并用中文回答用户的问题。"""
        
        # 构建消息
        messages = [
            {'role': 'system', 'content': system_message},
            {'role': 'user', 'content': user_input}
        ]
        
        # 获取工具定义
        functions = self.get_available_tools()
        
        try:
            logger.info("🔄 开始调用LLM...")
            
            # 调用LLM
            response = self.llm.chat(
                messages=messages,
                functions=functions,
                stream=False
            )
            
            logger.info(f"📤 LLM原始响应类型: {type(response)}")
            
            # 处理响应
            return self._handle_response(response, messages, functions)
            
        except Exception as e:
            logger.error(f"❌ 处理消息错误: {str(e)}")
            logger.error(f"❌ 错误详情: {traceback.format_exc()}")
            return f"抱歉，处理您的请求时发生了错误: {e}"
    
    def _handle_response(self, response, messages: list, functions: list) -> str:
        """处理LLM响应"""
        if isinstance(response, list) and len(response) > 0:
            first_response = response[0]
            logger.info(f"📤 处理第一个响应: {first_response}")
            
            # 检查是否有函数调用
            if 'function_call' in first_response and first_response['function_call']:
                return self._handle_function_call(first_response, messages, functions)
            else:
                # 普通文本响应
                logger.info("💬 普通文本响应")
                return first_response.get('content', str(first_response))
        else:
            # 其他格式的响应
            logger.info("💬 其他格式响应")
            return str(response)
    
    def _handle_function_call(self, response, messages: list, functions: list) -> str:
        """处理函数调用"""
        logger.info("🔧 检测到函数调用")
        
        func_call = response['function_call']
        func_name = func_call['name']
        
        # 解析参数
        try:
            func_args_str = func_call['arguments']
            func_args = self._parse_function_arguments(func_args_str)
        except Exception as e:
            logger.error(f"❌ 解析函数参数失败: {e}")
            return f"解析函数参数时发生错误: {e}"
        
        logger.info(f"📞 调用函数: {func_name}，参数: {func_args}")
        print(f"🔧 调用工具: {func_name}")
        
        # 通过工具注册表调用函数
        func_result = self.tool_registry.call_tool(func_name, **func_args)
        logger.info(f"📋 函数执行结果: {func_result}")
        
        # 将函数结果发送回LLM
        messages.append({
            'role': 'assistant',
            'content': None,
            'function_call': {
                'name': func_name,
                'arguments': func_call['arguments']
            }
        })
        messages.append({
            'role': 'function',
            'name': func_name,
            'content': func_result
        })
        
        logger.info("🔄 将函数结果发送回LLM...")
        
        # 再次调用LLM获取最终回答
        try:
            final_response = self.llm.chat(
                messages=messages,
                functions=functions,
                stream=False
            )
            
            logger.info(f"📤 最终LLM响应: {final_response}")
            
            # 处理最终响应
            if isinstance(final_response, list) and len(final_response) > 0:
                return final_response[0].get('content', str(final_response[0]))
            else:
                return str(final_response)
                
        except Exception as e:
            logger.error(f"❌ 获取最终回答时出错: {e}")
            return f"获取最终回答时发生错误: {e}"
    
    def _parse_function_arguments(self, args_str: str) -> dict:
        """解析函数参数"""
        if isinstance(args_str, str):
            if args_str.startswith('"{') and args_str.endswith('}"'):
                # 处理双重编码的情况
                args_str = args_str[1:-1]  # 去掉外层引号
                args_str = args_str.replace('\\"', '"')  # 恢复内层引号
            elif args_str == '"{}"':
                # 处理空对象的情况
                args_str = '{}'
            return json.loads(args_str)
        else:
            return args_str or {}


def main():
    """主函数"""
    try:
        print("🤖 Jarvis - 智能AI助手 (模块化版本)")
        print("=" * 50)
        
        # 加载环境变量
        logger.info("📥 加载环境变量...")
        load_dotenv()
        
        # 配置LLM
        llm_cfg = {
            'model': os.getenv('MODEL_NAME', 'deepseek-ai/DeepSeek-V2.5'),
            'model_server': os.getenv('OPENAI_BASE_URL', 'https://api.siliconflow.cn/v1'),
            'api_key': os.getenv('OPENAI_API_KEY'),
            'generate_cfg': {
                'top_p': 0.8,
                'temperature': 0.7,
                'max_tokens': 1000
            }
        }
        
        print(f"📝 使用模型: {llm_cfg['model']}")
        print(f"🔗 API地址: {llm_cfg['model_server']}")
        
        # 创建Jarvis实例
        jarvis = JarvisAgent(llm_cfg)
        
        # 显示可用工具
        tools = jarvis.get_available_tools()
        tool_names = [tool['name'] for tool in tools]
        print(f"🛠️  可用工具 ({len(tools)}个): {', '.join(tool_names)}")
        
        print("\n💬 开始对话 (输入 'quit' 退出):")
        print("-" * 50)
        
        while True:
            try:
                user_input = input("\n用户: ").strip()
                if user_input.lower() in ['quit', 'exit', '退出']:
                    print("👋 再见!")
                    break
                
                if not user_input:
                    continue
                
                # 处理用户输入
                response = jarvis.process_message(user_input)
                print(f"Jarvis: {response}")
                
            except KeyboardInterrupt:
                print("\n\n👋 程序被中断，再见!")
                break
            except Exception as e:
                logger.error(f"❌ 对话处理错误: {str(e)}")
                print(f"❌ 发生错误: {e}")
                
    except Exception as e:
        logger.error(f"❌ 主程序错误: {str(e)}")
        logger.error(f"❌ 错误详情: {traceback.format_exc()}")
        print(f"❌ 程序启动失败: {e}")


if __name__ == "__main__":
    main() 