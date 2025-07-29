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