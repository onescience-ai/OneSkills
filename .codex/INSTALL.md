# Install OneSkills for Codex

Use Codex native skill discovery to enable OneScience / OneSkills skills. This follows the same pattern as `superpowers-zh`: clone the repository and link its `skills/` directory into `~/.agents/skills`.

## Prerequisites

- Git
- Codex with native skills discovery enabled

## Install Skills

### macOS / Linux

```bash
git clone https://github.com/onescience-ai/oneskills.git ~/.codex/oneskills
mkdir -p ~/.agents/skills
ln -s ~/.codex/oneskills/skills ~/.agents/skills/oneskills
```

### Windows PowerShell

```powershell
git clone https://github.com/onescience-ai/oneskills.git "$env:USERPROFILE\.codex\oneskills"
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.agents\skills"
cmd /c mklink /J "%USERPROFILE%\.agents\skills\oneskills" "%USERPROFILE%\.codex\oneskills\skills"
```

Restart Codex after installing so it can discover the skills.

## Optional MCP Setup

`scnet_mcp` is an external runtime channel. OneSkills does not bundle the SCnet MCP server. If your machine already has a SCnet MCP server, copy and edit the example config:

```bash
cp ~/.codex/oneskills/onescience-plugin/config-examples/codex.mcp.example.json ~/.codex/oneskills/.mcp.json
```

Then replace the placeholder command, args, and environment variables with the actual local SCnet MCP launch configuration.

## Verify

```bash
ls -la ~/.agents/skills/oneskills
```

You should see a symlink or junction pointing to the repository `skills/` directory.

Expected skill directories:

```text
onescience-workflow
onescience-role
onescience-skill
onescience-hardware
onescience-coder
onescience-runtime
onescience-debug
onescience-installer
```

In Codex, try a prompt such as:

```text
使用 oneskills
```

The expected entry skill is `onescience-workflow`.

## Update

```bash
cd ~/.codex/oneskills
git pull
```

Because skills are linked, updates are available after restarting Codex.

## Uninstall

```bash
rm ~/.agents/skills/oneskills
```

Optional:

```bash
rm -rf ~/.codex/oneskills
```

On Windows, remove the junction and clone directory:

```powershell
Remove-Item -LiteralPath "$env:USERPROFILE\.agents\skills\oneskills" -Recurse -Force
Remove-Item -LiteralPath "$env:USERPROFILE\.codex\oneskills" -Recurse -Force
```
