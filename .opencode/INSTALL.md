# Install OneSkills for OpenCode

Use the repository-local OpenCode plugin to enable OneScience / OneSkills skills inside OpenCode. This path keeps the integration self-contained in the cloned repository and does not require Python.

## One-Line User Prompt

Users can paste this single sentence into OpenCode:

```text
Fetch and follow instructions from https://github.com/onescience-ai/oneskills/blob/master/.opencode/INSTALL.md to install OneSkills for OpenCode from the current repository checkout.
```

OpenCode should update the local `opencode.json` if needed, point it at `.opencode/plugins/oneskills.js`, restart guidance should be given after config changes, and the user should not be asked to manually discover skill paths unless the default plugin flow fails.

## Prerequisites

- [OpenCode.ai](https://opencode.ai) installed
- A local checkout of this repository
- Network access to GitHub if the user is fetching this file remotely

## Install

Add the local plugin to the `plugin` array in your OpenCode config.

### Project-level config

If you want OneSkills only for the current repository, add this to the project `opencode.json`:

```json
{
  "plugin": [".opencode/plugins/oneskills.js"]
}
```

### Global config

If you want to load this repository checkout from a global OpenCode config, use the absolute path to the plugin file instead:

```json
{
  "plugin": ["/absolute/path/to/oneskills/.opencode/plugins/oneskills.js"]
}
```

On Windows, that looks like:

```json
{
  "plugin": ["D:\\path\\to\\oneskills\\.opencode\\plugins\\oneskills.js"]
}
```

If `plugin` already exists, append the OneSkills entry instead of replacing existing plugins.

Restart OpenCode after saving the config.

## What this loads

The local plugin at `.opencode/plugins/oneskills.js`:

- registers the repository `skills/` directory automatically
- injects a OneSkills bootstrap into the first user message
- maps OneSkills prompts to OpenCode-native tools
- keeps the integration self-contained inside this repository

This means you normally do not need to manually add `skills.paths` to `opencode.json` when using the plugin.

## Verify

Before restarting OpenCode, confirm the plugin file exists:

```text
.opencode/plugins/oneskills.js
```

After restarting OpenCode, try one of these prompts:

```text
使用 oneskills
```

```text
进入 onescience
```

```text
use skill tool to list skills
```

The expected entry behavior is that OneSkills routes general OneScience requests through `onescience-workflow`.

## Troubleshooting

### Plugin not loading

1. Check that `.opencode/plugins/oneskills.js` exists.
2. Verify the `plugin` entry in `opencode.json` points to the right path.
3. Restart OpenCode after editing config.
4. If you configured a global path, make sure it points to this repository checkout.

### Skills not found

1. Use the `skill` tool to list discovered skills.
2. Confirm the repository still contains `skills/onescience-workflow/SKILL.md`.
3. Confirm the plugin loaded successfully.
4. If the plugin flow is blocked in your environment, fall back to explicitly adding the repository `skills/` directory through OpenCode's skill path configuration.

### Repository moved

If you move this repository, update the plugin path in any global `opencode.json` that points at the old checkout.

## Update

Pull the latest repository changes, then restart OpenCode so the plugin and skills reload from the updated checkout.

## Uninstall

Remove the OneSkills plugin entry from `opencode.json`, then restart OpenCode.