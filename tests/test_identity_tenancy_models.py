from docbrain.db.base import Base, import_all_models


def test_identity_and_tenancy_tables_are_registered() -> None:
    import_all_models()

    assert {
        "users",
        "password_credentials",
        "organizations",
        "memberships",
    }.issubset(Base.metadata.tables)

