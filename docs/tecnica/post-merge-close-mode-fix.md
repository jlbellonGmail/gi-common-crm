# Corrección: modo vacío en el cierre post-merge de ramas Feature legacy

## Contexto

`AGENTS.md` documenta que omitir `-Version` en `start-work-unit.ps1`
conserva la "interfaz legacy": una rama `feature/NN-slug` sin prefijo de
versión es una forma válida de Feature. El workflow
`.github/workflows/post-merge-close-feature.yml` no reflejaba esa validez
para el paso automático de cierre.

## Defecto

En el paso "Derivar slug y modo de work unit", la rama de la condición
Bash para `feature/NN-slug` (sin versión) emitía `version=` y `slug=...`
pero no `mode=` ni `branch=`, a diferencia de las otras tres ramas de la
misma condición (`feature/vX.Y.Z-NN-slug`, `milestone/slug`,
`maintenance/vX.Y.Z-TNN-slug`). El paso siguiente invoca
`./scripts/close-feature.ps1 -Mode '${{ steps.feature.outputs.mode }}'`,
y `-Mode` está declarado con `[ValidateSet("Feature","Milestone",
"Maintenance")]` en `close-feature.ps1`: una cadena vacía no pertenece al
conjunto y PowerShell aborta el paso antes de ejecutar ninguna lógica de
cierre.

## Evidencia real observada

El merge de la PR #1 (`feature/01-fundacion-diseno`, unidad
`01-fundacion-diseno`, sin `-Version`) disparó el workflow, que falló en
ese paso exacto (run `35556510071`, job `106201062447`,
`Cannot validate argument on parameter 'Mode'`). La PR quedó `MERGED` en
GitHub, pero `ROADMAP.md` en `develop` no se actualizó de `[-]` a `[x]`.

## Corrección

Se agregaron las dos líneas de salida faltantes (`branch=$head_ref`,
`mode=Feature`) a esa rama de la condición, igualándola a las otras tres.
No se modificó `close-feature.ps1` ni el guard de `develop`.

## Incidencia relacionada, fuera de alcance

`Get-MaintenanceIdentity` (`scripts/workunit-lib.ps1`) admite ramas
`maintenance/TNN-slug` **sin** prefijo de versión, pero la condición Bash
del mismo workflow para `maintenance/` sólo reconoce el patrón **con**
versión (`maintenance/vX.Y.Z-TNN-slug`). Una rama `maintenance/TNN-slug`
sin versión cae hoy en el `else` del workflow (`skip=true`): no falla, pero
tampoco cierra ROADMAP automáticamente. No se corrige en esta unidad por
no haber causado un fallo real todavía y para mantener el cambio acotado
al defecto observado; queda registrada aquí para una corrección futura si
se decide usar esa variante.
