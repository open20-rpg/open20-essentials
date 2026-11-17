// Sets the pack version (run by semantic-release before each release). Two
// places carry it and must match: the manifest Dungeondraft and Battle Maps
// read (pack/open20-essentials.json) and the one build.py writes it from.
// A new version also makes Battle Maps reinstall the built-in copy.
// Usage: node scripts/bump-version.mjs <version>
import { readFileSync, writeFileSync } from "node:fs"

const version = process.argv[2]
if (!/^\d+\.\d+\.\d+$/.test(version ?? "")) {
  console.error("usage: node scripts/bump-version.mjs <x.y.z>")
  process.exit(1)
}
const edit = (path, re) => {
  const text = readFileSync(path, "utf8")
  if (!re.test(text)) throw new Error(`no version in ${path}`)
  writeFileSync(path, text.replace(re, `$1${version}$2`))
}
edit("pack/open20-essentials.json", /("version":\s*")[^"]*(")/)
edit("scripts/build.py", /("version":\s*")[^"]*(")/)
console.log(`version set to ${version}`)
