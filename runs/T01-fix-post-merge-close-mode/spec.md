# Spec: T01-fix-post-merge-close-mode

## Objetivo

Corregir `.github/workflows/post-merge-close-feature.yml` para que el cierre
automático de ROADMAP funcione también para ramas `feature/NN-slug` sin
prefijo de versión — la interfaz legacy explícitamente documentada en
`AGENTS.md` ("Omitir `-Version` conserva la interfaz legacy") — sin alterar
el comportamiento ya correcto para `feature/vX.Y.Z-NN-slug`, `milestone/slug`
ni `maintenance/vX.Y.Z-TNN-slug`.

## Contexto y evidencia del defecto real

El merge de la PR #1 (`feature/01-fundacion-diseno` → `develop`, unidad
`01-fundacion-diseno`, sin `-Version`) disparó
`post-merge-close-feature.yml`. El job `close-feature` falló en el paso
"Cerrar feature en ROADMAP remoto" con:

```
Cannot validate argument on parameter 'Mode'. The argument "" does not
belong to the set... ValidateSet attribute.
```

Causa raíz confirmada leyendo el propio workflow (`runs/jobs/106201062447`,
run `35556510071`): la rama `head_ref='feature/01-fundacion-diseno'` cae en
la segunda condición (`^feature/([0-9]{2}-[a-z0-9]+(-[a-z0-9]+)*)$`), que
sólo emite `version=` y `slug=...`, sin emitir `mode=` ni `branch=` —a
diferencia de las otras tres ramas de la condición, que sí los emiten—. El
paso siguiente invoca
`./scripts/close-feature.ps1 -Mode '${{ steps.feature.outputs.mode }}'`
con una cadena vacía, y `close-feature.ps1` declara `-Mode` con
`[ValidateSet("Feature","Milestone","Maintenance")]`, por lo que PowerShell
rechaza el argumento antes de ejecutar ninguna lógica de cierre.

Efecto verificado: PR #1 quedó `MERGED` en GitHub (evidencia real, no
simulada), pero `ROADMAP.md` en `develop` siguió marcando
`01-fundacion-diseno` como `[-]` en vez de `[x]`, y `STATUS.md` no se
sincronizó.

## Alcance

Sólo se modifica el paso "Derivar slug y modo de work unit" de
`post-merge-close-feature.yml` (agregar las dos líneas de salida faltantes
en la rama legacy `feature/NN-slug`). No se toca `close-feature.ps1`,
`workunit-lib.ps1`, `guard-develop-branch.yml`, ni ninguna otra rama de la
condición. No se corrige aquí la ausencia de soporte para
`maintenance/TNN-slug` sin versión en el mismo workflow (gap distinto,
detectado durante la revisión, de menor severidad porque falla de forma
segura — `skip=true` — sin lanzar una excepción; se documenta como
incidencia para una unidad futura, fuera de alcance de esta corrección).

## Criterios de aceptación

- La rama legacy `feature/NN-slug` emite `mode=Feature` y `branch=$head_ref`,
  igual que las otras tres ramas de la misma condición.
- El YAML resultante es sintácticamente válido.
- La suite del circuito (`pytest -q tests/`) sigue en verde.
- No se relaja `guard-develop-branch.yml` ni se introduce force-push.
- `close-feature.ps1` sigue siendo el único mecanismo que escribe
  `ROADMAP.md`/`STATUS.md` en `develop`; este cambio sólo corrige los
  argumentos con los que se lo invoca.
