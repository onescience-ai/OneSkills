# 技能元信息脚本契约

元信息来源为 `scripts/discover_skill_metadata.py` 实际读取的已安装技能 frontmatter，不需要智能体原生 list/metadata 接口。技能执行接口与元信息发现互相独立。

## 调用

从本次实际安装的 `onescience-orchestrator` 目录定位脚本，任意工作目录均可运行：

```bash
# 资源召回前：获取全部资源技能元信息
python "<orchestrator_dir>/scripts/discover_skill_metadata.py" --type resource
# 专家召回前：获取全部专家技能元信息
python "<orchestrator_dir>/scripts/discover_skill_metadata.py" --type expert
# 计划融合或执行技能选择前：获取全部执行技能元信息
python "<orchestrator_dir>/scripts/discover_skill_metadata.py" --type executor
# 需要一次获取全部类型时省略 --type
python "<orchestrator_dir>/scripts/discover_skill_metadata.py"
# 类型筛选可与安装根目录参数组合
python "<orchestrator_dir>/scripts/discover_skill_metadata.py" --type resource --skills-root "<技能父目录A>" --skills-root "<技能父目录B>"
```

按当前流程所需类型查询，不要求首次发现全部类型。`--type` 取值为 resource、expert、executor、orchestrator；省略时返回四种类型。已完整接收的本轮相同安装范围结果覆盖所需类型时可直接复用，否则先查询对应类型，再做匹配和正式技能调用。元信息查询仅发现候选，不代替 resource / expert / executor 的正式请求与结果闭环。

默认根目录为脚本所在 orchestrator 的父目录；不会搜索当前项目、用户 HOME 或其他猜测路径。显式 `--skills-root` 会替换默认根目录，应包含本次需要发现的全部已安装技能；不要同时扫描同一套技能的源码和安装副本。根目录只扫描直接子目录的 `SKILL.md`，支持技能目录符号链接，不递归进入 assets/references。传入父目录而非单个技能目录。

依赖 Python 3 和 PyYAML。先复用已有 PyYAML 的 Python 环境；确实缺失时按当前环境安装授权执行 `python -m pip install -r "<orchestrator_dir>/scripts/requirements.txt"`，或记录具体依赖缺失，不将其描述为“宿主缺少元信息接口”。

## 输出与校验

标准输出一次返回一个完整 JSON 文档，默认紧凑格式，保留所有字段及数组元素，不分页、不限制技能数量或输出字节数。`--compact` 仍可显式指定同样的格式；`--pretty` 仅为人工检查增加缩进。退出码 `0` 表示扫描完整，`1` 表示扫描错误，非法命令行参数返回 `2`。主要字段：

- `metadata_source`: 固定为 `skill_frontmatter_script`。
- `script_path`、`skills_roots`: 本次实际使用的脚本与扫描范围。
- `query_types`: 本次返回元信息的类型范围；筛选时为单个类型的数组，未筛选时为四种类型的数组。
- `skills`: 按名称排序的查询范围内全部元信息，每项包含 `name`、`description`、`type`、`capabilities` 和取证用 `skill_file`。提供给 planner 的 `available_execution_skills` 只投影前四个字段。
- `inventories.resource|expert|executor|orchestrator`: 各自包含 `all_<type>_skills`、`read_<type>_skills`、`missing_<type>_skills`、`<type>_inventory_complete`。
- `inventory_complete`、`errors`、`ignored_skills`: 全局扫描状态、具体路径/字段错误和未采用 OneScience 元信息契约的普通第三方技能路径。
- `skill_count`: `skills` 中实际返回的记录数。
- `output_complete`: 文档末尾的完成标记；只有扫描完整且 `query_types` 范围内全部记录均已加入文档时为 true。它是脚本侧标记，不能证明宿主已完整传递响应。

每次查询都在同一次响应中返回所选类型的全部技能及完整字段，技能增加后也不分页。完整性以查询范围为准：`--type resource` 的 `output_complete=true` 仅表示 resource 元信息完整返回，不表示已收到 expert 或 executor 元信息。

