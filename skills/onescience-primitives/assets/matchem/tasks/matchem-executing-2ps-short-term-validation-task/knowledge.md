# 骨架任务：执行 2 ps 短时验证

- domain: matchem
- 复用场景数: 1
- 实例任务数: 1

## 步骤描述（跨场景聚合去重）
- 软件依赖、固定原子、控温及续算预检通过后，用 LAMMPS + MACE 分别执行 2 ps 短测。

## 执行 prompt（跨场景聚合去重）
- 在 {TEST_DURATION_PS} 的短测中，依据获准的共同温度、系综、步长与采样方案执行 C12/C13 动力学。明确授权自主定案时，优先采用已给且可核验的工况，其余按已授权资料、模型适用域、真实引擎接口及实际资源定案，事前记录依据、选择和偏离。必要条件无法据证确定时，停止相应门禁并交付原因与最后健康材料。交互或未经授权自主定案时按调用方的确认流程执行，长时采样另行授权。 上游模型准入和两套预检通过后，分别报告有效时间、温度、能量、约束、轨迹和续算证据。

## 输入槽（var/hint/default）
- {TEST_DURATION_PS} | required=True | type=float | var_name=短时测试时长 | hint=每种同位素 2 ps | default=2.0
- {TARGET_TEMPERATURE} | required=False | type=float | var_name=目标温度 | hint=优先用已给且核实的温度；获明确自主授权时按证据定案，缺依据则停门；其余按确认流程 | default=None

## 产出
- C12 测试轨迹
- C13 测试轨迹
- 运行质量报告
- 温度和能量输出、运行日志、重启文件和续算记录

## 质量门禁 quality_gate
- 无未解释异常
- 模型正常加载
- 约束持续有效
- 轨迹与续算材料可用

## 可调资源（edge:resource，仅真实存在）
- 实际模型和引擎证据由实例任务绑定。

## 实例任务（本骨架在各场景的实例化）
- matchem-executing-2ps-short-term-co2-cu111-water-k-interface-inst

## 复用场景
- CO2_Cu111_12C13C_MACE_LAMMPS动力学验证
