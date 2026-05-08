# Claude and Codex Plugin Installation

This guide describes how to install OneSkills skills and optional SCnet MCP configuration in Claude Code and Codex. The layout mirrors the `superpowers-zh` pattern:

- Claude uses `.claude-plugin/plugin.json` plus `.claude-plugin/marketplace.json`.
- Codex uses native skill discovery by linking `skills/` into `~/.agents/skills`.
- MCP is optional and must point to a locally installed SCnet MCP server.

## Claude Code

### 1. Install Skills as a Plugin

Add the public OneSkills marketplace:

```text
/plugin marketplace add https://github.com/onescience-ai/oneskills
```

Install the plugin:

```text
/plugin install oneskills@oneskills
```

Restart Claude Code after installation, or run `/reload-plugins` if your Claude Code version supports it. The plugin exposes every directory under the repository `skills/` directory.

### Local Development Install

For local development against a clone, use the repository root as the marketplace:

```bash
git clone https://github.com/onescience-ai/oneskills.git ~/oneskills
cd ~/oneskills
```

Start Claude Code from the parent directory:

```text
/plugin marketplace add ./oneskills
```

Do not add `./oneskills/.claude-plugin` as the marketplace path for local development. The marketplace file lives there, but the plugin source is `./`, and it must resolve to the repository root so Claude Code installs the full plugin including the top-level `skills/` directory.

Expected installed skills:

- `onescience-workflow`
- `onescience-role`
- `onescience-skill`
- `onescience-hardware`
- `onescience-coder`
- `onescience-runtime`
- `onescience-debug`
- `onescience-installer`

### 2. Verify Claude Code Can See the Skills

After restart, use the plugin manager:

```text
/plugin
```

Confirm `oneskills` appears under Installed plugins. Then test with prompts:

```text
使用 oneskills
```

Expected behavior: enters `onescience-workflow` as the public workflow entry.

```text
使用 onescience-coder 技能，帮我分析当前项目需要改哪些代码
```

Expected behavior: directly enters `onescience-coder`.

If Claude Code does not appear to load the skills, check that the installed plugin source contains `skills/onescience-workflow/SKILL.md`. For local testing, the source should be the repository root, not `.claude-plugin/`.

### 3. Optional SCnet MCP

`scnet_mcp` is an external service. OneSkills only provides the routing and runtime contract. If your local machine already has the SCnet MCP server, copy the example config and edit it:

```bash
cp ~/oneskills/onescience-plugin/config-examples/claude.mcp.example.json ~/oneskills/.mcp.json
```

Replace:

- `REPLACE_WITH_SCNET_MCP_COMMAND`
- `args`
- `SCNET_TOKEN`

with the real local SCnet MCP launch configuration.

## Codex

Codex installation is documented in `.codex/INSTALL.md`.

Short version:

```bash
git clone https://github.com/onescience-ai/oneskills.git ~/.codex/oneskills
mkdir -p ~/.agents/skills
ln -s ~/.codex/oneskills/skills ~/.agents/skills/oneskills
```

Windows PowerShell:

```powershell
git clone https://github.com/onescience-ai/oneskills.git "$env:USERPROFILE\.codex\oneskills"
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.agents\skills"
cmd /c mklink /J "%USERPROFILE%\.agents\skills\oneskills" "%USERPROFILE%\.codex\oneskills\skills"
```

Restart Codex after installation.

Optional MCP:

```bash
cp ~/.codex/oneskills/onescience-plugin/config-examples/codex.mcp.example.json ~/.codex/oneskills/.mcp.json
```

Then edit the copied `.mcp.json` with the real SCnet MCP command and credentials.

## Notes

- `oneskills` is a brand entry alias, not a new execution skill.
- `onescience-workflow` remains the public workflow entry.
- `onescience-runtime` may choose `execution_channel=scnet_mcp` only when the user explicitly requests SCnet / MCP execution and the local MCP server is available.
- Claude Code plugin installation depends on the top-level `skills/` directory. The published repository must include both `.claude-plugin/` and `skills/`; otherwise the marketplace installs metadata without usable skills.
