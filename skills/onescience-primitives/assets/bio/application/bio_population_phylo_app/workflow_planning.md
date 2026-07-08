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
2. 选择对应模板或轻量工具。
3. coder 生成参数化命令或补全 manifest。
4. 若用户要正式推断或统计建模，交给后续分析流程和 runtime。

# constraints

- 不得混淆亲缘、群体结构、系统发育和传播链证据。
- 不得在缺少参考、群体来源或采样时间时解释结果。
- 应用卡只生成交接和工具入口，不直接代表已执行工具。

# next_phase_recommendation

正式树推断、GWAS、填补或传播分析应转入对应分析应用或执行配置，并由 runtime 执行。

# fallback

若输入不足，输出缺失字段清单和模板；若格式不确定，先执行轻量 QC 或要求用户确认列名映射。
