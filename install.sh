#!/bin/bash
# Sisyphus Academica — Interactive Installer
# Installs 25 agents into OpenCode with portable paths, prompts for config
#
# Usage: bash install.sh [--yes] [--dev] [--latex] [--check]
#   --yes     Skip all prompts, use defaults
#   --dev     Install Python dev dependencies
#   --latex   Verify LaTeX availability
#   --check   Validate installation

set -euo pipefail

SISYPHUS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OPENCODE_AGENTS="${OPENCODE_AGENTS:-$HOME/.config/opencode/agents}"
OPENCODE_SKILLS="${OPENCODE_SKILLS:-$HOME/.config/opencode/skills}"
OPENCODE_CONFIG="${OPENCODE_CONFIG:-$HOME/.config/opencode}"

SKIP_PROMPTS=false
for arg in "$@"; do [ "$arg" = "--yes" ] && SKIP_PROMPTS=true && break; done

echo "╔═══════════════════════════════════════════════════╗"
echo "║     Sisyphus Academica — Interactive Installer    ║"
echo "╚═══════════════════════════════════════════════════╝"
echo ""

# ------------------------------------------------------------------
# Helper: ask a question (free-form answer)
# ------------------------------------------------------------------
ask() {
    local var_name="$1" prompt="$2" default="${3:-}"
    if [ "$SKIP_PROMPTS" = true ]; then
        eval "$var_name=\"$default\""
        return
    fi
    local hint=""
    [ -n "$default" ] && hint=" [$default]"
    read -r -p "$prompt$hint: " input
    eval "$var_name=\"${input:-$default}\""
}

# ------------------------------------------------------------------
# Helper: yes/no confirmation
# ------------------------------------------------------------------
confirm() {
    local prompt="$1" default="${2:-y}"
    if [ "$SKIP_PROMPTS" = true ]; then
        [ "$default" = "y" ] && return 0 || return 1
    fi
    local hint="[Y/n]"
    [ "$default" = "n" ] && hint="[y/N]"
    read -r -p "$prompt $hint " answer
    case "${answer:-$default}" in
        [yY]|[yY][eE][sS]) return 0 ;;
        *) return 1 ;;
    esac
}

# ==================================================================
# PHASE 0: SUBSCRIPTION INTERVIEW (omo-style)
# ==================================================================
echo "[0/7] Subscription interview..."
echo ""

# Q0: Author name
ask AUTHOR_NAME "What is your name?" "${USER:-argahv}"

# Write name to CITATION.cff
if grep -q 'given-names: ""' "$SISYPHUS_DIR/CITATION.cff" 2>/dev/null; then
    FAMILY="${AUTHOR_NAME##* }"
    GIVEN="${AUTHOR_NAME% *}"
    [ -z "$GIVEN" ] && GIVEN="$FAMILY" && FAMILY=""
    [ -z "$FAMILY" ] && FAMILY="$GIVEN" && GIVEN=""
    sed -i "s/family-names: \".*\"/family-names: \"$FAMILY\"/" "$SISYPHUS_DIR/CITATION.cff"
    sed -i "s/given-names: \".*\"/given-names: \"$GIVEN\"/" "$SISYPHUS_DIR/CITATION.cff"
    echo "  ✓ CITATION.cff updated with name: $GIVEN $FAMILY"
fi

# Q1: Platform — OpenCode or manual
if command -v opencode &>/dev/null; then
    echo "  ✓ OpenCode $(opencode --version 2>/dev/null | head -1) detected"
    HAS_OPENCODE=true
    PLATFORM="opencode"
else
    echo "  ⚠ OpenCode not found (install from https://opencode.ai/docs)"
    HAS_OPENCODE=false
    if confirm "  Continue without OpenCode? (CLI tools only, no agent orchestration)" "n"; then
        PLATFORM="manual"
        echo "  → Manual mode: Python CLI tools only"
    else
        echo "  → Install OpenCode first, then re-run: bash install.sh"
        echo "  → Ref: https://opencode.ai/docs"
        exit 0
    fi
fi

# Q2: oh-my-openagent integration
if [ "$PLATFORM" = "opencode" ]; then
    if [ -f "$OPENCODE_CONFIG/oh-my-openagent.json" ] || [ -f "$OPENCODE_CONFIG/oh-my-openagent.jsonc" ]; then
        echo "  ✓ oh-my-openagent detected — agents integrate into omo ecosystem"
        HAS_OMO=true
    else
        HAS_OMO=false
        if confirm "  Do you have oh-my-openagent installed? (for omo integration)" "n"; then
            echo "  → Install oh-my-openagent first: bunx oh-my-openagent install"
            echo "  → Then re-run: bash install.sh"
            echo "  → Continuing with standalone config for now"
        fi
    fi
