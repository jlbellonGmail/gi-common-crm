# Persistencia CRM

El host debe proporcionar una conexión PostgreSQL al adaptador DB-API y un
contexto confiable con `tenant_id`. La API HTTP recibe `X-GI-Tenant-Id` y
`X-GI-User-Id` desde el host autenticado; no debe aceptar esos valores como
identidad autoafirmada del cliente final.
