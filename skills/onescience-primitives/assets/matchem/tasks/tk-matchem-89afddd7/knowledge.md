# 骨架任务：Li/Ni 混排与结构稳定性计算

- domain: matchem
- 复用场景数: 1
- 实例任务数: 1

## 步骤描述（跨场景聚合去重）
- 在母体和掺杂结构中枚举对称不等价的 Li/Ni 交换构型，计算混排能；同时提取脱锂引起的晶格参数、体积和层间距变化。

## 执行 prompt（跨场景聚合去重）
- 基于 {RELAXED_STRUCTURES} 构造对称不等价 Li/Ni 混排构型，计算 Emixing=E(mixed)-E(layered)，并统计 Δa、Δc、ΔV、层间距变化；明确 Emixing 的符号约定。

## 输入槽（var/hint/default）
- {RELAXED_STRUCTURES} | required=True | type=doc | var_name=弛豫结构集合 | hint=s02 输出。 | default={RELAXED_STRUCTURES}
- {LI_CONTENT} | required=True | type=float | var_name=脱锂状态 | hint=用于比较相同 x。 | default={LI_CONTENT}

## 产出
- Li/Ni 混排能表
- 晶格应变与体积变化表
- 结构稳定性对比图

## 质量门禁 quality_gate
- 不得把较低混排能误报为更稳定的层状结构
- 混排构型与母体参考结构具有相同化学计量
- 能量差采用统一参考零点并保留结构文件

## 可调资源（edge:resource，仅真实存在）
- tools/pymatgen

## 实例任务（本骨架在各场景的实例化）
- it-95688cfa

## 复用场景
- LiNiCo_高镍层状正极掺杂结构优化与应变风险分析
