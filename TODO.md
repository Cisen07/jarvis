# 背景

我希望在本目录下（./jarvis），基于Qwen-Agent（https://github.com/QwenLM/Qwen-Agent）实现一个本地的Agent。

基础环境已经安装好了：

```
(qwen)  chailin@chailindeMacBook-Air  ~  conda activate qwen
```

## git

本项目的git配置：

```
(qwen)  chailin@chailindeMacBook-Air  ~/go/src/jarvis   main ±  git config --get user.name && git config --get user.email && git config --get core.sshCommand
Cisen07
935520966@qq.com
ssh -i ~/.ssh/github -F /dev/null
(qwen)  chailin@chailindeMacBook-Air  ~/go/src/jarvis   main ± 
```

本项目的远程git仓库：

```
git@github.com:Cisen07/jarvis.git
```

## API Key

使用硅基流动的API，相关配置如下：

```
model = "GLM-4.1V-9B-Thinking" # 或者平台中的其他支持 function calling 模型，参见[Function Calling](https://docs.siliconflow.cn/cn/userguide/guides/function-calling)
base_url = "https://api.siliconflow.cn/v1"
api_key = "your-api-key-here"
```

# 任务

- [x] 任务1.1: 阅读https://github.com/QwenLM/Qwen-Agent之后，基础的代码框架在./jarvis目录中搭建出来，并完成hello world。看看有没有预置的Function Calls？如果有的话，选取其中比较简单的进行调试；如果没有的话，实现一个简单的本地可用的Function Calls试试。

- [x] 任务1.2: 如果我希望实现一个自动多轮交互的版本呢？看起来当前的框架并不支持agent自行进行多function call调用：

**核心变更：**
1. **自动多轮交互机制**：重构`process_message`方法，支持在单个用户请求中自动进行多轮LLM调用
2. **智能迭代控制**：添加`_handle_response_iteration`方法，能够判断是否需要继续迭代还是返回最终答案
3. **规划响应识别**：实现`_seems_like_planning_response`方法，识别LLM是否在规划任务（如"首先...然后..."）而非给出最终答案
4. **综合回答优化**：改进系统提示，要求LLM在最终回答中包含所有问题的答案，不只回答最后一个问题
5. **强制完整回答**：在最后几轮迭代时添加提醒，确保LLM给出综合性的完整回答

**测试结果：**
成功实现了自动多轮交互，能够在一个用户请求中依次调用多个工具（如先获取时间，再进行计算）。

**关键改进 - LLM决定结束机制：**
引入`[FINAL]`标记让LLM自主决定何时结束交互：
- 系统提示指导LLM在完成所有任务时使用`[FINAL]`标记
- 检测到`[FINAL]`标记时立即结束交互并返回最终答案
- 移除所有启发式判断逻辑，完全信任LLM的决策
- 避免了强制判断和无限循环的问题

```
改进后的交互流程：
用户: 现在几点？以及123*2345等于多少？
第1轮：调用get_current_time工具获取时间
第2轮：调用calculator工具计算结果  
第3轮：LLM回复"[FINAL]现在是XX时间，123*2345=288435"
系统检测到[FINAL]标记，结束交互并返回完整答案
``` 

- [x] 任务1.3: 新增一个工具，能够执行终端命令。如何新增工具请参考jarvis/README.md中的说明。

**核心变更：**
1. **新增TerminalTool工具**：创建`tools/terminal_tool.py`，实现终端命令执行功能
2. **安全防护机制**：内置危险命令检测，禁止执行如`rm -rf /`、`shutdown`等危险操作
3. **执行环境控制**：支持指定工作目录，默认使用当前目录；30秒超时保护避免无限等待
4. **命令解析安全**：使用`shlex.split`安全解析命令参数，避免注入攻击；不使用shell模式执行
5. **详细结果返回**：返回包含命令、工作目录、返回码、标准输出、标准错误的完整信息
6. **工具注册集成**：在`tools/__init__.py`中注册新工具，支持通过LLM自动调用

**测试结果：**
成功实现终端命令执行功能，能够安全执行常见命令如`ls`、`pwd`、`echo`、`cat`等，同时具备完善的安全防护和错误处理机制。

