# 全量技能覆盖与智能代码迁移方案

## 目标

把 `scientific-agent-skills` 从一个外部 Agent Skill 集合，持续转化为 OneSkills 可检索、可规划、可交接、必要时可执行的能力网络。目标不是目录级复制，而是让每一个源技能都有明确状态：已整合、候选整合、拆分整合、待审核或暂不迁移。

当前源仓库包含 163 个有效 `SKILL.md` 技能。目标仓库已经具备统一 primitive registry 和 `onescience-primitive-distiller`，下一阶段需要把一次性人工蒸馏扩展为可重复的全量 inventory、候选生成、人工确认和受控物化流程。

## 一、整合对象模型

源技能通常同时包含五种内容，不应全部落在同一个 primitive 中：

| 源内容 | OneSkills 对象 | 说明 |
| --- | --- | --- |
| 领域知识、限制、选择依据 | `resource` primitive | 可被检索、规划和交接 |
| 第三方包、CLI、SDK | `tool` primitive | 记录 provider、版本和环境要求 |
| 数据库、API、数据集 | `database` / `dataset` primitive | 记录访问、分页、限流、来源和数据契约 |
| 固定任务流程、模板集合 | `application` primitive | 面向任务组合多个能力 |
| 稳定输入输出的脚本 | `executor` candidate | 仅在门禁通过后物化执行资产 |
| 复杂取舍、fallback、领域解释 | `expert` candidate | 保留决策逻辑，不强行脚本化 |

一个源技能可以拆成多个 primitive。例如单细胞技能应拆为数据容器、公共数据集、分析工具、统计工具、可视化和应用工作流，再通过 `primitive_dependencies` 连接。

## 二、全量覆盖状态机

每个源技能都必须经过以下状态，而不是用“目录是否存在”判断覆盖：

```text
discovered
    -> inventoried
    -> classified
    -> matched_explicitly | matched_heuristically | uncovered
    -> distilled_resource
    -> split_into_primitives
    -> execution_candidate
    -> approved_execution_asset
    -> consumer_connected
```

允许的终态包括：

- `resource_only`：知识已整合，暂不迁移代码。
- `resource_with_execution_assets`：部分代码经过白名单和哈希登记，可供显式请求使用。
- `primitive_plus_executor`：知识和稳定执行器分离维护。
- `split_primitives`：一个源技能拆成多个职责清晰的 primitive。
- `propose_expert`：主要迁移领域决策逻辑。
- `blocked_or_deferred`：缺少许可证、依赖、数据访问或验证证据。

覆盖率必须至少分成三层统计：

1. **来源覆盖率**：是否存在 `source.distilled_from`。
2. **知识覆盖率**：触发范围、工作流、接口、限制、示例和 references 是否被提取。
3. **执行覆盖率**：源代码是否经过审查、物化、验证并进入执行资产白名单。

## 三、知识蒸馏逻辑

### 1. Inventory

盘点 `SKILL.md`、frontmatter、references、scripts、assets、示例、安装说明和依赖声明。只生成摘要、计数、路径、大小和哈希，不读取后执行源代码。

### 2. 内容分层

- `description`、tags、触发词进入 `metadata.json`。
- `When to use`、workflow 和 examples 转成 `workflow_planning.md`。
- API、参数、依赖、输入输出和环境要求转成 `spec.md`。
- 安装、命令、常见错误和操作限制转成 `usage.md`。
- 长 references 按主题放入 companion references 或拆分 primitive，避免复制整篇上游文档。
- 科学限制、统计假设、数据泄漏风险、伪重复和结果解释必须保留，不能只提取 API。

长参考资料统一进入 primitive 的可选 `references/`，并通过 `metadata.json.knowledge_assets` 登记。默认检索只返回参考资料索引；只有调用方明确请求扩展知识时才读取正文。这样可以完整保留上游方法知识，同时不把大段文本或参考资料误当成执行资产。

### 3. 语义拆分

检测工具、数据库、工作流、分析模型、可视化和输出交付等关注点。出现多个独立关注点时，生成 `split_primitives` 候选，并输出建议依赖关系，而不是生成一个过宽的万能原语。

## 四、智能代码迁移逻辑

代码迁移必须是“候选生成 + 证据门禁”，不能是“发现 `.py` 就复制”。

### 代码证据

对 `scripts/` 和可执行 `assets/` 记录：

