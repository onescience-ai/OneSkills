
## access
数据获取路径优先使用 `${ONESCIENCE_DATASETS_DIR}/diffdock`；若运行环境未设置 `ONESCIENCE_DATASETS_DIR`，则回退到默认挂载路径 `/public/share/sugonhpcapp01/onestore/onedatasets/diffdock`。训练/评测数据主路径为 `datasets/`。datasets 下可见 PDBBind_processed、BindingMOAD_2020_processed、P-L、inferdata、splits 和 esm_pdbbind/full；score_model 目录保存推理/打分权重。

## data_schema
训练侧通常是处理好的复合物图、对接姿态与 split；推理侧是输入蛋白和配体描述、缓存图和模型参数。

## task_usage
适用于蛋白-配体对接、结合姿态评分、虚筛和推理构图。

## integration_paths
优先按 split 文件和 processed 数据集构建训练集，再用 inferdata 处理在线输入；若使用 ESM 嵌入，应同步检查嵌入字典与样本 ID。

## preparation_requirements
先确认 PDBBind 与 MOAD 的 split 一致性，再核对缓存目录和 torsion/noise 参数。

## consumption_interfaces
消费端通常接收 HeteroData 图、配体/受体特征、噪声标签和评分模型配置。

## operation_limits
不要把数据目录、数据库目录和模型权重目录混为一类；不要假设所有子目录都能直接作为训练样本；如果某个目录只是参考数据库，应先把它定位为外部依赖，再决定是否写入 datapipe。
