#!/bin/bash
# MedAI Academic Writing — Quick Install
# Symlinks agents into OpenCode, installs dependencies

set -euo pipefail

SISYPHUS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OPENCODE_AGENTS="$HOME/.config/opencode/agents"
OPENCODE_SKILLS="$HOME/.config/opencode/skills"

echo "╔═══════════════════════════════════════════════════╗"
echo "║     MedAI Academic Writing — Installation             ║"
echo "╚═══════════════════════════════════════════════════╝"
echo ""

# 1. Install Humanizer skill if not present
echo "[1/4] Installing Humanizer skill..."
if [ ! -f "$OPENCODE_SKILLS/humanizer/SKILL.md" ]; then
    mkdir -p "$OPENCODE_SKILLS"
    git clone https://github.com/blader/humanizer.git "$OPENCODE_SKILLS/humanizer" 2>/dev/null
    echo "  ✓ Humanizer installed"
else
    echo "  ✓ Humanizer already exists"
fi

# 2. Install academic-humanizer skill
echo "[2/4] Installing academic-humanizer skill..."
mkdir -p "$OPENCODE_SKILLS/skill-academic-humanizer"
cp "$SISYPHUS_DIR/skills/skill-academic-humanizer.md" "$OPENCODE_SKILLS/skill-academic-humanizer/SKILL.md"
echo "  ✓ Academic Humanizer installed"

# 3. Symlink orchestrator
echo "[3/4] Installing orchestrator..."
mkdir -p "$OPENCODE_AGENTS"
ln -sf "$SISYPHUS_DIR/orchestrator/research-director.md" "$OPENCODE_AGENTS/research-director.md"
ln -sf "$SISYPHUS_DIR/subagents/writer.md" "$OPENCODE_AGENTS/writer.md"
ln -sf "$SISYPHUS_DIR/subagents/verifier.md" "$OPENCODE_AGENTS/verifier.md"
ln -sf "$SISYPHUS_DIR/subagents/style-auditor.md" "$OPENCODE_AGENTS/style-auditor.md"
ln -sf "$SISYPHUS_DIR/subagents/literature-scout.md" "$OPENCODE_AGENTS/literature-scout.md"
ln -sf "$SISYPHUS_DIR/subagents/formatter.md" "$OPENCODE_AGENTS/formatter.md"
ln -sf "$SISYPHUS_DIR/novelty-engines/heretic.md" "$OPENCODE_AGENTS/heretic.md"
ln -sf "$SISYPHUS_DIR/novelty-engines/contrarian.md" "$OPENCODE_AGENTS/contrarian.md"
ln -sf "$SISYPHUS_DIR/novelty-engines/cross-pollinator.md" "$OPENCODE_AGENTS/cross-pollinator.md"
echo "  ✓ Agents installed"

# 4. Make tools executable
echo "[4/4] Setting up tools..."
chmod +x "$SISYPHUS_DIR/tools/"*.py 2>/dev/null || true

# Create data dirs
mkdir -p "$SISYPHUS_DIR/data"
mkdir -p "$SISYPHUS_DIR/out/papers"
mkdir -p "$SISYPHUS_DIR/out/figures"

echo ""
echo "╔═══════════════════════════════════════════════════╗"
echo "║     MedAI Academic Writing — INSTALLED                ║"
echo "║                                                   ║"
echo "║  Next steps:                                      ║"
echo "║  1. Provide a voice sample in data/voice-profile   ║"
echo "║     (2-3 paragraphs of your published writing)     ║"
echo "║  2. Select research-director from agent tab        ║"
echo "║  3. Type: "write a paper about [topic]"             ║"
echo "╚═══════════════════════════════════════════════════╝"
