```yaml
status: approved
attempt: 1
scope: T01-fix-post-merge-close-mode
head: HEAD
base: develop
```

# Code review

## Diff revisado

- `.github/workflows/post-merge-close-feature.yml`: se agregaron
  `echo "branch=$head_ref" >> "$GITHUB_OUTPUT"` y
  `echo "mode=Feature" >> "$GITHUB_OUTPUT"` a la rama `elif` que reconoce
  `feature/NN-slug` (interfaz legacy sin versión), igualándola a las
  otras tres ramas de la misma condición.
- `docs/tecnica/post-merge-close-mode-fix.md`: nota técnica que documenta
  el defecto real, la evidencia de log que lo confirma y la incidencia
  relacionada (rama `maintenance/TNN-slug` sin versión) que queda fuera de
  alcance.

## Verificación

- Sintaxis YAML validada (`yaml.safe_load`).
- Las cuatro ramas de la condición (`feature` con versión, `feature` sin
  versión, `milestone`, `maintenance` con versión) emiten ahora,
  simétricamente, `version`, `slug`, `branch` y `mode`.
- El cambio no toca `close-feature.ps1`, `guard-develop-branch.yml` ni
  ninguna política de protección de `develop`.
- No hay cambios de código de producto: es un fix acotado al circuito de
  gobernanza, consistente con el alcance declarado en `spec.md`/`plan.md`.
- Suite completa del circuito (`pytest -q tests/`) corrida en este
  worktree: 267 passed, 2 warnings no relacionadas (advertencias de hilo
  por decodificación `cp1252` en `test_agentic_evals.py`, preexistentes y
  no vinculadas a este cambio). Ver `test-report-1.md`.

## Conclusión

El diff es mínimo, proporcional al defecto real evidenciado en logs de
GitHub Actions, y no introduce regresiones. Aprobado.
