# Plan

1. Reproducir la causa raíz leyendo el log real del job fallido (`gh api
   .../actions/jobs/<id>/logs`) y el propio YAML, sin asumir el defecto.
2. Agregar `echo "branch=$head_ref"` y `echo "mode=Feature"` a la rama
   `elif` de `feature/NN-slug` sin versión, replicando exactamente el patrón
   ya usado en las otras tres ramas de la misma condición `if/elif`.
3. Validar sintaxis YAML (`yaml.safe_load`) y revisar manualmente que las
   cuatro ramas de la condición queden simétricas.
4. Ejecutar la suite completa del circuito (`pytest -q tests/`) para
   confirmar que no hay regresión en `test_close_feature_script.py` ni en
   pruebas relacionadas con workflows.
5. Producir evidencia SDD `FULL` (spec, plan, tasks, decisión, auditoría,
   test-report, code-review, documentación técnica y de usuario) porque
   ASSESS clasificó el cambio como `HIGH`/`FULL` al tocar
   `.github/workflows/`.
6. Publicar como rama `maintenance/T01-fix-post-merge-close-mode` (auxiliar,
   sin unidad canónica en ROADMAP — el propio `Resolve-MaintenanceScope` la
   reconoce como `auxiliary` por el token `close` en el slug) y abrir PR
   contra `develop`.
7. Una vez la PR tenga CI verde, completar el cierre pendiente de la Unidad
   01 ejecutando `close-feature.ps1` directamente (evidencia de PR #1 ya
   mergeada, sin repetir el merge) para no dejar `01-fundacion-diseno`
   bloqueada mientras esta corrección espera su propio HITL de merge.
