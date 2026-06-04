# Contract: uma_path_utils.py

## 基本信息

- 组件名：`UMA Path Utils`
- 所属模块族：`materials / uma / func_utils`
- 统一入口：`resolve_jd_path`
- 注册名：`not_applicable`
- 主源码：`./onescience/src/onescience/modules/func_utils/uma_path_utils.py`

## 组件职责

解析 UMA 初始化所需的 `Jd.pt` 路径，保证 Wigner/rotation basis 常量能被模型加载。

## 输入契约

- 可选 `jd_path`
- 环境变量：`ONESCIENCE_UMA_JD_PATH`
- checkpoint 附近路径
- 当前工作目录或 package 内置路径候选

## 输出契约

- 返回可读的 `Jd.pt` 绝对路径
- 找不到时抛出明确异常

## 关键参数

- `jd_path`
- `ONESCIENCE_UMA_JD_PATH`

## 典型调用位置

- `eSCNMDBackbone` 初始化
- UMA checkpoint 推理
- UMA fine-tuning Hydra 配置
- `FAIRChemCalculator` 初始化

## 常见修改点

- 部署到新集群：优先显式传 `jd_path` 或设置环境变量。
- 打包 checkpoint：确保 `Jd.pt` 与模型文件一起发布。
- 多节点运行：确认所有节点看到的是同一路径。

## 风险点

- 运行目录变化后，依赖 `cwd/models/Jd.pt` 的隐式路径容易失效。
- 多节点作业需要所有 rank 都能访问同一路径。
- Jd 常量与 `lmax/mmax` 假设不一致会造成初始化或 forward 错误。

## 源码锚点

- `./onescience/src/onescience/modules/func_utils/uma_path_utils.py`
- `./onescience/src/onescience/models/UMA/uma_escn_md.py`
- `./onescience/src/onescience/utils/uma/calculate/pretrained_mlip.py`

## 下钻关系

- 主模型：`./uma_hydra_model.md`
- calculator：`./uma_calculator.md`
