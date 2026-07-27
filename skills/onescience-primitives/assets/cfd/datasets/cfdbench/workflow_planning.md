## description
为 CFDBench 二维规则网格 case 数据选择静态预测或自回归预测 workflow。

## when_to_use
任务需要 tube/cavity/cylinder/dam 的条件化二维速度场预测时使用。

## inputs
数据获取路径：`/public/share/sugonhpcapp01/onestore/onedatasets/CFDBench`。输入为 `problem/subset/case*/case.json,u.npy,v.npy`。

## outputs
输出为 data_name、split_ratios、case_params schema、batch 协议和 u/v 误差。

## procedure
1. 选择 problem 和 subset，构造 `source.data_name`。
2. 枚举 case 并抽检 `case.json/u/v`。
3. 固定 seed 和 split ratios。
4. 选择静态模式或 `task_type=auto`。
5. 做单 batch 检查，确认 label 和 mask。
6. 训练并按 problem/subset 输出指标。

## constraints
只读取 u/v；不同 task_type 返回字段不同；problem 和 subset 必须与 datapipe 支持列表一致。

## next_phase_recommendation
若目标为 rollout，选 auto 模式；若目标为条件场重建，选静态帧模式。

## fallback
若某个 problem 解析失败，先用 `cavity/bc` 做 smoke test。