- [x] 任务1.4: 我已经调整了system prompt以强调了【不要使用诸如tool▁calls▁begin这样单轮多function_call的模式，一次交互最多只能调用一个工具】，但是不是我的prompt写的不够好，看起来还是不太行。

**核心变更：**
1. **自定义工具调用格式支持**：新增`_contains_custom_tool_call`和`_parse_custom_tool_call`方法，支持解析`<｜tool▁calls▁begin｜>`等Qwen-Agent特有的工具调用格式
2. **智能格式检测**：在响应处理中添加自定义格式检测，能够识别并正确解析非标准OpenAI格式的工具调用
3. **兼容性增强**：同时支持标准function_call格式和自定义工具调用格式，提高模型兼容性
4. **改进的System Prompt**：优化系统提示，明确说明支持的工具调用格式和使用规则
5. **错误处理完善**：增强JSON解析和工具调用的错误处理机制，提供详细的错误信息和日志

**测试结果：**
成功解决了LLM使用`<｜tool▁calls▁begin｜>`格式导致的工具调用失败问题，现在能够正确识别和执行自定义格式的工具调用。

```
(qwen)  chailin@chailindeMacBook-Air  ~/go/src/jarvis   main ±  ./run.sh --log-level INFO
🤖 启动 Jarvis AI助手...
================================
🚀 启动Jarvis...
🤖 Jarvis - 智能AI助手 (自动多轮交互版本)
==================================================
📝 使用模型: deepseek-ai/DeepSeek-V2.5
🔗 API地址: https://api.siliconflow.cn/v1
2025-07-29 18:10:25,357 - INFO - 🚀 创建LLM实例...
2025-07-29 18:10:25,358 - INFO - ✅ LLM创建成功!
🛠️  可用工具 (3个): get_current_time, calculator, execute_terminal_command

💬 开始对话 (输入 'quit' 退出):
--------------------------------------------------

用户: 告诉我/Users/chailin/go/src/platform/test.go这个文件中有多少个字段。
2025-07-29 18:10:41,969 - INFO - 📝 用户输入: 告诉我/Users/chailin/go/src/platform/test.go这个文件中有多少个字段。
2025-07-29 18:10:41,974 - INFO - 🔄 开始自动多轮对话处理...
2025-07-29 18:10:41,976 - INFO - 🔄 第 1 轮对话
2025-07-29 18:10:41,976 - INFO - 💭 向LLM发送用户问题，等待分析和响应...
2025-07-29 18:11:04,121 - INFO - HTTP Request: POST https://api.siliconflow.cn/v1/chat/completions "HTTP/1.1 200 OK"
2025-07-29 18:11:04,144 - INFO - 📤 处理响应: {'role': 'assistant', 'content': "要统计 `/Users/chailin/go/src/platform/test.go` 文件中有多少个字段，我们可以使用 `execute_terminal_command` 工具来执行一个终端命令，该命令将读取文件内容并统计字段数。\n\n首先，我们需要读取文件内容，然后使用正则表达式或其他方法来统计字段数。不过，为了简化操作，我们可以假设字段是以大写字母开头的标识符，并且每个字段之间用空格或换行符分隔。\n\n以下是一个可能的命令：\n\n```bash\ngrep -oE '[A-Z][a-zA-Z0-9]*' /Users/chailin/go/src/platform/test.go | wc -l\n```\n\n这个命令会匹配所有以大写字母开头的标识符，并统计它们的数量。\n\n接下来，我们调用 `execute_terminal_command` 工具来执行这个命令。\n\n", 'extra': {}}
2025-07-29 18:11:04,144 - INFO - 💬 LLM提供了文本响应: 要统计 `/Users/chailin/go/src/platform/test.go` 文件中有多少个字段，我们可以使用 `execute_terminal_command` 工具来执行一个终端命令，该命令将读取文件内容并统计字段数。

首先，我们需要读取文件内容，然后使用正则表达式或其他方法来统计字段数。不过，为了简化操作，我们可以假设字段是以大写字母开头的标识符，并且每个字段之间用空格或换行符分隔。

以下是一个可能的命令：

```bash
grep -oE '[A-Z][a-zA-Z0-9]*' /Users/chailin/go/src/platform/test.go | wc -l
```

这个命令会匹配所有以大写字母开头的标识符，并统计它们的数量。

接下来，我们调用 `execute_terminal_command` 工具来执行这个命令。


2025-07-29 18:11:04,144 - INFO - 🤔 LLM可能需要更多信息或进一步思考，继续对话...
2025-07-29 18:11:04,144 - INFO - 🔄 第 2 轮对话
2025-07-29 18:11:04,144 - INFO - 💭 向LLM发送工具执行结果，等待进一步处理...
2025-07-29 18:11:15,246 - INFO - HTTP Request: POST https://api.siliconflow.cn/v1/chat/completions "HTTP/1.1 200 OK"
2025-07-29 18:11:15,268 - INFO - 📤 处理响应: {'role': 'assistant', 'content': '<｜tool▁calls▁begin｜>', 'extra': {}}
2025-07-29 18:11:15,271 - INFO - 💬 LLM提供了文本响应: <｜tool▁calls▁begin｜>
2025-07-29 18:11:15,271 - INFO - 🤔 LLM可能需要更多信息或进一步思考，继续对话...
2025-07-29 18:11:15,271 - INFO - 🔄 第 3 轮对话
2025-07-29 18:11:15,271 - INFO - 💭 向LLM发送工具执行结果，等待进一步处理...
2025-07-29 18:11:19,615 - INFO - HTTP Request: POST https://api.siliconflow.cn/v1/chat/completions "HTTP/1.1 200 OK"
2025-07-29 18:11:19,617 - INFO - 📤 处理响应: {'role': 'assistant', 'content': '<｜tool▁calls▁begin｜><｜tool▁call▁begin｜>function<｜tool▁sep｜>execute_terminal_command\n```json\n{"command": "grep -oE \'[A-Z][a-zA-Z0-9]*\' /Users/chailin/go/src/platform/test.go | wc -l"}\n```<｜tool▁call▁end｜><｜tool▁calls▁end｜>', 'extra': {}}
2025-07-29 18:11:19,618 - INFO - 💬 LLM提供了文本响应: <｜tool▁calls▁begin｜><｜tool▁call▁begin｜>function<｜tool▁sep｜>execute_terminal_command
```json
{"command": "grep -oE '[A-Z][a-zA-Z0-9]*' /Users/chailin/go/src/platform/test.go | wc -l"}
```<｜tool▁call▁end｜><｜tool▁calls▁end｜>
2025-07-29 18:11:19,618 - INFO - 🤔 LLM可能需要更多信息或进一步思考，继续对话...
2025-07-29 18:11:19,618 - INFO - 🔄 第 4 轮对话
2025-07-29 18:11:19,618 - INFO - 💭 向LLM发送工具执行结果，等待进一步处理...
2025-07-29 18:11:30,946 - INFO - HTTP Request: POST https://api.siliconflow.cn/v1/chat/completions "HTTP/1.1 200 OK"
2025-07-29 18:11:30,948 - INFO - 📤 处理响应: {'role': 'assistant', 'content': '<｜tool▁calls▁begin｜>\n\n<｜tool▁call▁begin｜>function<｜tool▁sep｜>execute_terminal_command\n```json\n{"command": "grep -oE \'[A-Z][a-zA-Z0-9]*\' /Users/chailin/go/src/platform/test.go | wc -l"}\n```<｜tool▁call▁end｜><｜tool▁calls▁end｜>', 'extra': {}}
2025-07-29 18:11:30,948 - INFO - 💬 LLM提供了文本响应: <｜tool▁calls▁begin｜>

<｜tool▁call▁begin｜>function<｜tool▁sep｜>execute_terminal_command
```json
{"command": "grep -oE '[A-Z][a-zA-Z0-9]*' /Users/chailin/go/src/platform/test.go | wc -l"}
```<｜tool▁call▁end｜><｜tool▁calls▁end｜>
2025-07-29 18:11:30,948 - INFO - 🤔 LLM可能需要更多信息或进一步思考，继续对话...
2025-07-29 18:11:30,948 - INFO - 🔄 第 5 轮对话
2025-07-29 18:11:30,948 - INFO - 💭 向LLM发送工具执行结果，等待进一步处理...
^C

👋 程序被中断，再见!
(qwen)  chailin@chailindeMacBook-Air  ~/go/src/jarvis   main ± 
```
