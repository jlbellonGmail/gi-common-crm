# Decisión

Se corrige únicamente la emisión de outputs faltante en el paso de
derivación de slug/modo del workflow post-merge; no se toca
`close-feature.ps1`, `guard-develop-branch.yml` ni la política de
protección de `develop`. `close-feature.ps1` sigue siendo el único
mecanismo que valida la PR mergeada contra `develop` y escribe
`ROADMAP.md`/`STATUS.md`; este cambio sólo asegura que el workflow lo
invoque con los argumentos correctos para la interfaz legacy sin versión.

Se publica como unidad `Maintenance` auxiliar (`T01-fix-post-merge-close-
mode`, sin ítem propio en ROADMAP) porque corrige el circuito, no el
producto CRM — mismo patrón ya usado en `gi-platform-core` para su unidad
`04-post-merge-close-dispatch`. El cierre pendiente de `01-fundacion-diseno`
se completa aparte, ejecutando `close-feature.ps1` directamente contra la
evidencia real de la PR #1 ya mergeada, sin esperar a que esta corrección
tenga su propio merge — evita dejar una unidad ya integrada bloqueada por
un defecto del workflow de cierre.

Se agrega `docs/tecnica/post-merge-close-mode-fix.md` por transparencia
(mismo criterio que el precedente de `gi-platform-core`), pero no se
enlaza en `docs/tecnica/index.md` ni se crea `docs/usuario/`:
`Get-WorkUnitInfo -Mode Maintenance` (`scripts/workunit-lib.ps1`) resuelve
`TechnicalDoc/UserDoc/TechnicalIndex/UserIndex` como `$null` para este
modo, y `scripts/update-doc-indexes.ps1` sólo soporta `Mode Feature`. El
contrato vigente para Maintenance no exige ni provee ese enlace; forzarlo
con el script de Feature sería inconsistente con esa resolución explícita,
y no hay una interfaz oficial equivalente para Maintenance. No hay
contenido de cara al usuario final del producto CRM que justifique
`docs/usuario/`.
