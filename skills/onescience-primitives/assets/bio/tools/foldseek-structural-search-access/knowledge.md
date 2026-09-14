# Foldseek 蛋白结构相似性搜索访问 (foldseek-structural-search-access)

## 定位与适用任务
用户持有物理三维坐标文件（.cif/.mmcif/.pdb）且要找结构相似蛋白时使用；产出 top 结构命中表、
指标判读与功能推断汇总。仅有序列/基因名/登录号而无坐标文件时禁止使用本卡。

## 访问方式与鉴权
Foldseek web server API 经封装脚本 search.py（<坐标文件> -o <json> > <md>）；无需 key。
库白名单：afdb50、afdb-swissprot、pdb100、BFVD、mgnify_esm30、cath50、gmgcl_id、bfmd、afdb-proteome。

## 核心操作模式
- 硬门禁一：无坐标文件立即 halt，建议先经预测结构获取任务或 PDB 工具卡下载结构。
- 硬门禁二：白名单外库请求立即 halt 并出示清单。
- 判读只读生成的 .md 表；JSON 仅留作后续专用工具消费；禁止自行解析原始三维坐标。

## 输出契约与关键字段
.md 人读表 + .json 全量结果。指标：Prob 趋近 1.0 = 高置信真实结构同源；Q-Cov 高 = 覆盖查询整体形状
而非局部 motif；E-value 与 Seq Identity 提供进化语境。

## 限流与合规
遵循 Foldseek 服务与 steineggerlab/foldseek 条款；脚本封装限流。

## 常见坑与降级
API 报错或文件缺失 → 如实告知并请用户核验路径；高度无序蛋白做全结构搜索无意义 →
先经置信判读任务限定有序域边界再搜。

## 来源与许可
封装自 google-deepmind/science-skills（Apache-2.0，commit 28b84826）之 foldseek_structural_search 技能；
上游条款见 search.foldseek.com 与 github.com/steineggerlab/foldseek。
