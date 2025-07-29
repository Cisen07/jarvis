#!/usr/bin/env python3
"""
Jarvis Hello World 示例
最简单的对话功能演示
"""

import os
from dotenv import load_dotenv
from qwen_agent.agents import Assistant

def main():
    print("🚀 Jarvis Hello World 示例")
    print("=" * 40)
    
    # 加载环境变量
    load_dotenv()
    
    # 配置LLM
    llm_cfg = {
        'model': os.getenv('MODEL_NAME', 'deepseek-ai/DeepSeek-V2.5'),
        'model_server': os.getenv('OPENAI_BASE_URL', 'https://api.siliconflow.cn/v1'),
        'api_key': os.getenv('OPENAI_API_KEY'),
        'generate_cfg': {
            'top_p': 0.8,
            'temperature': 0.7
        }
    }
    
    print(f"📝 使用模型: {llm_cfg['model']}")
    
    try:
        # 创建Assistant
        bot = Assistant(llm=llm_cfg, name='Jarvis', description='智能AI助手')
        print("✅ Jarvis启动成功!")
        
        print("\n💬 开始对话 (输入 'quit' 退出):")
        print("-" * 40)
        
        while True:
            user_input = input("\n用户: ").strip()
            if user_input.lower() in ['quit', 'exit', '退出']:
                print("👋 再见!")
                break
            
            if not user_input:
                continue
            
            # 获取回复
            response = []
            for chunk in bot.run(user_input):
                response.append(chunk)
            
            print(f"Jarvis: {''.join(response)}")
            
    except Exception as e:
        print(f"❌ 启动失败: {e}")

if __name__ == "__main__":
    main() 