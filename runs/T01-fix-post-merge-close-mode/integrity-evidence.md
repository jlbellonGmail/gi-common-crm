status: PASS
scope: T01-fix-post-merge-close-mode

Salida real de `pwsh ./scripts/check-integrity.ps1` en el worktree
`T01-fix-post-merge-close-mode` (branch `maintenance/T01-fix-post-merge-
close-mode`, base `develop` en `d4e0943`):

```
WARNING STATUS:AUTO stale: snapshot=feature/01-fundacion-diseno/ actual=maintenance/T01-fix-post-merge-close-mode/d4e0943f5be61fd19176b13c2ccdd68dda653f89
PASS integridad global ROADMAP/runs/SUMMARY/Git/STATUS
```

El único `WARNING` es esperado: el bloque `STATUS:AUTO` de `STATUS.md`
todavía referencia la rama/HEAD de `01-fundacion-diseno` (última vez que
se corrió `update-status.ps1`), no un error de integridad. `PASS` final
confirma consistencia de ROADMAP/runs/SUMMARY/Git.

- `pytest -q tests/`: `267 passed, 2 warnings` en dos corridas
  independientes (ver `test-report-1.md`), sin `FAILED` ni `ERROR`.
