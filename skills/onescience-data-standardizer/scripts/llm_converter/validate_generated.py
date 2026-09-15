"""AST-based static validator for Tier2 LLM-synthesized converter scripts.

Enforces the hard constraints declared in prompts/system.md:
  - valid Python syntax
  - no hardcoded absolute path literals
  - no os.environ.get for path resolution
  - argparse present
  - writes dataset_card.json (directly or via helper)
  - defines a main() entrypoint or __main__ guard
  - declares `# requirements:` header
  - no network calls (requests / urllib.request / httpx / socket.socket)
  - no writes into --source-dir (best-effort heuristic)

Returns a structured report; raises nothing. Callers decide whether to
retry synthesis or abort.
"""

from __future__ import annotations

import ast
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

ABS_PATH_LITERAL_RE = re.compile(
    r"""^["'](/(?:home|data|public|mnt|media|opt|srv|usr|var|tmp|Users|Volumes)/|"""
    r"""[A-Za-z]:[\\/])"""
)
NETWORK_MODULES = {"requests", "httpx", "urllib.request", "aiohttp", "socket"}
NETWORK_CALL_NAMES = {"urlopen", "Request", "Session", "get", "post", "put",
                      "delete", "patch", "head", "connect", "create_connection"}


@dataclass
class ValidationIssue:
    severity: str          # "error" | "warning"
    code: str
    message: str
    lineno: Optional[int] = None
    col_offset: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "severity": self.severity,
            "code": self.code,
            "message": self.message,
            "lineno": self.lineno,
            "col_offset": self.col_offset,
        }


@dataclass
class ValidationReport:
    ok: bool
    issues: List[ValidationIssue] = field(default_factory=list)
    stats: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ok": self.ok,
            "issues": [i.to_dict() for i in self.issues],
            "stats": self.stats,
        }

    def errors(self) -> List[ValidationIssue]:
        return [i for i in self.issues if i.severity == "error"]

    def warnings(self) -> List[ValidationIssue]:
        return [i for i in self.issues if i.severity == "warning"]


# ----------------------------------------------------------------------
# Individual checks
# ----------------------------------------------------------------------

def _check_syntax(source: str) -> Optional[ast.AST]:
    try:
        return ast.parse(source)
    except SyntaxError:
        return None


def _check_requirements_header(source: str,
                               issues: List[ValidationIssue]) -> None:
    head = "\n".join(source.splitlines()[:10])
    if "# requirements:" not in head:
        issues.append(ValidationIssue(
            "error", "missing_requirements_header",
            "script must declare '# requirements: <pkg>=<ver>, ...' within "
            "the first 10 lines", lineno=1))


def _check_shebang(source: str, issues: List[ValidationIssue]) -> None:
    first = source.splitlines()[0] if source else ""
    if not first.startswith("#!"):
        issues.append(ValidationIssue(
            "warning", "missing_shebang",
            "first line should be '#!/usr/bin/env python3'", lineno=1))


def _walk_strings(tree: ast.AST,
                  issues: List[ValidationIssue]) -> None:
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            if ABS_PATH_LITERAL_RE.match(node.value):
                issues.append(ValidationIssue(
                    "error", "hardcoded_absolute_path",
                    f"string literal looks like an absolute path: "
                    f"{node.value[:80]!r}",
                    lineno=node.lineno, col_offset=node.col_offset))


def _check_environ_paths(tree: ast.AST,
                         issues: List[ValidationIssue]) -> None:
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        # os.environ.get("...") / os.getenv("...")
        name = ""
        if isinstance(func, ast.Attribute):
            name = func.attr
        if name not in ("get", "getenv"):
            continue
        # Look at the first arg for path-looking env var names.
        if not node.args:
            continue
        arg0 = node.args[0]
        if not (isinstance(arg0, ast.Constant) and isinstance(arg0.value, str)):
            continue
        env_name = arg0.value.upper()
        pathish = any(tok in env_name for tok in
                      ("PATH", "DIR", "HOME", "ROOT", "LOCATION"))
        # ONESCIENCE_DATASETS_DIR is explicitly forbidden for path resolution.
        if pathish:
            issues.append(ValidationIssue(
                "error", "environ_path_resolution",
                f"os.environ.get({arg0.value!r}) looks like path resolution; "
                f"paths must come from argparse",
                lineno=node.lineno, col_offset=node.col_offset))


