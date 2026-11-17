// Commit messages must follow Conventional Commits: semantic-release derives
// each version (and its release notes) from them. See AGENTS.md.
export default {
  extends: ["@commitlint/config-conventional"],
  // semantic-release's own commits carry the release notes in the body.
  ignores: [(message) => message.startsWith("chore(release):")],
}