fi

# Q3: Claude subscription (like omo's --claude flag)
echo ""
echo "  ── LLM Subscriptions ──"

HAS_CLAUDE=false
CLAUDE_MAX20=false
if confirm "  Do you have a Claude subscription (Pro/Max)?" "n"; then
    HAS_CLAUDE=true
    if confirm "  Do you have Claude Max (20x usage)?" "n"; then
        CLAUDE_MAX20=true
    fi
fi

# Strong warning when no Claude (like omo's "MUST STRONGLY WARN")
if [ "$HAS_CLAUDE" = false ]; then
    echo ""
    echo "  ⚠ WARNING: Sisyphus Academica's writing and novelty engines work best"
    echo "    with Claude models. Without a Claude subscription, paper quality may"
    echo "    noticeably degrade. GPT models and free-tier alternatives will"
    echo "    require 2-3x more revision rounds to match Claude output."
    echo ""
fi

# Q4: OpenAI subscription (like omo's --openai flag)
HAS_OPENAI=false
if confirm "  Do you have an OpenAI/ChatGPT subscription?" "n"; then
    HAS_OPENAI=true
fi

# Derive combined provider
if [ "$HAS_CLAUDE" = true ] && [ "$HAS_OPENAI" = true ]; then
    LLM_PROVIDER="both"
elif [ "$HAS_CLAUDE" = true ]; then
    LLM_PROVIDER="anthropic"
elif [ "$HAS_OPENAI" = true ]; then
    LLM_PROVIDER="openai"
else
    LLM_PROVIDER="9router"
fi

# Q5: Semantic Scholar API key (like omo's --opencode-zen style flag)
echo ""
echo "  ── API Keys ──"

ask SEMANTIC_SCHOLAR_KEY "  Semantic Scholar API key? (free — get at semanticscholar.org/product/api)" ""
if [ -n "$SEMANTIC_SCHOLAR_KEY" ]; then
    if [ -f "$SISYPHUS_DIR/.env" ]; then
        if grep -q 'SEMANTIC_SCHOLAR_API_KEY=' "$SISYPHUS_DIR/.env"; then
            sed -i "s/SEMANTIC_SCHOLAR_API_KEY=.*/SEMANTIC_SCHOLAR_API_KEY=$SEMANTIC_SCHOLAR_KEY/" "$SISYPHUS_DIR/.env"
        else
            echo "SEMANTIC_SCHOLAR_API_KEY=$SEMANTIC_SCHOLAR_KEY" >> "$SISYPHUS_DIR/.env"
        fi
    else
        cp "$SISYPHUS_DIR/.env.example" "$SISYPHUS_DIR/.env"
        sed -i "s/SEMANTIC_SCHOLAR_API_KEY=.*/SEMANTIC_SCHOLAR_API_KEY=$SEMANTIC_SCHOLAR_KEY/" "$SISYPHUS_DIR/.env"
    fi
    echo "  ✓ API key saved to .env"
else
    echo "  → Skipping (100 req/min rate limit applies)"
fi

# Q6: Voice sample
echo ""
echo "  ── Voice Calibration ──"
HAS_VOICE_SAMPLE=false
if [ -f "$SISYPHUS_DIR/data/voice-profile/sample.txt" ]; then
    if confirm "  Voice sample found. Use existing?" "y"; then
        HAS_VOICE_SAMPLE=true
    fi
else
    if confirm "  Do you have a writing sample for voice calibration?" "n"; then
        HAS_VOICE_SAMPLE=true
        echo "  → Paste 2-3 paragraphs of published writing into:"
        echo "    $SISYPHUS_DIR/data/voice-profile/sample.txt"
    fi
fi

# Q7: LaTeX
echo ""
echo "  ── LaTeX / PDF ──"
if command -v pdflatex &>/dev/null; then
    echo "  ✓ LaTeX detected: $(pdflatex --version 2>/dev/null | head -1)"
    HAS_LATEX=true
elif command -v docker &>/dev/null; then
    echo "  ⚠ LaTeX not installed locally. Docker available."
    if confirm "  Use Docker for LaTeX compilation?" "y"; then
        HAS_LATEX=true
    else
        HAS_LATEX=false
    fi
else
    echo "  ⚠ LaTeX not found. Papers will output .tex only."
    HAS_LATEX=false
fi

