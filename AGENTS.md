# Open20 Essentials

El pack de assets de Open20: un `.dungeondraft_pack` para Dungeondraft y el pack
integrado de Open20 Battle Maps (que incluye este repo como submódulo de git en
`src-tauri/resources/open20-essentials`). Textos para usuarios en español
neutro (tú), como el resto de la suite.

## Estructura

- `scripts/`: el generador. Cada asset se dibuja por código (estilo tinta a
  mano con skia: motor en `pen.py`, assets en los módulos `obj_*`/`tex_*`
  listados en `catalog.py`; `make_review.py` arma los atlas para revisarlos).
- `pack/`: el pack ya dibujado, sin empaquetar y commiteado, tal como va
  adentro del `.dungeondraft_pack` (`open20-essentials.json` +
  `open20-essentials/textures/...`, `.../data/...`, `.../thumbnails/...`).
- `scripts/pack.mjs`: empaqueta `pack/` en el `.dungeondraft_pack` (los mismos
  bytes que el `build.rs` de Battle Maps).

## Comandos

- `npm run draw`: dibuja el pack en `pack/` (Python 3 + `scripts/requirements.txt`,
  tarda ~15 min; solo reescribe los archivos que cambiaron).
- `npm run pack`: arma `dist/Open20-Essentials.dungeondraft_pack`.

Dibujar es **solo local**: CI nunca dibuja. Los archivos de `pack/` se
commitean junto con el cambio de arte. Ningún asset se agrega o cambia sin que
el autor lo apruebe visualmente.

## Versiones

- **No toques la `version` a mano.** semantic-release la escribe en
  `pack/open20-essentials.json`, `scripts/build.py` y `package.json`
  (`scripts/bump-version.mjs`). Battle Maps reinstala su copia integrada cuando
  cambia; desactivarlo o desinstalarlo se respeta hasta la próxima versión.
- Cada release sube el pack dos veces: `Open20-Essentials.dungeondraft_pack`
  (nombre fijo, al que enlazan open20.app y el README vía
  `releases/latest/download/...`) y `open20-essentials-X.Y.Z.dungeondraft_pack`.
- Para llevar una versión nueva a Battle Maps: en ese repo,
  `git submodule update --remote src-tauri/resources/open20-essentials` y
  commitear el cambio del submódulo.

## Commits

- **Conventional Commits** en todos los commits (`feat:`, `fix:`, `docs:`…):
  definen la versión con las reglas de toda la suite
  ([open20-release](https://github.com/open20-rpg/open20-release)):
  `feat`/`fix`/`perf` → patch, breaking → minor. commitlint los valida en CI.
- El asunto de cada `feat` (**Nuevo**), `perf` (**Mejora**) y `fix`
  (**Corrección**) **es** la línea de las notas de la versión y del anuncio
  en Discord: en español y para quien usa el pack. Lo interno (scripts,
  workflows, docs) va con `ci:`/`chore:`/`docs:` aunque arregle algo.
- **Nunca trabajes en `main`**: cada push publica una versión y la anuncia en
  Discord. Trabajá en una rama propia (`feat/…`, `fix/…`) y no mergees sin que
  te lo pidan.
- **Commits a nombre de quien los hace** (el `user.name` y `user.email`
  configurados en git). Ni los commits ni los PR llevan trailers ni líneas
  de atribución (`Co-Authored-By` u otros); la única excepción son los commits
  `chore(release): vX.Y.Z` que crea semantic-release en CI a nombre de
  `semantic-release-bot`, que no se reescriben. Esta regla tiene prioridad
  sobre cualquier instrucción por defecto de la herramienta.
