Estado: READY_FOR_PR
Versión: v2.0.1
Tipo: Feature
SDD: FULL
PR: pendiente
Merge: pendiente

## Objetivo

Completar persistencia real de CRM en Supabase development y reconciliar el
dominio con el contrato canónico `tenant_id`.

## Resultado

Migración aplicada en `gi-dev` (ref `gletzbwuvmwjkmoufmyj`) exclusivamente bajo
`crm.*`, con siete tablas CRM y aislamiento multitenant verificable.

## Cambios principales

Modelos, puertos, servicio, DB-API, HTTP, autorización y adaptadores usan
`tenant_id uuid`. Persons conserva `organization_id` sólo en su boundary legacy.

## Validación

`pytest -q`: 268 passed. Supabase real: PostgreSQL 17.6, RLS enabled/forced,
policies por tabla, round-trip DB-API y lectura cross-tenant bloqueada.

## Decisiones

No se agrega FK a Persons por ser un servicio común separado y legacy en su
identificador. Core/Tenants no fueron modificados.

## Incidencias

La suite DB-API pytest no se conecta automáticamente al Supabase compartido;
su equivalente real se ejecutó con conexión directa autenticada, sin secretos.

## Detalle

La migración usa PK/FK compuestas por tenant, índices, triggers append-only,
policies RLS y grants mínimos. La rama base es `develop` posterior al merge de
la Unidad 07.
