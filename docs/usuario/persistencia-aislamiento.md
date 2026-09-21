# Ítem 04 — Persistencia y aislamiento

## Para qué sirve

Guarda los Leads de forma real y separada por organización: los datos de
una organización nunca son visibles ni modificables desde otra, ni
siquiera por error de código, porque la base de datos misma lo impide
(Row-Level Security forzado), no sólo el código de la aplicación.

## Cómo probarlo localmente con Postgres real

```bash
docker run -d --name gi-crm-test-pg -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=crm_test -p 55433:5432 postgres:16-alpine
CRM_TEST_DATABASE_URL="postgresql://postgres:postgres@localhost:55433/crm_test" \
  pytest -q tests_crm/test_dbapi_postgres.py
docker rm -f gi-crm-test-pg
```

Sin `CRM_TEST_DATABASE_URL` definida, esta prueba se salta automáticamente
(no falla el resto de la suite). No se ejecuta contra el proyecto Supabase
compartido de Core/Persons: eso es una decisión aparte, pendiente de
autorización humana (`08-persistencia-supabase-real` en `ROADMAP.md`).

## Cómo aplicar el esquema

El archivo `supabase/migrations/20260921000100_crm.sql` es SQL estándar:
se aplica con cualquier cliente de Postgres o con el flujo de migraciones
de Supabase, igual que las migraciones ya existentes de Core y Persons.
