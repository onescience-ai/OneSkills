# 骨架任务：独立验证与结论

- domain: matchem
- 复用场景数: 21
- 实例任务数: 21

## 步骤描述（跨场景聚合去重）
- 用独立实验或高保真计算验证优先候选。

## 执行 prompt（跨场景聚合去重）
- 有 {VALIDATION_DATA} 时进行独立验证；没有时明确为待验证预测，不得宣称实验成功。

## 输入槽（var/hint/default）
- {VALIDATION_DATA} | required=False | type=doc | var_name=独立验证数据 | hint=留出测试集、外部实验或高保真计算结果。 | default=optional

## 产出
- PASS/REJECT/BLOCKED 结论
- 验证对照

## 质量门禁 quality_gate
- 失败候选保留记录
- 预测与验证分开报告

## 可调资源（edge:resource，仅真实存在）
- models/data-efficient-machine-learning-potentials-modeling-catalytic

## 实例任务（本骨架在各场景的实例化）
- matchem-independent-validation-b2-multi-principal-intermeta-inst
- matchem-independent-validation-co2-photocatalyst-data-inst
- matchem-independent-validation-half-heusler-thermoelectric-inst
- matchem-independent-validation-halide-perovskite-compatible-inst
- matchem-independent-validation-high-entropy-carbide-hardnes-inst
- matchem-independent-validation-high-entropy-ceramic-ml-inst
- matchem-independent-validation-high-entropy-solid-solution-inst
- matchem-independent-validation-lead-free-hybrid-perovskite-inst
- matchem-independent-validation-long-acting-injectable-inst
- matchem-independent-validation-mechanical-metamaterial-inst
- matchem-independent-validation-metallic-glass-machine-inst
- matchem-independent-validation-mof-mechanical-stability-inst
- matchem-independent-validation-mof-synthesis-multimodal-inst
- matchem-independent-validation-organic-semiconductor-inst
- matchem-independent-validation-perovskite-crystallization-inst
- matchem-independent-validation-perovskite-encapsulation-inst
- matchem-independent-validation-perovskite-temperature-inst
- matchem-independent-validation-porous-material-data-efficie-inst
- matchem-independent-validation-thermal-metamaterial-visible-inst
- matchem-independent-validation-thermally-stable-inorganic-inst
- matchem-independent-validation-vibration-stable-material-inst

## 复用场景
- B2多主元金属间化合物单相发现
- CO2光催化剂数据驱动可合成性筛选
- MOF合成应用多模态机器学习关联
- MOF结构力学稳定性机器学习预测
- 力学超材料目标响应逆向设计
- 半赫斯勒热电材料无监督发现
- 卤化物钙钛矿兼容分子数据驱动优化
- 多孔材料数据高效基础模型构建
- 振动稳定材料机器学习筛选
- 无铅杂化钙钛矿稳定性机器学习筛选
- 有机半导体主动学习发现
- 热稳定无机荧光粉主晶格机器学习筛选
- 热超材料可见红外兼容伪装逆向设计
- 金属玻璃机器学习成分筛选
- 钙钛矿封装层降解抑制机器学习筛选
- 钙钛矿温度稳定性机器人学习发现
- 钙钛矿结晶机器学习加速优化
- 长效注射聚合物配方机器学习优化
- 高熵固溶体形成机器学习预测
- 高熵碳化物硬度成分机器学习设计
- 高熵陶瓷机器学习发现
