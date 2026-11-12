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
 *      Breakpoint 3 — remote commercial-software compute without a workbench:
 *        Gate R: when ~/.ssh/config declares >=2 platform SSH connections, any
 *        remote entry (skill onescience-runtime / onescience-mlmd-campaign-
 *        orchestrator, or bash sbatch/srun/ssh/scp/rsync) is blocked until
 *        onescience-runsite has been invoked, forcing the workbench selection
 *        popup to appear before any remote job. Fail-open when <2 connections.
 *      Breakpoint 4 — artifacts dumping into a remote home root (Gate H):
 *        for bash scp / rsync / ssh / sbatch, when an output artifact would land
 *        directly in the target node's HOME root, output.args.command is
 *        MUTATED to redirect it under ~/rsi-<sessionKey>/ (English+digits,
 *        derived from sessionID) and create that dir first; paths that already
 *        carry a subdirectory are left untouched. A prefilter regex lets the
 *        overwhelming majority of non-transfer commands pass through untouched.
 *      Breakpoint 5 — main-process long waits (Gate L):
 *        a bash sleep >=30s, timeout >=60s, or while/for..sleep poll loop is
 *        blocked; the model is told to dispatch the wait to a task subagent
 *        instead of stalling the main agent. Short waits fall through.
 *    Session state is keyed by sessionID so concurrent sessions stay isolated.
 *
 * The gap gates consume runtime artifacts on disk (`.onescience/gaps.jsonl`)
 * and real tool-call traces, not model self-declaration, so they cannot be
 * satisfied by "saying" a step happened.
 */

import path from 'path';
import fs from 'fs';
import os from 'os';
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
  /(crystallography\.net|qiserver\.ugr\.es|api\.openalex\.org|europepmc|ebi\.ac\.uk|unpaywall|export\.arxiv\.org|arxiv\.org\/(?:abs|pdf)|doi\.org\/api|icsd|materialsproject\.org|rcsb\.org|wwpdb\.org|drugbank\.ca|uniprot\.org|climate\.copernicus\.eu)/i;

// ---------------------------------------------------------------------------
// Gate R configuration — runsite workbench gate. Remote commercial-software
// compute (a campaign/pipeline executor handoff or a submitted remote job) must
// be preceded by an onescience-runsite workbench selection whenever >=2 platform
// SSH connections exist, so the SSH selection popup reliably appears. Consumes
// the real ~/.ssh/config on disk and the runsite skill-invocation trace, not
// model self-declaration. Fail-open when fewer than 2 connections.
// ---------------------------------------------------------------------------

const RUNSITE_SKILL_KEY = 'runsite';
const REMOTE_ENTRY_SKILL_KEYS = ['runtime', 'mlmd-campaign-orchestrator', 'campaign-orchestrator'];
const REMOTE_EXEC_TOKENS = ['ssh ', 'sbatch', 'srun', 'salloc', 'scp ', 'rsync '];

const isRunsiteSkill = (name) => name.includes(RUNSITE_SKILL_KEY);
const isRemoteEntrySkill = (name) => REMOTE_ENTRY_SKILL_KEYS.some((k) => name.includes(k));
const looksRemoteExec = (cmd) => {
  const s = ` ${String(cmd || '').toLowerCase()} `;
  return REMOTE_EXEC_TOKENS.some((t) => s.includes(t));
};

