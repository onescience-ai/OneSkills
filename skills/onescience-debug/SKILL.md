---
name: onescience-debug
description: 对 OneScience 项目的测试识别与测试编排技能。用于识别一个请求是否属于可测试任务，并在模型测试、Earth DataPipe 测试、完整训练或推理流程测试这三类测试路径中自动映射到最合适的一条。适用于用户要求验证 OneScience 相关实现是否可执行、可读取、可启动、可运行若干步，尤其是涉及 model、datapipe 或 dataset、train、inference、config、runner、case 目录等内容的任务。用户不需要显式说明应采用哪条测试路径，技能应根据任务范围与交付边界自行判断。
---

# OneScience 测试技能

这个技能的目标是先判断任务是不是“可测试任务”，再把它映射到最合适的测试路径。不要要求用户先说明该走哪条测试路径。

当你需要判断任务识别层级、典型信号或测试路径映射时，读取 `./references/test_routing.md`。
当你需要处理“远程测试上下文不完整”的异常场景时，读取 `../../references/remote_fallback.md`。

## 执行闭环

1. 先判断任务是否属于可测试任务。
2. 再按 `./references/test_routing.md` 的规则确定最合适的测试路径。
3. 只读取该测试路径对应的 reference。
4. 提取入口文件、依赖、配置和最小运行参数。
5. 优先复用已有测试脚本与执行脚本。
6. 缺失时按对应 reference 补齐最小可运行测试资产。
7. 优先使用当前环境可用的执行方式提交测试；若测试依赖远程环境，先调用 `onescience-hardware` 获取完整硬件画像，再由合适的执行层提交测试；运行类测试优先交给 `onescience-runtime`，环境未就绪时先交给 `onescience-installer`；若存在 `scnet` MCP 且任务适合远程执行，也可通过它收集 `.out` / `.err`。
8. 输出结构化测试报告；若未成功提交，则先报告提交失败，不推断结果。

## 分层边界

- 本 skill 负责判断“测什么、怎么测、如何汇报”，不负责替代 `onescience-runtime` 做运行提交
- 当测试只需要代码适配信息时，可参考实现侧上下文；当测试需要远程连接、队列、module、conda 或路径事实时，必须依赖完整硬件画像
- 不要把给 `onescience-coder` 使用的代码生成交接摘要误当成远程测试执行输入
- 若远程测试所需环境事实缺失，只阻断远程测试阶段，不要误报整个代码任务失败

## 输出要求

- 当前任务为何属于可测试任务
- 识别出的任务类型
- 最终映射到的测试路径
- 这样映射的依据
- 实际执行的测试项
- PASS / FAIL 或可执行 / 不可执行结论
- 关键错误、风险和后续建议

## 约束

- 当前只允许映射到 3 条测试路径：`./references/e2e_pipeline_test.md`、`./references/model_test.md`、`./references/earth_datapipe_test.md`。
- 不要要求用户显式指定测试路径。
- 不要因为任务里出现 model 或 datapipe 关键词，就直接映射到局部测试。
- 不要自动安装依赖；缺什么就报告什么。
- 不要在没有执行证据时声称“测试通过”。
- 不要把某一种特定执行后端写死成唯一选择。
