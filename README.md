# Jarvis - 基于Qwen-Agent的模块化AI助手

本项目基于[Qwen-Agent](https://github.com/QwenLM/Qwen-Agent)框架，采用模块化架构实现了一个支持Function Calls的本地AI助手。

## 🎯 功能特性

- ✅ 模块化工具管理架构
- ✅ 基础对话功能
- ✅ 自定义Function Calls（时间查询、数学计算）
- ✅ 详细的日志输出（便于调试）
- ✅ 支持硅基流动API
- ✅ 易于扩展新工具

## 📁 项目结构

```
jarvis/
├── .env                    # API配置文件
├── requirements.txt        # 项目依赖
├── README.md              # 项目说明
├── jarvis.py              # 🎯 主程序入口 (模块化架构)
├── hello_world.py         # 基础对话示例
├── run.sh                 # 一键启动脚本
├── TODO.md               # 任务记录
└── tools/                 # 🔧 工具包目录
    ├── __init__.py        # 工具包初始化，工具注册
    ├── base.py           # 工具基类定义
    ├── registry.py       # 工具注册表管理
    ├── time_tool.py      # 时间查询工具
    ├── calculator_tool.py # 计算器工具
    └── create_tool.py    # 新工具创建脚本
```

## 🚀 快速开始

### 1. 环境准备

确保已激活conda环境：

```bash
conda activate qwen
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置API

项目使用硅基流动的API，配置信息在`.env`文件中：

```bash
# 硅基流动API配置
OPENAI_API_KEY=your-api-key-here
OPENAI_BASE_URL=https://api.siliconflow.cn/v1
MODEL_NAME=deepseek-ai/DeepSeek-V2.5
```

## 💻 使用方法

### 主程序 - 模块化Function Calls

```bash
python jarvis.py
# 或者使用启动脚本
./run.sh
```

支持的功能：
- **时间查询**: "现在几点了？"、"what time is it?"
- **数学计算**: "计算3*14/2"、"帮我算一下sqrt(16)"
- **终端命令**: "执行ls -la命令"、"查看当前目录"、"运行pwd命令"
- **普通对话**: 任何其他问题

### 基础示例

```bash
python hello_world.py
```

仅支持基础对话功能，适合测试API连接。

## 🛠️ 工具管理

### 当前可用工具

1. **get_current_time** - 获取当前时间
   - 文件: `tools/time_tool.py`
   - 支持时区参数
   - 返回详细的时间信息

2. **calculator** - 数学计算器
   - 文件: `tools/calculator_tool.py`
   - 支持基本运算符 (+, -, *, /)
   - 支持数学函数 (sqrt, sin, cos, etc.)
   - 安全的表达式解析

3. **execute_terminal_command** - 终端命令执行
   - 文件: `tools/terminal_tool.py`
   - 支持大部分常见命令行操作 (ls, pwd, echo, cat等)
   - 包含安全检查，禁止危险命令
   - 30秒执行超时保护

4. **get_weather** - 天气查询 (示例，未启用)
   - 文件: `tools/weather_tool.py`
   - 模拟天气数据，可扩展为真实API

### 🔧 添加新工具

#### 方法1: 使用工具生成脚本

```bash
cd tools
python create_tool.py <tool_name> <ClassName> "工具描述"

# 示例：创建翻译工具
python create_tool.py translate TranslateTool "文本翻译工具"
```

这将自动生成工具模板文件，然后：

1. 编辑生成的工具文件，实现具体逻辑
2. 在 `tools/__init__.py` 中注册新工具：
   ```python
   from .translate_tool import TranslateTool
   tool_registry.register(TranslateTool())
   ```
3. 重启Jarvis即可使用

#### 方法2: 手动创建工具

1. **继承BaseTool类**：
   ```python
   from tools.base import BaseTool
   
   class YourTool(BaseTool):
       def get_name(self) -> str:
           return "your_tool_name"
       
       def get_description(self) -> str:
           return "工具描述"
       
       def get_parameters(self) -> Dict[str, Any]:
           return {
               "type": "object",
               "properties": {
                   "param1": {
                       "type": "string",
                       "description": "参数描述"
                   }
               },
               "required": ["param1"]
           }
       
       def execute(self, param1: str) -> str:
           # 实现工具逻辑
           result = {"result": f"处理结果: {param1}"}
           return json.dumps(result, ensure_ascii=False)
   ```

2. **注册工具**：
   在 `tools/__init__.py` 中添加：
   ```python
   from .your_tool import YourTool
   tool_registry.register(YourTool())
   ```

### 工具架构优势

- **模块化**: 每个工具独立文件，易于维护
- **统一接口**: 所有工具继承BaseTool，接口一致
- **自动注册**: 通过ToolRegistry自动管理工具
- **类型安全**: 完整的类型注解
- **错误处理**: 统一的错误处理和日志记录
- **易于测试**: 每个工具可独立测试

## 📊 日志输出

程序包含详细的日志输出，方便调试：

- `📝` 注册工具信息
- `📝` 用户输入记录
- `🔄` LLM调用状态
- `🔧` 工具调用检测
- `✅` 成功状态
- `❌` 错误信息

## 🔧 故障排除

### 常见问题

1. **API连接失败**: 检查`.env`文件中的API配置
2. **模型不支持Function Calls**: 确保使用支持的模型（如DeepSeek-V2.5）
3. **工具调用失败**: 查看日志中的详细错误信息
4. **导入错误**: 确保tools包结构正确，__init__.py文件存在

### 调试模式

如需更详细的调试信息，可以修改`jarvis.py`中的日志级别：

```python
logging.basicConfig(level=logging.DEBUG, ...)
```

## 📋 开发记录

详细的开发过程和任务完成情况请查看`TODO.md`文件。

## 🤝 贡献

欢迎提交问题和改进建议！新工具的贡献特别欢迎。 