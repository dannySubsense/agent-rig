#!/bin/bash
set -e

# Notebook Orchestration — Multi-Agent Notebook Framework
# Version: 04182026

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP_DIR=~/.claude/backup/$(date +%Y%m%d_%H%M%S)

echo "═══════════════════════════════════════════════════════════════════"
echo "  NOTEBOOK ORCHESTRATION INSTALLER"
echo "  Multi-Agent Notebook Framework"
echo "═══════════════════════════════════════════════════════════════════"
echo ""

# Create directories
mkdir -p ~/.claude/agents
mkdir -p ~/.claude/commands
mkdir -p ~/.claude/skills
mkdir -p ~/.claude/templates

# Function to install with backup
install_with_backup() {
    local src="$1"
    local dest_dir="$2"
    local filename=$(basename "$src")
    local dest="$dest_dir/$filename"

    if [ -f "$dest" ]; then
        if ! cmp -s "$src" "$dest"; then
            mkdir -p "$BACKUP_DIR"
            cp "$dest" "$BACKUP_DIR/$filename"
            echo "  ⚠ $(basename "$src") (backed up existing)"
        else
            echo "  ✓ $(basename "$src") (unchanged)"
            return
        fi
    else
        echo "  ✓ $(basename "$src")"
    fi
    cp "$src" "$dest"
}

# Copy agents
echo "Installing agents..."
for agent in "$SCRIPT_DIR"/agents/*.md; do
    if [ -f "$agent" ]; then
        install_with_backup "$agent" ~/.claude/agents
    fi
done

# Copy commands
echo ""
echo "Installing commands..."
for cmd in "$SCRIPT_DIR"/commands/*.md; do
    if [ -f "$cmd" ]; then
        install_with_backup "$cmd" ~/.claude/commands
    fi
done

# Copy skills (directories with SKILL.md)
echo ""
echo "Installing skills..."
for skill_dir in "$SCRIPT_DIR"/skills/*/; do
    if [ -d "$skill_dir" ]; then
        skill_name=$(basename "$skill_dir")
        mkdir -p ~/.claude/skills/"$skill_name"
        src="$skill_dir"SKILL.md
        dest=~/.claude/skills/"$skill_name"/SKILL.md

        if [ -f "$dest" ]; then
            if ! cmp -s "$src" "$dest"; then
                mkdir -p "$BACKUP_DIR/skills/$skill_name"
                cp "$dest" "$BACKUP_DIR/skills/$skill_name/SKILL.md"
                echo "  ⚠ $skill_name (backed up existing)"
            else
                echo "  ✓ $skill_name (unchanged)"
                continue
            fi
        else
            echo "  ✓ $skill_name"
        fi
        cp "$src" "$dest"
    fi
done

# Copy templates
echo ""
echo "Installing templates..."
for template in "$SCRIPT_DIR"/templates/*; do
    if [ -f "$template" ]; then
        install_with_backup "$template" ~/.claude/templates
    fi
done

echo ""
if [ -d "$BACKUP_DIR" ]; then
    echo "⚠ Existing files backed up to: $BACKUP_DIR"
    echo ""
fi
echo "═══════════════════════════════════════════════════════════════════"
echo "  INSTALLATION COMPLETE"
echo "═══════════════════════════════════════════════════════════════════"
echo ""
echo "Installed to:"
echo "  Agents:    ~/.claude/agents/"
echo "  Commands:  ~/.claude/commands/"
echo "  Skills:    ~/.claude/skills/"
echo "  Templates: ~/.claude/templates/"
echo ""
echo "Next steps:"
echo "  1. (Optional) Copy invariants template to your project:"
echo "     cp ~/.claude/templates/NOTEBOOK-INVARIANTS.md ./docs/research/"
echo ""
echo "  2. Start a notebook session:"
echo "     claude"
echo "     > /notebook-start"
echo ""
echo "See QUICKSTART.md for more details."
echo ""