def _check_argparse(tree: ast.AST, source: str,
                    issues: List[ValidationIssue]) -> None:
    imports_argparse = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "argparse":
                    imports_argparse = True
        elif isinstance(node, ast.ImportFrom):
            if node.module == "argparse":
                imports_argparse = True
    has_argument_parser = "ArgumentParser" in source
    if not (imports_argparse and has_argument_parser):
        issues.append(ValidationIssue(
            "error", "missing_argparse",
            "script must import argparse and instantiate ArgumentParser"))
        return
    for required in ("--source-dir", "--target-dir"):
        if required not in source:
            issues.append(ValidationIssue(
                "error", "missing_required_arg",
                f"argparse must define {required}"))


def _check_dataset_card_write(tree: ast.AST, source: str,
                              issues: List[ValidationIssue]) -> None:
    if "dataset_card.json" in source:
        return
    if "write_dataset_card" in source:
        return
    issues.append(ValidationIssue(
        "error", "missing_dataset_card",
        "script must write <target_dir>/dataset_card.json (either literally "
        "or by calling write_dataset_card)"))


def _check_readme_write(source: str, issues: List[ValidationIssue]) -> None:
    if "README.md" not in source:
        issues.append(ValidationIssue(
            "error", "missing_readme",
            "script must write <target_dir>/README.md"))


def _check_main_entry(tree: ast.AST, source: str,
                      issues: List[ValidationIssue]) -> None:
    has_main_def = any(
        isinstance(n, ast.FunctionDef) and n.name == "main"
        for n in tree.body
    )
    has_guard = '__name__' in source and '__main__' in source
    if not (has_main_def or has_guard):
        issues.append(ValidationIssue(
            "error", "missing_main_entry",
            "script must define def main() or an if __name__ == '__main__' guard"))


def _check_network(tree: ast.AST,
                   issues: List[ValidationIssue]) -> None:
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".")[0]
                if alias.name in NETWORK_MODULES or root in NETWORK_MODULES:
                    issues.append(ValidationIssue(
                        "error", "network_import",
                        f"network module import forbidden: {alias.name}",
                        lineno=node.lineno))
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            root = mod.split(".")[0]
            if mod in NETWORK_MODULES or root in NETWORK_MODULES:
                issues.append(ValidationIssue(
                    "error", "network_import",
                    f"network module import forbidden: {mod}",
                    lineno=node.lineno))


def _check_source_dir_writes(tree: ast.AST,
                             issues: List[ValidationIssue]) -> None:
    """Best-effort: flag writes to variables named source_dir/src/root_raw.

    We cannot statically prove where a Path points, so we look for suspicious
    patterns like `source_dir.mkdir`, `open(source_dir / ..., 'w')`,
    `(source_dir / x).write_text`, `shutil.rmtree(source_dir)`, etc.
    """
    suspicious_attrs = {"source_dir", "src_dir", "raw_dir", "source", "src"}
    write_verbs = {"write_text", "write_bytes", "mkdir", "unlink", "rmdir",
                   "rmtree", "rename", "replace"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Attribute) and func.attr in write_verbs:
                base = func.value
                base_name = None
                if isinstance(base, ast.Name):
                    base_name = base.id
                elif isinstance(base, ast.BinOp):
                    # source_dir / "sub"
                    left = base.left
                    if isinstance(left, ast.Name):
                        base_name = left.id
                elif isinstance(base, ast.Attribute):
                    base_name = base.attr
                if base_name and base_name.lower() in suspicious_attrs:
                    issues.append(ValidationIssue(
                        "error", "source_dir_write",
                        f"write operation on source-like variable "
                        f"{base_name!r}: {func.attr}(); --source-dir must be read-only",
                        lineno=node.lineno, col_offset=node.col_offset))
        # open(source_dir / ..., "w") / "wb" / "a"
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) \
                and node.func.id == "open":
            if len(node.args) >= 2:
                mode_arg = node.args[1]
                mode = None
                if isinstance(mode_arg, ast.Constant) and isinstance(mode_arg.value, str):
                    mode = mode_arg.value
                if mode and any(c in mode for c in "wxa"):
                    target = node.args[0]
                    name = None
                    if isinstance(target, ast.Name):
                        name = target.id
                    elif isinstance(target, ast.BinOp) and isinstance(target.left, ast.Name):
                        name = target.left.id
                    if name and name.lower() in suspicious_attrs:
                        issues.append(ValidationIssue(
                            "error", "source_dir_write",
                            f"open() in write mode on source-like variable {name!r}",
                            lineno=node.lineno))


