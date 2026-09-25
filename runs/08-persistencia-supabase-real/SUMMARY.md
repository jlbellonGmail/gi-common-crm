status: approved
attempt: 1
feedback: []

# Unidad 08 — persistencia Supabase real

Se migró el dominio CRM al contrato canónico `tenant_id uuid`, se aplicó la
migración exclusivamente en el schema `crm` del proyecto Supabase `gi-dev`
(ref `gletzbwuvmwjkmoufmyj`), y se verificaron tablas, claves, RLS, policies y
aislamiento positivo/negativo entre tenants.
