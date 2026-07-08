# description

该规划卡用于判断一个生信模型是否需要通过 OneScience `Module` 基类接入统一模型生命周期。它关注模型包装、checkpoint、registry 和运行时恢复，不参与模型算法选择。

# when_to_use

- 任务要求把 MedGemma 或其他生信模型接入 OneScience 模型保存、加载、registry、统一 runner。
- 需要从 `.mdlus` checkpoint 恢复模型，或把已有 torch 模型包装成 OneScience 模型。
- 需要排查模型无法导入、无法保存、无法恢复、构造参数不可序列化等生命周期问题。
- 不要在需要蛋白结构生成、配体对接、亲和力打分、分子扩散生成时把它当作算法组件使用。

# inputs

- 目标模型类名与模块路径。
- 模型构造函数参数及其可序列化性。
- 可选 `ModelMetaData`。
- checkpoint 路径、版本字段和包内文件结构。
- 当前 `onescience.modules` 导出状态与实际 import 路径。

# outputs

- 是否应继承 `Module` 的判断。
- 推荐导入路径和包装方式。
- checkpoint 保存、加载或恢复流程。
- 需要修正的 registry、导出、参数序列化或版本兼容问题。
- 对下游 coder 的代码引用范围。

# procedure

1. 检查目标模型是否已继承 `Module`，或是否只是普通 `torch.nn.Module`。
2. 若已继承，验证导入路径可用，尤其检查包级 `onescience.modules` 是否导出 `Module`。
3. 检查模型 `__init__` 参数是否均可 JSON 序列化，避免保存时写入失败。
4. 如需保存，调用 `save` 生成 `.mdlus`，并确认包内包含权重、构造参数和元数据。
5. 如需恢复，优先使用 `from_checkpoint`，需要在迁移旧路径时核对 `__module__` 和 registry。
6. 若目标是普通 torch 模型，使用 `from_torch` 生成包装类，再注册到 `ModelRegistry`。

# constraints

- 不能假设 `Module` 已被 `onescience.modules.__init__` 包级导出，必须以实际代码为准。
- 不能把 `Module` 的生命周期能力解释为生物算法能力。
- checkpoint 包必须包含 `args.json`、`metadata.json`、`model.pt`。
- `metadata.json` 中的 `mdlus_file_version` 必须与当前基类版本兼容。
- 动态 import 和 registry 恢复依赖类名、模块路径、注册名稳定。

# next_phase_recommendation

若当前任务是 MedGemma 接入或调试，下一步应验证 `from onescience.modules import Module` 是否成功；如果失败，建议改为 `from onescience import Module`、显式导入 `onescience.modules.module.Module`，或补充包级导出。若任务是 DiffDock、GenScore、LaProteina 或 TargetDiff 的算法组件规划，应转向它们各自模型目录或已有分子/蛋白组件契约，而不是继续扩展该基类卡。

# fallback

如果 `Module` 导入或恢复链路不可用，可临时退回普通 `torch.nn.Module` 运行，并在模型外部保存配置和权重；若 checkpoint 无法通过 `from_checkpoint` 恢复，可手动实例化目标模型后调用 `load_state_dict`，同时记录缺失的构造参数和版本信息，供后续修复 OneScience 生命周期适配层。
