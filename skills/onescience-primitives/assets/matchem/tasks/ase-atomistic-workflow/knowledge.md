# ASE 原子尺度工作流 (ase-atomistic-workflow)

## 任务目标
以 ASE（Atomic Simulation Environment）为统一框架，提供后端无关的原子尺度模拟工作流编排：将用户请求路由至 static（单点能量/力/应力）、relax（几何优化）、md（分子动力学）、neb（反应路径/过渡态）四类工作流，并通过 calculator 适配层（GPAW / MACE）隔离后端配置。输出可复现的任务布局与运行脚本，执行交接 dpdisp-submit。

## 适用范围 / 不适用场景
适用：需要后端无关工作流编排的原子尺度模拟；GPAW（DFT）或 MACE（机器学习势）后端的结构优化、MD、NEB；工作流逻辑与 calculator 配置分离的场景。
不适用：路由层不硬编码后端特定参数，不直接执行计算；非 ASE 生态的后端（如 VASP 原生流程）应走对应专属技能。

## 实体槽（Entity Slots）
- workflow_type: static / relax / md / neb
- backend: gpaw / mace（通过 ase-calculators 路由选择）
- optimizer: BFGS / FIRE 等（relax/neb）
- fmax: 力收敛阈值（relax/neb）
- max_steps: 最大优化步数
- ensemble: NVE / NVT / NPT（md）
- timestep: MD 时间步长
- temperature: 目标温度
- n_images: NEB 镜像数
- climbing_image: 是否启用 climbing-image（NEB）
- constraints: 固定原子/层约束（relax）

## 输入输出契约
输入：
- 结构文件（static/relax/md）或初始+末态结构（neb）
- 选定的后端 adapter（GPAW 或 MACE）
- 工作流类型特定参数：optimizer/fmax/max_steps（relax）、timestep/steps/ensemble/temperature（md）、n_images/optimizer/convergence（neb）
- 请求属性：energy/force/stress（static）

输出：
- 工作流脚本/任务布局（Python 脚本）
- 优化器/收敛/MD 控制摘要
- 假设与未决选择列表
- 若需执行，附 dpdisp-submit 交接说明

## 方法路线（可替换）
顶层路由：ase → ase-workflows（工作流）+ ase-calculators（后端适配）。
- static：单点评估，标准化输出 energy/forces/stress
- relax：BFGS/FIRE 优化器，fmax 收敛判据，支持固定原子/层约束与应力感知弛豫
- md：ensemble/integrator/thermostat 设置，支持 pressure/barostat、初始速度策略、checkpoint/restart
- neb：镜像插值、climbing-image、spring-constant 策略，输出路径与势垒
- 后端适配：GPAW（DFT）或 MACE（ML 势），混合请求先走 ase-workflows 再调 ase-calculators

## 操作序列（Operations）
1. 顶层路由判断：workflow-level → ase-workflows；backend-level → ase-calculators
2. 工作流分类：static/relax/md/neb，意图模糊则问一个聚焦问题
3. 收集最小上下文：结构、目标、收敛判据、输出需求
4. 请求后端适配：通过 ase-calculators 路由选择 GPAW 或 MACE，验证后端前置条件
5. 生成工作流脚本：optimizer/ensemble/NEB 设置、constraints、trajectory/log 策略
6. 输出可复现任务布局与运行脚本
7. 附 dpdisp-submit 交接说明（若需执行）

## 验证契约（Validations）
- 后端前置条件：验证所选 adapter（GPAW/MACE）的最低依赖已满足
- 工作流与后端分离：workflow 脚本不含 backend-specific calculator 参数硬编码
- 假设显式暴露：所有未决选择上报用户
- 收敛策略完整：relax 需 fmax + max_steps；md 需 timestep + steps + ensemble；neb 需 n_images + convergence
- 输出可复现：任务布局含完整脚本与配置

## 资源引用（Resources）
- 核心框架：ASE（Python，https://gitlab.com/ase/ase）
- 后端 adapter：GPAW（DFT）、MACE（机器学习势）
- 提交工具：dpdisp-submit（作业提交与执行）
- 路由子技能：ase/ase-workflows/{static,relax,md,neb}、ase/ase-calculators/{gpaw,mace}

## 前后置任务（Task Graph）
无强制前后置。内部依赖：混合请求先走 ase-workflows 再调 ase-calculators 作为依赖。执行阶段统一交接 dpdisp-submit。

## 缺口与降级（Fallback / Gap）
- 后端未指定：提供 GPAW/MACE 选项，问一个聚焦问题让用户选择
- 意图模糊：不猜测，仅问一个澄清问题
- 后端前置不满足：报告缺失依赖，不自行安装或编造
- 混合请求：先路由 ase-workflows，再调 ase-calculators 补充后端配置
- 执行请求：路由层不执行，交接 dpdisp-submit
- restart 需求（md/relax）：显式 checkpoint/restart 策略，不假设默认行为
