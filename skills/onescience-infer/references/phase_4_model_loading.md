# 阶段 4：模型加载

目标：在完整推理前，证明 config、weights 和 runner 构建是一致的。

## Checkpoint 和 Config

解析以下内容：

- Checkpoint URI 或本地路径
- 可用时的 revision、branch、tag 或文件 hash
- Config 文件路径和 override
- Processor、tokenizer、datapipe 或归一化资产
- Device 和 dtype
- HuggingFace 模型是否要求 trust remote code

如果模型加载需要执行不受信任的远程代码，必须明确提示，并在适当时请求授权。

## Runner 契约

将 `model_loading_plan.md` 保存到 `infer_workdir`，并在其中定义 runner 接口；该文件是后续 codegen 与 execution 阶段读取的模型加载契约：
```text
load_config(config_path, overrides) -> config
load_checkpoint(checkpoint_path, device, dtype) -> weights/model
build_runner(config, weights, device) -> runner
prepare_batch(input_artifact) -> batch
run_inference(runner, batch, parameters) -> raw_output
postprocess(raw_output) -> output_artifacts
```

优先使用项目原生 runner 和官方推理示例。只有在文档细节足够且没有原生 runner 时，才构建通用 runner。

## Smoke Load

完整执行前，优先做低成本 smoke load：

- 加载 config
- 解析 checkpoint 文件
- 实例化模型或 runner
- 如果设备可用，将模型移动到请求的设备
- 支持时运行 no-op、shape-only 或 tiny sample 检查

在 manifest 中记录 smoke-load 证据。如果 smoke load 因缺少依赖失败，记录缺失 package、版本约束、来源和触发证据，并在阶段 6 的 `runtime_request.json.package_requirements` 中交给 `onescience-runtime`；如果因缺少文件或 checkpoint/config 不兼容失败，返回阻塞状态。
