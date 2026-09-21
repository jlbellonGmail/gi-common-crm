# Ítem 06 — Seguimiento multivertical (actividad, asignación, conversión)

Ver [Arquitectura de CRM](arquitectura-crm.md) (ADR-C01) para por qué CRM
no conoce ninguna vertical por nombre. Este documento describe la
implementación real de seguimiento comercial y conversión.

## Actividad

`add_activity(kind, notes)` acepta `kind` en `{"note", "call", "email",
"meeting", "other"}` (`ACTIVITY_KINDS`); cualquier otro valor lanza
`ValidationError`. Cada actividad es append-only (`list_activities`,
orden cronológico) y requiere que el Lead exista en la organización del
llamador.

## Asignación y reasignación

`assign_lead`/`reassign_lead` (mismo método) cambian `owner_user_id` bajo
concurrencia optimista y registran un `LeadAssignmentEvent` append-only
(`from_user_id`, `to_user_id`, actor, fecha) — `list_assignments` expone
el historial completo, nunca sólo el responsable actual.

## Referencias externas de vertical y conversión

`LeadExternalReference` es la única forma en que CRM referencia una
entidad creada por una vertical al convertir el Lead (paciente, cliente,
expediente, oportunidad, ...): `vertical_code` + `external_type` +
`external_id`, con `UNIQUE(organization_id, vertical_code, external_type,
external_id)` — la misma combinación no puede registrarse dos veces
(`DuplicateExternalReferenceError`), pero el mismo `external_id` es válido
en dos verticales distintas (no hay colisión entre, por ejemplo, un
`patient` de una vertical y un `client` de otra).

`convert_lead(vertical_code, external_type, external_id)` exige
`status == "won"` (`InvalidTransitionError` en cualquier otro estado) e
inserta la referencia directamente — no delega en
`add_external_reference` para no exigir dos permisos (`crm:lead:convert:
write` y `crm:lead:external-reference:write`) para una sola acción
comercial.

Ninguna vertical concreta (Dental, Law, GI-OT, ...) aparece por nombre en
`gi_crm`: `tests_crm/test_no_vertical_coupling.py` lo verifica
estáticamente sobre el código fuente y la migración SQL.
