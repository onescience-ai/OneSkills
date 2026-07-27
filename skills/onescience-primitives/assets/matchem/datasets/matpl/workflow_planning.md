## description
为 MatPL/PWMLFF 多格式材料势数据选择 parser、split、训练和验证路线的规划知识。

## when_to_use
当任务需要使用 `matchem/matpl` 中 AuAg、Cu、HfO2、LiSiC 数据训练 PWMLFF/MatPL 力场、解析 MOVEMENT 或验证 LAMMPS 力场时使用。

## inputs
数据获取路径：`/public/share/sugonhpcapp01/onestore/onedatasets/matchem/matpl`。任务输入规范：extxyz、PWdata 目录、MOVEMENT 文件、训练/测试 JSON 和可选 LAMMPS 资产。

## outputs
输出为格式化样本索引、parser 选择、元素表、train/val/test split、能量/力/virial 字段定义和验证协议。

## procedure
1. 先确定材料体系：AuAg、Cu、HfO2、LiSiC 或多体系混合。
2. 按文件类型选择 parser：ASE 处理 xyz，PWMLFF/PWmat parser 处理 MOVEMENT，MatPL/PWMLFF reader 处理 PWdata。
3. 明确哪些目录是训练样本，哪些是 LAMMPS 运行资产。
4. 使用已有 `nn_train.json`、`nn_test.json`、`valid_movement` 或按组分/轨迹隔离建立 split。
5. 抽样解析 frame，确认元素、坐标、cell、energy、force、virial/stress 单位和 shape。
6. 生成训练配置并做单 batch 验证。
7. 按体系、组分和 split 输出评测指标。

## constraints
不要把 `nn_lmps` 当作监督样本；不要在相邻轨迹帧上做泄漏式随机划分；混合体系必须显式声明元素表和采样权重。

## next_phase_recommendation
若 parser 和 split 已明确，进入 PWMLFF/MatPL 训练；若 parser 不确定，先对单个小文件做解析 smoke test。

## fallback
若某个 PWdata 子目录无法解析，保留失败日志并从可解析子集开始；若 virial/stress 缺失，降级为 energy/force 训练。
