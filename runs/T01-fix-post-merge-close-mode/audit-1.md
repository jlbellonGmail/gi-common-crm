```yaml
status: approved
attempt: 1
scope: T01-fix-post-merge-close-mode
```

# Auditoría de planificación

Se revisó `spec.md`/`plan.md` contra el log real del job fallido
(`run 35556510071`, job `106201062447`) y el YAML vigente. El defecto
identificado (rama `feature/NN-slug` sin `mode=`/`branch=`) es
verificable directamente en el archivo y coincide exactamente con el
mensaje de error observado (`ValidateSet` sobre `-Mode ''`). El alcance
propuesto es mínimo y proporcional: dos líneas `echo` agregadas, sin tocar
`close-feature.ps1` ni el guard de `develop`. La exclusión explícita del
gap análogo en `maintenance/TNN-slug` sin versión es razonable — no causó
ningún fallo real y se documenta como incidencia en vez de expandir el
alcance sin evidencia de necesidad inmediata.

La planificación puede avanzar a build/tests.
