```yaml
status: approved
attempt: 1
scope: T01-fix-post-merge-close-mode
```

# Reporte de tests

## Suite del circuito (`pytest -q tests/`)

Dos corridas reales en el worktree `T01-fix-post-merge-close-mode`
(commit `d4e0943` + fix sin commitear al momento de correrlas):

1. Primera corrida (`Out-File`, background): `267 passed, 2 warnings in
   412.33s (0:06:52)`. El runner de background reportó
   "failed with exit code 1", pero el log no contiene ningún `FAILED` ni
   error de test — sólo el resumen de warnings conocido.
2. Segunda corrida de confirmación (`Tee-Object -Variable`, capturando
   `$LASTEXITCODE` explícitamente vía `exit $LASTEXITCODE`): `267 passed,
   2 warnings in 419.16s (0:06:59)`, **exit code 0** confirmado.

Conclusión: el "exit code 1" reportado por el primer intento fue un
artefacto de cómo `pwsh -Command "... | Out-File ..."` propaga (o no)
`$LASTEXITCODE` del comando nativo cuando es el elemento de un pipeline,
no una falla real de la suite. La segunda corrida, con captura explícita
del código de salida, confirma `exit 0` con el mismo resultado de tests
(267 passed) que la primera. No hay regresión.

Los 2 warnings (`PytestUnhandledThreadExceptionWarning` por
`UnicodeDecodeError` en `cp1252` dentro de `test_agentic_evals.py`) son
preexistentes y cosméticos: ya estaban documentados en `STATUS.md` de la
unidad `01-fundacion-diseno` (`267 passed, 2 warnings in 394.60s`) antes
de este cambio, y no están relacionados con el workflow corregido.

## Alcance no cubierto por pytest

El fix modifica un workflow de GitHub Actions
(`post-merge-close-feature.yml`), que no corre en `pytest -q tests/`
localmente. La validación de esta unidad específica es:

- Sintaxis YAML válida (`yaml.safe_load`).
- Simetría de las cuatro ramas de la condición de derivación de
  slug/modo (inspección manual del archivo).
- La corrección será validada en producción real la próxima vez que el
  workflow se dispare sobre una rama `feature/NN-slug` sin versión — la
  propia PR de esta unidad, al mergear a `develop` desde
  `maintenance/T01-fix-post-merge-close-mode`, no ejercita esa rama de la
  condición (es `maintenance/`, sin versión, que cae en el `else`/`skip`
  documentado como incidencia fuera de alcance). El primer caso real que
  sí la ejercitará es el cierre pendiente de `01-fundacion-diseno`,
  hecho mediante invocación directa de `close-feature.ps1` (no a través
  del workflow) precisamente para no depender de un ciclo adicional de
  merge-post-merge antes de cerrar esa unidad.
