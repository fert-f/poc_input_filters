#!/bin/bash

# https://github.com/trailofbits/skills/tree/main/plugins/modern-python/skills/modern-python


skill_git=https://github.com/trailofbits/skills/tree/main/plugins/modern-python/skills/modern-python
skill_git=https://github.com/semgrep/skills/tree/main/skills/code-security
repo_url="${skill_git%%/tree/*}.git"

skill_path=${skill_git##*tree/main/}
skill_name=${skill_git##*/}
echo "Cloning $repo_url to copy $skill_path to .github/skills/$skill_name ..."

temp_dir=$(mktemp -d)
git clone --depth 1 "$repo_url" "$temp_dir"
mkdir -p .github/skills
cp -r "$temp_dir/$skill_path" ".github/skills/$skill_name"
