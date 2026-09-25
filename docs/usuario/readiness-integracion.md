# Readiness e integración: CI real de product-tests

## Para qué sirve

Hasta esta feature, el check `product-tests` de cualquier PR o push a
`develop`/`main` siempre pasaba en verde sin verificar nada real: era un
placeholder heredado del template, porque en ese momento `gi-common-crm`
todavía no tenía stack de producto definido. Ahora `product-tests` corre
de verdad la suite de tests de `gi_crm` (`tests_crm/`) contra un Postgres
real, igual que hacías localmente con `CRM_TEST_DATABASE_URL` apuntando a
un contenedor Docker.

## Qué vas a ver en "Checks" de una PR o en la pestaña Actions

- **`circuit-tests`**: sin cambios, corre `pytest -v` sobre `tests/` (los
  tests del propio circuito agéntico).
- **`product-tests`**: levanta un Postgres 16 como servicio del job,
  instala `gi_crm` con los extras `[http,postgres]` más
  `requirements-crm-dev.txt`, y corre `pytest -v tests_crm/` contra ese
  Postgres real. Ya no es un placeholder: si algo en `gi_crm` rompe
  (dominio, persistencia o API), este check queda rojo y bloquea el
  merge, igual que `circuit-tests`.
- **`local-reconciler-tests`**: sin cambios.

Los tres son obligatorios y corren en paralelo.

## Cómo correr la misma suite en tu máquina antes de abrir una PR

1. Levantá un Postgres local (por ejemplo con Docker):
   ```
   docker run --rm -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=crm_test -p 5432:5432 postgres:16-alpine
   ```
2. Instalá `gi_crm` con los extras necesarios y las dependencias de test:
   ```
   pip install -e ".[http,postgres]"
   pip install -r requirements-crm-dev.txt
   ```
3. Corré la suite apuntando al Postgres levantado:
   ```
   CRM_TEST_DATABASE_URL=postgresql://postgres:postgres@localhost:5432/crm_test pytest -v tests_crm/
   ```

Es exactamente lo que hace el job `product-tests` en CI — si te pasa en
verde localmente con estos pasos, tenés una señal confiable de que el
check también va a pasar en la PR.

## Si no tenés Docker a mano

Parte de `tests_crm/` (la que usa `InMemoryLeadStore` y no depende de
Postgres) corre igual sin la variable `CRM_TEST_DATABASE_URL` seteada;
los tests que sí necesitan Postgres real se saltan localmente en ese
caso, pero **no** se saltan en CI, donde el servicio de Postgres siempre
está disponible.

## Relación con el placeholder anterior

`docs/tecnica/ci-wiring-product-tests.md` documenta la feature del
template que introdujo el placeholder y por qué, en ese momento, era
correcto dejarlo vacío. Esa página queda como registro histórico; el
comportamiento real y vigente de `product-tests` en este repositorio es
el descrito acá y en `docs/tecnica/readiness-integracion.md`.
