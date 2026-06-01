#!/bin/bash
# MedAI Academic Writing — Quick Install
# Symlinks agents into OpenCode, installs dependencies

set -euo pipefail

MEDAI_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OPENCODE_AGENTS="$HOME/.config/opencode/agents"
OPENCODE_SKILLS="$HOME/.config/opencode/skills"
ARS_REPO="https://github.com/Imbad0202/academic-research-skills.git"
ARS_DIR="$OPENCODE_SKILLS/academic-research-skills"

normalize_agent_config_paths() {
    local config_template="$MEDAI_DIR/config/agent-config.json"
    local config_file="$HOME/.config/opencode/agent-config.json"
    local config_tmp=""

    if [ ! -f "$config_template" ]; then
        echo "  • Skipping config path normalization (missing config/agent-config.json)"
        return 1
    fi

    if ! command -v python3 >/dev/null 2>&1; then
        echo "  • Skipping config path normalization (python3 not found)"
        return 1
    fi

    mkdir -p "$(dirname "$config_file")"
    if [ -f "$config_file" ]; then
        cp "$config_file" "${config_file}.bak.$(date +%Y%m%d%H%M%S)"
    fi
    config_tmp="$(mktemp "${config_file}.XXXXXX")"
    cp "$config_template" "$config_tmp"

    if ! python3 - "$config_tmp" "$MEDAI_DIR" <<'PY'
import json
import pathlib
import sys

config_path = pathlib.Path(sys.argv[1])
project_root = pathlib.Path(sys.argv[2]).resolve().as_posix()
home_dir = pathlib.Path.home().resolve().as_posix()
papers_glob = f"{project_root}/out/papers/*"
root_glob = f"{project_root}/*"
humanizer_glob = f"{home_dir}/.config/opencode/skills/humanizer/*"
skills_glob = f"{home_dir}/.config/opencode/skills/*"
legacy_project_roots = {
    "~/medai",
    "/root/medai",
    "/root/sisyphus-academica",
}

template_path_keys = {
    "./*",
    "./out/papers/*",
    "~/medai/*",
    "~/medai/out/papers/*",
    "/root/medai/*",
    "/root/medai/out/papers/*",
    "/root/sisyphus-academica/*",
    "/root/sisyphus-academica/out/papers/*",
    "~/.config/opencode/skills/humanizer/*",
    "~/.config/opencode/skills/*",
}

def normalize_write_key(key: str) -> str:
    if key == "./out/papers/*":
        return papers_glob
    if key == "./*":
        return root_glob

    if any(key == f"{root}/out/papers/*" for root in legacy_project_roots):
        return papers_glob
    if any(key == f"{root}/*" for root in legacy_project_roots):
        return root_glob

    return key

def normalize_external_key(key: str) -> str:
    if key == "./*":
        return root_glob
    if key == "~/.config/opencode/skills/humanizer/*":
        return humanizer_glob
    if key == "~/.config/opencode/skills/*":
        return skills_glob
    if "/.config/opencode/skills/humanizer/*" in key:
        return humanizer_glob
    if key == "/tmp/opencode/*":
        return key
    if any(key == f"{root}/*" for root in legacy_project_roots):
        return root_glob
    return key

def set_permission_path(target: dict, key: str, value: str) -> None:
    current = target.get(key)
    if current is not None and current != value:
        raise ValueError(
            f"Permission normalization collision on key '{key}': '{current}' vs '{value}'"
        )
    target[key] = value

def assert_no_unresolved_paths(permission: dict, agent_name: str) -> None:
    write = permission.get("write")
    if isinstance(write, dict):
        for key in write:
            if key in template_path_keys:
                raise ValueError(
                    f"Unresolved write permission path for agent '{agent_name}': {key}"
                )

    external = permission.get("external_directory")
    if isinstance(external, dict):
        for key in external:
            if key == "/tmp/opencode/*":
                continue
            if key in template_path_keys:
                raise ValueError(
                    f"Unresolved external_directory path for agent '{agent_name}': {key}"
                )

with config_path.open("r", encoding="utf-8") as handle:
    config = json.load(handle)

for agent_name, agent in config.get("agents", {}).items():
    permission = agent.get("permission", {})

    write = permission.get("write")
    if isinstance(write, dict):
        normalized_write = {}
        for key, value in write.items():
            set_permission_path(normalized_write, normalize_write_key(key), value)
        permission["write"] = normalized_write

    external = permission.get("external_directory")
    if isinstance(external, dict):
        normalized_external = {}
        for key, value in external.items():
            set_permission_path(normalized_external, normalize_external_key(key), value)
        permission["external_directory"] = normalized_external

    assert_no_unresolved_paths(permission, agent_name)

with config_path.open("w", encoding="utf-8") as handle:
    json.dump(config, handle, indent=2)
    handle.write("\n")
PY
    then
        rm -f "$config_tmp"
        return 1
    fi

    mv -f "$config_tmp" "$config_file"

    return 0
}

