
# **OpenCode Installation Guide**

## **Install OpenCode**

1. Install [Node.js](https://nodejs.org/en/download/) (v18.0 or higher).

2. Run the following command in your terminal to install OpenCode.

```
npm install -g opencode-ai
```

Run the following command to verify the installation. If a version number is displayed, the installation was successful.

```
opencode -v
```

3. Configure credentials

Open the configuration file with a text editor:

- macOS / Linux: `~/.config/opencode/opencode.json`
- Windows: `C:\Users\<username>\.config\opencode\opencode.json`

**Agent installed successfully:**

![image](images/opencode-installed.png)

## OneSkills Installation

Enter the following command in the OpenCode dialog and execute it. OpenCode will check out and install OneSkills from the current repository according to the installation instructions.

```shell
Please follow the instructions at https://github.com/onescience-ai/oneskills/blob/master/.opencode/INSTALL.md to check out and install OneSkills for OpenCode from the current repository
```

**OneSkills installation complete:**

![image](images/opencode-oneskills-installed.png)
