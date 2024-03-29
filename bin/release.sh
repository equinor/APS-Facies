#!/usr/bin/env bash
# Borrowed from https://github.com/asdf-vm/asdf/blob/master/release.sh ((c) 2014 2014 Akash Manohar J)
# This portion is licensed under MIT

# Unoffical Bash "strict mode"
# http://redsymbol.net/articles/unofficial-bash-strict-mode/
set -euo pipefail
#ORIGINAL_IFS=$IFS
IFS=$'\t\n' # Stricter IFS settings

if [[ $OSTYPE == darwin* ]]; then
    GREP=ggrep
else
    GREP=grep
fi

# shellcheck disable=SC2006
usage() {
    cat <<EOF

Usage: release.sh [new version]

This script is only intended for use by asdf maintainers when releasing new
versions of asdf. Plugin developers and asdf users do not need this script.

This script updates the hardcoded versions in the source code and README and
then commits them on the current branch. It then tags that commit with the
specified version.

If you run this script in error, or with the wrong version, you can undo the
changes by finding the original state in the list of actions listed in the
reflog:

    git reflog

Then revert to the original state by running `git checkout` with the reference
previous to the release tagging changes:

    git checkout HEAD@{21}

Then checkout the original branch again:

    git checkout master

You are back to the original state!

EOF
}

error_exit() {
    usage
    exit 1
}

new_version="${1:-}"
new_tag_name="v$new_version"

# Make sure the user provides a version
if [[ -z "$new_version" ]]
then
    echo "ERROR: no new version specified"
    error_exit
fi

# Make sure version passed in is a plain semantic version to guard against
# leading 'v'.
if ! [[ "${new_version:0:1}" =~ ^[0-9]+$ ]]; then
    echo >&2 "ERROR: semantic version should not start with a letter"
    error_exit
fi

# Make sure the version the user provided hasn't already been tagged
if git tag | grep "$new_tag_name" > /dev/null; then
    echo >&2 "ERROR: git tag with that version already exists"
    exit 1
fi

# Make sure the changelog already contains details on the new version
if ! grep "$new_version$" CHANGELOG.md; then
    echo >&2 "ERROR: changelog entry for this version is missing"
    exit 1
fi

# Make sure the changelog doesn't contain duplicate issue numbers
nonunique_issue_numbers=$($GREP -o -P '#[\d]+' CHANGELOG.md | sort || true)
unique_issue_numbers=$($GREP -o -P '#[\d]+' CHANGELOG.md | sort -u || true)
if [[ "${nonunique_issue_numbers}" != "${unique_issue_numbers}" ]]; then
    echo >&2 "ERROR: Duplicate issue numbers in changelog."
    exit 1
fi

echo "INFO: Checking that all changes are committed and pushed"
git pull

# Disallow unstaged changes in the working tree
if ! git diff-files --check --exit-code --ignore-submodules -- >&2; then
    echo >&2 "ERROR: You have unstaged changes."
    exit 1
fi

# Disallow uncommitted changes in the index
if ! git diff-index --cached --exit-code -r --ignore-submodules HEAD -- >&2; then
    echo >&2 "ERROR: Your index contains uncommitted changes."
    exit 1
fi

# Update version in package.json
sed -i.bak 's|"version": ".*",|"version": "$new_version",|g' gui/package.json
rm gui/package.json.bak

echo "INFO: Committing and tagging new version"

# Commit the changed files before tagging the new release
git add gui/package.json
git commit -m "Update version to ${new_version}. See CHANGELOG.md for details"

git tag -a "$new_tag_name" -m "Version ${new_version}"

echo "INFO: done."
echo "INFO: Now you can push this local branch to the GitHub repository: \`git push <remote> master $new_tag_name\`"