normalize_research_director_paths() {
    local director_file="$OPENCODE_AGENTS/research-director.md"

    if [ ! -f "$director_file" ]; then
        echo "  • Skipping research-director path normalization (missing installed research-director.md)"
        return 1
    fi

    if ! command -v python3 >/dev/null 2>&1; then
        echo "  • Skipping research-director path normalization (python3 not found)"
        return 1
    fi

    if ! python3 - "$director_file" "$MEDAI_DIR" <<'PY'
from pathlib import Path
import re
import sys

director_path = Path(sys.argv[1])
project_root = Path(sys.argv[2]).resolve().as_posix()
home_dir = Path.home().resolve().as_posix()

project_glob = f"{project_root}/*"
humanizer_glob = f"{home_dir}/.config/opencode/skills/humanizer/*"
skills_glob = f"{home_dir}/.config/opencode/skills/*"
tool_output_glob = f"{home_dir}/.local/share/opencode/tool-output/*"

template_project_keys = {
    "./*",
    "~/medai/*",
    "/root/medai/*",
    "/root/sisyphus-academica/*",
}

def normalize_external_key(key: str) -> str:
    if key in template_project_keys:
        return project_glob

    if key in {"~/.config/opencode/skills/humanizer/*", "/root/.config/opencode/skills/humanizer/*"}:
        return humanizer_glob

    if key in {"~/.config/opencode/skills/*", "/root/.config/opencode/skills/*"}:
        return skills_glob

    if key in {"~/.local/share/opencode/tool-output/*", "/root/.local/share/opencode/tool-output/*"}:
        return tool_output_glob

    if key.endswith("/.config/opencode/skills/humanizer/*"):
        return humanizer_glob

    if key.endswith("/.config/opencode/skills/*"):
        return skills_glob

    if key.endswith("/.local/share/opencode/tool-output/*"):
        return tool_output_glob

    return key

text = director_path.read_text(encoding="utf-8")

if not text.startswith("---\n"):
    sys.exit(0)

frontmatter_end = text.find("\n---\n", 4)
if frontmatter_end == -1:
    sys.exit(0)

frontmatter = text[4:frontmatter_end]
rest = text[frontmatter_end + 5 :]

lines = frontmatter.splitlines()
updated_lines = []
rewrite_count = 0

in_external_directory = False
external_indent = 0
line_pattern = re.compile(r"^(\s*)([^:#][^:]*):\s*(allow|ask|deny)\s*$")
normalized_external_keys = []

for line in lines:
    stripped = line.strip()

    if stripped.startswith("external_directory:"):
        in_external_directory = True
        external_indent = len(line) - len(line.lstrip(" "))
        updated_lines.append(line)
        continue

    if in_external_directory:
        if stripped and (len(line) - len(line.lstrip(" "))) <= external_indent:
            in_external_directory = False
        else:
            match = line_pattern.match(line)
            if match:
                indent, key, policy = match.groups()
                new_key = normalize_external_key(key.strip())
                if new_key != key.strip():
                    rewrite_count += 1
                normalized_external_keys.append(new_key)
                line = f"{indent}{new_key}: {policy}"

    updated_lines.append(line)

new_frontmatter = "\n".join(updated_lines)

template_placeholders = {
    "./*",
    "~/medai/*",
    "/root/medai/*",
    "/root/sisyphus-academica/*",
    "~/.config/opencode/skills/humanizer/*",
    "/root/.config/opencode/skills/humanizer/*",
    "~/.config/opencode/skills/*",
    "/root/.config/opencode/skills/*",
    "~/.local/share/opencode/tool-output/*",
    "/root/.local/share/opencode/tool-output/*",
}

for key in normalized_external_keys:
    if key in template_placeholders:
        raise ValueError(f"Unresolved research-director path placeholder: {key}")

director_path.write_text(f"---\n{new_frontmatter}\n---\n{rest}", encoding="utf-8")
print(f"rewrote {rewrite_count} research-director external_directory entries")
PY
    then
        return 1
    fi

    return 0
}

echo "╔═══════════════════════════════════════════════════╗"
echo "║     MedAI Academic Writing — Installation         ║"
echo "╚═══════════════════════════════════════════════════╝"
echo ""

# 1. Install Humanizer skill if not present
echo "[1/6] Installing Humanizer skill..."
if [ ! -f "$OPENCODE_SKILLS/humanizer/SKILL.md" ]; then
    mkdir -p "$OPENCODE_SKILLS"
    git clone https://github.com/blader/humanizer.git "$OPENCODE_SKILLS/humanizer" 2>/dev/null
    echo "  ✓ Humanizer installed"
else
    echo "  ✓ Humanizer already exists"
fi