// Count platform SSH connections declared in ~/.ssh/config (opencode ssh marker
// preferred; falls back to distinct Host aliases). Read-only, best-effort.
const sshConnectionCount = (cwd) => {
  let content = null;
  for (const p of [path.join(os.homedir(), '.ssh', 'config'), path.join(cwd, '.ssh', 'config')]) {
    const t = readTextIfExists(p);
    if (t) { content = t; break; }
  }
  if (!content) return 0;
  const markers = (content.match(/#\s*>{3}\s*opencode\s+ssh/gi) || []).length;
  if (markers > 0) return markers;
  const hosts = (content.match(/^Host\s+(.+)$/gim) || [])
    .map((l) => l.replace(/^Host\s+/i, '').trim())
    .flatMap((v) => v.split(/\s+/))
    .filter((h) => h && h !== '*' && !h.includes('*'));
  return new Set(hosts).size;
};

// ---------------------------------------------------------------------------
// Artifact-home rewrite (Gate H): when an scp / rsync / ssh / sbatch command
// would drop an output artifact directly into the target node's HOME root,
// rewrite the destination so it lands under a per-session subdirectory
// ~/rsi-<key>/ (English + digits, traceable to the sessionID) instead of
// littering home. Paths that already carry a meaningful subdirectory (~/work/x, ~/runs/e42/x,
// ./data/x, /abs/dir/x) are left untouched — the model is expected to name a
// real task dir, Gate H is only the lazy-dump-to-home safety net.
// Implemented by MUTATING output.args.command (best-effort; falls through
// silently if a shape is not confidently parseable).
// ---------------------------------------------------------------------------

const ARTIFACT_HOME_PREFIX = 'rsi'; // ~/rsi-<key>/
const sessionKeyOf = (sessionID) => {
  const raw = String(sessionID || '').replace(/[^a-zA-Z0-9]/g, '');
  const tail = raw.slice(-8) || 'run';
  return `${ARTIFACT_HOME_PREFIX}-${tail}`.toLowerCase();
};

// True when a remote path points at the bare home root: a single filename
// directly under ~ / $HOME / /home/<user> / the default (home-relative) scp
// location — NOT inside any existing subdirectory.
const isBareHomePath = (p) => {
  if (!p) return false;
  const s = p.trim();
  if (s === '~' || s === '~/' || s === '$HOME' || s === '$HOME/' || s === '.') return true;
  let rest = null;
  if (/^~\/[^/]+$/.test(s)) rest = s.slice(2);
  else if (/^\$HOME\/[^/]+$/.test(s)) rest = s.slice(6);
  else if (/^\/home\/[^/]+\/[^/]+$/.test(s)) rest = s.split('/').pop();
  else if (/^[^./][^/]*$/.test(s) && !s.includes('/')) rest = s; // bare "foo.dat"
  return rest !== null && !!rest && !rest.includes('/');
};

// Split a shell-ish command tail into tokens, honoring single/double quotes
// and treating whitespace and a trailing `;` as boundaries outside quotes.
// Each token keeps its raw text (with quotes) and its unquoted value.
const tokenizeShell = (s) => {
  const toks = [];
  let i = 0;
  while (i < s.length) {
    while (i < s.length && (/\s/.test(s[i]) || s[i] === ';')) i++;
    if (i >= s.length) break;
    let raw = '';
    let val = '';
    while (i < s.length && !/\s/.test(s[i]) && s[i] !== ';') {
      const ch = s[i];
      if (ch === '"' || ch === "'") {
        const q = ch; raw += ch; i++;
        while (i < s.length && s[i] !== q) { raw += s[i]; val += s[i]; i++; }
        if (i < s.length) { raw += s[i]; i++; }
      } else { raw += ch; val += ch; i++; }
    }
    toks.push({ raw, val });
  }
  return toks;
};

// A scp destination path that dumps into the home root: empty (host:),
// ~ / ~/ / $HOME / $HOME/ (dir-only) or a single bare filename.
const isBareHomeTarget = (p) => {
  if (p === '' || p === undefined || p === null) return true;
  return isBareHomePath(p);
};

// Rewrite scp/rsync upload destination: `[scp|rsync] [src...] [[user@]host:]<bare>`.
// Quote-aware (handles `scp "a.txt" "host:~/"`), and treats a dir-only
// destination (`host:` / `host:~/`) as "copy the source basename into the key
// dir". Only a REMOTE destination is in scope; a purely local copy is skipped.
// rsync is same-family as scp for the `host:path` destination syntax.
const rewriteScp = (cmd, key) => {
  const lead = cmd.match(/^\s*(?:scp|rsync)\s+/);
  if (!lead) return null;
  const rest = cmd.slice(lead[0].length);
  const trailing = (rest.match(/(\s*;?\s*)$/) || ['', ''])[0];
  const core = rest.slice(0, rest.length - trailing.length);
  const toks = tokenizeShell(core);
  if (toks.length === 0) return null;
  const dest = toks[toks.length - 1];
  const colon = dest.val.indexOf(':');
  if (colon < 0) return null; // local dest -> not a remote artifact upload
  const hostSpec = dest.val.slice(0, colon); // may be user@host or host
  if (!/^[\w.+-]*@?[\w.-]+$/.test(hostSpec) || hostSpec.includes('/')) return null;
  const path = dest.val.slice(colon + 1);
  if (!isBareHomeTarget(path)) return null;
  let newPath;
  if (path === '' || path === '~' || path === '~/' || path === '$HOME' || path === '$HOME/') {
    newPath = `~/${key}/`; // dir-only: source basename lands inside the key dir
  } else {
    const fn = path.replace(/^(?:~\/|\$HOME\/)/, '').split('/').pop();
    newPath = `~/${key}/${fn}`;
  }
  const newDestVal = `${hostSpec}:${newPath}`;
  const q = dest.raw[0] === '"' || dest.raw[0] === "'" ? dest.raw[0] : '';
  const newDestRaw = q ? `${q}${newDestVal}${q}` : newDestVal;
  const idx = cmd.lastIndexOf(dest.raw);
  const head = cmd.slice(0, idx);
  const tailAfter = cmd.slice(idx + dest.raw.length);
  const mkdir = `ssh ${hostSpec} 'mkdir -p ~/${key}'; `;
  return `${mkdir}${head}${newDestRaw}${tailAfter}`;
};

// Match `ssh [host] "remote command"`, allowing the host to be quoted
// (`ssh "host" "..."`). Returns { host, q, inner, tail } or null.
const matchSshQuoted = (cmd) => {
  const m = cmd.match(/^(\s*ssh\s+)(["']?)([\w.+-]*@?[\w.-]+)\2\s+(['"])([\s\S]*?)\4(\s*;?\s*)$/);
  if (!m) return null;
  return { host: m[3], q: m[4], inner: m[5], tail: m[6] };
};

// Rewrite ssh remote-command output redirections: `ssh host "cmd > <bare>"`
const rewriteSsh = (cmd, key) => {
  const mm = matchSshQuoted(cmd);
  if (!mm) return null;
  const { host, q, inner, tail } = mm;
  // find `> path` / `>> path` whose target is a bare home path
  let changed = false;
  const newInner = inner.replace(/(>>?)\s*([^\s;|&]+)/g, (op2, op, pathTok) => {
    const clean = pathTok.replace(/^['"]|['"]$/g, '');
    if (!isBareHomePath(clean)) return op2;
    const fn = clean.replace(/^(?:~\/|\$HOME\/)/, '').split('/').pop();
    changed = true;
    return `${op} ~/${key}/${fn}`;
  });
  if (!changed) return null;
  const mkdir = `ssh ${host} 'mkdir -p ~/${key}'; `;
  return `${mkdir}ssh ${host} ${q}${newInner}${q}${tail}`.replace(/\s+$/, '');
};

// Rewrite sbatch: force --output/--error under the key dir when absent or bare.
// Handles both a bare `sbatch job.sbatch` and one wrapped in `ssh host "..."`.
const rewriteSbatch = (cmd, key) => {
  if (!/\bsbatch\b/.test(cmd)) return null;
  // Fix a bare --output/--error/-o/-e value that points at the home root.
  const fixFlags = (str) =>
    str.replace(/(--output|--error|-o|-e)([=\s])([^\s'"]+)/g, (mm, flag, sep, val) => {
      const clean = val.replace(/^['"]|['"]$/g, '');
      if (isBareHomePath(clean)) {
        const fn = clean.replace(/^(?:~\/|\$HOME\/)/, '').split('/').pop();
        return `${flag}${sep}~/${key}/${fn}`;
      }
      return mm;
    });
  const hasOut = /(?:\s-o\s|--output[=\s])/.test(cmd);
  const hasErr = /(?:\s-e\s|--error[=\s])/.test(cmd);
  const extra = `${hasOut ? '' : ` --output=~/${key}/slurm-%j.out`}${hasErr ? '' : ` --error=~/${key}/slurm-%j.err`}`;

  const sshWrapped = matchSshQuoted(cmd);
  if (sshWrapped) {
    const { host, q, inner, tail } = sshWrapped;
    const already = new RegExp(`/${key}/`).test(inner);
    if (!extra && already) return null;
    let newInner = fixFlags(inner);
    if (extra) newInner = newInner.replace(/(\bsbatch\b[^'";]*)/, `$1${extra}`);
    const mkdir = `ssh ${host} 'mkdir -p ~/${key}'; `;
    return `${mkdir}ssh ${host} ${q}${newInner}${q}${tail}`.replace(/\s+$/, '');
  }

  // plain local sbatch
  const already = new RegExp(`/${key}/`).test(cmd);
  if (!extra && already) return null;
  let fixed = fixFlags(cmd);
  if (extra) fixed = fixed.replace(/(\bsbatch\b[^;]*)/, `$1${extra}`);
  return fixed.replace(/\s+$/, '');
};

// Master dispatcher: return the rewritten command, or null if nothing changed.
// Fast-path prefilter: only commands mentioning scp/rsync/ssh/sbatch can ever
// touch the remote-home rewrite logic, so the vast majority of bash calls
// (file edits, python, git, ls, ...) exit on a single regex test and pass
// through untouched. Only the small scp/rsync/ssh/sbatch subset is inspected.
const ARTIFACT_PREFILTER_RE = /\b(?:scp|rsync|ssh|sbatch)\b/;
const rewriteArtifactCommand = (cmd, key) => {
  const s = String(cmd || '');
  if (!ARTIFACT_PREFILTER_RE.test(s)) return null; // 99.5% pass-through
  if (/\b(?:scp|rsync)\b/.test(s)) {
    const r = rewriteScp(s, key);
    if (r) return r;
  }
  if (/\bsbatch\b/.test(s)) {
    const r = rewriteSbatch(s, key);
    if (r) return r;
  }
  if (/\bssh\b/.test(s)) {
    const r = rewriteSsh(s, key);
    if (r) return r;
  }
  return null;
};

// ---------------------------------------------------------------------------
// Long-wait blocking guard (Gate L): a main-process bash that would stall the
// session on sleep / timeout / a poll-loop is refused so the agent dispatches
// the wait to a task subagent instead of blocking. Thresholds are seconds.
// ---------------------------------------------------------------------------

const LONG_SLEEP_SEC = 30;   // sleep >= 30s -> blocking
const LONG_TIMEOUT_SEC = 60; // timeout >= 60s -> blocking

const parseDur = (n, unit) => {
  const v = parseFloat(n);
  if (Number.isNaN(v)) return 0;
  if (/h$/i.test(unit)) return v * 3600;
  if (/m$/i.test(unit) && !/ms$/i.test(unit)) return v * 60;
  return v; // plain seconds
};

// Returns { blocking, reason } for a bash command string.
const looksLongBlocking = (cmd) => {
  const s = String(cmd || '');
  // explicit sleep with a duration >= threshold
  const sleepRe = /\bsleep\s+(\d+(?:\.\d+)?\s*(?:s|m|h|ms)?|\d+h\d*m?|\d*m\d*s?)/gi;
  let m;
  while ((m = sleepRe.exec(s)) !== null) {
    const tok = m[1].trim();
    const unit = (tok.match(/[a-z]+$/i) || ['s'])[0];
    const num = tok.replace(/[a-z]+$/i, '');
    if (parseDur(num, unit) >= LONG_SLEEP_SEC) {
      return { blocking: true, reason: `sleep ${tok} (>=${LONG_SLEEP_SEC}s)` };
    }
  }
  // timeout <duration> ... with duration >= threshold
  const toRe = /\btimeout\s+(\d+(?:\.\d+)?[smh]?|\d+:\d+(?::\d+)?)/gi;
  while ((m = toRe.exec(s)) !== null) {
    const tok = m[1].trim();
    let sec;
    if (tok.includes(':')) {
      const parts = tok.split(':').map((x) => parseInt(x, 10) || 0);
      sec = parts.length === 3 ? parts[0] * 3600 + parts[1] * 60 + parts[2]
        : parts.length === 2 ? parts[0] * 60 + parts[1] : parts[0];
    } else {
      const unit = (tok.match(/[a-z]+$/i) || ['s'])[0];
      sec = parseDur(tok.replace(/[a-z]+$/i, ''), unit);
    }
    if (sec >= LONG_TIMEOUT_SEC) {
      return { blocking: true, reason: `timeout ${tok} (>=${LONG_TIMEOUT_SEC}s)` };
    }
  }
  // busy poll loop: while ... sleep/watch, or repeated squeue|grep RUNNING
  if (/\bwhile\b[\s\S]*\bsleep\b/.test(s) || /\bfor\b[\s\S]*\bsleep\b/.test(s)) {
    return { blocking: true, reason: 'while/for 轮询循环内嵌 sleep' };
  }
  if (/\bwatch\s+-n\s+(\d{2,})/.test(s)) {
    const n = parseInt((s.match(/\bwatch\s+-n\s+(\d+)/) || [])[1], 10);
    if (n >= LONG_SLEEP_SEC) return { blocking: true, reason: `watch -n ${n}s` };
  }
  return { blocking: false, reason: '' };
};

// Build a copy-paste-ready `task(...)` handoff for a blocked long-wait command,
// so the model dispatches a subagent to carry out the wait instead of stalling
// the main agent (or just reporting the block). The plugin cannot call `task`
// itself — only the model can — so this returns the exact call to issue now.
const buildSubagentHandoff = (cmd) => {
  const s = String(cmd || '').trim();
  // bare `sleep <dur>` -> subagent just waits that long and reports
  const sleepOnly = s.match(/^sleep\s+(\S+)(?:\s+.*)?$/i);
  if (sleepOnly && !/ssh|srun|sbatch|squeue/.test(s)) {
    const d = sleepOnly[1];
    return `task(subagent_type="general", prompt="Wait ${d} (run: sleep ${d}) in the background, then report that the wait is complete. Do not block the main agent.")`;
  }
  // job / remote wait -> subagent polls to completion
  return `task(subagent_type="general", prompt="Run and supervise this long job without blocking the main agent: ${s}. Poll its status read-only every 60s until it finishes, then return a short summary and the artifact path(s).")`;
};

// Detect whether a session is a subagent (spawned by the task tool) by reading
// its parentID via the client. Gate L must NOT block long waits inside a
// subagent — that is exactly where the wait is supposed to happen. Best-effort
// with a per-session cache; on any failure we treat it as the main agent.
const subagentCache = new Map();
const isSubagentSession = async (client, sessionID) => {
  const id = String(sessionID || '');
  if (!id) return false;
  if (subagentCache.has(id)) return subagentCache.get(id);
  let isSub = false;
  try {
    if (client && client.session && typeof client.session.get === 'function') {
      const res = await client.session.get({ path: { id } });
      const data = (res && res.data) || res;
      isSub = !!(data && data.parentID);
    }
  } catch (_) {
    isSub = false;
  }
  subagentCache.set(id, isSub);
  return isSub;
};

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
// Delivered verbatim to the model while the provenance self-check is still
// outstanding for a session that went online. ASCII only: this string is pushed
// into chat parts and must not perturb the surrounding template literals.
const PROV_GATE_NOTE = [
  '',
  '[oneskills] PROVENANCE GATE - before delivering the final answer, run:',
  '  python skills/onescience-online-knowledge/scripts/check_provenance.py --answer <draft.md> --workdir <online dir>',
  'Every concrete identifier (DOI / COD / arXiv / PDB / UniProt id) must appear verbatim in tool-produced',
  'evidence (lit_result.json / structure_result.json / param_result.json / formula-verified CIF), or be',
  'marked as a model prior on the same line. Exit code 2 means fix the draft before delivery, and the',
  'agent-authored online_knowledge.json does not count as a source (circular).',
  'Never present an identifier that cannot be traced to a retrieval receipt.',
  '',
].join('\n');

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
      runsiteCalled: false,
      litSearchSeen: false,
      provDone: false,
      provNotes: 0,
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
- For ANY scientific computing, simulation, modeling, or data-analysis task —包括但不限于: DFT, VASP, Quantum ESPRESSO, CP2K, MD, AIMD, LAMMPS, GROMACS, MACE, DeePMD, NEB, CFD, OpenFOAM, quantum chemistry, Gaussian, ORCA, Psi4, NWChem, xTB, CCSD(T), TDDFT, Monte Carlo, GCMC, FEM, COMSOL, ANSYS, ABAQUS, multiphysics, FDTD, photonics, bioinformatics, genomics, protein, RNA-seq, single-cell, molecular docking, AutoDock, Vina, virtual screening, drug design, QSAR, materials, crystal, surface, interface, adsorption, catalysis, battery, alloy, semiconductor, electrochemistry, Butler-Volmer, EIS, PyBaMM, corrosion, spectroscopy, IR, Raman, UV-Vis, XPS, NMR, EPR, XAS, climate, weather, WRF, geophysics, astrophysics, plasma, polymer, coarse-grained, MARTINI, soft matter, model training, fine-tuning, inference, paper reproduction, dataset construction, data analysis, visualization, HPC/SLURM job submission, slab building, adsorbate placement, solvation, doping, defect, POSCAR/INCAR/KPOINTS, selective dynamics, SciPy, NumPy, Julia, FEniCS, ODE/PDE solvers, numerical methods, Bayesian optimization, **or ANY other scientific/engineering/research computing task** — ALWAYS start with \`onescience-orchestrator\`. It performs intent recognition, primitive/knowledge recall, expert planning, and executor dispatch, asking for the concrete research goal before entering execution. The user does NOT need to say "使用OneScience" or any magic trigger words.
- If the user explicitly names a specific sub-skill (e.g. "使用 onescience-runtime 执行"), route directly to that sub-skill, skipping orchestrator.
- Use \`onescience-coder\` for code generation or code modification (when dispatched by orchestrator or explicitly requested).
- Use \`onescience-runtime\` only for run / submit / poll / diagnose tasks.
- Use \`onescience-installer\` only for install / repair / verify tasks.
- For paper reproduction, do not search, open, download, clone, or reference official or third-party implementation repositories.`;

  const gateNote = `**Enforced gates (this plugin will block tool calls that violate them):**
- Breakpoint 1: after \`onescience-orchestrator\` is loaded, before \`onescience-primitives\` has been invoked, execution tools (bash / write / edit / apply_patch / task) are blocked. Load primitives first and complete resource recall.
- Do not read or grep \`onescience-primitives/assets/\` directly. Invoke the \`onescience-primitives\` skill first; only its own retrieval may touch the assets.
- Breakpoint 2: after calling primitives, before any run / write / calculation, record the retrieval decision by appending a \`gaps.jsonl\` line under \`.onescience/\` with a \`knowledge_gap\` boolean (primitives step 10).
- If \`knowledge_gap=true\` (no domain-specific local hit), you MUST call \`onescience-online-knowledge\` to retrieve verified, cited evidence before writing scripts, submitting jobs, or answering domain parameters. The literature channel is always lit_search (OpenAlex + Europe PMC + Crossref); the structure/parameter channel is chosen BY DOMAIN, not a fixed COD mandate: materials/crystal->COD, bio/protein/docking->PDB/UniProt/DrugBank, climate/weather->reanalysis datasets (e.g. ERA5), fluid/CFD/plasma->property model libraries; if the domain has no structured reference database, the literature channel alone suffices. Never substitute model memory, default parameters, fabricated data, or hand-rolled curl/wget queries against the authoritative domain endpoints (COD / PDB / OpenAlex / arXiv, ...) for this step — use the skill's scripts, which self-verify results.
- Retrieved values must be consumed with provenance: literature facts carry [n] citations, structures carry a domain-appropriate identifier (COD id for crystals, PDB id for proteins, dataset DOI for climate reanalysis), software parameters carry software-doc sources; model-prior fallbacks must be explicitly marked as “⚠ 未经在线核实” and never disguised as a cited source. Before delivering the final answer, run scripts/check_provenance.py (from the onescience-online-knowledge skill) on it: every concrete identifier (DOI / COD id / arXiv id / PDB id / UniProt id) must either appear verbatim in this round's tool-produced evidence (lit_result.json / structure_result.json / param_result.json / formula-verified CIF) or be marked as model prior on the same line; exit code 2 means fix the draft before delivery, and the agent-authored online_knowledge.json does not count as a source (circular).`;

  const runsiteGateNote = `**Runsite workbench gate (Gate R, enforced by this plugin):**
- When \`~/.ssh/config\` declares 2 or more platform SSH connections, any remote commercial-software compute — handing off to \`onescience-runtime\` or \`onescience-mlmd-campaign-orchestrator\`, or running \`sbatch\`/\`srun\`/\`ssh\`/\`scp\`/\`rsync\` — is blocked until \`onescience-runsite\` has been invoked for this task.
- Call \`onescience-runsite\` first: it read-only probes each SSH connection's software matrix (VASP/LAMMPS/accelerator/Slurm/conda) and pops the workbench selection box via the question tool, marking the connection that truly has the required software and is reachable as （推荐）. This is the ONLY interactive popup; all other remote fields (remote_work_dir / execution_mode / partition / accelerator) are auto-derived.`;

  const artifactGateNote = `**Artifact-home & long-wait guards (Gate H + Gate L, enforced by this plugin):**
- Gate H (artifact-home rewrite): when a bash \`scp\` / \`rsync\` / \`ssh\` / \`sbatch\` command would write an output artifact directly into the remote node's HOME root, the plugin rewrites the target path to \`~/rsi-<sessionKey>/\` and creates that dir first, so home stays tidy. A prefilter means ordinary commands pass through untouched. Name a meaningful task dir yourself (e.g. \`~/dft-slab-42/out.log\`) when you can; the rewrite is only the safety net for lazy bare-home dumps.
- Gate L (long-wait guard): a main-process bash \`sleep\` of 30s or more, a \`timeout\` of 60s or more, or a \`while/for ... sleep\` poll loop is BLOCKED. When blocked, do NOT just report the block or retry in bash - immediately dispatch the wait to a \`task\` subagent (the gate error hands you the exact call to issue) so the main agent stays free to do other work while the subagent waits/polls read-only and returns a summary plus artifact path. Short waits below the thresholds run normally.`;

  const sections = [
    bootstrapMarker,
    'OneSkills is available from the local repository checkout.',
    routingGuide,
    gateNote,
    runsiteGateNote,
    artifactGateNote,
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
      // Deliver the provenance gate on every request while it is outstanding:
      // an online retrieval has already run (flagged in tool.execute.before) and
      // the self-check has not been executed yet. This channel is used because the
      // after-hook does not reliably expose the command that just ran, and because
      // the Gate-B note only fires when knowledge_gap=true (measured adoption 1/2).
      // Non-blocking: it appends one text part, and it gives up after 3 deliveries.
      try {
        const msgs = (output && output.messages) || [];
        let lastUser = null;
        for (let i = msgs.length - 1; i >= 0; i -= 1) {
          const m = msgs[i];
          if (m && m.info && m.info.role === 'user') { lastUser = m; break; }
        }
        if (lastUser) {
          const stP = getSessionState(lastUser.info.sessionID);
          if (stP.litSearchSeen && !stP.provDone && stP.provNotes < 3 && lastUser.parts.length) {
            const refP = lastUser.parts[lastUser.parts.length - 1];
            lastUser.parts.push({ ...refP, type: 'text', text: PROV_GATE_NOTE });
            stP.provNotes += 1;
          }
        }
      } catch (_) {
        /* never break the chat pipeline over a reminder */
      }
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
      // Remember whether this session already went online, and whether the
      // provenance self-check has run; the messages transform reads these flags.
      const cmdProv = String(args.command || '');
      if (/lit_search\.py/.test(cmdProv)) state.litSearchSeen = true;
      if (/check_provenance\.py/.test(cmdProv)) { state.provDone = true; state.litSearchSeen = true; }
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
            state.runsiteCalled = false;
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
        if (isRunsiteSkill(name)) {
          // runsite is the workbench resolver itself — always allowed, and it
          // releases Gate R because a workbench selection is being made now.
          state.runsiteCalled = true;
          await note(client, 'info', 'runsite invoked; workbench gate released for this session');
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
                '必须先调用 skill `onescience-online-knowledge`（文献通道走 lit_search；结构/参数通道按任务领域选权威源，而非一律 COD：材料/晶体→COD、生化/蛋白/分子对接→PDB/UniProt/DrugBank、气候/天气→再分析观测数据集(如 ERA5)、流体/CFD/等离子→物性模型库；若该领域没有对应结构化参考库，仅走文献通道即可）' +
                '真实联网查证并产出带该领域权威出处（文献 DOI / 结构编号 COD 或 PDB / 气候数据集 DOI / software-doc）的证据后，' +
                '再继续写脚本、提交作业或回答领域参数。' +
                '禁止用模型记忆、默认参数或模拟数据替代检索，也禁止自行 curl/wget 查询 COD/PDB/OpenAlex/arXiv 等权威端点——' +
                '必须使用该技能内带化学式回验等自校验机制的脚本。',
            );
          }
          // fileDecision === false → verified local hit, allow execution.
        }
      }

      // --- Gate R (runsite workbench gate): remote commercial-software compute
      // must be preceded by an onescience-runsite workbench selection whenever
      // >=2 platform SSH connections exist. Blocks handing off to a campaign/
      // pipeline executor or submitting a remote job until runsite has resolved
      // the workbench (which pops the SSH selection box). Fail-open when <2.
      if (state.orchestratorLoaded && !state.runsiteCalled && sshConnectionCount(cwd) >= 2) {
        const remoteViaSkill = toolName === 'skill' && isRemoteEntrySkill(name);
        const remoteViaBash = toolName === 'bash' && looksRemoteExec(args.command);
        if (remoteViaSkill || remoteViaBash) {
          await note(client, 'warn', `Gate R blocked ${toolName}: remote compute before runsite workbench selection`);
          throw new Error(
            '[OneSkills] 检测到 ~/.ssh/config 存在 2 个及以上平台 SSH 连接，且当前操作要进入远端计算' +
            '（调用远端执行/流水线类技能，或 sbatch/srun/ssh/scp 等远端作业），但本会话尚未经 ' +
            '`onescience-runsite` 确定执行工作台。必须先调用 skill `onescience-runsite`：它会只读探测各 ' +
            'SSH 连接的软件矩阵（VASP/LAMMPS/加速器/Slurm/conda），并通过 question 工具弹出工作台选择框，' +
            '把真正具备所需商软且可连通的连接标（推荐）供用户确认。在 runsite 工作台弹窗返回用户选择之前，' +
            '不得提交任何远端作业或进入远端执行类技能。',
          );
        }
      }

      // --- Gate H (artifact-home rewrite): when a bash scp / rsync / ssh /
      // sbatch command would drop an artifact directly into the remote node's
      // home root, rewrite output.args.command to redirect it under ~/rsi-<key>/
      // and create that dir first. A prefilter regex short-circuits the vast
      // majority of non-transfer commands. Non-blocking best-effort: only mutate
      // when the rewrite function is confident, otherwise leave the command
      // untouched.
      if (toolName === 'bash') {
        try {
          const original = String(args.command || '');
          const key = sessionKeyOf(input && input.sessionID);
          const rewritten = rewriteArtifactCommand(original, key);
          if (rewritten && rewritten !== original) {
            if (output && output.args) output.args.command = rewritten;
            else if (input && input.args) input.args.command = rewritten;
            await note(client, 'info', `Gate H rewrote home artifact path under ~/${key}/`);
          }
        } catch (_) {
          /* never let a rewrite failure block the command */
        }
      }

      // --- Gate L (long-wait blocking guard): a main-process bash sleep /
      // timeout / poll-loop that would stall the session for a long time is
      // blocked; the model is told to dispatch the wait to a task subagent so
      // the main agent stays responsive. Short waits fall through.
      if (toolName === 'bash') {
        const lw = looksLongBlocking(args.command);
        if (lw.blocking) {
          // A subagent session is exactly where the long wait SHOULD happen —
          // let it run. Only the main (root) agent is forced to hand off.
          const isSub = await isSubagentSession(client, input && input.sessionID);
          if (isSub) {
            await note(client, 'info', `Gate L allowed long wait inside subagent: ${lw.reason}`);
          } else {
            await note(client, 'warn', `Gate L blocked bash: ${lw.reason}`);
            const handoff = buildSubagentHandoff(args.command);
            throw new Error(
              '[OneSkills] 检测到长耗时阻塞命令（' + lw.reason + '），主 agent 进程禁止 sleep/timeout 空等。\n' +
              '不要只是复述本拦截信息，也不要用 bash 重试 sleep/timeout。请立即调用下面这个 task 把等待交给子智能体，' +
              '主 agent 在子智能体等待期间继续处理其他事项，拿到结果后再回报用户：\n' +
              '  ' + handoff,
            );
          }
        }
      }

      // Read-only intents (read/glob/grep/webfetch/todowrite, primitives,
      // online-knowledge, live-literature, planning skills) fall through and
      // are always allowed.
      return;
    },
  };
};

// Exported for unit testing of the pure rewrite / guard helpers; the OpenCode
// plugin loader only consumes OneSkillsPlugin above and ignores these.
export { rewriteArtifactCommand, looksLongBlocking, isBareHomePath, sessionKeyOf };
