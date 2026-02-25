#!/bin/bash
set -e

echo "🚀 Starting Dev Container setup..."

# ── Python dependencies ──────────────────────────────────────────
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
pip install pytest black ruff

# ── Claude Code ──────────────────────────────────────────────────
echo "🤖 Installing Claude Code..."
npm install -g @anthropic-ai/claude-code

# ── Verify installations ─────────────────────────────────────────
echo ""
echo "✅ Setup complete! Versions installed:"
python --version
claude --version

echo ""
echo "👉 Next step: set ANTHROPIC_API_KEY in your host environment to use Claude Code."