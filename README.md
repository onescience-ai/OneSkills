# <div align="center">OneSkills</div>

<p align="center">
  A skills library for AI-native scientific research built around <strong>OneScience</strong>.
</p>

<p align="center">
  Reusable skills for <strong>workflow orchestration</strong>, <strong>coding</strong>, <strong>debugging</strong>, <strong>runtime submission</strong>, and <strong>environment setup</strong>.
</p>

<p align="center">
  Works with <strong>Claude Code</strong>, <strong>Codex CLI</strong>, <strong>Trae</strong>, and other skill-based agents through optional integration adapters.
</p>

---

## What is OneSkills?

`OneSkills` 是面向 AI4S（AI for Science）场景的通用技能仓库。

它把科研开发中的工作流理解、角色协作、代码生成、远程运行与调试经验，整理成可复用的 `SKILL.md` 能力模块，供不同智能体消费。

仓库核心是：

- `skills/`：通用技能
- `references/`：通用参考资料
- `integrations/`：可选的智能体适配层

## Core Pipeline

推荐主链：

```text
onescience-workflow -> onescience-role -> onescience-skill -> onescience-hardware -> onescience-coder -> onescience-runtime -> onescience-debug
```

其中：

- `onescience-workflow`：理解用户真实科研任务
- `onescience-role`：做角色协作拆分
- `onescience-skill`：选择最小执行链
- 执行技能：负责硬件感知、代码实现、运行、安装、排障

## Included Skills

- `onescience-workflow`
- `onescience-role`
- `onescience-skill`
- `onescience-hardware`
- `onescience-coder`
- `onescience-runtime`
- `onescience-debug`
- `onescience-installer`

## Supported Requests

当前 `oneskills` 可以直接支持以下用户需求：

- 科研任务梳理：理解“我要接入数据 / 改模型 / 跑远程 / 做评估”这类真实科研目标
- 工作流与角色拆解：判断当前任务该由谁推进、角色如何交接、下一步进入哪条执行链
- OneScience 代码实现：完成 DataPipe、模型、组件、配置与入口脚本相关实现或改造
- 远程环境感知：识别 Host、DCU / GPU、队列、module、conda 与路径约束
- 远程运行提交：基于 `onescience.json` 与 `tpl.slurm` 生成并提交作业
- 测试与排障：识别模型测试、Earth DataPipe 测试或完整训练 / 推理流程测试路径
- 环境安装：在远程 DCU 环境安装并验证 `OneScience`
- 自定义领域扩展：指导用户补充领域画像、角色协作、模板资产或新增稳定执行能力

更直观地说，用户可以直接提出这类问题：

- “帮我把这个科研任务拆成正确的技能链”
- “帮我接入某个数据集 / 改某个模型 / 补配置”
- “帮我识别远程环境并准备运行”
- “帮我提交到远端跑起来”
- “帮我判断该怎么测、为什么失败”
- “帮我在 DCU 环境安装 OneScience”

## Install

推荐使用统一安装器：

```bash
python3 install/install_oneskills.py --agent codex --project /your/project
```

支持的目标包括：

- `codex`
- `claude`
- `trae`
- `opencode`
- `generic`（需额外提供 `--skills-dir`）

常用方式：

```bash
python3 install/install_oneskills.py --agent codex --project /your/project
python3 install/install_oneskills.py --agent claude --project /your/project
python3 install/install_oneskills.py --agent trae --project /your/project
```

开发期如果希望技能目录始终跟随当前仓库更新，可使用软链接模式：

```bash
python3 install/install_oneskills.py --agent codex --project /your/project --mode symlink
```

如果还要把运行资产一并装到项目根目录：

```bash
python3 install/install_oneskills.py --agent codex --project /your/project --with-runtime-assets
```

卸载：

```bash
python3 install/install_oneskills.py --agent codex --project /your/project --uninstall
```

更多参数见：

- `install/README.md`
- `install/install_oneskills.py`
- `docs/user-guides/claude_codex_plugin_install.md`

跨平台建议：

- `macOS / Linux`：可使用 `copy` 或 `symlink`
- `Windows`：建议使用默认 `copy`；若显式传入 `--mode symlink`，安装器会自动降级为 `copy`

常见问题见：

- `install/README.md`

### Manual fallback

如果你不想使用安装器，也可以手动复制。

### Codex CLI

```bash
git clone https://github.com/onescience-ai/oneskills.git
mkdir -p /your/project/.codex
cp -r oneskills/skills/* /your/project/.codex/skills/
```

### Claude Code

推荐使用 Claude Code 插件安装：

```text
/plugin marketplace add https://github.com/onescience-ai/oneskills
/plugin install oneskills@oneskills
```

安装后重启 Claude Code，或在支持的版本中执行 `/reload-plugins`。

本地开发调试时，也可以 clone 后把仓库根目录作为 marketplace：

```bash
git clone https://github.com/onescience-ai/oneskills.git
```

```text
/plugin marketplace add ./oneskills
/plugin install oneskills@oneskills
```
### Trae

```bash
git clone https://github.com/onescience-ai/oneskills.git
mkdir -p /your/project/.trae
cp -r oneskills/skills/* /your/project/.trae/skills/
```

### Other agents

你也可以使用 generic 模式安装到任意技能目录：

```bash
python3 install/install_oneskills.py --agent generic --project /your/project --skills-dir .agent/skills
```

## Custom Skills

如果你想在不破坏当前产品分层的前提下扩展自定义技能，建议先阅读：

- `docs/user-guides/extend_domain_experience.md`
- `docs/open-source/custom_skill_contribution.md`

推荐原则：

- 优先扩展现有分层
- 优先补领域画像与模板资产
- 只有新增稳定执行能力时，才新增新的 skill

## Optional Integrations

- `integrations/generic-agent.md`
- `integrations/codex/README.md`
- `integrations/claude/`
- `.claude-plugin/`：Claude Code 插件元数据与 marketplace 示例
- `.codex/INSTALL.md`：Codex 原生 skills 发现安装方式

Claude Code 推荐执行 `/plugin marketplace add https://github.com/onescience-ai/oneskills`。本地测试时执行 `/plugin marketplace add ./oneskills`，不要添加 `./oneskills/.claude-plugin`。这样 marketplace 中的 `source: "./"` 才会指向仓库根目录，并安装完整的 `skills/` 目录。

## Contribution Notes

本仓库公开通用技能、公开参考资料与用户可用文档。

如果你想了解如何在本仓库里扩展自定义技能，优先阅读：

- `docs/open-source/custom_skill_contribution.md`