# ==================================================================
# SUMMARY
# ==================================================================
echo ""
echo "  ── Install Plan ──"
echo "  Name:     $AUTHOR_NAME"
echo "  Platform: ${PLATFORM:-opencode}"
echo "  Claude:   $([ "$HAS_CLAUDE" = true ] && echo "yes $([ "$CLAUDE_MAX20" = true ] && echo '(max20)')" || echo "no")"
echo "  OpenAI:   $([ "$HAS_OPENAI" = true ] && echo yes || echo no)"
echo "  Provider: $LLM_PROVIDER"
echo "  LaTeX:    $([ "$HAS_LATEX" = true ] && echo yes || echo no)"
echo "  Voice:    $([ "$HAS_VOICE_SAMPLE" = true ] && echo yes || echo no)"

if ! confirm "  Proceed with installation?" "y"; then
    echo "  → Aborted."
    exit 0
fi
echo ""

# ==================================================================
# INSTALL AGENT FILE with portable path transformation
# ==================================================================
install_agent_file() {
    local src="$1"
    local basename="$(basename "$src")"
    local dest="$OPENCODE_AGENTS/$basename"
    if [ ! -f "$src" ]; then
        echo "  ⚠ Missing source: $src"
        return 1
    fi
    mkdir -p "$OPENCODE_AGENTS"
    sed \
        -e "s|/root/sisyphus-academica|$SISYPHUS_DIR|g" \
        -e "s|/root/\.config/opencode|$OPENCODE_CONFIG|g" \
        -e "s|/root/\.local/share/opencode|$HOME/.local/share/opencode|g" \
        -e "s|/tmp/opencode|/tmp/opencode|g" \
        "$src" > "$dest"
    echo "  ✓ $basename"
}

# ==================================================================
# Transform config/agent-config.json
# ==================================================================
install_config() {
    local src="$SISYPHUS_DIR/config/agent-config.json"
    local dest="$OPENCODE_AGENTS/../agent-config.json"
    if [ ! -f "$src" ]; then
        echo "  ⚠ Missing config: $src"
        return
    fi
    mkdir -p "$OPENCODE_CONFIG"
    sed \
        -e "s|/root/sisyphus-academica|$SISYPHUS_DIR|g" \
        -e "s|/root/\.config/opencode|$OPENCODE_CONFIG|g" \
        -e "s|/root/\.local/share/opencode|$HOME/.local/share/opencode|g" \
        "$src" > "$dest"
    echo "  ✓ agent-config.json → $dest"
}

# ==================================================================
# Configure models based on subscription answers
# ==================================================================
configure_models() {
    local config_file="$OPENCODE_CONFIG/agent-config.json"
    [ ! -f "$config_file" ] && return

    case "$LLM_PROVIDER" in
        anthropic)
            sed -i 's|"model": "9router/opencode-free"|"model": "anthropic/claude-sonnet-4"|g' "$config_file"
            if [ "$CLAUDE_MAX20" = true ]; then
                sed -i 's|"variant": "think"|"variant": "think"|' "$config_file"
                echo "  → Claude Max20: all agents set to Claude Sonnet 4 (unlimited)"
            else
                echo "  → All agents set to Claude Sonnet 4"
            fi
            ;;
        openai)
            sed -i 's|"model": "9router/opencode-free"|"model": "openai/gpt-4o"|g' "$config_file"
            echo "  → All agents set to GPT-4o"
            echo "  ⚠ Note: Novelty engines and writer perform better with Claude."
            echo "    Edit config/agent-config.json to use Claude for those agents."
            ;;
        both)
            sed -i 's|"model": "9router/opencode-free"|"model": "anthropic/claude-sonnet-4"|g' "$config_file"
            echo "  → Writers, novelty engines, reviewers → Claude Sonnet 4"
            echo "  → Edit config/agent-config.json to set verifier/literature-scout to openai/gpt-4o"
            ;;
        9router)
            echo "  → Using default 9router gateway (no change needed)"
            ;;
    esac
}

# ==================================================================
# [1/7] Install Humanizer skill
# ==================================================================
echo "[1/7] Installing Humanizer skill..."
if [ ! -f "$OPENCODE_SKILLS/humanizer/SKILL.md" ]; then
    mkdir -p "$OPENCODE_SKILLS"
    if command -v git &>/dev/null; then
        git clone https://github.com/blader/humanizer.git "$OPENCODE_SKILLS/humanizer" 2>/dev/null || {
            echo "  ⚠ Could not clone humanizer. Install manually:"
            echo "    git clone https://github.com/blader/humanizer.git \$OPENCODE_SKILLS/humanizer"
        }
    else
        echo "  ⚠ git not found."
    fi
    echo "  ✓ Humanizer installed"
else
    echo "  ✓ Humanizer already exists"
fi