# 2. Install academic-humanizer skill
echo "[2/6] Installing academic-humanizer skill..."
mkdir -p "$OPENCODE_SKILLS/skill-academic-humanizer"
if [ -f "$MEDAI_DIR/skills/skill-academic-humanizer/SKILL.md" ]; then
    cp "$MEDAI_DIR/skills/skill-academic-humanizer/SKILL.md" "$OPENCODE_SKILLS/skill-academic-humanizer/SKILL.md"
elif [ -f "$MEDAI_DIR/skills/skill-academic-humanizer.md" ]; then
    cp "$MEDAI_DIR/skills/skill-academic-humanizer.md" "$OPENCODE_SKILLS/skill-academic-humanizer/SKILL.md"
else
    echo "  ✗ Missing academic-humanizer skill source"
    exit 1
fi
echo "  ✓ Academic Humanizer installed"

# 3. Install ARS multi-skill suite
echo "[3/6] Installing academic-research-skills suite..."
ARS_ALREADY_INSTALLED=true
for skill in deep-research academic-paper academic-paper-reviewer academic-pipeline; do
    if [ ! -f "$OPENCODE_SKILLS/$skill/SKILL.md" ]; then
        ARS_ALREADY_INSTALLED=false
        break
    fi
done

if [ "$ARS_ALREADY_INSTALLED" = true ]; then
    echo "  ✓ ARS skills already installed"
else
    if [ ! -d "$ARS_DIR/.git" ]; then
        git clone "$ARS_REPO" "$ARS_DIR" 2>/dev/null
        echo "  ✓ ARS repository cloned"
    else
        echo "  ✓ ARS repository already exists"
    fi

    ln -sfn "$ARS_DIR/deep-research" "$OPENCODE_SKILLS/deep-research"
    ln -sfn "$ARS_DIR/academic-paper" "$OPENCODE_SKILLS/academic-paper"
    ln -sfn "$ARS_DIR/academic-paper-reviewer" "$OPENCODE_SKILLS/academic-paper-reviewer"
    ln -sfn "$ARS_DIR/academic-pipeline" "$OPENCODE_SKILLS/academic-pipeline"
    echo "  ✓ ARS skills linked"
fi

# 4. Symlink orchestrator
echo "[4/6] Installing orchestrator..."
mkdir -p "$OPENCODE_AGENTS"
director_dest="$OPENCODE_AGENTS/research-director.md"
director_tmp="$(mktemp "${director_dest}.XXXXXX")"
cp "$MEDAI_DIR/orchestrator/research-director.md" "$director_tmp"
mv -f "$director_tmp" "$director_dest"
ln -sf "$MEDAI_DIR/subagents/writer.md" "$OPENCODE_AGENTS/writer.md"
ln -sf "$MEDAI_DIR/subagents/verifier.md" "$OPENCODE_AGENTS/verifier.md"
ln -sf "$MEDAI_DIR/subagents/style-auditor.md" "$OPENCODE_AGENTS/style-auditor.md"
ln -sf "$MEDAI_DIR/subagents/literature-scout.md" "$OPENCODE_AGENTS/literature-scout.md"
ln -sf "$MEDAI_DIR/subagents/formatter.md" "$OPENCODE_AGENTS/formatter.md"
ln -sf "$MEDAI_DIR/novelty-engines/heretic.md" "$OPENCODE_AGENTS/heretic.md"
ln -sf "$MEDAI_DIR/novelty-engines/contrarian.md" "$OPENCODE_AGENTS/contrarian.md"
ln -sf "$MEDAI_DIR/novelty-engines/cross-pollinator.md" "$OPENCODE_AGENTS/cross-pollinator.md"
echo "  ✓ Agents installed"

# 5. Make tools executable
echo "[5/6] Setting up tools..."
chmod +x "$MEDAI_DIR/tools/"*.py 2>/dev/null || true

# Create data dirs
mkdir -p "$MEDAI_DIR/data"
mkdir -p "$MEDAI_DIR/out/papers"
mkdir -p "$MEDAI_DIR/out/figures"

echo "[6/6] Normalizing paths..."
if normalize_agent_config_paths; then
    echo "  ✓ Config paths anchored to $MEDAI_DIR"
else
    echo "  ✗ Config path normalization failed"
    exit 1
fi

if normalize_research_director_paths; then
    echo "  ✓ Research director paths anchored to $MEDAI_DIR and $HOME"
else
    echo "  ✗ Research director path normalization failed"
    exit 1
fi

echo ""
echo "╔═══════════════════════════════════════════════════╗"
echo "║     MedAI Academic Writing — INSTALLED            ║"
echo "║                                                   ║"
echo "║  Next steps:                                      ║"
echo "║  1. Provide a voice sample in data/voice-profile   ║"
echo "║     (2-3 paragraphs of your published writing)     ║"
echo "║  2. Select research-director from agent tab        ║"
echo "║  3. Ask for deep review, paper draft, or revision  ║"
echo "║     planning to trigger ARS skill workflows        ║"
echo "╚═══════════════════════════════════════════════════╝"