- 相对路径、扩展名、文件大小和 SHA-256。
- CLI/API 信号，如 `argparse`、`click`、`typer`、`main`、输入输出函数。
- 依赖和安装信号，如 `pip install`、`uv install`、容器或系统命令。
- 风险信号：网络访问、凭证处理、子进程、动态执行、绝对路径、删除/覆盖文件。
- 测试、fixture、示例和错误处理信号。

### 执行化门禁

代码只有满足以下条件才可进入 `execution_assets`：

1. 来源、许可证和版本明确。
2. 输入、输出、退出码和失败模式可以写成契约。
3. 依赖可以在独立环境中声明和安装。
4. 不包含密钥、私有 URL、硬编码本地路径或未审查网络行为。
5. 不包含隐式破坏性操作，或破坏性操作有显式开关和工作区边界。
6. 代码路径在 primitive 目录内，白名单路径不允许 `..` 或绝对路径。
7. 文件哈希登记，运行前再次校验。
8. 在隔离环境中完成最小 smoke run，并记录输出契约。

不能满足门禁时，保留代码的接口和行为说明作为知识，但将代码标记为 `resource_only` 或 `blocked_or_deferred`。

## 五、迁移候选排序

建议优先级由以下证据组成：

```text
priority = coverage_gap
         + stable_interface
         + scientific_reuse
         + knowledge_depth
         + consumer_demand
         - security_risk
         - dependency_risk
         - validation_gap
```

优先整合：

- 被多个 application/workflow 共同需要的工具、数据容器和数据库。
- 输入输出稳定、可重复运行、具有明确 CLI/API 的脚本。
- 能补齐完整科研任务链的能力，如数据获取、统计、可视化和交付。
- 上游 references 丰富但执行依赖不稳定的技能，先做高质量 resource。

暂缓或拆分：

- 同时包含多个无关平台、服务和任务链的宽技能。
- 依赖私有账号、商业 API、GPU、实验室设备或本地软件的技能。
- 只有一次性示例、 notebook 状态、硬编码路径或强副作用脚本的技能。

## 六、下一步实施批次

### P0：建立全量迁移清单

- 执行 `build_skill_migration_manifest.py`。
- 为 163 个技能生成覆盖状态、内容通道、代码风险和目标匹配。
- 将显式来源、名称匹配和未覆盖技能分开统计。

### P1：补齐高复用知识和执行候选

- 生物数据与组学：`biopython`、`pysam`、`gget`、`pathway-enrichment`。
- 化学与药物：`rdkit`、`deepchem`、`datamol`、`molfeat`。
- 通用分析：`scikit-learn`、`matplotlib`、`seaborn`、`exploratory-data-analysis`。
- 文献与科研判断：`paper-lookup`、`peer-review`、`hypothesis-generation`。

每批先完成 resource 蒸馏，再选择少量稳定脚本进入执行化审查。

### P2：建立受控物化器

在候选清单稳定后，实现两个受控物化器：

- `materialize_knowledge_assets`：复制或重写已选择的 references，生成 `knowledge_assets` 索引、来源和哈希；禁止将代码文件作为普通知识文件静默执行。
- `materialize_execution_assets`：只接受人工批准的代码路径，复制到 primitive 目录，生成执行白名单和哈希，补充依赖与隔离运行记录。

两个物化器都不得自动执行源代码或修改 orchestrator 业务逻辑。

### P3：连接消费者并提升等级

- 为 application/workflow 自动生成依赖候选，人工确认后写入 `primitive_dependencies`。
- 对重复消费且边界稳定的资源提升为 executor。
- 对需要取舍和 fallback 的资源提升为 expert。
- 继续保留源版本和 provenance，支持上游更新后的增量重蒸馏。

## 七、当前实现

`skills/onescience-primitive-distiller/scripts/build_skill_migration_manifest.py` 已提供只读 inventory：

- 扫描源技能和目标原语。
- 识别显式来源、名称匹配和别名匹配。
- 提取知识通道和关注点。
- 对脚本和可执行资产进行风险扫描、哈希登记和执行化评分。
- 输出 JSON 全量清单和 Markdown 优先级摘要。

该工具是迁移准备工具，不是自动代码搬运器。后续物化必须建立在候选清单、人工批准、许可证检查、依赖隔离和最小运行证据之上。
