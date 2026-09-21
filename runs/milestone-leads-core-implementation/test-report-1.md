---
status: approved
attempt: 1
feedback:
  - Sin hallazgos bloqueantes. Suite del circuito y del producto en verde;
    persistencia real verificada contra Postgres efímero, incluyendo un
    bug real detectado y corregido (`bump_lead_version`).
---

# Test report 1 — Milestone leads-core-implementation

## `pytest -q tests/` (circuito, sin cambios de alcance en este diff)

```
267 passed, 2 warnings in 351.53s (0:05:51)
```

Ejecución completa en verde, sin fallos ni tests salteados. En una corrida
previa durante este mismo Milestone, 3 tests (`test_ready_for_pr_reuses_
existing_pr_without_duplicate`, `test_start_reconciler_from_linked_
worktree`, `test_reconciler_never_removes_dirty_worktree`) fallaron en la
corrida completa pero pasaron en aislamiento al re-ejecutarlos solos —
comportamiento consistente con contención de recursos locales (Docker
Desktop/subprocesos Windows concurrentes), no con una regresión: el diff de
esta unidad es puramente aditivo (`gi_crm/`, `tests_crm/`,
`supabase/migrations/20260921000100_crm.sql`, `pyproject.toml`, `docs/`) y
no toca nada bajo `scripts/` ni `tests/`. Esta corrida final, sin
contención, confirma 267/267 en verde.

Las dos advertencias son `PytestUnhandledThreadExceptionWarning` por
`UnicodeDecodeError` en hilos lectores de subprocess (encoding `cp1252` de
la consola de Windows), preexistentes al circuito y no relacionadas con
`gi_crm`.

## `pytest -q tests_crm/` (producto, sin Postgres real)

```
62 passed, 4 skipped, 2 warnings in 6.57s
```

Los 4 tests salteados son `tests_crm/test_dbapi_postgres.py`, activados
sólo con `CRM_TEST_DATABASE_URL` definida (mismo patrón que
`PERSONS_TEST_DATABASE_URL` de `gi-common-persons`). El resto de la suite
(62 tests: dominio, máquina de estados, concurrencia optimista,
duplicados/Person linking, aislamiento multitenant, autorización
fail-safe, cardinalidad Person↔Lead, referencias externas/conversión, no
acoplamiento a verticales, contrato de puertos, `LeadsApi`, HTTP con
`TestClient`, adaptadores HTTP contra transporte simulado) corre íntegra
con `InMemoryLeadStore`/fakes, sin ninguna dependencia externa.

Advertencias: `PytestUnknownMarkWarning` por el marcador `integration` sin
registrar en el `pytest.ini` raíz (ese archivo pertenece al circuito,
`testpaths = tests`; no se modifica desde esta unidad) — cosmético, no
afecta el resultado. `DeprecationWarning` de `anyio`/`starlette` en
`TestClient`, ajeno a `gi_crm`.

## `pytest -q tests_crm/test_dbapi_postgres.py` con Postgres real (Docker)

Verificado localmente contra un contenedor efímero `postgres:16-alpine`
(no el proyecto Supabase compartido de Core/Persons):

```bash
docker run -d --name gi-crm-test-pg -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=crm_test -p 55433:5432 postgres:16-alpine
CRM_TEST_DATABASE_URL="postgresql://postgres:postgres@localhost:55433/crm_test" \
  pytest -q tests_crm/test_dbapi_postgres.py
docker rm -f gi-crm-test-pg
```

Resultado: **4 passed** (`test_insert_and_read_back_lead_under_own_tenant`,
`test_rls_blocks_reading_other_org_lead`,
`test_update_lead_fields_conflicts_on_stale_version`,
`test_duplicate_external_reference_is_rejected`).

En el proceso se encontraron y corrigieron, con evidencia real (no
simulada):

1. **Rol `authenticated` ausente en Postgres plano** (Supabase lo provee
   por defecto; un contenedor vanilla no) — corregido con un `create role
   if not exists` idempotente en el propio fixture de prueba, no en la
   migración de producto.
2. **Migración no idempotente por diseño** (`CREATE TRIGGER` no soporta
   `IF NOT EXISTS` en Postgres) — corregido reestructurando el fixture a
   alcance de módulo (una sola aplicación real de la migración por sesión
   de pruebas, igual que un despliegue real) con conexión propia y
   rollback por test.
3. **Bug real de producto**: `PostgresLeadStore.bump_lead_version`
   delegaba en el helper genérico `update_lead_fields(..., version=
   "version + 1")`, que parametriza todo valor como literal — el
   *superusuario* de Postgres además hace bypass silencioso de RLS
   incluso con `FORCE ROW LEVEL SECURITY`, así que sólo se detectó al
   correr como `authenticated` vía `set role`. Corregido en
   `gi_crm/dbapi.py` con una sentencia SQL literal propia
   (`set version = version + 1`) y sólo los valores de la cláusula
   `WHERE` como parámetros ligados. Ningún test in-memory podía detectar
   este bug: sólo se descubrió al ejercer Postgres real, lo que confirma
   el valor del criterio de aceptación #12 de `spec.md`.

Contenedor detenido y eliminado tras la verificación; se reconfirmó que la
suite se saltea limpiamente sin `CRM_TEST_DATABASE_URL` definida.

## Conclusión

Los 12 criterios de aceptación de `spec.md` tienen evidencia de prueba
automatizada correspondiente (ver mapeo test↔criterio en
`docs/tecnica/*.md` de cada ítem). Sin regresiones en el circuito. Veredicto:
`approved`, intento 1.
