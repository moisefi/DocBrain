from docbrain.db.base import NAMING_CONVENTION, Base


def test_database_metadata_uses_naming_convention() -> None:
    assert Base.metadata.naming_convention == NAMING_CONVENTION
