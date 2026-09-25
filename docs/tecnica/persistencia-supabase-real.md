# Persistencia CRM en Supabase

La persistencia CRM reside en el schema `crm` del proyecto de desarrollo
Supabase `gi-dev`. Todas las tablas usan `tenant_id uuid` como frontera y
claves compuestas tenant-aware. `person_id` es una referencia lógica al
servicio Persons; no se crea una FK entre servicios comunes.

La migración `supabase/migrations/20260921000100_crm.sql` crea tablas, índices,
triggers append-only, grants mínimos y RLS forzado. Cada transacción DB-API
debe fijar `app.tenant_id` con `SET LOCAL`; las policies rechazan acceso de
otro tenant. La compatibilidad `organization_id` de Persons queda aislada en
`gi_crm.adapters.persons_http`.
