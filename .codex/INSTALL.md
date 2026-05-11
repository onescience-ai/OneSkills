# Install OneSkills for Codex

Use Codex native skill discovery to enable OneScience / OneSkills skills. This path does not require Python. It installs skills with the previous clone + link approach, and downloads the SCnet MCP server binary directly from:

```text
https://gitee.com/onescience-ai/agent-cloud-interaction-protocol/releases/download/v0.1/scnet-mcp-server.exe
```

It also installs the OneScience source snapshot used by code-reading skills from:

```text
https://gitee.com/onescience-ai/onescience/releases/download/0.3.0/onescience-0.3.0.zip
```

## One-Line User Prompt

Users can paste this single sentence into Codex:

```text
Fetch and follow instructions from https://raw.githubusercontent.com/onescience-ai/OneSkills/refs/heads/master/.codex/INSTALL.md to install OneSkills skills, download the SCnet MCP server, and generate the Codex MCP config template.
```

Codex should complete the installation commands for the current operating system, generate the MCP config template, and then tell the user which SCnet credential fields still need local values. Do not ask the user for SCnet secrets during installation; leave credential fields empty in the generated template.

## Prerequisites

- Git
- Codex with native skills discovery enabled
- Network access to GitHub and Gitee
- `unzip` on macOS / Linux, or PowerShell `Expand-Archive` on Windows

## Install Skills And MCP

### macOS / Linux

```bash
if [ -d ~/.codex/oneskills/.git ]; then
  git -C ~/.codex/oneskills pull
else
  git clone https://github.com/onescience-ai/oneskills.git ~/.codex/oneskills
fi
mkdir -p ~/.agents/skills
if [ ! -e ~/.agents/skills/oneskills ]; then
  ln -s ~/.codex/oneskills/skills ~/.agents/skills/oneskills
fi
mkdir -p ~/.codex/oneskills/mcp-tools
curl -L -o ~/.codex/oneskills/mcp-tools/scnet-mcp-server.exe https://gitee.com/onescience-ai/agent-cloud-interaction-protocol/releases/download/v0.1/scnet-mcp-server.exe
mkdir -p ~/.codex/oneskills/source-cache
curl -L -o ~/.codex/oneskills/source-cache/onescience-0.3.0.zip https://gitee.com/onescience-ai/onescience/releases/download/0.3.0/onescience-0.3.0.zip
rm -rf ~/.codex/oneskills/onescience ~/.codex/oneskills/source-cache/onescience-extract
mkdir -p ~/.codex/oneskills/source-cache/onescience-extract
unzip -q ~/.codex/oneskills/source-cache/onescience-0.3.0.zip -d ~/.codex/oneskills/source-cache/onescience-extract
first_dir="$(find ~/.codex/oneskills/source-cache/onescience-extract -mindepth 1 -maxdepth 1 -type d | head -n 1)"
mv "$first_dir" ~/.codex/oneskills/onescience
```

### Windows PowerShell

```powershell
$repo = "$env:USERPROFILE\.codex\oneskills"
if (Test-Path -LiteralPath "$repo\.git") {
  git -C $repo pull
} else {
  git clone https://github.com/onescience-ai/oneskills.git $repo
}
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.agents\skills"
if (-not (Test-Path -LiteralPath "$env:USERPROFILE\.agents\skills\oneskills")) {
  cmd /c mklink /J "%USERPROFILE%\.agents\skills\oneskills" "%USERPROFILE%\.codex\oneskills\skills"
}
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.codex\oneskills\mcp-tools"
Invoke-WebRequest -Uri "https://gitee.com/onescience-ai/agent-cloud-interaction-protocol/releases/download/v0.1/scnet-mcp-server.exe" -OutFile "$env:USERPROFILE\.codex\oneskills\mcp-tools\scnet-mcp-server.exe" -UseBasicParsing
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.codex\oneskills\source-cache"
$zipPath = "$env:USERPROFILE\.codex\oneskills\source-cache\onescience-0.3.0.zip"
$extractPath = "$env:USERPROFILE\.codex\oneskills\source-cache\onescience-extract"
$sourcePath = "$env:USERPROFILE\.codex\oneskills\onescience"
Invoke-WebRequest -Uri "https://gitee.com/onescience-ai/onescience/releases/download/0.3.0/onescience-0.3.0.zip" -OutFile $zipPath -UseBasicParsing
Remove-Item -LiteralPath $sourcePath -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -LiteralPath $extractPath -Recurse -Force -ErrorAction SilentlyContinue
Expand-Archive -LiteralPath $zipPath -DestinationPath $extractPath -Force
$firstDir = Get-ChildItem -LiteralPath $extractPath -Directory | Select-Object -First 1
Move-Item -LiteralPath $firstDir.FullName -Destination $sourcePath
```

Restart Codex after installing so it can discover the skills.

Code-reading skills resolve source anchors such as `./onescience/src/onescience/...` to:

```text
~/.codex/oneskills/onescience
```

They should not scan arbitrary local paths such as `D:\Projects\OneScience\onescience`.

## MCP Setup

The MCP executable path after installation is:

