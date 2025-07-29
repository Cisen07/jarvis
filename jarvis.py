#!/usr/bin/env python3
"""
Jarvis - 基于Qwen-Agent的本地AI助手 (重构版)
使用模块化的工具管理架构，支持自动多轮交互
"""

import os
import json
import logging
import traceback
import argparse
from dotenv import load_dotenv
from qwen_agent.llm import get_chat_model

# 导入工具管理
from tools import tool_registry

# 设置日志格式
def setup_logging(level=logging.INFO):
    """设置日志配置"""
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )

logger = logging.getLogger(__name__)


class JarvisAgent:
    """Jarvis AI助手主类"""
    
    def __init__(self, llm_config: dict):
        """初始化Jarvis"""
        self.llm_config = llm_config
        self.llm = None
        self.tool_registry = tool_registry
        self.max_iterations = 10  # 最大迭代次数，防止无限循环
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
    
    def _generate_system_message(self) -> str:
        """从工具注册表自动生成系统提示"""
        # 基础提示
        base_message = "你是一个智能助手。你可以使用以下工具来帮助用户："
        
        # 获取所有工具信息
        tools = self.tool_registry.get_all_tools()
        tool_descriptions = []
        
        for tool_name, tool in tools.items():
            description = f"- {tool_name}: {tool.get_description()}"
            tool_descriptions.append(description)
        
        # 组合完整的系统提示
        tools_text = "\n".join(tool_descriptions)
        
        full_message = f"""{base_message}
{tools_text}

请根据用户的需求选择合适的工具，并用中文回答用户的问题。

**工具调用规则：**
1. 当需要调用工具时，使用标准的function_call格式，或者使用以下自定义格式：
   ```
   <｜tool▁call▁begin｜>function<｜tool▁sep｜>工具名称
   ```json
   {{"参数名": "参数值"}}
   ```<｜tool▁call▁end｜>
   ```

2. 一次只能调用一个工具，不要使用多工具调用格式

3. 调用工具后等待结果，然后基于结果继续回答或调用下一个工具

**结束规则：**
- 当你完成了用户的所有请求并准备给出最终答案时，请在回复的开头加上"[FINAL]"标记
- 例如："[FINAL]现在是下午3点，计算结果是123。"
- 只有当你确认已经获取了所有必要信息并能完整回答用户问题时，才使用[FINAL]标记
- 没有[FINAL]标记，则表示你还需要继续调用工具获取更多信息"""
        
        return full_message
    
    def process_message(self, user_input: str, system_message: str = None) -> str:
        """处理用户消息 - 支持自动多轮交互"""
        logger.info(f"📝 用户输入: {user_input}")
        
        # 如果没有提供系统提示，自动生成
        if system_message is None:
            system_message = self._generate_system_message()
        
        # 构建消息
        messages = [
            {'role': 'system', 'content': system_message},
            {'role': 'user', 'content': user_input}
        ]
        
        # 获取工具定义
        functions = self.get_available_tools()
        
        try:
            logger.info("🔄 开始自动多轮对话处理...")
            
            # 进行多轮交互，直到没有更多函数调用需要处理
            for iteration in range(self.max_iterations):
                logger.info(f"🔄 第 {iteration + 1} 轮对话")
                
                # 根据当前轮次输出不同的日志信息
                if iteration == 0:
                    logger.info("💭 向LLM发送用户问题，等待分析和响应...")
                else:
                    logger.info("💭 向LLM发送工具执行结果，等待进一步处理...")
                
                # 调用LLM
                response = self.llm.chat(
                    messages=messages,
                    functions=functions,
                    stream=False
                )
                
                logger.debug(f"📤 LLM响应类型: {type(response)}")
                
                # 处理响应
                result = self._handle_response_iteration(response, messages, functions, iteration + 1)
                
                # 如果返回了最终结果（不是函数调用），则结束循环
                if result is not None:
                    logger.info(f"✅ 多轮交互完成，共进行了 {iteration + 1} 轮对话")
                    return result
            
            # 如果达到最大迭代次数，返回最后的消息内容
            logger.warning(f"⚠️ 达到最大迭代次数 {self.max_iterations}，强制结束")
            return "抱歉，处理您的请求时达到了最大迭代次数。请重新提问或简化您的请求。"
            
        except Exception as e:
            logger.error(f"❌ 处理消息错误: {str(e)}")
            logger.debug(f"❌ 错误详情: {traceback.format_exc()}")
            return f"抱歉，处理您的请求时发生了错误: {e}"
    
    def _handle_response_iteration(self, response, messages: list, functions: list, round_num: int):
        """处理单次LLM响应迭代"""
        if isinstance(response, list) and len(response) > 0:
            first_response = response[0]
            logger.info(f"📤 处理响应: {first_response}")
            
            # 检查是否有函数调用
            if 'function_call' in first_response and first_response['function_call']:
                # 处理函数调用，但不返回最终结果，继续迭代
                logger.info("🔧 LLM决定调用工具来获取信息")
                self._handle_function_call_iteration(first_response, messages, functions, round_num)
                return None  # 继续迭代
            else:
                # 普通文本响应，检查是否是最终答案
                content = first_response.get('content', str(first_response))
                logger.info(f"💬 LLM提供了文本响应: {content}")
                
                # 检查是否包含自定义工具调用格式
                if self._contains_custom_tool_call(content):
                    logger.info("🔧 检测到自定义工具调用格式，尝试解析...")
                    tool_call_result = self._parse_custom_tool_call(content, messages, functions)
                    if tool_call_result is not None:
                        return tool_call_result
                    return None  # 继续迭代
                
                # 将助手的回复添加到消息历史中
                messages.append({
                    'role': 'assistant', 
                    'content': content
                })
                
                # 检查是否包含[FINAL]标记，表示LLM认为任务已完成
                if content.startswith('[FINAL]'):
                    logger.info("🎯 LLM表示任务已完成（检测到[FINAL]标记）")
                    # 移除[FINAL]标记并返回最终答案
                    final_answer = content.replace('[FINAL]', '').strip()
                    return final_answer
                
                # 没有[FINAL]标记，继续迭代让LLM决定下一步
                logger.info("🤔 LLM可能需要更多信息或进一步思考，继续对话...")
                return None  # 继续迭代
        else:
            # 其他格式的响应
            logger.info("💬 LLM提供了其他格式响应")
            content = str(response)
            messages.append({'role': 'assistant', 'content': content})
            return content
    
    def _handle_function_call_iteration(self, response, messages: list, functions: list, round_num: int):
        """处理函数调用迭代（不返回最终结果）"""
        
        func_call = response['function_call']
        func_name = func_call['name']
        
        # 解析参数
        try:
            func_args_str = func_call['arguments']
            func_args = self._parse_function_arguments(func_args_str)
        except Exception as e:
            logger.error(f"❌ 解析函数参数失败: {e}")
            # 将错误添加到消息中继续处理
            messages.append({
                'role': 'assistant',
                'content': f"解析函数参数时发生错误: {e}"
            })
            return
        
        logger.info(f"🔧 准备调用工具: {func_name}")
        logger.info(f"📋 工具参数: {func_args}")
        print(f"🔧 正在执行: {func_name}")
        
        # 通过工具注册表调用函数
        func_result = self.tool_registry.call_tool(func_name, **func_args)
        
        # 简化工具结果用于日志显示
        try:
            result_obj = json.loads(func_result)
            if 'stdout' in result_obj and result_obj['stdout']:
                preview = result_obj['stdout'][:100] + ('...' if len(result_obj['stdout']) > 100 else '')
                logger.info(f"✅ 工具执行完成，输出预览: {preview}")
            elif 'result' in result_obj:
                preview = str(result_obj['result'])[:100] + ('...' if len(str(result_obj['result'])) > 100 else '')
                logger.info(f"✅ 工具执行完成，结果预览: {preview}")
            else:
                logger.info("✅ 工具执行完成")
        except:
            logger.info("✅ 工具执行完成")
        
        logger.debug(f"📋 完整工具结果: {func_result}")
        
        # 将函数调用和结果添加到消息历史中
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
        
        logger.info("🔄 工具结果已发送给LLM，等待下一步指令...")
    
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
    
    def _contains_custom_tool_call(self, content: str) -> bool:
        """检查内容是否包含自定义工具调用格式"""
        custom_markers = [
            '<｜tool▁calls▁begin｜>',
            '<｜tool▁call▁begin｜>',
            'function<｜tool▁sep｜>',
            '<｜tool▁call▁end｜>',
            '<｜tool▁calls▁end｜>'
        ]
        return any(marker in content for marker in custom_markers)
    
    def _parse_custom_tool_call(self, content: str, messages: list, functions: list):
        """解析自定义工具调用格式"""
        try:
            # 特殊处理：如果只有开始标记但没有完整内容，提示LLM继续
            if '<｜tool▁calls▁begin｜>' in content and '<｜tool▁call▁begin｜>' not in content:
                logger.info("🤔 检测到不完整的工具调用开始标记，提示LLM继续...")
                messages.append({
                    'role': 'assistant',
                    'content': content
                })
                # 添加提示让LLM继续完成工具调用
                messages.append({
                    'role': 'user',
                    'content': '请继续完成工具调用，使用正确的格式调用需要的工具。'
                })
                return None
            
            # 检查是否包含完整的工具调用
            if '<｜tool▁call▁begin｜>' in content and '<｜tool▁call▁end｜>' in content:
                # 提取工具调用部分
                start_marker = '<｜tool▁call▁begin｜>'
                end_marker = '<｜tool▁call▁end｜>'
                
                start_pos = content.find(start_marker)
                end_pos = content.find(end_marker)
                
                if start_pos != -1 and end_pos != -1:
                    tool_call_content = content[start_pos + len(start_marker):end_pos].strip()
                    logger.info(f"🔍 提取的工具调用内容: {tool_call_content}")
                    
                    # 解析函数名和参数
                    if 'function<｜tool▁sep｜>' in tool_call_content:
                        parts = tool_call_content.split('function<｜tool▁sep｜>', 1)
                        if len(parts) == 2:
                            func_name = parts[1].split('\n')[0].strip()
                            
                            # 查找JSON参数
                            json_start = tool_call_content.find('```json')
                            json_end = tool_call_content.find('```', json_start + 7)
                            
                            if json_start != -1 and json_end != -1:
                                json_content = tool_call_content[json_start + 7:json_end].strip()
                                logger.info(f"🔧 准备调用工具: {func_name}")
                                logger.info(f"📋 工具参数: {json_content}")
                                
                                try:
                                    func_args = json.loads(json_content)
                                    print(f"🔧 正在执行: {func_name}")
                                    
                                    # 通过工具注册表调用函数
                                    func_result = self.tool_registry.call_tool(func_name, **func_args)
                                    
                                    # 简化工具结果用于日志显示
                                    try:
                                        result_obj = json.loads(func_result)
                                        if 'stdout' in result_obj and result_obj['stdout']:
                                            preview = result_obj['stdout'][:100] + ('...' if len(result_obj['stdout']) > 100 else '')
                                            logger.info(f"✅ 工具执行完成，输出预览: {preview}")
                                        elif 'result' in result_obj:
                                            preview = str(result_obj['result'])[:100] + ('...' if len(str(result_obj['result'])) > 100 else '')
                                            logger.info(f"✅ 工具执行完成，结果预览: {preview}")
                                        else:
                                            logger.info("✅ 工具执行完成")
                                    except:
                                        logger.info("✅ 工具执行完成")
                                    
                                    logger.debug(f"📋 完整工具结果: {func_result}")
                                    
                                    # 将函数调用和结果添加到消息历史中
                                    messages.append({
                                        'role': 'assistant',
                                        'content': None,
                                        'function_call': {
                                            'name': func_name,
                                            'arguments': json_content
                                        }
                                    })
                                    messages.append({
                                        'role': 'function',
                                        'name': func_name,
                                        'content': func_result
                                    })
                                    
                                    logger.info("🔄 工具结果已发送给LLM，等待下一步指令...")
                                    return None  # 继续迭代
                                    
                                except json.JSONDecodeError as e:
                                    logger.error(f"❌ JSON解析失败: {e}")
                                    error_msg = f"工具调用参数格式错误: {e}"
                                    messages.append({
                                        'role': 'assistant',
                                        'content': error_msg
                                    })
                                    return None
            
            # 如果无法解析，将内容添加到消息历史并继续
            logger.warning("⚠️ 无法解析自定义工具调用格式，作为普通消息处理")
            messages.append({
                'role': 'assistant',
                'content': content
            })
            return None
            
        except Exception as e:
            logger.error(f"❌ 解析自定义工具调用时出错: {e}")
            messages.append({
                'role': 'assistant',
                'content': f"工具调用解析错误: {e}"
            })
            return None


