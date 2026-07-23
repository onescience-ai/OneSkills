# description

把实验室仪器输出标准化为 ASM JSON/CSV，并形成 LIMS/ELN 或数据工程 handoff。

# when_to_use

用于 plate reader、qPCR、cell counter、spectrophotometer、chromatography、electrophoresis 等仪器文件标准化。

# inputs

- instrument_type 和 input_files。
- raw_measurements、calculated_fields、metadata_fields。
- target_schema、validation_rules 和 deliverable。

# outputs

- ASM JSON。
- flattened CSV。
- validation report。
- parser handoff。

# procedure

1. 根据任务标签判断任务属于仪器数据标准化。
2. 读取字段分类和支持仪器边界。
3. 选择本 application 的最小 Python 脚本集合，并确定用户输入、输出路径、仪器类型和参数。
4. 从用户明确提供的项目目录创建或复用 `<project_dir>/app/`；复制选中的 `.py` 入口及其本地 Python 依赖闭包并保持相对结构，目标同名文件已存在时先比较内容，未经确认不得覆盖。
5. 静态分析复制后脚本的 import，把标准库、本地模块和第三方包分开，形成所需包及版本约束清单。
6. 在当前 Python 环境检查第三方包是否已安装、已安装版本是否满足约束，并以只读依赖解析检查安装或升级是否会破坏现有包约束。
7. 若依赖均已存在且兼容，跳过安装；若有已安装但版本冲突的依赖，报告包名、当前版本、要求版本和受影响包，等待用户选择环境隔离、调整版本或停止。
8. 若依赖缺失且解析无冲突，向用户说明待安装包、版本和目标环境并询问是否安装；得到明确同意后才可安装。若缺失依赖的安装会产生冲突，报告冲突和可选方案，由用户选择，禁止自动安装。
9. 依赖门禁通过后，coder 生成指向 `<project_dir>/app/` 内复制脚本的参数化命令或 parser 扩展任务；runtime 使用用户已确认的输入执行转换、校验和展平。

# constraints

- 不得混淆原始测量和计算值。
- 不得自动换算不明单位。
- 不得丢失样本、孔位、批次和仪器设置。

# next_phase_recommendation

转换后可交给 QC report app 生成报告，或交给数据工程扩展生产 parser。

# fallback

若仪器类型不支持，输出字段分类表和 parser 开发 handoff；若单位/字段不明，只执行结构检查并列出待确认项。
