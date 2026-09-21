"""Adaptadores de transporte opcionales para gi_crm.ports.

Ninguno importa un cliente HTTP concreto: reciben un `transport` inyectado
por el host (callable `(method, url, *, json=None) -> dict`), para no
imponer una dependencia de runtime a quien sólo usa la biblioteca en
proceso. Ver ADR-C05 en docs/tecnica/arquitectura-crm.md: estos
adaptadores están documentados y probados sólo contra un transporte
simulado; ninguno se declara verificado end-to-end contra un servicio real
de Core/Persons, porque hoy ninguno de los dos expone HTTP.
"""
