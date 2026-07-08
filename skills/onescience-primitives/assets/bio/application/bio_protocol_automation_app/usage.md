# launch

该卡以模板启用为主。coder 应复制并补全模板，而不是直接执行：

```sh
cp script/bio_protocol_templates/liquid_handler_protocol.yaml ./liquid_handler_protocol.yaml
```

# input_schema

需要提供实验任务、样本/构件、协议来源、仪器平台、layout/plate map、controls、replicates、安全和审核点。液体处理还需要 `robot_platform`、`deck_map`、`labware`、`reagents`、`plate_map`、`transfer_steps`、`dead_volume` 和 `simulation_plan`。ELN/注册任务还需要 materials、reagents、sample registry、construct registry、inventory、version 和 traceability 字段。图像定量任务还需要 lane/spot/ROI、exposure、background、loading control、saturation flag、technical/biological replicate、normalization 和 replicate aggregation 字段。

# runtime_interfaces

- 模板入口：`liquid_handler_protocol.yaml`、`protocol_record.yaml`、`blot_quantification_layout.csv`
- 适用任务标签：`liquid-handling-protocols`、`protocol-registry-eln`、`assay-image-quantification`
- execution_kind：template_only

# main_functions

- emit liquid handler protocol template
- emit protocol record
- emit blot quantification layout
- emit ELN and inventory registration fields
- emit simulation and review checklist

# execution_resources

无计算资源要求。若后续生成机器人专用脚本，需要单独的设备 SDK、仿真器或平台适配器。

# operation_limits

该卡不直接控制机器人、不验证湿实验可行性、不保存 ELN 凭据、不执行图像定量算法。需要设备执行或图像分析时必须先经过 simulation、参数校验和人工审核。
