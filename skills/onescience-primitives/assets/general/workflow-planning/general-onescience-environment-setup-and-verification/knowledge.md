# OneScience 环境准备与验证通用流程

## 适用范围
面向使用 OneScience 工具链执行科研任务的场景，确保任务启动前 CLI 工具、conda 环境、运行站点配置正确就绪。适用于本地或远程计算节点，覆盖环境安装、配置发现、预检验证等环节。不适用于已就绪的环境或无需 OneScience 工具链的任务。

## 输入
- 任务描述（含领域、目标、资源需求）
- 运行站点信息（本地路径或远程 SSH/SLURM 参数）
- 已有的 OneScience 配置文件（如 `~/.onescience/` 下的 `runsite.json`，可选）

## 输出
- 环境就绪状态报告（readiness status）
- 可执行的 OneScience CLI 命令
- 激活的 conda 环境及依赖库
- 任务执行路由决策（本地执行/SLURM 提交）

## 流程节点
1. **配置发现** → 调用 `onescience-runsite` 技能，解析或生成 `runsite.json`，确定目标环境参数。
2. **环境预检** → 调用 `onescience-installer` 技能，执行 `preflight_validation`，检查 CLI 可用性、conda 环境存在性、依赖库版本。
3. **环境修复** → 若预检失败，installer 根据配置安装/修复环境，创建或复用 conda 环境，安装 Python 包和系统依赖。
4. **验证通过** → 再次执行预检，确认 `onescience --version` 成功、关键库可导入。
5. **路由执行** → 根据就绪状态选择执行通道（本地或 SLURM），调用 `onescience-runtime` 技能提交任务。

## 关键参数
### 通用判据
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| CLI 可用性 | `onescience --version` 返回版本号 | [U1] | 基本前置条件 |
| conda 环境名 | 任务指定或默认 `onescience-env` | [U1] | 环境隔离 |
| Python 依赖库 | scikit-learn, ase, pandas 等 | [U1] | 根据任务领域动态确定 |
| 运行站点配置文件 | `~/.onescience/runsite.json` | [U1] | 必填字段：work_dir, env_modules, queue 等 |

### 校准数值（来自有机半导体主动学习发现任务）
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 失败错误信息 | “无法执行onescience命令，因为未找到onescience.exe” | [U1] | 表明 CLI 未安装或不在 PATH |
| 缺失环境 | conda 环境 ‘onescience-env’ 不存在 | [U1] | 需要创建环境 |
| 预检阶段 | preflight_validation 未执行或结果未消费 | [U1] | 工作流顺序错误 |

## 边界与分流
- 若 `runsite.json` 不存在且无法自动生成默认配置，触发用户交互获取运行站点信息。
- 若 installer 安装失败（如网络问题、权限不足），任务中止并输出诊断日志。
- 若预检通过但执行阶段环境变化（如环境被删除），重新触发预检。

## 质量检查
- 预检必须通过后才能进入执行阶段。
- `onescience --version` 必须返回有效版本。
- 关键库导入测试（如 `python -c "import sklearn"`）无报错。
- conda 环境列表确认环境已激活。

## 回退策略
- 环境修复失败时，建议用户手动安装 OneScience 或检查网络/权限。
- 远程节点连接失败时，切换到本地执行或更换节点。

## 资源召回建议
当任务启动失败并出现环境相关错误时召回本卡片。配套资源：`onescience-installer`、`onescience-runsite`、`onescience-runtime` 技能。

## 补充证据（用户自有）
[U1] 有机半导体主动学习发现任务归因报告，任务ID 379，2026-09-16（用户自有, 未经公开源验证）

## 证据来源
无论文证据，基于用户自有任务归因报告。