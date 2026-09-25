```yaml
status: approved
attempt: 1
feedback: []
```

# QA

`pytest -q tests_crm`: 63 passed, 4 skipped (los skips son los tests DB-API
que requieren `CRM_TEST_DATABASE_URL`; la verificación equivalente contra
Supabase real se ejecutó separadamente con conexión autenticada y RLS).

Verificación real: PostgreSQL 17.6, schema `crm`, siete tablas con `tenant_id
uuid`, RLS enabled/forced, tres policies por tabla, y lectura cross-tenant
bloqueada (tenant A: 1, tenant B: 0).
