# Spec

- Persistencia PostgreSQL real para Leads CRM.
- `tenant_id uuid` es la frontera canónica; `person_id` es opcional y no se
  crea una FK entre servicios comunes.
- RLS forzado y policies de lectura/escritura basadas en `app.tenant_id`.
- No se modifican schemas `core`, `tenants` ni `persons`.
