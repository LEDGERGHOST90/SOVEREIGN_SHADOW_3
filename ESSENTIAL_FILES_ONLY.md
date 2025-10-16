# 🎯 WHAT YOU ACTUALLY NEED VS DOCUMENTATION BLOAT

## 🚨 THE PROBLEM:
You have **25 markdown files** creating noise in your workspace.
Most are documentation/prompts for OTHER systems (Notion, Abacus, DeepAgent).

## ✅ ESSENTIAL FILES (Keep These):
1. **README.md** - Main documentation
2. **NEXT_SESSION_STARTER.md** - Quick start guide
3. **FULL_EXECUTION_SEQUENCE.md** - 8-phase launch protocol
4. **GITHUB_SETUP_INSTRUCTIONS.md** - How to push to GitHub
5. **TODO_COMPLETION_SUMMARY.md** - What's been done

## 📦 MOVE TO docs/ (Archive Documentation):
- PROMPT_FOR_NOTION_INTEGRATION.md
- PROMPT_FOR_ABACUS_DEPLOYMENT.md
- PROMPT_FOR_ABACUS_LIVE_SCANNER.md
- PROMPT_FOR_DEEPAGENT_DESIGN.md
- DEPLOYMENT_PROMPTS_GUIDE.md
- DEEPAGENT_BRIEFING.md
- DEEPAGENT_TECHNICAL_INTEGRATION.md
- DEEPAGENT_CONNECTION_GUIDE.md
- SHADOW_SCANNER_ARCHITECTURE.md
- DEPLOYMENT_COMPLETE.md
- DEPLOYMENT_STRATEGY.md
- INTEGRATION_STATUS.md
- LAUNCH_SEQUENCE.md
- LEGACY_LOOP_CONNECTION_SUMMARY.md
- CONTEXT_EMERGENCY_SUMMARY.md
- ENV_PRODUCTION_SETUP_GUIDE.md
- GITHUB_STRATEGY.md
- MCP_SERVER_SETUP.md
- TRADING_ENGINE_CONNECTION.md
- QUICK_START.md

## 🚀 WHAT YOU NEED TO DO:
```bash
# Create docs folder
mkdir -p docs/reference docs/guides docs/prompts

# Move documentation
mv PROMPT_*.md docs/prompts/
mv DEEPAGENT_*.md docs/reference/
mv DEPLOYMENT_*.md docs/reference/
mv *_GUIDE.md docs/guides/
mv *_STRATEGY.md docs/guides/
mv SHADOW_SCANNER_ARCHITECTURE.md docs/reference/
mv INTEGRATION_STATUS.md docs/reference/
mv LEGACY_LOOP_CONNECTION_SUMMARY.md docs/reference/
mv CONTEXT_EMERGENCY_SUMMARY.md docs/reference/

# Keep only essentials in root
# - README.md
# - NEXT_SESSION_STARTER.md
# - FULL_EXECUTION_SEQUENCE.md
# - GITHUB_SETUP_INSTRUCTIONS.md
# - TODO_COMPLETION_SUMMARY.md
```

## 🔧 WEBHINT ERROR:
The "unable to start webhint" error is from VS Code extensions.
It's trying to lint your markdown/web files but failing.

**Fix:**
1. Disable webhint extension in VS Code
2. Or ignore the error (it doesn't affect trading)
3. Or remove .vscode folder if you don't need VS Code settings
