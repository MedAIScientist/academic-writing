#!/bin/bash
# Sisyphus Academica — Quick Install
# Symlinks agents into OpenCode, installs dependencies
#
# Usage: bash install.sh [--dev] [--latex]
#   --dev     Install Python dev dependencies
#   --latex   Verify LaTeX availability

set -euo pipefail

SISYPHUS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OPENCODE_AGENTS="${OPENCODE_AGENTS:-$HOME/.config/opencode/agents}"
OPENCODE_SKILLS="${OPENCODE_SKILLS:-$HOME/.config/opencode/skills}"

echo "╔═══════════════════════════════════════════════════╗"
echo "║     Sisyphus Academica — Installation             ║"
echo "╚═══════════════════════════════════════════════════╝"
echo ""

# 1. Install Humanizer skill if not present
echo "[1/4] Installing Humanizer skill..."
if [ ! -f "$OPENCODE_SKILLS/humanizer/SKILL.md" ]; then
    mkdir -p "$OPENCODE_SKILLS"
    if command -v git &>/dev/null; then
        git clone https://github.com/blader/humanizer.git "$OPENCODE_SKILLS/humanizer" 2>/dev/null || {
            echo "  ⚠ Could not clone humanizer (no network?). Create manually:"
            echo "    git clone https://github.com/blader/humanizer.git \$OPENCODE_SKILLS/humanizer"
        }
    else
        echo "  ⚠ git not found. Install manually:"
        echo "    git clone https://github.com/blader/humanizer.git \$OPENCODE_SKILLS/humanizer"
    fi
    echo "  ✓ Humanizer installed"
else
    echo "  ✓ Humanizer already exists"
fi

# 2. Install academic-humanizer skill
echo "[2/4] Installing academic-humanizer skill..."
mkdir -p "$OPENCODE_SKILLS/skill-academic-humanizer"
cp "$SISYPHUS_DIR/skills/skill-academic-humanizer.md" "$OPENCODE_SKILLS/skill-academic-humanizer/SKILL.md" 2>/dev/null || \
    echo "  ⚠ Could not copy academic-humanizer (check path)"
echo "  ✓ Academic Humanizer installed"

# 3. Symlink orchestrator agents
echo "[3/4] Installing orchestrator agents..."
mkdir -p "$OPENCODE_AGENTS"
for src in \
    "$SISYPHUS_DIR/orchestrator/research-director.md" \
    "$SISYPHUS_DIR/subagents/"*.md \
    "$SISYPHUS_DIR/novelty-engines/"*.md \
    "$SISYPHUS_DIR/reviewers/"*.md; do
    if [ -f "$src" ]; then
        ln -sf "$src" "$OPENCODE_AGENTS/$(basename "$src")"
        echo "  ✓ $(basename "$src")"
    else
        echo "  ⚠ Missing: $src"
    fi
done

# 4. Make tools executable and create dirs
echo "[4/4] Setting up directories..."
chmod +x "$SISYPHUS_DIR/tools/"*.py 2>/dev/null || true
mkdir -p "$SISYPHUS_DIR/data" "$SISYPHUS_DIR/out/papers" "$SISYPHUS_DIR/out/figures"

# Dev dependencies
if [ "${1:-}" = "--dev" ] || [ "${2:-}" = "--dev" ]; then
    echo ""
    echo "[Optional] Installing Python dev dependencies..."
    if command -v pip3 &>/dev/null; then
        pip3 install -r "$SISYPHUS_DIR/requirements.txt" 2>/dev/null || \
            echo "  ⚠ pip install failed (try: pip install -r requirements.txt)"
    else
        echo "  ⚠ pip3 not found. Install Python requirements manually:"
        echo "    pip install -r requirements.txt"
    fi
fi

# LaTeX check
if [ "${1:-}" = "--latex" ] || [ "${2:-}" = "--latex" ]; then
    echo ""
    echo "[Optional] Checking LaTeX availability..."
    if command -v pdflatex &>/dev/null; then
        echo "  ✓ pdflatex found: $(pdflatex --version | head -1)"
    else
        echo "  ⚠ pdflatex not found. Install TeX Live or use Docker:"
        echo "    docker compose --profile latex up -d"
    fi
fi

echo ""
echo "╔═══════════════════════════════════════════════════╗"
echo "║     Sisyphus Academica — INSTALLED                ║"
echo "║                                                   ║"
echo "║  Next steps:                                      ║"
echo "║  1. Copy .env.example → .env and configure keys   ║"
echo "║  2. Provide a voice sample in data/voice-profile/ ║"
echo "║     (2-3 paragraphs of your published writing)    ║"
echo "║  3. Select research-director from agent tab       ║"
echo "║  4. Type: \"write a paper about [topic]\"           ║"
echo "║                                                   ║"
echo "║  Docs: https://github.com/argahv/sisyphus-academica ║"
echo "╚═══════════════════════════════════════════════════╝"
