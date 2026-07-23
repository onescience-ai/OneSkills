# description

把群体遗传和系统发育请求转为可执行轻量 QC 或标准化分析计划。

# when_to_use

用于 Newick 树校验、GWAS summary stats 检查、比较基因组计划、填补/PRS 交接和病原监测元数据整理。

# inputs

- 输入数据类型：Newick、VCF/PLINK、GWAS summary、alignment、metadata。
- taxon/population、reference/build、sample metadata。
- statistical model、QC checkpoints 和 interpretation limits。

# outputs

- QC JSON/表格。
- 分析计划 YAML 或 manifest。
- 下游正式分析的交接材料。

# procedure

1. 根据任务标签判定是 phylo、GWAS、comparative genomics、imputation/PRS 还是 surveillance。
2. 选择对应模板或最小 Python 工具脚本，并确定用户输入、输出路径和脚本参数。
3. 从用户明确提供的项目目录创建或复用 `<project_dir>/app/`；复制选中的 `.py` 入口及其本地 Python 依赖闭包并保持相对结构，目标同名文件已存在时先比较内容，未经确认不得覆盖。
4. 静态分析复制后脚本的 import，把标准库、本地模块和第三方包分开，形成所需包及版本约束清单。
5. 在当前 Python 环境检查第三方包是否已安装、已安装版本是否满足约束，并以只读依赖解析检查安装或升级是否会破坏现有包约束。
6. 若依赖均已存在且兼容，跳过安装；若有已安装但版本冲突的依赖，报告包名、当前版本、要求版本和受影响包，等待用户选择环境隔离、调整版本或停止。
7. 若依赖缺失且解析无冲突，向用户说明待安装包、版本和目标环境并询问是否安装；得到明确同意后才可安装。若缺失依赖的安装会产生冲突，报告冲突和可选方案，由用户选择，禁止自动安装。
8. 依赖门禁通过后，coder 生成指向 `<project_dir>/app/` 内复制脚本的参数化命令或补全 manifest，并使用用户已确认的输入执行。若用户要正式推断或统计建模，交给后续分析流程和 runtime。

# constraints

- 不得混淆亲缘、群体结构、系统发育和传播链证据。
- 不得在缺少参考、群体来源或采样时间时解释结果。
- 应用卡只生成交接和工具入口，不直接代表已执行工具。

# next_phase_recommendation

正式树推断、GWAS、填补或传播分析应转入对应分析应用或执行配置，并由 runtime 执行。

# fallback

若输入不足，输出缺失字段清单和模板；若格式不确定，先执行轻量 QC 或要求用户确认列名映射。
