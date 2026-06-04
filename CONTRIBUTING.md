# Contributing

Thanks for contributing to `OneSkills`.

## Scope

Public contributions should focus on:

- `skills/`
- `references/`
- `integrations/`
- `install/`
- `docs/`

Do not add private maintenance material to the public product surface.

## Before You Change Anything

Read the relevant public docs first:

- [README.md](README.md)
- [install/README.md](install/README.md)
- [docs/open-source/README.md](docs/open-source/README.md)

Keep changes minimal:

- extend an existing skill before adding a new one
- extend assets or references before duplicating execution logic
- keep agent-specific behavior in `integrations/`, not in core `skills/`

## Required Checks

Run the checks that are available in the public repository before opening a PR:

```bash
python3 install/install_oneskills.py --help
```

If you changed the installer, also run:

```bash
python3 install/install_oneskills.py --agent generic --project /tmp/oneskills-smoke --skills-dir /tmp/oneskills-smoke/skills
```

## Documentation Expectations

Update docs when behavior changes.

Typical places:

- product overview: `README.md`
- install behavior: `install/README.md`
- public extension guidance: `docs/`
- integration usage: `integrations/`

## Pull Request Notes

A useful PR description should state:

- what changed
- which user-facing behavior changed
- which directories were affected
- which public checks were run
- whether there are compatibility caveats
