
# **Claude Code Installation Guide**

## Install Claude Code

### macOS

1. Install or update [Node.js](https://nodejs.org/en/download/) (v18.0 or higher).
2. Run the following command in your terminal to install Claude Code.

```
npm install -g @anthropic-ai/claude-code
```

3. Verify the installation by checking the version.

```
claude --version
```

### Windows

To use Claude Code on Windows, you first need to install WSL or [Git for Windows](https://git-scm.com/install/windows), then run the following commands in WSL or Git Bash.

```
npm install -g @anthropic-ai/claude-code
```

> For details, see the [Windows setup guide](https://docs.anthropic.com/en/docs/claude-code/setup#windows-setup) in the Claude Code official documentation.

## Skip Onboarding

Create or edit `~/.claude.json` and set `hasCompletedOnboarding` to `true` to skip the Anthropic login verification.

```
{
  "hasCompletedOnboarding": true
}
```

## Configure Credentials

Create `~/.claude/settings.json` with the following configuration.

```json
{
    "env": {
        "ANTHROPIC_AUTH_TOKEN": "YOUR_API_KEY",
        "ANTHROPIC_BASE_URL": "xxx",
        "ANTHROPIC_MODEL": "xxx"
    }
}
```

**Agent installed successfully:**

![image](images/claude-code-installed.png)

## OneSkills Installation

1. Enter the following command to add OneSkills to the Claude Code marketplace.

```shell
/plugin marketplace add https://github.com/onescience-ai/oneskills
```

2. Enter the following command to install the `oneskills@oneskills` plugin.

```shell
/plugin install oneskills@oneskills
```

**Installation complete:**

![image](images/claude-oneskills-installed.png)
