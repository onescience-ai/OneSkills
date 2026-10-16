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
- For ANY scientific computing, simulation, modeling, or data-analysis task —包括但不限于: DFT, VASP, Quantum ESPRESSO, CP2K, MD, AIMD, LAMMPS, GROMACS, MACE, DeePMD, NEB, CFD, OpenFOAM, quantum chemistry, Gaussian, ORCA, Psi4, NWChem, xTB, CCSD(T), TDDFT, Monte Carlo, GCMC, FEM, COMSOL, ANSYS, ABAQUS, multiphysics, FDTD, photonics, bioinformatics, genomics, protein, RNA-seq, single-cell, molecular docking, AutoDock, Vina, virtual screening, drug design, QSAR, materials, crystal, surface, interface, adsorption, catalysis, battery, alloy, semiconductor, electrochemistry, Butler-Volmer, EIS, PyBaMM, corrosion, spectroscopy, IR, Raman, UV-Vis, XPS, NMR, EPR, XAS, climate, weather, WRF, geophysics, astrophysics, plasma, polymer, coarse-grained, MARTINI, soft matter, model training, fine-tuning, inference, paper reproduction, dataset construction, data analysis, visualization, HPC/SLURM job submission, slab building, adsorbate placement, solvation, doping, defect, POSCAR/INCAR/KPOINTS, selective dynamics, SciPy, NumPy, Julia, FEniCS, ODE/PDE solvers, numerical methods, Bayesian optimization, **or ANY other scientific/engineering/research computing task** — ALWAYS start with \`onescience-orchestrator\`. It performs intent recognition, primitive/knowledge recall, expert planning, and executor dispatch. The user does NOT need to say "使用OneScience" or any magic trigger words.
- If the user explicitly names a specific sub-skill (e.g. "使用 onescience-runtime 执行"), route directly to that sub-skill, skipping orchestrator.
- Use \`onescience-coder\` for code generation or code modification (when dispatched by orchestrator or explicitly requested).
- Use \`onescience-runtime\` only for run / submit / poll / diagnose tasks.
- Use \`onescience-installer\` only for install / repair / verify tasks.
- For paper reproduction, do not search, open, download, clone, or reference official or third-party implementation repositories.
- Only EXCLUDE (when clearly unrelated to science/engineering/data-analysis/simulation): pure web/app frontend, pure CRUD business code, pure IT ops (deployment/network/account), syntax/API-usage daily Q&A. Any task involving experimental data fitting, scientific model selection, parameter identification, error analysis, result interpretation, or scientific code writing MUST go through \`onescience-orchestrator\` — even if it looks like just 'writing code' or 'running a script'.`;

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
