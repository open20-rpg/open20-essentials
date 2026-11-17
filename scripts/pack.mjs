// Packs pack/ into a .dungeondraft_pack: a Godot 3 PCK (format 1), the same
// bytes Open20 Battle Maps' build.rs writes. Header, index of
// `res://packs/<relative path>` entries, then the files back to back; MD5s are
// left zero, which the format allows.
//
//   node scripts/pack.mjs   ->  dist/Open20-Essentials.dungeondraft_pack
//                               dist/open20-essentials-<version>.dungeondraft_pack
import { mkdirSync, readFileSync, readdirSync, statSync, writeFileSync } from "node:fs"
import { join, relative, sep } from "node:path"
import { fileURLToPath } from "node:url"

const ROOT = fileURLToPath(new URL("..", import.meta.url))
const SRC = join(ROOT, "pack")
const DIST = join(ROOT, "dist")

/** Every file under dir, as paths relative to SRC with "/", in byte order. */
function collect(dir, out = []) {
  for (const name of readdirSync(dir)) {
    const path = join(dir, name)
    if (statSync(path).isDirectory()) collect(path, out)
    else out.push(relative(SRC, path).split(sep).join("/"))
  }
  return out
}

const files = collect(SRC).sort((a, b) => Buffer.compare(Buffer.from(a), Buffer.from(b)))
if (!files.length) throw new Error("pack/ is empty: run `npm run draw` first")
const datas = files.map((rel) => readFileSync(join(SRC, rel)))
const paths = files.map((rel) => Buffer.from(`res://packs/${rel}`))

const indexSize = paths.reduce((n, p) => n + 4 + p.length + 8 + 8 + 16, 0)
let offset = BigInt(88 + indexSize)
const header = Buffer.alloc(88)
;[0x43504447, 1, 3, 4, 0].forEach((v, i) => header.writeUInt32LE(v, i * 4))
header.writeUInt32LE(files.length, 84)
const index = []
paths.forEach((p, i) => {
  const entry = Buffer.alloc(4 + p.length + 32)
  entry.writeUInt32LE(p.length, 0)
  p.copy(entry, 4)
  entry.writeBigUInt64LE(offset, 4 + p.length)
  entry.writeBigUInt64LE(BigInt(datas[i].length), 12 + p.length)
  index.push(entry)
  offset += BigInt(datas[i].length)
})
const out = Buffer.concat([header, ...index, ...datas])

const { version } = JSON.parse(readFileSync(join(SRC, "open20-essentials.json"), "utf8"))
mkdirSync(DIST, { recursive: true })
for (const name of ["Open20-Essentials.dungeondraft_pack", `open20-essentials-${version}.dungeondraft_pack`]) {
  writeFileSync(join(DIST, name), out)
}
console.log(`packed ${files.length} files, ${(out.length / 1e6).toFixed(1)} MB, v${version}`)
