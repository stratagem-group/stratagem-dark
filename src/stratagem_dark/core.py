# SPDX-License-Identifier: MIT
"""Validated profile resolution and deterministic, unprivileged staging."""
import hashlib
import json
import os
from pathlib import Path
import re
import shutil

IDENTIFIER = re.compile(r"[a-z0-9][a-z0-9+._-]*\Z")
PROFILES = {"core", "operator", "defender", "research", "full"}
TOOL_KEYS = {"id", "repository", "package", "category", "isolation", "upstream",
             "license_expression", "license_review", "description"}
DEFAULTS = {
    "desktop/hyprland/stratagem-dark.conf": "usr/share/stratagem-dark/defaults/hyprland/stratagem-dark.conf",
    "config/foot/foot.ini": "usr/share/stratagem-dark/defaults/foot/foot.ini",
    "branding/tokens.json": "usr/share/stratagem-dark/branding/tokens.json",
    "branding/wordmark.svg": "usr/share/stratagem-dark/branding/wordmark.svg",
    "LICENSE": "usr/share/licenses/stratagem-dark/LICENSE",
    "THIRD_PARTY_NOTICES.md": "usr/share/licenses/stratagem-dark/THIRD_PARTY_NOTICES.md",
}


class ValidationError(ValueError):
    """Invalid project input or unsupported operation."""


def canonical(value):
    return json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False) + "\n"


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValidationError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def read_json(path):
    return json.loads(path.read_text(), object_pairs_hook=_pairs)


def require(condition, message):
    if not condition:
        raise ValidationError(message)


def identifier(value):
    return isinstance(value, str) and IDENTIFIER.fullmatch(value) is not None


def id_list(value):
    return (isinstance(value, list) and all(identifier(v) for v in value)
            and len(value) == len(set(value)))


def fields(value, keys, label):
    require(isinstance(value, dict) and set(value) == keys, f"invalid fields: {label}")


