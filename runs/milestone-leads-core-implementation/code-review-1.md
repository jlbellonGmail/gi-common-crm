```yaml
status: approved
attempt: 1
feedback: []
```

# Code review — milestone-leads-core-implementation (ítems 02–06)

## Alcance revisado

Diff vigente sobre `develop` en la rama `milestone/leads-core-implementation`
(commit base `092b4df` + trabajo posterior sin commitear todavía): paquete
completo `gi_crm/` (`models.py`, `errors.py`, `ports.py`, `authorization.py`,
`service.py`, `memory.py`, `dbapi.py`, `api.py`, `adapters/core_http.py`,
`adapters/persons_http.py`, `http/app.py`, `http/schemas.py`,
`http/errors.py`), `supabase/migrations/20260921000100_crm.sql`,
`pyproject.toml`, la suite completa `tests_crm/` (16 archivos, 62 tests
en verde + 4 de Postgres real activados con `CRM_TEST_DATABASE_URL`), los
10 documentos nuevos (`docs/tecnica/`+`docs/usuario/` por ítem del
manifest) y sus índices, y las correcciones de `spec.md`/`plan.md`/
`tasks.md`.

## Verificación contra criterios de aceptación de `spec.md`

1. **Límites de módulos** — `tests_crm/test_contract_and_migration.py` y
   `test_no_vertical_coupling.py` verifican por AST/grep que `gi_crm` no
   importa `gi_platform_core`/`gi_persons` ni referencia ninguna vertical
   por nombre. Confirmado leyendo `gi_crm/ports.py`: sólo `Protocol`
   locales.
2. **Aislamiento multitenant** — `test_tenant_isolation.py` cubre las 9
   operaciones listadas en el criterio con pruebas negativas reales
   (`NotFoundError` cruzado), no sólo inspección de esquema.
3. **Autorización fail-safe** — `test_authorization.py` cubre denegación,
   `CoreUnavailableError` ante fallo de transporte, y respeto de
   `location_id`; `gi_crm/authorization.py::require()` nunca autoriza por
   defecto.
4. **Persons caído** — `test_service_duplicates.py` cubre
   `PersonsUnavailableError` sin bloquear el resto del ciclo de vida.
5. **Cardinalidad Person↔Lead** — `test_cardinality.py` y la migración SQL
   (verificado explícitamente en `test_contract_and_migration.py`: ausencia
   de `UNIQUE(organization_id, person_id)`).
6. **Máquina de estados** — `test_service_domain.py` cubre transiciones
   válidas/inválidas y `archived` desde cualquier estado no terminal.
7. **Concurrencia optimista** — `test_service_concurrency.py` cubre
   `update_lead`/`assign_lead`/`change_status`; el caso de `change_status`
   fue corregido durante esta unidad para aislar correctamente el conflicto
   de versión del error de transición inválida (ver `tasks.md`).
8. **Conversión/vertical** — `test_external_reference.py` cubre el
   `UNIQUE` compuesto y su rechazo explícito.
9. **Persistencia real** — verificado end-to-end contra Postgres efímero
   real (no simulado): RLS forzado confirmado sin bypass bajo el rol
   `authenticated` (no superusuario), migración aplicada una vez con
   semántica de despliegue real. Ver `test-report-1.md` para el detalle,
   incluido el bug real encontrado y corregido en `bump_lead_version`.
10. **Equivalencia de contrato** — `test_api_library.py`/
    `test_http_contract.py` comparan biblioteca y HTTP sobre el mismo
    estado.
11. **Modalidad HTTP con Core/Persons** — `adapters/core_http.py` y
    `adapters/persons_http.py` llevan docstring explícito de bloqueo
    end-to-end; `test_adapters_http.py` sólo prueba contra transporte
    simulado, consistente con lo declarado.
12. **Pruebas reales de persistencia disponibles** — confirmado: suite
    completa en verde sin dependencias externas, subconjunto de Postgres
    activable y verificado con evidencia real en `test-report-1.md`;
    `product-tests` del CI permanece intacto (fuera de alcance, ver
    `decision.md`).

## Otros hallazgos

- El fix de `gi_crm/http/app.py` (headers opcionales + traducción manual a
  400) preserva el contrato de error único (`CrmError`-shape) en vez de
  dejar que Pydantic devuelva un 422 genérico — coherente con el resto del
  diseño de errores del paquete.
- `bump_lead_version` como sentencia SQL literal propia (en vez de
  reutilizar `update_lead_fields`) es la corrección correcta: separa
  expresiones SQL de valores parametrizables sin reabrir la superficie de
  inyección en el resto del store.
- La corrección de nombres de documentación (`docs/tecnica/<docSlug>.md`
  por ítem, derivado de `Get-WorkUnitInfo -Mode Feature`, no un puñado de
  documentos libres por tema) quedó aplicada consistentemente en
  `spec.md`, `plan.md`, `tasks.md` y en los 10 archivos reales; los índices
  fueron actualizados vía el script canónico, sin edición manual.
- `.gitignore` fue extendido con `*.egg-info/`, `build/`, `dist/` para no
  commitear el artefacto de instalación editable generado localmente
  (`gi_common_crm.egg-info/`) — correcto, sin tocar reglas existentes.

## Veredicto

Sin hallazgos bloqueantes. La evidencia es proporcional a `FULL` (paquete
de producto completo, persistencia real, API pública en dos modalidades,
multitenancy). La unidad puede pasar a `ready-for-pr.ps1` una vez
commiteado el diff vigente.
