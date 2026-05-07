# OneSkills Installer

本目录提供 `OneSkills` 面向不同智能体的统一安装入口。

## 支持的目标

- `codex`
- `claude`
- `trae`
- `opencode`
- `generic`

## 推荐用法

安装到指定项目：

```bash
python3 install/install_oneskills.py --agent codex --project /path/to/project
```

安装运行资产：

```bash
python3 install/install_oneskills.py --agent codex --project /path/to/project --with-runtime-assets
```

开发期使用软链接：

```bash
python3 install/install_oneskills.py --agent codex --project /path/to/project --mode symlink
```

卸载：

```bash
python3 install/install_oneskills.py --agent codex --project /path/to/project --uninstall
```

## 跨平台说明

- `macOS / Linux`：`copy` 与 `symlink` 都可正常使用
- `Windows`：推荐使用默认 `copy` 模式
- 如果在 `Windows` 上显式传入 `--mode symlink`，安装器会自动降级为 `copy`

## 说明

- `--project` 支持相对路径和绝对路径
- `generic` 模式适合其他支持技能目录约定的智能体

## FAQ

### 1. 会安装到哪里？

安装器会根据 `--agent` 自动选择技能目录：

- `codex` → `.codex/skills/`
- `claude` → `.claude/skills/`
- `trae` → `.trae/skills/`
- `opencode` → `.opencode/skills/`

如果使用 `generic`，则由 `--skills-dir` 明确指定。

### 2. 重复安装怎么办？

如果目标路径已存在，安装器会提示冲突。

这时可选择：

- 先用 `--uninstall` 卸载
- 或使用 `--force` 直接覆盖

### 3. `--with-runtime-assets` 会安装什么？

会额外把下面两个运行资产放到项目根目录：

- `onescience.json`
- `tpl.slurm`

适合需要远程运行提交的项目；如果只是本地使用技能做分析或代码生成，可以不加这个参数。

### 4. `--uninstall` 会删除什么？

安装器会删除它自己安装过的内容，包括：

- 对应 agent 的技能目录下本次安装的 `OneSkills` 条目
- 对应的集成说明文件
- 如有安装，则删除本次安装的运行资产
- 安装记录文件 `.oneskills/install-state/<agent>.json`

它不会删除未被安装器记录的其他用户文件。

### 5. Claude / Codex 插件模式怎么安装？

如果你希望按插件方式安装 Claude Code，或按 Codex 原生 skills 发现方式安装，请看：

- `docs/user-guides/claude_codex_plugin_install.md`
- `.codex/INSTALL.md`

MCP 配置示例在：

- `onescience-plugin/config-examples/claude.mcp.example.json`
- `onescience-plugin/config-examples/codex.mcp.example.json`
