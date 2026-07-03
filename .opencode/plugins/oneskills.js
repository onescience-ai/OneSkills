/**
 * OneSkills plugin for OpenCode.ai
 *
 * Injects OneSkills bootstrap context via message transform.
 * Auto-registers the local repository skills directory via config hook.
 */

import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(__dirname, '..', '..');
const skillsDir = path.join(repoRoot, 'skills');
const installGuidePath = path.join(repoRoot, '.opencode', 'INSTALL.md');
const bootstrapMarker = 'You have OneSkills loaded for this repository.';

// Module-level cache for bootstrap content.
// The bootstrap text does not change during a session, so building it once
// avoids repeated file checks and string assembly on every agent step.
let bootstrapCache = undefined; // undefined = not yet loaded, null = unavailable

const readTextIfExists = (filePath) => {
  if (!fs.existsSync(filePath)) return null;
  return fs.readFileSync(filePath, 'utf8');
};

const getBootstrapContent = () => {
  if (bootstrapCache !== undefined) return bootstrapCache;
  if (!fs.existsSync(skillsDir)) {
    bootstrapCache = null;
    return null;
  }

  const installGuide = readTextIfExists(installGuidePath);
  const toolMapping = `**Tool Mapping for OpenCode:**
When OneSkills prompts request actions, substitute OpenCode equivalents:
- Create or update todos → \`todowrite\`
- Dispatch a subagent → OpenCode task/subagent tool
- Invoke a skill → OpenCode's native \`skill\` tool
- Read files → \`read\`
- Create, edit, or delete files → \`apply_patch\`
- Run shell commands → \`bash\`
- Search files → \`grep\`, \`glob\`
- Fetch a URL → \`webfetch\``;

  const routingGuide = `**Default OneSkills routing:**
- If the user says “使用 / 启动 / 打开 / 进入 onescience” or “使用 / 启动 / 打开 / 进入 oneskills”, start with \`onescience-workflow\` and ask for the concrete research goal before entering execution.
- Then use \`onescience-role\` to identify the responsible role and handoff.
- Then use \`onescience-skill\` to choose the smallest execution chain.
- Use \`onescience-coder\` for code generation or code modification.
- Use \`onescience-runtime\` only for run / submit / poll / diagnose tasks.
- Use \`onescience-installer\` only for install / repair / verify tasks.
- For paper reproduction, do not search, open, download, clone, or reference official or third-party implementation repositories.`;

  const sections = [
    bootstrapMarker,
    'OneSkills is available from the local repository checkout.',
    routingGuide,
    toolMapping,
    installGuide ? `**Local install note:**\nUse \.opencode/plugins/oneskills.js from this repository as the OpenCode plugin entry.` : null,
  ].filter(Boolean);

  bootstrapCache = `<EXTREMELY_IMPORTANT>\n${sections.join('\n\n')}\n</EXTREMELY_IMPORTANT>`;
  return bootstrapCache;
};

export const OneSkillsPlugin = async () => {
  return {
    // Inject skills path into live config so OpenCode discovers repository skills
    // without requiring symlinks or manual skills.paths edits.
    config: async (config) => {
      if (!fs.existsSync(skillsDir)) return;

      config.skills = config.skills || {};
      config.skills.paths = config.skills.paths || [];
      if (!config.skills.paths.includes(skillsDir)) {
        config.skills.paths.push(skillsDir);
      }
    },

    // Inject bootstrap into the first user message of each session.
    // Using a user message avoids repeatedly expanding system prompt content.
    'experimental.chat.messages.transform': async (_input, output) => {
      const bootstrap = getBootstrapContent();
      if (!bootstrap || !output.messages.length) return;

      const firstUser = output.messages.find((message) => message.info.role === 'user');
      if (!firstUser || !firstUser.parts.length) return;

      if (firstUser.parts.some((part) => part.type === 'text' && part.text.includes(bootstrapMarker))) {
        return;
      }

      const referencePart = firstUser.parts[0];
      firstUser.parts.unshift({ ...referencePart, type: 'text', text: bootstrap });
    },
  };
};
