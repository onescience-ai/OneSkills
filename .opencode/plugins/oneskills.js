/**
 * OneSkills plugin for OpenCode.ai
 *
 * 1) Injects OneSkills bootstrap context via message transform (soft layer).
 * 2) Enforces the skill-recall chain with HARD gates via tool.execute.before/after
 *    (code layer). Two breakpoints are covered:
 *      Breakpoint 1 — orchestrator loaded but primitives skipped:
 *        Gate 1: after `onescience-orchestrator` is loaded, execution tools
 *        (bash / write / edit / apply_patch / task) are blocked until
 *        `onescience-primitives` has been invoked for resource recall.
 *        Gate A: direct reads of primitives knowledge assets are blocked until
 *        the primitives skill itself is invoked (no recall bypass).
 *      Breakpoint 2 — primitives recalled but online fallback skipped:
 *        Gate B: after primitives, no write / compute / submit action is
 *        allowed until the retrieval decision is recorded
 *        (`.onescience/gaps.jsonl`, `knowledge_gap` boolean) or observed in
 *        the primitives result. If the gap is true, the model must first
 *        invoke `onescience-online-knowledge` (unified online verification:
 *        literature + crystal structure via COD + software parameters).
 *        `onescience-live-literature` still counts as a literature-only
 *        release for backward compatibility. Gate B also blocks hand-rolled
 *        curl/wget against COD / OpenAlex / Europe PMC / Unpaywall / arXiv
 *        while the gap is open — the skill's self-verifying scripts must be
 *        used instead.
 *    Fail-open: sessions that never load the orchestrator are never gated.
 *    Session state is keyed by sessionID so concurrent sessions stay isolated.
 *
 * The gap gates consume runtime artifacts on disk (`.onescience/gaps.jsonl`)
 * and real tool-call traces, not model self-declaration, so they cannot be
 * satisfied by "saying" a step happened.
 */

import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(__dirname, '..', '..');
const skillsDir = path.join(repoRoot, 'skills');
const installGuidePath = path.join(repoRoot, '.opencode', 'INSTALL.md');
const bootstrapMarker = 'You have OneSkills loaded for this repository.';

// ---------------------------------------------------------------------------
// Gate configuration
// ---------------------------------------------------------------------------

const ORCHESTRATOR_SKILL = 'onescience-orchestrator';

// Assets belong to the primitives skill; direct reads are the recall bypass.
const ASSETS_RE = new RegExp(`onescience-primitives[\\\\/]assets`, 'i');

// Tools that constitute "starting real work" — Gate 1 requires recall first.
// read / glob / grep / webfetch / todowrite stay allowed: the recall itself and
// skill-doc reading depend on them.
const EXECUTION_TOOLS = new Set(['bash', 'shell', 'write', 'edit', 'apply_patch', 'task']);

// Skills that only read / retrieve / plan — never blocked by Gate B.
const READONLY_SKILLS = [
  'primitives', 'live-literature', 'live_literature',
  'online-knowledge', 'online_knowledge',
  'orchestrator', 'model-gate',
];

// Skills that produce or run work — blocked while a knowledge gap is open.
const EXECUTE_SKILL_KEYS = [
  'runtime', 'runsite', 'trainer', 'infer', 'coder', 'installer',
  'paper-repro', 'parallel', 'data-analyzer', 'modelscope-publish',
  'knowledge-harvester', 'knowledge-capture', 'primitive-distiller',
];

// Bash tokens that indicate a write / compute / submit action.
const WRITE_TOKENS = [
  'sbatch', 'srun', 'salloc', 'module load', 'conda create', 'conda install',
  'conda activate', 'pip install', 'pip3 install', 'npm install', 'yarn add',
  'mkdir', 'touch', ' tee ', 'rm -', 'mv ', 'cp ', 'chmod', 'chown', 'wget',
  'curl -o', 'git apply', 'git am',
];

// Data/knowledge endpoints: querying them by hand while the gap gate is open
// is an improvised-retrieval bypass — the model must use the skill scripts.
const IMPROVISED_RETRIEVAL_RE =
  /(crystallography\.net|qiserver\.ugr\.es|api\.openalex\.org|europepmc|ebi\.ac\.uk|unpaywall|export\.arxiv\.org|arxiv\.org\/(?:abs|pdf)|doi\.org\/api|icsd|materialsproject\.org)/i;

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

const readTextIfExists = (filePath) => {
  if (!fs.existsSync(filePath)) return null;
  return fs.readFileSync(filePath, 'utf8');
};

