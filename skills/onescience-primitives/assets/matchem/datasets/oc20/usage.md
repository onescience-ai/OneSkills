## access
数据获取路径优先使用 `${ONESCIENCE_DATASETS_DIR}/matchem/oc20`；若运行环境未设置 `ONESCIENCE_DATASETS_DIR`，则回退到默认挂载路径 `/public/share/sugonhpcapp01/onestore/onedatasets/matchem/oc20`。可选入口为浅层 extxyz split、`orig_data` extxyz 集合和 `uma_oc20_finetune` 的 ASE LMDB split。

## data_schema
extxyz 入口包含结构、元素、坐标、能量、力、晶胞和 PBC 等字段；ASE LMDB 入口包含 UMA datapipe 可读取的 AtomicData 记录及 `metadata.npz`。`*.lock`、`*.failed`、`*.log` 是伴随文件，不参与样本读取。

## task_usage
适用于 OC20 S2EF 任务、吸附-催化体系能量/力预测、UMA 微调、材料势模型验证和 ASE LMDB datapipe 调试。

## integration_paths
若使用 UMA，优先读取 `uma_oc20_finetune/data/uma_conserving_data_task_energy_force.yaml` 和 `uma_sm_finetune_template.yaml`，以 `train/*.aselmdb` 和 `val/*.aselmdb` 构建 dataloader。若使用 extxyz，走 ASE reader 并保留 `tags/fixed/sid/fid` 等可用元数据。

## preparation_requirements
需要确认 extxyz 文件与 LMDB 是否同源，避免重复计数；检查 train/val 分片数量、`metadata.npz` 是否可读、每条样本是否包含 energy 和 forces；验证 tags、fixed atoms、cell、pbc 是否被 datapipe 保留。

## consumption_interfaces
主要消费端为 UMA ESCN MD/MoE 和 OneScience materials datapipe，也可适配 MACE 类势模型。batch 需要包含 `pos`、`atomic_numbers`、`cell`、`pbc`、`energy`、`forces`、`tags/fixed`、`sid/fid`、`natoms`。

## evaluation_protocol
按 S2EF 协议报告 energy MAE 和 forces MAE，并可按原子数、吸附体系类别或是否固定原子拆分。UMA 微调验证应使用 `uma_oc20_finetune/val`。

## resource_profile
ASE LMDB 适合多 worker 随机读取；extxyz 适合预转换缓存。OC20 样本构图开销较高，应先设置 `max_atoms`、cutoff 和 batch size。

## operation_limits
- 不要读取 `.lock`、`.failed`、`.log` 作为样本。
- 不要同时把浅层 extxyz 和 `orig_data` 同源文件重复加入训练。
- 固定原子和 tags 影响 loss/metric，不能在转换时丢弃。
- LMDB 与 `metadata.npz` 必须按 split 配套。