def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='Jarvis AI助手')
    parser.add_argument('--log-level', 
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       default='INFO',
                       help='设置日志级别 (默认: INFO)')
    parser.add_argument('--debug', 
                       action='store_true',
                       help='启用DEBUG模式 (等同于 --log-level DEBUG)')
    
    args = parser.parse_args()
    
    # 设置日志级别
    if args.debug:
        log_level = logging.DEBUG
    else:
        log_level = getattr(logging, args.log_level.upper())
    
    setup_logging(log_level)
    
    try:
        print("🤖 Jarvis - 智能AI助手 (自动多轮交互版本)")
        print("=" * 50)
        
        # 加载环境变量
        logger.debug("📥 加载环境变量...")
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
        if log_level == logging.DEBUG:
            print(f"🐛 调试模式已启用")
        
        # 创建Jarvis实例
        jarvis = JarvisAgent(llm_cfg)
        
        # 显示可用工具
        tools = jarvis.get_available_tools()
        tool_names = [tool['name'] for tool in tools]
        print(f"🛠️  可用工具 ({len(tools)}个): {', '.join(tool_names)}")
        
        # 在调试模式下显示自动生成的系统提示
        if log_level == logging.DEBUG:
            print("\n🔍 自动生成的系统提示:")
            print("-" * 50)
            system_msg = jarvis._generate_system_message()
            print(system_msg)
            print("-" * 50)
        
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
        logger.debug(f"❌ 错误详情: {traceback.format_exc()}")
        print(f"❌ 程序启动失败: {e}")


if __name__ == "__main__":
    main() 