// Best-effort structured log; never let logging break the gate.
const note = async (client, level, message) => {
  try {
    if (client && client.app && typeof client.app.log === 'function') {
      await client.app.log({ body: { service: 'oneskills-gate', level, message } });
    }
  } catch (_) {
    /* logging is optional */
  }
};

const skillNameFrom = (args) => {
  if (!args) return '';
  const v = args.name || args.skill || args.skill_name || args.skillName || args.id || '';
  return String(v).toLowerCase();
};

// Robustly pull the skill name from a hook's input/output for either direction.
const extractSkillName = (input, output) => {
  const src =
    (output && output.args) ||
    (input && input.args) ||
    (output && typeof output === 'object' && (output.name ? output : null)) ||
    input ||
    {};
  return skillNameFrom(src);
};

const isOrchestratorSkill = (name) => name.trim() === ORCHESTRATOR_SKILL;
const isPrimitiveSkill = (name) => name.includes('primitives');
const isLiveLiterature = (name) =>
  name.includes('live-literature') ||
  name.includes('live_literature') ||
  (name.includes('live') && name.includes('literature'));
const isOnlineKnowledge = (name) =>
  name.includes('online-knowledge') || name.includes('online_knowledge');
const isOnlineFallbackSkill = (name) => isOnlineKnowledge(name) || isLiveLiterature(name);
const isExecuteSkill = (name) =>
  EXECUTE_SKILL_KEYS.some((k) => name.includes(k)) && !READONLY_SKILLS.some((k) => name.includes(k));

const looksWriteOrCompute = (cmd) => {
  const s = ` ${String(cmd || '').toLowerCase()} `;
  if (WRITE_TOKENS.some((t) => s.includes(` ${t}`) || s.includes(t))) return true;
  // output redirection to a file (not a comparison like >= or <=)
  if (/[^=<>]\s*>\s*[^=]|>>/.test(s)) return true;
  return false;
};

// Read the freshest knowledge_gap decision the primitives skill recorded.
// Returns: undefined (no decision), true (gap open), false (local hit verified).
const latestGapDecision = (cwd) => {
  const p = path.join(cwd, '.onescience', 'gaps.jsonl');
  if (!fs.existsSync(p)) return undefined;
  try {
    const lines = fs.readFileSync(p, 'utf8').split('\n').filter((l) => l.trim());
    for (let i = lines.length - 1; i >= 0; i--) {
      try {
        const o = JSON.parse(lines[i]);
        if (typeof o.knowledge_gap === 'boolean') return o.knowledge_gap;
      } catch (_) {
        /* skip malformed line, keep scanning upward */
      }
    }
  } catch (_) {
    /* ignore read errors */
  }
  return undefined;
};

