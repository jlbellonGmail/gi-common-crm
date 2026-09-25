status: approved
attempt: 1
feedback: []

# Code review

El diff usa `tenant_id` en modelos, servicios, puertos, DB-API, HTTP y
autorización. La compatibilidad legacy con Persons está aislada en su
adaptador. No hay dependencias hacia verticales.
