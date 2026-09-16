#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OneSkills Task-Centric knowledge lint (optional, offline, stdlib only).

Scope
-----
Strict checks run only on "TC cards": cards whose metadata.type is one of
task / workflow / scenario, or whose tags use the TC namespaces
(edge:, slot:, atom:, runnable:).  Legacy instance cards (type=workflow-planning
without TC tags) are only checked for the 9-field contract, and only with --all.

Checks
------
1. metadata.json parses; field set is EXACTLY the 9 contract fields.
2. type is in the allowed vocabulary; domain matches the directory name;
   TC cards live in the category matching their type (scenario/ workflow/ tasks/).
3. Card body exists: knowledge.md (flexible form) OR spec.md+usage.md (4-file form).
4. edge:resource:<category>/<name> resolves to assets/<domain>/<category>/<name>/.
5. edge:task:<name> resolves to assets/<domain>/tasks/<name>/.
6. edge:workflow:<name> resolves to assets/<domain>/workflow/<name>/ (type=workflow).
7. edge:next:<t> / edge:prev:<t> resolve to assets/<domain>/tasks/<t>/.
8. atom:<id> exists in references/tc/atoms.jsonl.
9. slot:<key>:<value> has exactly 3 colon-separated segments.
10. runnable:script implies a non-empty script/ directory inside the card.
11. Vocabulary edges (edge:method/operation/validation/fallback_method) are
    reported as INFO only - they are allowed to have no card.

Usage
-----
    python validate_knowledge.py            # TC cards only
    python validate_knowledge.py --all      # also lint legacy 9-field contract
    python validate_knowledge.py --json     # machine readable report

