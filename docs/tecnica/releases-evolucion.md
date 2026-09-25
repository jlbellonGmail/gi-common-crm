# Releases y evolución determinísticos

F15 añade `scripts/release-readiness.ps1` como ruta canónica y read-only para
evaluar un candidato SemVer. El gate exige ejecutarse sobre `develop` limpio,
comprueba que el commit local/remoto coincide, que todas las unidades
declaradas por el proyecto están cerradas, que existe la auditoría de release,
que CI está verde sobre ese SHA, que la integridad pasa, que `main` es ancestro
(si existe) y que el tag candidato no existe. No exige unidades transversales
del Template que el proyecto no haya adoptado ni tags históricos de otro
proyecto. `-DryRun` hace explícito que no se crean PR, tag, release ni cambios
remotos; F15 no publica ninguna versión.

El flujo posterior es `develop` validado → PR contra `main` → gates → merge
humano → comprobación del commit final → tag anotado `vX.Y.Z` → release breve.
La primera release puede crear `main`; las siguientes sólo llegan por PR. Un
hotfix usa una rama desde el tag estable, pasa el mismo gate y se reincorpora
a `develop`; no se introduce GitFlow adicional. El run se ubica bajo
`runs/<version>/`, por lo que el mecanismo es reutilizable para `v2.1.0` y
`v3.0.0`.
