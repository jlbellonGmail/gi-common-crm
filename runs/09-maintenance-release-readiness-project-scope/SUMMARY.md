Estado: READY_FOR_PR
Versión: v0.1.0
Tipo: Maintenance
SDD: FULL
PR: pendiente de publicación
Merge: pendiente de HITL

## Objetivo

Desbloquear el release-readiness de v0.1.0 sin agregar funcionalidad CRM.

## Resultado

El gate ya no exige unidades transversales no adoptadas ni el tag histórico de
otro proyecto; valida todas las unidades declaradas en el ROADMAP.

## Cambios principales

Cambio acotado a `scripts/release-readiness.ps1` y evidencia/documentación de
Maintenance.

## Validación

Implementación revisada; la suite específica del gate y la suite CRM pasan.
La validación final del circuito y los checks de CI se ejecutan sobre el
commit final antes de publicar la PR.

## Decisiones

La unidad 18 queda fuera del alcance v0.1.0 y no se agrega artificialmente al
ROADMAP CRM.

## Incidencias

El gate original estaba acoplado a la historia del Template Starter.

## Detalle

No se modifican Core, Tenants, Persons, Supabase ni el dominio CRM.
