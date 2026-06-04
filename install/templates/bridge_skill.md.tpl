---
name: {skill_name}
description: Bridge skill for the project-local OneSkills installation. Resolve this skill against the current project instead of the user-level skill directory.
---

{bridge_marker}
# {skill_name}

Use the project-local OneSkills installation for the current project.

Authoritative skill file:
- `{project_skill_file}` relative to the current project root

OneScience source root:
- `{project_onescience_source}` relative to the current project root

Reference resolution rules:
- `./references/...` -> `{project_skill_refs}...`
- `../../references/...` -> `{project_shared_refs}...`
- `./onescience/...` -> `{project_onescience_source}...`
- Do not resolve these paths against the current working directory textually; resolve them against the project-local skill location above.

If the authoritative skill file or OneScience source root does not exist, tell the user to run the OneSkills installer in the current project first.