def _check_determinism(source: str, tree: ast.AST,
                       issues: List[ValidationIssue]) -> None:
    if "random." in source or "np.random." in source:
        if "default_rng" not in source and "seed" not in source.lower():
            issues.append(ValidationIssue(
                "warning", "nondeterministic_randomness",
                "randomness detected without an explicit seed; use "
                "numpy.random.default_rng(seed) for reproducibility"))


def _check_self_copy(tree: ast.AST,
                     issues: List[ValidationIssue]) -> None:
    """Flag shutil.copy*/move/rename whose source is this script (__file__).

    The orchestrator already persists the generated converter to
    ``<target_dir>/_converter/``. A generated script that copies itself
    into the target tree raises ``shutil.SameFileError`` at runtime when
    source and destination resolve to the same path.
    """
    copy_verbs = {"copy", "copy2", "copyfile", "move", "rename", "replace"}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        verb = None
        if isinstance(func, ast.Attribute) and func.attr in copy_verbs:
            verb = func.attr
        elif isinstance(func, ast.Name) and func.id in copy_verbs:
            verb = func.id
        if not verb or not node.args:
            continue
        src = node.args[0]
        # Unwrap Path(__file__).resolve() / str(Path(__file__)) etc.
        uses_file = False
        for sub in ast.walk(src):
            if isinstance(sub, ast.Name) and sub.id == "__file__":
                uses_file = True
                break
        if uses_file:
            issues.append(ValidationIssue(
                "error", "self_copy",
                f"{verb}() with __file__ as source: do not copy/move your "
                f"own script; the orchestrator already persists it to "
                f"_converter/ (causes shutil.SameFileError at runtime)",
                lineno=node.lineno, col_offset=node.col_offset))


# ----------------------------------------------------------------------
# Public API
# ----------------------------------------------------------------------

def validate(source: str) -> ValidationReport:
    issues: List[ValidationIssue] = []
    _check_shebang(source, issues)
    _check_requirements_header(source, issues)

    tree = _check_syntax(source)
    if tree is None:
        issues.append(ValidationIssue(
            "error", "syntax_error", "script failed ast.parse"))
        return ValidationReport(ok=False, issues=issues,
                                stats={"lines": source.count("\n") + 1})

    _walk_strings(tree, issues)
    _check_environ_paths(tree, issues)
    _check_argparse(tree, source, issues)
    _check_dataset_card_write(tree, source, issues)
    _check_readme_write(source, issues)
    _check_main_entry(tree, source, issues)
    _check_network(tree, issues)
    _check_source_dir_writes(tree, issues)
    _check_self_copy(tree, issues)
    _check_determinism(source, tree, issues)

    stats = {
        "lines": source.count("\n") + 1,
        "chars": len(source),
        "ast_nodes": sum(1 for _ in ast.walk(tree)),
        "imports": sorted({
            (n.module or "") if isinstance(n, ast.ImportFrom)
            else ",".join(a.name for a in n.names)
            for n in ast.walk(tree)
            if isinstance(n, (ast.Import, ast.ImportFrom))
        }),
    }
    ok = not any(i.severity == "error" for i in issues)
    return ValidationReport(ok=ok, issues=issues, stats=stats)


def validate_file(path: Path) -> ValidationReport:
    source = Path(path).read_text(encoding="utf-8")
    return validate(source)


# ----------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------

def _cli() -> int:
    import argparse
    parser = argparse.ArgumentParser(
        description="Statically validate a Tier2 LLM-synthesized converter")
    parser.add_argument("script", help="Path to the generated .py file")
    parser.add_argument("--strict", action="store_true",
                        help="Treat warnings as errors")
    args = parser.parse_args()

    report = validate_file(Path(args.script))
    if args.strict and report.warnings():
        report.ok = False
    print(json.dumps(report.to_dict(), indent=2, ensure_ascii=False))
    return 0 if report.ok else 1


if __name__ == "__main__":
    sys.exit(_cli())