```text
~/.codex/oneskills/mcp-tools/scnet-mcp-server.exe
```

On Windows, the absolute command path is:

```text
%USERPROFILE%\.codex\oneskills\mcp-tools\scnet-mcp-server.exe
```

Use that executable as the MCP server command in your local Codex MCP configuration. A Windows example is:

```json
{
  "mcpServers": {
    "scnet": {
      "command": "C:\\Users\\YOUR_USER\\.codex\\oneskills\\mcp-tools\\scnet-mcp-server.exe",
      "env": {
        "SCNET_USERNAME": "",
        "SCNET_ACCESS_KEY": "",
        "SCNET_SECRET_KEY": "",
        "SCNET_DEFAULT_REGION": "核心节点【分区一】",
        "SCNET_USE_REAL_API": "true",
        "SCNET_WORK_DIR": "",
        "SCNET_DEFAULT_QUEUE": ""
      }
    }
  }
}
```

On macOS / Linux, keep the same `env` block and change only `command`:

```json
{
  "mcpServers": {
    "scnet": {
      "command": "/home/YOUR_USER/.codex/oneskills/mcp-tools/scnet-mcp-server.exe",
      "env": {
        "SCNET_USERNAME": "",
        "SCNET_ACCESS_KEY": "",
        "SCNET_SECRET_KEY": "",
        "SCNET_DEFAULT_REGION": "核心节点【分区一】",
        "SCNET_USE_REAL_API": "true",
        "SCNET_WORK_DIR": "",
        "SCNET_DEFAULT_QUEUE": ""
      }
    }
  }
}
```

Replace `YOUR_USER`, `SCNET_USERNAME`, `SCNET_ACCESS_KEY`, `SCNET_SECRET_KEY`, `SCNET_WORK_DIR`, and `SCNET_DEFAULT_QUEUE` with local values.

## Generate MCP Config Template

Create a config template at `~/.codex/oneskills/.mcp.json`.

### macOS / Linux

```bash
cat > ~/.codex/oneskills/.mcp.json <<EOF
{
  "mcpServers": {
    "scnet": {
      "command": "$HOME/.codex/oneskills/mcp-tools/scnet-mcp-server.exe",
      "env": {
        "SCNET_USERNAME": "",
        "SCNET_ACCESS_KEY": "",
        "SCNET_SECRET_KEY": "",
        "SCNET_DEFAULT_REGION": "核心节点【分区一】",
        "SCNET_USE_REAL_API": "true",
        "SCNET_WORK_DIR": "",
        "SCNET_DEFAULT_QUEUE": ""
      }
    }
  }
}
EOF
```

Then fill in the empty SCnet values.

### Windows PowerShell

```powershell
$mcpCommand = Join-Path $env:USERPROFILE ".codex\oneskills\mcp-tools\scnet-mcp-server.exe"
$mcpConfig = @{
  mcpServers = @{
    scnet = @{
      command = $mcpCommand
      env = @{
        SCNET_USERNAME = ""
        SCNET_ACCESS_KEY = ""
        SCNET_SECRET_KEY = ""
        SCNET_DEFAULT_REGION = "核心节点【分区一】"
        SCNET_USE_REAL_API = "true"
        SCNET_WORK_DIR = ""
        SCNET_DEFAULT_QUEUE = ""
      }
    }
  }
}
$mcpConfig | ConvertTo-Json -Depth 5 | Set-Content -Encoding UTF8 "$env:USERPROFILE\.codex\oneskills\.mcp.json"
```

Then fill in the empty SCnet values.

## Verify

### macOS / Linux

```bash
ls -la ~/.agents/skills/oneskills
ls -la ~/.codex/oneskills/mcp-tools/scnet-mcp-server.exe
```

### Windows PowerShell

```powershell
Get-Item "$env:USERPROFILE\.agents\skills\oneskills"
Get-Item "$env:USERPROFILE\.codex\oneskills\mcp-tools\scnet-mcp-server.exe"
```

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

### macOS / Linux

```bash
cd ~/.codex/oneskills
git pull
curl -L -o ~/.codex/oneskills/mcp-tools/scnet-mcp-server.exe https://gitee.com/onescience-ai/agent-cloud-interaction-protocol/releases/download/v0.1/scnet-mcp-server.exe
```

### Windows PowerShell

```powershell
Set-Location "$env:USERPROFILE\.codex\oneskills"
git pull
Invoke-WebRequest -Uri "https://gitee.com/onescience-ai/agent-cloud-interaction-protocol/releases/download/v0.1/scnet-mcp-server.exe" -OutFile "$env:USERPROFILE\.codex\oneskills\mcp-tools\scnet-mcp-server.exe" -UseBasicParsing
```

Restart Codex after updating.

## Uninstall

### macOS / Linux

```bash
rm ~/.agents/skills/oneskills
rm -rf ~/.codex/oneskills
```

### Windows PowerShell

```powershell
Remove-Item -LiteralPath "$env:USERPROFILE\.agents\skills\oneskills" -Recurse -Force
Remove-Item -LiteralPath "$env:USERPROFILE\.codex\oneskills" -Recurse -Force
```
