# launch

作为 Python API 基类使用，通常由具体模型继承后实例化；单独运行时可用下面方式验证 checkpoint 生命周期接口：

```sh
python -c "from onescience.modules.module import Module; print(Module.__model_checkpoint_version__)"
```

# input_schema

模型子类需要满足两个输入约束：构造函数参数应可 JSON 序列化，便于 `Module.__new__` 捕获并写入 `args.json`；模型权重应能通过 `state_dict` 保存和恢复。调用 `load` 或 `from_checkpoint` 时，输入路径应指向 `.mdlus` 包，包内必须包含 `model.pt`、`args.json` 和 `metadata.json`。

# runtime_interfaces

- `instantiate`: 根据 `__name__`、`__module__`、`__args__` 构造模型，优先走 `ModelRegistry`，否则动态 import。
- `save`: 将当前模型权重、构造参数和元数据写入 `.mdlus` 包。
- `load`: 将 checkpoint 权重加载到当前实例。
- `from_checkpoint`: 从 checkpoint 解包、实例化并加载权重，返回新模型实例。
- `from_torch`: 把普通 torch 模型类包装为可注册的 OneScience `Module` 子类。
- `device`: 返回模型注册 buffer 所在设备。
- `num_parameters`: 统计可学习参数总量。
- `debug`: 切换更详细的日志输出。

# main_functions

- `instantiate`
- `save`
- `load`
- `from_checkpoint`
- `from_torch`
- `device`
- `num_parameters`
- `debug`

# execution_resources

该组件本身只需要 Python 运行环境和 torch；保存、加载 checkpoint 时需要临时目录、tar 打包能力和 OneScience filesystem 工具。实际 GPU/CPU 资源需求由继承它的具体模型决定，例如 MedGemma 的推理资源由 vLLM 或 Transformers runner 及模型规模决定，而不是由 `Module` 基类决定。

# operation_limits

`Module` 不实现具体 `forward` 业务逻辑，也不负责生物数据预处理、模型训练循环或推理策略。构造参数必须能序列化，否则 checkpoint 恢复链路不可靠；动态 import 依赖模块路径和类名稳定；`.mdlus` 版本字段必须和当前 `Module.__model_checkpoint_version__` 一致；当前 `medgemma` 通过 `onescience.modules` 包级导入 `Module` 的路径存在导出风险，运行前应做导入检查。若仅需要公共入口，优先验证 `from onescience import Module` 或 `from onescience.modules.module import Module`。