// Detect knowledge_gap=true inside the primitives skill's own result text
// (secondary signal for when gaps.jsonl has not yet been written).
const primitivesReportGap = (output) => {
  let text = '';
  try {
    if (typeof output === 'string') text = output;
    else {
      const out =
        (output && (output.output || output.result || output.text || output.content)) || output;
      text = typeof out === 'string' ? out : JSON.stringify(out || '');
    }
  } catch (_) {
    return false;
  }
  return /knowledge_gap["'`\s]*[:=]["'`\s]*true/i.test(text) ||
    /knowledge_gap[^\n]{0,40}\btrue\b/i.test(text);
};

const referencesAssets = (toolName, args) => {
  if (toolName === 'bash') return ASSETS_RE.test(args && args.command || '');
  if (toolName === 'read') return ASSETS_RE.test(String((args && (args.filePath || args.path || args.file)) || ''));
  if (toolName === 'glob') return ASSETS_RE.test(String((args && (args.path || args.pattern)) || ''));
  if (toolName === 'grep') return ASSETS_RE.test(String((args && (args.path || args.glob)) || ''));
  return false;
};

// Per-session state keyed by sessionID → concurrent sessions stay isolated.
const sessionStates = new Map();
const getSessionState = (sessionID) => {
  const key = sessionID || '__default__';
  let state = sessionStates.get(key);
  if (!state) {
    state = {
      orchestratorLoaded: false,
      primitivesCalled: false,
      onlineFallbackCalled: false,
      gapPending: false,
      awaitPrimitivesResult: false,
    };
    sessionStates.set(key, state);
  }
  return state;
};

// ---------------------------------------------------------------------------
// Bootstrap (soft layer)
// ---------------------------------------------------------------------------

let bootstrapCache; // undefined = not loaded, null = unavailable

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
- If the user says “使用 / 启动 / 打开 / 进入 onescience” or “使用 / 启动 / 打开 / 进入 oneskills”, start with \`onescience-orchestrator\` and ask for the concrete research goal before entering execution.
- Use \`onescience-coder\` for code generation or code modification.
- Use \`onescience-runtime\` only for run / submit / poll / diagnose tasks.
- Use \`onescience-installer\` only for install / repair / verify tasks.
- For paper reproduction, do not search, open, download, clone, or reference official or third-party implementation repositories.`;

  const gateNote = `**Enforced gates (this plugin will block tool calls that violate them):**
- Breakpoint 1: after \`onescience-orchestrator\` is loaded, before \`onescience-primitives\` has been invoked, execution tools (bash / write / edit / apply_patch / task) are blocked. Load primitives first and complete resource recall.
- Do not read or grep \`onescience-primitives/assets/\` directly. Invoke the \`onescience-primitives\` skill first; only its own retrieval may touch the assets.
- Breakpoint 2: after calling primitives, before any run / write / calculation, record the retrieval decision by appending a \`gaps.jsonl\` line under \`.onescience/\` with a \`knowledge_gap\` boolean (primitives step 10).
- If \`knowledge_gap=true\` (no domain-specific local hit), you MUST call \`onescience-online-knowledge\` (unified online verification: literature + crystal structure via COD + software parameters) to retrieve verified, cited evidence before writing scripts, submitting jobs, or answering domain parameters. Never substitute model memory, default parameters, fabricated data, or hand-rolled curl/wget queries against COD / OpenAlex / arXiv for this step — use the skill's scripts, which self-verify results.
- Retrieved values must be consumed with provenance: literature facts carry [n] citations, structures carry COD ids, software parameters carry software-doc sources; model-prior fallbacks must be explicitly marked as “⚠ 未经在线核实” and never disguised as a cited source.`;

  const sections = [
    bootstrapMarker,
    'OneSkills is available from the local repository checkout.',
    routingGuide,
    gateNote,
    toolMapping,
    installGuide ? `**Local install note:**\nUse \.opencode/plugins/oneskills.js from this repository as the OpenCode plugin entry.` : null,
  ].filter(Boolean);

  bootstrapCache = `<EXTREMELY_IMPORTANT>\n${sections.join('\n\n')}\n</EXTREMELY_IMPORTANT>`;
  return bootstrapCache;
};

// ---------------------------------------------------------------------------
// Plugin
// ---------------------------------------------------------------------------