Exit code: 0 = no errors, 1 = errors found.
"""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "skills" / "onescience-primitives" / "assets"
ATOMS = ROOT / "skills" / "onescience-primitives" / "references" / "tc" / "atoms.jsonl"

CONTRACT_FIELDS = {
    "name", "type", "domain", "version", "visibility",
    "created_at", "updated_at", "description", "tags",
}
ALLOWED_TYPES = {
    "task", "workflow", "scenario", "model", "tool", "dataset",
    "benchmark", "metric", "method", "workflow-planning",
}
TC_TYPES = {"task", "workflow", "scenario"}
TC_TYPE_CATEGORY = {"scenario": "scenario", "workflow": "workflow", "task": "tasks"}
RESOLVE_EDGE_NS = {"resource", "task", "workflow", "next", "prev",
                   "scenario", "instance", "skeleton"}
VOCAB_EDGE_NS = {"method", "operation", "validation", "fallback_method"}

errors = []
warnings = []
infos = []


def err(card, msg):
    errors.append({"card": card, "message": msg})


def warn(card, msg):
    warnings.append({"card": card, "message": msg})


def info(card, msg):
    infos.append({"card": card, "message": msg})


def load_atoms():
    ids = set()
    if not ATOMS.exists():
        return ids
    for line in ATOMS.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            ids.add(json.loads(line)["atom_id"])
        except Exception:
            pass
    return ids


def scan_cards():
    """Return list of (rel, domain, category, name, metadata dict|None)."""
    out = []
    if not ASSETS.exists():
        return out
    for meta in sorted(ASSETS.glob("*/*/*/metadata.json")):
        parts = meta.relative_to(ASSETS).parts
        domain, category, name = parts[0], parts[1], parts[2]
        rel = "assets/" + "/".join(parts[:3])
        try:
            data = json.loads(meta.read_text(encoding="utf-8"))
        except Exception as exc:
            err(rel, "metadata.json is not valid JSON: %s" % exc)
            data = None
        out.append((rel, domain, category, name, data, meta.parent))
    return out


def is_tc(data):
    if not data:
        return False
    if data.get("type") in TC_TYPES:
        return True
    for t in data.get("tags") or []:
        if isinstance(t, str) and t.split(":", 1)[0] in ("edge", "slot", "atom", "runnable"):
            return True
    return False


def check_contract(rel, data, strict):
    fields = set(data.keys())
    missing = CONTRACT_FIELDS - fields
    extra = fields - CONTRACT_FIELDS
    if missing:
        err(rel, "missing contract fields: %s" % ", ".join(sorted(missing)))
    if extra:
        # extra fields are invisible to catalog_search; hard error only for TC cards,
        # legacy cards carry historical batch fields (scenario_id, provider_kind, ...)
        msg = "extra fields outside the 9-field contract: %s" % ", ".join(sorted(extra))
        (err if strict else warn)(rel, msg)
    t = data.get("type")
    if t not in ALLOWED_TYPES:
        msg = "type %r not in allowed vocabulary" % (t,)
        (err if strict else warn)(rel, msg)
    if not isinstance(data.get("tags"), list):
        err(rel, "tags must be a list")
    if not (data.get("description") or "").strip():
        (err if strict else warn)(rel, "description is empty")
    if data.get("domain") != rel.split("/")[1]:
        msg = "domain %r does not match directory %r" % (data.get("domain"), rel.split("/")[1])
        (err if strict else warn)(rel, msg)
    tcat = TC_TYPE_CATEGORY.get(t)
    if strict and tcat and rel.split("/")[2] != tcat:
        err(rel, "type %r must live in category %r, found %r"
            % (t, tcat, rel.split("/")[2]))


def check_body(rel, card_dir, strict):
    has_knowledge = (card_dir / "knowledge.md").exists()
    has_spec = (card_dir / "spec.md").exists() and (card_dir / "usage.md").exists()
    has_wfp = (card_dir / "workflow_planning.md").exists()
    if not (has_knowledge or has_spec or has_wfp):
        if strict:
            err(rel, "no card body: need knowledge.md OR spec.md+usage.md OR workflow_planning.md")
        else:
            warn(rel, "no card body found")


def check_edges(rel, domain, tags, by_type, card_dirs):
    for tag in tags:
        if not isinstance(tag, str):
            err(rel, "non-string tag: %r" % (tag,))
            continue
        seg = tag.split(":")
        head = seg[0]

        if head == "src":
            # provenance tag, never a graph edge
            if len(seg) < 3 or not seg[1] or not seg[2]:
                err(rel, "malformed src tag (need src:<key>:<value>): %s" % tag)
            continue

        if head == "slot":
            if len(seg) != 3 or not seg[1] or not seg[2]:
                err(rel, "malformed slot tag (need slot:<key>:<value>): %s" % tag)
            continue

        if head == "atom":
            if len(seg) != 2:
                err(rel, "malformed atom tag: %s" % tag)
            elif seg[1] not in ATOM_IDS:
                err(rel, "dangling atom reference (not in references/tc/atoms.jsonl): %s" % tag)
            continue

        if head == "runnable":
            if len(seg) == 1:
                # bare "runnable" is a plain searchable keyword, not a namespaced tag
                continue
            if len(seg) != 2:
                err(rel, "malformed runnable tag: %s" % tag)
            elif seg[1] == "script":
                sdir = card_dirs[rel] / "script"
                scripts = list(sdir.glob("*.py")) if sdir.exists() else []
                if not scripts:
                    err(rel, "runnable:script but no script/*.py under the card")
            continue

        if head != "edge" or len(seg) < 3:
            continue

        ns, target = seg[1], ":".join(seg[2:])
        if ns in VOCAB_EDGE_NS or ns == "src":
            info(rel, "vocabulary edge (no card required): %s" % tag)
            continue
        if ns == "step":
            parts2 = target.split(":")
            if len(parts2) != 2 or not parts2[0] or not parts2[1]:
                err(rel, "edge:step must be <step_id>:<task>: %s" % tag)
            elif (domain, "tasks", parts2[1]) not in card_dirs_set:
                err(rel, "dangling edge:step -> %s (no assets/%s/tasks/%s)"
                    % (tag, domain, parts2[1]))
            continue
        if ns not in RESOLVE_EDGE_NS:
            warn(rel, "unknown edge namespace %r in tag %s" % (ns, tag))
            continue
        if not target:
            err(rel, "empty edge target: %s" % tag)
            continue

        if ns == "resource":
            if "/" not in target:
                err(rel, "edge:resource must be <category>/<name>: %s" % tag)
                continue
            cat, nm = target.split("/", 1)
            key = (domain, cat, nm)
            if key not in card_dirs_set:
                err(rel, "dangling edge:resource -> %s (no assets/%s/%s/%s)" % (tag, domain, cat, nm))
        elif ns in ("task", "next", "prev", "instance", "skeleton"):
            key = (domain, "tasks", target)
            if key not in card_dirs_set:
                err(rel, "dangling edge:%s -> %s (no assets/%s/tasks/%s)" % (ns, tag, domain, target))
        elif ns == "workflow":
            key = (domain, "workflow", target)
            if key not in card_dirs_set:
                err(rel, "dangling edge:workflow -> %s (no assets/%s/workflow/%s)"
                    % (tag, domain, target))
            elif by_type.get(key) != "workflow":
                err(rel, "edge:workflow -> %s resolves to type=%r, expected 'workflow'"
                    % (tag, by_type.get(key)))
        elif ns == "scenario":
            key = (domain, "scenario", target)
            if key not in card_dirs_set:
                err(rel, "dangling edge:scenario -> %s (no assets/%s/scenario/%s)"
                    % (tag, domain, target))
            elif by_type.get(key) != "scenario":
                err(rel, "edge:scenario -> %s resolves to type=%r, expected 'scenario'"
                    % (tag, by_type.get(key)))


ATOM_IDS = load_atoms()
card_dirs_set = set()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true", help="also lint legacy cards strictly")
    ap.add_argument("--json", action="store_true", help="machine readable output")
    ap.add_argument("--quiet", action="store_true", help="only print the summary")
    args = ap.parse_args()

    cards = scan_cards()
    by_type = {}
    dirs = {}
    for rel, domain, category, name, data, cdir in cards:
        card_dirs_set.add((domain, category, name))
        dirs[rel] = cdir
        if data:
            by_type[(domain, category, name)] = data.get("type")

    tc_count = 0
    for rel, domain, category, name, data, cdir in cards:
        if data is None:
            continue
        tc = is_tc(data)
        if tc:
            tc_count += 1
        if not tc and not args.all:
            continue
        check_contract(rel, data, strict=tc)
        check_body(rel, cdir, strict=tc)
        if tc:
            check_edges(rel, domain, data.get("tags") or [], by_type, dirs)

    report = {
        "cards_scanned": len(cards),
        "tc_cards": tc_count,
        "errors": len(errors),
        "warnings": len(warnings),
        "infos": len(infos),
    }

    if args.json:
        print(json.dumps({"summary": report, "errors": errors,
                          "warnings": warnings}, ensure_ascii=False, indent=2))
    else:
        if not args.quiet:
            for e in errors:
                print("[ERROR] %s :: %s" % (e["card"], e["message"]))
            for w in warnings:
                print("[WARN ] %s :: %s" % (w["card"], w["message"]))
        print("--- summary ---")
        for k, v in report.items():
            print("%s: %s" % (k, v))
        print("atoms_loaded: %d" % len(ATOM_IDS))
        print("RESULT: %s" % ("PASS" if not errors else "FAIL"))

    return 0 if not errors else 1


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    sys.exit(main())
