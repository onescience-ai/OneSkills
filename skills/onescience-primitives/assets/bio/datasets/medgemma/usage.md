
## access
数据获取路径优先使用 `${ONESCIENCE_DATASETS_DIR}/medgemma`；若运行环境未设置 `ONESCIENCE_DATASETS_DIR`，则回退到默认挂载路径 `/public/share/sugonhpcapp01/onestore/onedatasets/medgemma`。可见 Chest_Xray、camelyonpatch、ehr、medqa、nct、CTLM、LLM-Research、navigator、test_images 等目录。

## data_schema
不同子目录对应图像、EHR、文本问答或多模态对照样本，字段由具体任务定义。

## task_usage
适用于医学问答、图像分类、病理识别、EHR 结构化分析和多模态对齐。

## integration_paths
应先按子任务选择目录，不要把所有目录混成一个统一数据集。

## preparation_requirements
先确认任务类型是图像、文本还是 EHR，再构建对应 split 和标签协议。

## consumption_interfaces
消费端通常需要图像张量、结构化记录、问答对或对照标签。

## operation_limits
不要把数据目录、数据库目录和模型权重目录混为一类；不要假设所有子目录都能直接作为训练样本；如果某个目录只是参考数据库，应先把它定位为外部依赖，再决定是否写入 datapipe。
