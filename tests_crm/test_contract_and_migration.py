"""Límites de módulos (criterio de aceptación #1) y forma real de la migración."""
import ast
from pathlib import Path


def test_no_vertical_or_private_core_persons_imports():
    for path in Path("gi_crm").rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        imports = [node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))]
        names = [alias.name for node in imports for alias in getattr(node, "names", [])]
        modules = [node.module or "" for node in imports if isinstance(node, ast.ImportFrom)]
        all_names = names + modules
        assert not any(name.lower() in {"dental", "law", "gi_ot", "clinicadental"} for name in all_names)
        assert not any(name.split(".")[0] in {"gi_platform_core", "gi_persons"} for name in all_names)


def test_migration_has_crm_schema_tenant_keys_and_forced_rls():
    sql = Path("supabase/migrations/20260921000100_crm.sql").read_text(encoding="utf-8").lower()
    for table in [
        "lead_source", "lead", "lead_status_event", "lead_activity",
        "lead_assignment_event", "lead_external_reference", "lead_audit",
    ]:
        assert f"create table crm.{table}" in sql
    assert "unique (tenant_id, vertical_code, external_type, external_id)" in sql
    assert "force row level security" in sql
    assert "current_setting(''app.tenant_id''" in sql
    # Cardinalidad Person<->Lead: sin UNIQUE sobre person_id (ADR-C01).
    assert "unique (tenant_id, person_id)" not in sql