执行工具的输出预算必须足以容纳整个 JSON。不得在脚本后接 `head` / `tail`，不得对描述、能力数组做切片，也不能只读技能名称或部分 `owns` 便宣布完成。脚本先构建完整结果再序列化输出，不会为了缩短响应裁剪记录。若工具提示截断，增大本次调用的输出预算，重新一次性获取全文；无法完整接收时报告具体输出限制，不根据片段继续路由。

接收完成条件：退出码为 0；响应无截断且为完整可解析的 JSON；`inventory_complete` 与末尾 `output_complete` 均为 true；`skill_count` 等于实际记录数；技能名称无重复；`query_types` 与本次请求一致；记录类型均在该范围内；仅对 `query_types` 中的每种类型，核对名称集合等于 `inventories` 中对应的 `all_*_skills`。`inventories` 中的 `read_*_skills` 是脚本侧成功解析的集合，只有完整接收并通过上述检查后才能将本次查询类型的库存写入调用方；其他类型的脚本库存即使显示完整，也不能据此将它们标记为调用方已读。

`--type` 过滤输出的 `skills` 并由 `query_types` 明示范围，不缩小扫描和校验范围。库存集合相等且没有扫描错误才能视为完整；解析失败而类型未知的文件也会令完整性为 false，不会被静默排除。空根目录或扫描到零个 `SKILL.md` 是错误。完整扫描后某个类型确实没有技能，可以返回该类型的空集合。

脚本校验 `name`、`description` 为非空字符串，`type` 为 resource/expert/executor/orchestrator，`capabilities` 为映射且含以下字符串列表（允许空列表）：`owns`、`not_owns`、`inputs`、`outputs`、`downstream`、`prereq`、`intent_aspects`、`operation_types`、`artifact_types`、`domains`、`trigger_keywords`。保留 frontmatter 的值，不合成职责。重复 YAML 键、不同文件声明同名技能、损坏 YAML、字段缺失、目录读取失败均返回错误；同一真实文件通过重复根目录/符号链接被发现时去重。

## Task State 与恢复

仅在脚本实际成功运行后保存发现证据：

```json
{
  "skill_metadata_discovery": {
    "metadata_source": "skill_frontmatter_script",
    "script_path": "<actual script path>",
    "skills_roots": ["<actual installed skills root>"],
    "command": ["python", "<actual script path>", "--type", "resource"],
    "query_types": ["resource"],
    "exit_code": 0,
    "inventory_complete": true,
    "errors": []
  }
}
```

完整接收并核对通过后，记录本次 `query_types`、`skill_count`、`output_complete=true` 与 `metadata_received_complete=true`；接收完成标记仅适用于该次查询范围。仅在范围包含 executor 时将 `inventories.executor` 写入 `executor_inventory`（保留已有用户可见摘要），resource、expert、orchestrator 以同样方式按实际接收范围维护库存。查询 resource 后，规划前仍需获取完整 executor 元信息并按原流程完成能力台账，不能用脚本侧的全局扫描状态代替。路径错误先定位实际安装目录后重跑；重复副本先明确本次安装范围；字段损坏应定位具体技能元信息，不得靠智能体补出值。真实错误仍未解除时报告对应缺失。

脚本保证完整文档的生成和输出，宿主的响应截断发生在脚本之外；`output_complete=true` 不等于模型已完整接收。调用方应检查工具截断提示与完整 JSON，不把局部内容当作完整发现。

恢复旧 Task State 时，`native_skill_metadata_interface_available=false` 或历史“缺少原生元信息接口”阻断已被本契约替代。重新运行脚本；成功后更新发现证据和 inventory，清除该旧阻断并继续原任务，无需用户重发任务或额外授权。实际元信息错误仍须修复，不因迁移而跳过校验。

coder、trainer 等子技能需要独立选择资源时也使用此脚本并传入 `--type resource`：通常位于已安装技能目录的 `../onescience-orchestrator/scripts/discover_skill_metadata.py`，必要时使用调用方传入的实际脚本路径和扫描根目录；不要请求原生元信息接口。frontmatter 发现不授权读取任何 resource 的 assets。
