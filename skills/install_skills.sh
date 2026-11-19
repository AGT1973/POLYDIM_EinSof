#!/usr/bin/env bash
# POLYDIM-EINSOF: Student Skills Pack Installer (Linux / macOS)
# Independent Research | Ariel Garcia Traba | Estándar 2030
set -e

echo "======================================================================"
echo "  POLYDIM-EINSOF: STUDENT SKILLS PACK INSTALLER (1-CLICK)"
echo "  Independent Research | Ariel Garcia Traba | Estándar 2030"
echo "======================================================================"
echo ""

SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DIRS=(
    "$HOME/.gemini/antigravity/skills"
    "$HOME/.gemini/config/skills"
)

SKILLS=("ghost" "whisper" "council" "model-bridge" "quick-query" "manifold-verify" "redteam" "einsof-bootstrap")

for TARGET_DIR in "${TARGET_DIRS[@]}"; do
    mkdir -p "$TARGET_DIR"
    echo "[*] Installing skills into: $TARGET_DIR"
    for s in "${SKILLS[@]}"; do
        if [ -f "$SOURCE_DIR/$s/SKILL.md" ]; then
            mkdir -p "$TARGET_DIR/$s"
            cp "$SOURCE_DIR/$s/SKILL.md" "$TARGET_DIR/$s/SKILL.md"
            echo "  [OK] Installed $s"
        fi
    done
done

echo ""
echo "[*] Running Silicon Verification..."
if [ -f "$SOURCE_DIR/scripts/manifold_verifier.py" ]; then
    python3 "$SOURCE_DIR/scripts/manifold_verifier.py" || true
fi

echo ""
echo "======================================================================"
echo "  [SUCCESS] Student Skills Pack Ready in Antigravity / Claude Code!"
echo "  Available slash commands: /ghost, /whisper, /council, /call, /query, /verify-manifold, /redteam"
echo "======================================================================"
