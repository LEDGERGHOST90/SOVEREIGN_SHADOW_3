#!/bin/bash
# merge_branches.sh — Merge all Claude Code branches into main

set -e

REPO_PATH="/Volumes/LegacySafe/SOVEREIGN_SHADOW_3"
cd "$REPO_PATH"

echo "🔄 Fetching all branches..."
git fetch origin

echo "📍 Checking out main..."
git checkout main
git pull origin main

BRANCHES=(
  "claude/brain-functionality-01Kn3CyFaZePLEmAPWxBEk6m"
  "claude/paper-trade-status-update-01FFrus9YTJsAUMJoJVFWb9U"
  "claude/update-github-sovereign-shadow-014ZxwouHnwQgt5QSLD61sqs"
)

for branch in "${BRANCHES[@]}"; do
  echo "🔀 Merging $branch..."
  git merge "origin/$branch" -m "Merge $branch into main" --no-edit || {
    echo "⚠️ Conflict in $branch — resolve manually"
    exit 1
  }
done

echo "🚀 Pushing to origin..."
git push origin main

echo "🧹 Cleaning up remote branches..."
for branch in "${BRANCHES[@]}"; do
  git push origin --delete "$branch" 2>/dev/null || echo "Branch $branch already deleted"
done

echo "✅ All branches merged and cleaned up."
