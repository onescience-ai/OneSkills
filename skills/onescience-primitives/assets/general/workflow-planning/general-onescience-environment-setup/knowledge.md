# OneScience 环境配置与安装知识

## 适用范围
适用于需要执行OneScience工作流的任何任务，特别是在任务启动前环境准备阶段。解决以下问题：
- 无法执行onescience命令
- conda环境不存在
- 环境依赖缺失
- 运行站点配置不明确

不适用于：
- 已经确认环境就绪的执行阶段
- 不涉及OneScience工具链的通用科研任务

## 输入
- 任务描述和领域要求
- 运行站点信息（本地/远程）
- 项目根目录的onescience.json（可选，可由runsite技能生成）
- 用户明确的环境配置意图（安装OneScience、安装Python包、安装HPC软件等）

## 输出
- 成功配置的OneScience环境
- 更新后的onescience.json.runtime.conda配置
- 环境就绪状态报告
- 可执行的onescience命令

## 流程节点
1. **配置发现** → 读取onescience.json，检查runtime.execution_profile.run_site和runtime.ssh配置
2. **意图识别** → 根据用户请求确定安装意图（bootstrap/python_packages/hpc_software）
3. **环境检测** → 检查目标环境是否已有onescience包和依赖
4. **环境创建/修复** → 根据检测结果创建conda环境或安装依赖
5. **验证** → 验证onescience命令可执行，关键库可导入
6. **写回** → 将环境配置写回onescience.json.runtime.conda

每步含：操作、参数、工具、质量门禁

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| run_site | local/remote | onescience.json | 运行站点类型 |
| execution_mode | slurm/null | onescience.json | 执行模式 |
| access_mode | ssh/scnet/"" | onescience.json | 接入方式 |
| install_intent | bootstrap/python_packages/hpc_software | 用户请求 | 安装意图 |
| conda_env_name | 任务相关名称 | backend_profiles.json | conda环境名 |
| python_version | 3.8-3.10 | backend_profiles.json | Python版本 |
| onescience_extras | earth/cfd/bio/matchem/all | install_domains.json | 领域extras |

## 边界与分流
- **本地环境**：直接执行conda和pip命令
- **远程环境**：必须通过SSH连接执行，不能在本端shell执行
- **HPC环境**：可能需要module加载和特定安装路径
- **autonomous_mode**：自动创建环境，不询问用户确认
- **标准模式**：创建环境前必须获得用户明确同意

异常处理：
- SSH连接失败 → 回到runsite技能重新配置
- 安装失败 → 报告失败原因，不写入成功状态
- 验证失败 → 进入修复流程

## 质量检查
- onescience命令可执行：`onescience --version`无报错
- 关键库可导入：`python -c "import onescience, torch, scikit-learn"`
- conda环境存在：`conda env list`显示目标环境
- 环境激活成功：`source activate <env_name>`无报错
- 配置写回成功：onescience.json.runtime.conda字段正确

## 回退策略
- 安装失败 → 检查网络连接、镜像源、权限问题
- 验证失败 → 尝试重新安装或修复依赖
- 远程连接失败 → 回到runsite技能重新配置SSH
- 环境冲突 → 考虑创建新环境或清理旧环境

## 资源召回建议
- 当任务启动报错"无法执行onescience命令"时召回本卡片
- 当检测到conda环境不存在时召回本卡片
- 当onescience.json.runtime.conda缺失时召回本卡片
- 配套资源：onescience-installer技能、backend_profiles.json、install_domains.json

## 证据来源
[1] onescience-installer技能文档 - 环境安装主流程与分支映射
[2] onescience-runtime技能文档 - preflight阶段环境就绪检查
[3] onescience-runsite技能文档 - 运行站点配置管理
[4] 任务379归因报告 - 环境配置知识缺失证据