class Project:
    def __init__(self, root):
        self.root = Path(root).resolve()
        catalog = read_json(self.root / "catalog/tools.json")
        fields(catalog, {"schema_version", "tools"}, "catalog")
        require(type(catalog["schema_version"]) is int and catalog["schema_version"] == 1,
                "unsupported catalog version")
        require(isinstance(catalog["tools"], list) and catalog["tools"], "empty catalog")
        self.tools = {}
        targets = set()
        for tool in catalog["tools"]:
            fields(tool, TOOL_KEYS, "tool")
            require(all(isinstance(v, str) and v.strip() for v in tool.values()),
                    "tool values must be nonempty strings")
            require(identifier(tool["id"]) and identifier(tool["package"]), "invalid tool identifier")
            for key, choices in {
                "repository": {"arch", "blackarch"},
                "category": {"runtime", "development", "desktop", "analysis", "network"},
                "isolation": {"host", "authorized-network", "isolated-vm"},
                "license_review": {"pending", "approved", "rejected"},
            }.items():
                require(tool[key] in choices, f"invalid {key}: {tool['id']}")
            require(re.fullmatch(r"https://\S+", tool["upstream"]) is not None, "HTTPS upstream required")
            require(tool["license_review"] != "approved" or tool["license_expression"] != "NOASSERTION",
                    "approved license needs an expression")
            require(tool["id"] not in self.tools, "duplicate tool ID")
            target = (tool["repository"], tool["package"])
            require(target not in targets, "duplicate package target")
            targets.add(target)
            self.tools[tool["id"]] = tool
        self.profiles = {}
        for path in sorted((self.root / "profiles").glob("*.json")):
            profile = read_json(path)
            fields(profile, {"schema_version", "id", "extends", "tools"}, "profile")
            require(type(profile["schema_version"]) is int and profile["schema_version"] == 1,
                    "unsupported profile version")
            require(identifier(profile["id"]) and profile["id"] == path.stem, "profile filename mismatch")
            require(id_list(profile["extends"]) and id_list(profile["tools"]), "invalid profile lists")
            self.profiles[profile["id"]] = profile
        require(set(self.profiles) == PROFILES, "expected exactly the five documented profiles")
        for name in sorted(self.profiles):
            self.resolve(name)
        require(not any(t["repository"] == "blackarch" for t in self.resolve("core")),
                "core must be independent of BlackArch")
        expected = {t["id"] for name in ("operator", "defender", "research") for t in self.resolve(name)}
        require({t["id"] for t in self.resolve("full")} == expected, "full must be curated union")

    def resolve(self, name):
        selected, visiting, done = set(), set(), set()

        def visit(current):
            require(current in self.profiles, f"unknown profile: {current}")
            require(current not in visiting, f"profile inheritance cycle: {current}")
            if current in done:
                return
            visiting.add(current)
            p = self.profiles[current]
            for parent in p["extends"]:
                visit(parent)
            for tool in p["tools"]:
                require(tool in self.tools, f"unknown tool: {tool}")
                selected.add(tool)
            visiting.remove(current)
            done.add(current)
        visit(name)
        result = [self.tools[t] for t in sorted(selected)]
        packages = [t["package"] for t in result]
        require(len(packages) == len(set(packages)), "conflicting repositories for package name")
        return result

    def plan(self, name):
        tools = self.resolve(name)
        # Hash implementations as well as metadata/defaults; exclude host paths/timestamps.
        paths = {self.root / p for p in DEFAULTS} | {self.root / "VERSION"}
        for directory in ("src", "bin", "bootstrap", "profiles", "catalog", "schemas"):
            paths.update(p for p in (self.root / directory).rglob("*")
                         if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc")
        inputs = {}
        for path in sorted(paths):
            require(not path.is_symlink(), f"symlink input forbidden: {path.name}")
            require(path.resolve().is_relative_to(self.root), "input escapes project")
            inputs[path.relative_to(self.root).as_posix()] = sha256(path.read_bytes())
        plan = {
            "schema_version": 1, "product": "STRATAGEM DARK",
            "version": (self.root / "VERSION").read_text().strip(),
            "profile": name, "architecture": "x86_64", "mode": "plan-only",
            "packages_locked": False, "live_apply_supported": False,
            "repositories": sorted({t["repository"] for t in tools}),
            "tools": tools, "inputs": inputs,
            "defaults": DEFAULTS,
            "blockers": ["Signed release lock and package adapter are not implemented.",
                         "Clean Arch VM acceptance has not passed."] +
                        [f"License review incomplete: {t['id']}" for t in tools
                         if t["license_review"] != "approved"],
        }
        plan["plan_sha256"] = sha256(canonical(plan).encode())
        return plan

    def stage(self, name, destination):
        require(os.geteuid() != 0, "staging must run as an unprivileged user")
        dest = Path(os.path.abspath(destination))
        require(not dest.exists() and not dest.is_symlink(), "stage destination must not exist")
        require(dest.parent.is_dir(), "stage parent must already exist")
        require(all(not p.is_symlink() for p in (dest.parent, *dest.parent.parents)),
                "symlink stage parents are forbidden")
        require(dest.parent.stat().st_uid == os.geteuid(), "stage parent must belong to current user")
        plan = self.plan(name)
        # Exclusive creation prevents overwriting an existing destination.
        dest.mkdir(mode=0o700)
        try:
            for source, target in DEFAULTS.items():
                data = (self.root / source).read_bytes()
                require(sha256(data) == plan["inputs"][source], "input changed during staging")
                path = dest / target
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(data)
                path.chmod(0o644)
            (dest / "plan.json").write_text(canonical(plan))
            (dest / "plan.json").chmod(0o644)
            files = {p.relative_to(dest).as_posix(): {"sha256": sha256(p.read_bytes()), "mode": "0644"}
                     for p in sorted(dest.rglob("*")) if p.is_file()}
            (dest / "manifest.json").write_text(canonical({"schema_version": 1, "files": files}))
            (dest / "manifest.json").chmod(0o644)
        except BaseException:
            shutil.rmtree(dest)
            raise
        return plan