export const OneSkillsPlugin = async ({ client, directory, worktree } = {}) => {
  const cwd = worktree || directory || process.cwd();

  return {
    // Register repository skills dir into live config.
    config: async (config) => {
      if (!fs.existsSync(skillsDir)) return;
      config.skills = config.skills || {};
      config.skills.paths = config.skills.paths || [];
      if (!config.skills.paths.includes(skillsDir)) {
        config.skills.paths.push(skillsDir);
      }
    },

    // Inject bootstrap into the first user message of each session.
    'experimental.chat.messages.transform': async (_input, output) => {
      const bootstrap = getBootstrapContent();
      if (!bootstrap || !output.messages.length) return;
      const firstUser = output.messages.find((m) => m.info.role === 'user');
      if (!firstUser || !firstUser.parts.length) return;
      if (firstUser.parts.some((p) => p.type === 'text' && p.text.includes(bootstrapMarker))) return;
      const referencePart = firstUser.parts[0];
      firstUser.parts.unshift({ ...referencePart, type: 'text', text: bootstrap });
    },

    // Observe the primitives result to arm the gap gate even before gaps.jsonl
    // lands, and mirror skill-invocation progress (secondary signal; the
    // `before` hook also flips flags because it reliably exposes output.args).
    'tool.execute.after': async (input, output) => {
      if (input.tool !== 'skill') return;
      const state = getSessionState(input && input.sessionID);
      const name = extractSkillName(input, output);
      if (isPrimitiveSkill(name)) {
        state.primitivesCalled = true;
        if (state.awaitPrimitivesResult) {
          state.awaitPrimitivesResult = false;
          if (primitivesReportGap(output) && !state.onlineFallbackCalled) {
            state.gapPending = true;
          }
        }
      } else if (isOnlineFallbackSkill(name)) {
        state.onlineFallbackCalled = true;
        state.gapPending = false;
      }
    },

    // Hard gates.
    'tool.execute.before': async (input, output) => {
      const toolName = String(input.tool || '').toLowerCase();
      const args = (output && output.args) || (input && input.args) || {};
      const state = getSessionState(input && input.sessionID);
      const name = toolName === 'skill' ? extractSkillName(input, output) : '';

      // Track skill-chain progress as soon as the model invokes a skill.
      if (toolName === 'skill') {
        if (isOrchestratorSkill(name)) {
          // Re-entering the orchestrator after recall already completed = a new
          // research task in the same session → require a fresh recall chain.
          if (state.primitivesCalled) {
            state.primitivesCalled = false;
            state.onlineFallbackCalled = false;
            state.gapPending = false;
          }
          state.orchestratorLoaded = true;
          return;
        }
        if (isPrimitiveSkill(name)) {
          state.primitivesCalled = true;
          state.awaitPrimitivesResult = true;
          if (!state.orchestratorLoaded) state.orchestratorLoaded = true;
          await note(client, 'info', 'primitives invoked; gate B active for this session');
          return;
        }
        if (isOnlineFallbackSkill(name)) {
          state.onlineFallbackCalled = true;
          state.gapPending = false;
          await note(client, 'info', `online fallback skill invoked (${name}); knowledge-gap gate released`);
          return;
        }
      }

      // --- Gate 1 (breakpoint 1): orchestrator loaded but primitives skipped.
      if (state.orchestratorLoaded && !state.primitivesCalled && EXECUTION_TOOLS.has(toolName)) {
        await note(client, 'warn', `Gate 1 blocked ${toolName}: execution before primitives recall`);
        throw new Error(
          '[OneSkills] 已加载 onescience-orchestrator，但尚未完成资源召回，不能进入执行。' +
            '请先用 skill 工具调用 `onescience-primitives` 完成知识原语召回' +
            '（resource_retrieval_request → matched_resources → gaps.jsonl 结论），再执行本操作。',
        );
      }

      // --- Gate A: force going through the primitives skill before touching assets.
      if (!state.primitivesCalled && referencesAssets(toolName, args)) {
        await note(client, 'warn', `Gate A blocked ${toolName}: direct assets access before primitives recall`);
        throw new Error(
          '[OneSkills] 不得直接读取 primitives 知识资产目录。' +
            '请先调用 skill `onescience-primitives` 走统一资源召回契约，' +
            '由 primitives 技能自身负责检索 assets。',
        );
      }

      // --- Gate B (breakpoint 2): knowledge-gap fallback gate.
      // Only after primitives has been recalled, and before an online fallback ran.
      if (state.primitivesCalled && !state.onlineFallbackCalled) {
        const fileDecision = latestGapDecision(cwd);
        // Effective gap: file says true, or file missing but the primitives
        // result itself already reported knowledge_gap=true.
        const gapOpen = fileDecision === true || (fileDecision === undefined && state.gapPending);
        const noDecision = fileDecision === undefined && !state.gapPending;

        const isExecuteAction =
          toolName === 'apply_patch' ||
          toolName === 'write' ||
          toolName === 'edit' ||
          (toolName === 'skill' && isExecuteSkill(name)) ||
          (toolName === 'bash' && (looksWriteOrCompute(args.command) ||
            // Improvised retrieval bypass while the gap is open.
            (gapOpen && IMPROVISED_RETRIEVAL_RE.test(String(args.command || '')))));

        if (isExecuteAction) {
          if (noDecision) {
            await note(client, 'warn', `Gate B blocked ${toolName}: no recorded retrieval decision`);
            throw new Error(
              '[OneSkills] 已调用 primitives，但没有落盘检索结论，不能进入执行/写文件。' +
                '请按 primitives step 10 把本轮 retrieval 结果追加到 `.onescience/gaps.jsonl`' +
                '（含布尔字段 `knowledge_gap`）：本地确有领域实质命中则 `knowledge_gap=false`；' +
                '若为空或仅命中泛化流程卡，则 `knowledge_gap=true` 并必须先调用 `onescience-online-knowledge`。',
            );
          }
          if (gapOpen) {
            await note(client, 'warn', `Gate B blocked ${toolName}: knowledge_gap=true, online fallback not called`);
            throw new Error(
              '[OneSkills] 检测到本地知识缺口（knowledge_gap=true），且尚未调用在线查证兜底。' +
                '必须先调用 skill `onescience-online-knowledge`（文献+晶体结构COD+软件参数三通道）' +
                '真实联网查证并产出带出处（DOI / COD编号 / software-doc）的证据后，' +
                '再继续写脚本、提交作业或回答领域参数。' +
                '禁止用模型记忆、默认参数或模拟数据替代检索，也禁止自行 curl/wget 查询 COD/OpenAlex/arXiv 等端点——' +
                '必须使用该技能内带化学式回验等自校验机制的脚本。',
            );
          }
          // fileDecision === false → verified local hit, allow execution.
        }
      }

      // Read-only intents (read/glob/grep/webfetch/todowrite, primitives,
      // online-knowledge, live-literature, planning skills) fall through and
      // are always allowed.
      return;
    },
  };
};
