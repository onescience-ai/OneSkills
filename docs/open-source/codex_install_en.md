
# **Codex Installation Guide**

## **Install Codex**

1. Install or update [Node.js](https://nodejs.org/en/download/) (v18.0 or higher).

2. Run the following command in your terminal to install Codex.

```
npm install -g @openai/codex
```

Run the following command to verify the installation.

```
codex --version
```

3. Configure credentials.

Edit the configuration file `~/.codex/config.toml` and set the environment variable `OPENAI_API_KEY`.

**Agent installed successfully:**

![image](images/codex-installed.png)

## OneSkills Installation

1. Open Codex and click the "Toggle Bottom Panel" button in the top-right corner.
2. Enter the following command in the bottom panel and wait for the installation to complete.

```shell
npx codex-marketplace add https://github.com/onescience-ai/oneskills --skills
```

![image](images/codex-marketplace-cmd.png)

**Installation complete:**

![image](images/codex-oneskills-installed.png)
