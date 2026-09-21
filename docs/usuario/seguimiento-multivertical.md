# Ítem 06 — Seguimiento multivertical

## Para qué sirve

Deja rastro de todo lo que pasa con un Lead (notas, llamadas, cambios de
responsable) y permite "convertirlo" en el registro real de la vertical
(por ejemplo, un paciente o un cliente) sin que CRM sepa qué vertical es
ni tenga que conocer su modelo de datos.

## Cómo registrar seguimiento

```python
service.add_activity(context, lead.lead_id, kind="call", notes="Primer contacto telefónico")
service.assign_lead(context, lead.lead_id, lead.version, "usuario-responsable")
```

## Cómo convertir un Lead ganado

```python
# El Lead debe estar en estado "won" antes de convertir.
referencia = service.convert_lead(
    context, lead.lead_id,
    vertical_code="dental", external_type="patient", external_id="12345",
)
```

Cada vertical usa su propio `vertical_code` (por ejemplo `"dental"` o
`"law"`); el mismo `external_id` puede repetirse en verticales distintas
sin conflicto, pero no dos veces dentro de la misma combinación
`vertical_code` + `external_type` + `external_id`.
