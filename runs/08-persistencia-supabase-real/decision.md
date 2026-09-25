# Decisión

CRM usa `tenant_id uuid` porque es el contrato público vigente de Core y
Tenants. Persons todavía expone `organization_id` en su servicio remoto; esa
forma queda confinada al adaptador de compatibilidad y nunca aparece en el
modelo, persistencia o API pública CRM. No se agrega FK a Persons por ser un
servicio común separado y por la incompatibilidad histórica de su identificador.
