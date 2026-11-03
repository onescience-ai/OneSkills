# modelscope-resource-provisioning — 工作流规划知识

## 固定四段式解析
1. 任务级资源规划：请求没有具体资源名时，先按 references/resource_planning.md
   把任务拆成资源需求、派生稳定英文安全逻辑名、构造检索词（不回问用户）。
2. 调用方显式路径：显式给了 repo_id / 本地路径则优先采用。
3. 本地探测：~/.onescience 缓存、工作区 data/、注册表记录命中即复用（cache_hit）。
4. 网络物化：先按 references/source_selection.md 评估选源（ModelScope 默认，
   或 HuggingFace / 官网直链），再定位 repo_id / 直链后物化。

## 选源（ModelScope 默认但非唯一最优）
共享目录 find（--find-shared）→ ModelScope（默认，SDK→CLI→Git LFS）→
HuggingFace（--source hf --hf-repo org/name）→ 官网直链（--source url --source-url）；
四类来源共用同一套缓存/锁/原子落位/完整性校验/体积上限纪律，来源只允许权威源。

## repo_id 定位链（选 ModelScope 时）
显式 → 资源卡抽取 → 默认约定 OneScience/<name> → 官方 OpenAPI 检索并按元数据打分自动择优。

## 自动择优打分（确定性，附理由）
逐字同名 > 名称互为前缀 / 包含 > 标题描述与请求词重合 > 任务语义重合 > 任务标签命中 >
下载量 > 可信机构命名空间 > likes > 体积在上限内更小；gated/private 与超上限者排除。

## 下载三级降级
SDK snapshot_download（主力，带重试）→ modelscope CLI download（兜底）→
git + git-lfs clone（末路，需显式开启）。错误按 auth/network/disk/checksum/repo_not_found
分类，不可重试类不浪费重试预算。

## 完成动作
完整性校验（可见文件数 / 必需文件通配 / 大小下界 / content_digest）→
把 {name, kind, repo_id, local_path, digest} 注册进 resource_registry.json 供复用。

## 何时才允许说「拿不到」
仅当检索确无可选仓库（no_selectable_repo）、任务级规划为空（resource_plan_empty）、
或认证 / 网络等硬失败时如实上报；不得用占位数据顶替。
