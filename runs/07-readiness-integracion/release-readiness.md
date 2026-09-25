# Evidencia: `scripts/release-readiness.ps1` (preflight read-only)

Ejecución real (no simulada), rama `feature/07-readiness-integracion`,
worktree `C:\Proyectos\worktrees\07-readiness-integracion`:

```
pwsh -NoProfile -ExecutionPolicy Bypass -File ./scripts/release-readiness.ps1 -Version v0.1.0
```

Salida real:

```
Write-Error: C:\Proyectos\worktrees\07-readiness-integracion\scripts\release-readiness.ps1:100
RELEASE REJECTED: ROADMAP incompleto: falta '18-status-observabilidad'.
```

Código de salida: `1` (rechazo).

## Por qué este rechazo es el resultado correcto, no un fallo de esta unidad

`scripts/release-readiness.ps1` es un artefacto heredado tal cual del
bootstrap de `template-starter` (snapshot inicial de este repositorio,
commit `92e50ad`). Su lista de ítems obligatorios de `ROADMAP.md`
(`18-status-observabilidad`, `19-unidades-paralelizacion`,
`20-releases-evolucion`, `21-validacion-integral-v2`,
`22-auditoria-release-v2`) y su ancla histórica de tag inmutable
(`v1.1.0` con SHA `d13ffcf3...`) son **específicos del propio historial de
`template-starter`**, no de `gi-common-crm`. Ninguno de esos ítems existe
en el `ROADMAP.md` de este repositorio (que tiene su propio backlog:
`01-fundacion-diseno`, el Milestone `02-06-leads-core-implementation`,
`07-readiness-integracion`, `08-persistencia-supabase-real`), así que el
script rechaza correctamente en el primer chequeo que no puede satisfacer.

Esto es evidencia real de que el mecanismo de preflight funciona
(read-only, no publica ni mergea nada — falla temprano y explícito, sin
falsos positivos), pero también confirma un hallazgo: **antes de que
`v0.1.0` de `gi-common-crm` pueda pasar por este gate, el script necesita
su propia parametrización** (lista de ítems de readiness reales de este
proyecto y, si corresponde, su propio ancla de tag histórico) — una
decisión de gobernanza de release específica de este proyecto, no
inventable desde esta unidad sin exceder su alcance declarado en
`spec.md` ("Explícitamente fuera de alcance": "Cualquier release, tag o
publicación de `v0.1.0`").

## Estado

Queda registrado como pendiente de decisión humana (no bloqueante para el
alcance de `07-readiness-integracion`, que sólo exige "ejecutar el script
y documentar su salida real" — cumplido). Ver `STATUS.md` para el
seguimiento de este pendiente hacia el HITL de release de `v0.1.0`.