# ==================================================================
# [2/7] Install academic-humanizer skill
# ==================================================================
echo "[2/7] Installing academic-humanizer skill..."
mkdir -p "$OPENCODE_SKILLS/skill-academic-humanizer"
cp "$SISYPHUS_DIR/skills/skill-academic-humanizer.md" "$OPENCODE_SKILLS/skill-academic-humanizer/SKILL.md" 2>/dev/null || \
    echo "  ⚠ Could not copy academic-humanizer"
echo "  ✓ Academic Humanizer installed"

# ==================================================================
# [3/7] Install orchestrator agents (25 total)
# ==================================================================
echo "[3/7] Installing orchestrator agents (25 total)..."
install_agent_file "$SISYPHUS_DIR/orchestrator/research-director.md"
for f in "$SISYPHUS_DIR/subagents/"*.md; do install_agent_file "$f"; done
for f in "$SISYPHUS_DIR/novelty-engines/"*.md; do install_agent_file "$f"; done
for f in "$SISYPHUS_DIR/reviewers/"*.md; do install_agent_file "$f"; done
echo "  → All agents installed in $OPENCODE_AGENTS"

# ==================================================================
# [4/7] Install config with path transformation
# ==================================================================
echo "[4/7] Installing agent configuration..."
install_config
configure_models

# ==================================================================
# [5/7] Set up directories and tools
# ==================================================================
echo "[5/7] Setting up directories..."
chmod +x "$SISYPHUS_DIR/tools/"*.py 2>/dev/null || true
mkdir -p "$SISYPHUS_DIR/data" "$SISYPHUS_DIR/out/papers" "$SISYPHUS_DIR/out/figures"

if echo "$@" | grep -q -- "--dev"; then
    echo ""
    echo "[Optional] Installing Python dependencies..."
    if command -v pip3 &>/dev/null; then
        pip3 install -r "$SISYPHUS_DIR/requirements.txt" 2>/dev/null || \
            echo "  ⚠ pip install failed (try: pip install -r requirements.txt)"
    else
        echo "  ⚠ pip3 not found."
    fi
fi

# ==================================================================
# [6/7] Provider authentication guide
# ==================================================================
echo "[6/7] Provider authentication..."
if [ "$PLATFORM" = "opencode" ]; then
    if [ "$HAS_CLAUDE" = true ]; then
        echo "  → Run 'opencode auth login' to authenticate Anthropic (Claude)"
    fi
    if [ "$HAS_OPENAI" = true ]; then
        echo "  → Run 'opencode auth login' to authenticate OpenAI (GPT)"
    fi
    if [ "$LLM_PROVIDER" = "9router" ]; then
        echo "  → Using 9router — no auth needed (gateway handles it)"
    fi
fi

# ==================================================================
# [7/7] Validation
# ==================================================================
echo "[7/7] Validating installation..."
errors=0
expected=25
count=0
for f in "$SISYPHUS_DIR/orchestrator/"*.md "$SISYPHUS_DIR/subagents/"*.md \
         "$SISYPHUS_DIR/novelty-engines/"*.md "$SISYPHUS_DIR/reviewers/"*.md; do
    base=$(basename "$f")
    [ -f "$OPENCODE_AGENTS/$base" ] && count=$((count + 1))
done

echo "  Agents installed: $count / $expected"
[ "$count" -ge "$expected" ] && echo "  ✓ All agents present" || { echo "  ⚠ Missing agents"; errors=$((errors + 1)); }

[ -f "$OPENCODE_CONFIG/agent-config.json" ] && echo "  ✓ Configuration installed" || { echo "  ⚠ Configuration missing"; errors=$((errors + 1)); }
[ -f "$SISYPHUS_DIR/.env" ] && echo "  ✓ .env configured" || echo "  ⚠ .env not configured — cp .env.example .env"

echo ""
[ "$errors" -eq 0 ] && echo "  ✓ Validation PASSED" || echo "  ⚠ $errors issue(s) found"

echo ""
echo "╔═══════════════════════════════════════════════════╗"
echo "║     Sisyphus Academica — INSTALLED                ║"
echo "╚═══════════════════════════════════════════════════╝"
echo ""
echo "  Profile:   $AUTHOR_NAME"
echo "  Provider:  $LLM_PROVIDER"
echo "  Agents:    25"
echo "  LaTeX:     $([ "$HAS_LATEX" = true ] && echo yes || echo no)"
echo ""
echo "  Next:"
echo "  1. OpenCode → agent tab → research-director"
echo "  2. Type: \"write a paper about [topic]\""
echo ""
echo "  Docs: https://github.com/argahv/sisyphus-academica"
