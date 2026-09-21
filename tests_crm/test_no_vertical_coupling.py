"""gi_crm no conoce ninguna vertical concreta (spec.md #1): sólo strings genéricos como vertical_code."""
from pathlib import Path

FORBIDDEN = {"dental", "law", "gi-ot", "gi_ot", "clinicadental"}


def test_no_vertical_names_anywhere_in_gi_crm_source():
    for path in Path("gi_crm").rglob("*.py"):
        text = path.read_text(encoding="utf-8").lower()
        for word in FORBIDDEN:
            assert word not in text, f"{path} references vertical '{word}'"


def test_no_vertical_names_in_migration():
    text = Path("supabase/migrations/20260921000100_crm.sql").read_text(encoding="utf-8").lower()
    for word in FORBIDDEN:
        assert word not in text
