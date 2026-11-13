import pytest
from src.models.cooperativa import Cooperativa
from src.repositories.cooperativa_repository import CooperativaRepository


def test_cooperativa_repository_crud(db_session):
    repo = CooperativaRepository(db_session)

    # 1. Create
    coop = Cooperativa(
        name="Cooperativa Loja",
        ruc="1104609829001",
        address="Av. Isidro Ayora y Terminal",
        phone="0987654321",
        email="contacto@cooploja.ec",
        logo_url="https://example.com/logo.png",
        is_active=True,
    )
    created = repo.create(coop)
    assert created.id is not None
    assert created.name == "Cooperativa Loja"
    assert created.ruc == "1104609829001"

    # 2. Get by ID
    fetched = repo.get_by_id(created.id)
    assert fetched is not None
    assert fetched.id == created.id

    # 3. Get by RUC
    by_ruc = repo.get_by_ruc("1104609829001")
    assert by_ruc is not None
    assert by_ruc.id == created.id

    # 4. Get by lower name (case insensitive)
    by_lower = repo.get_by_lower_name("COOPERATIVA LOJA")
    assert by_lower is not None
    assert by_lower.id == created.id

    by_lower_missing = repo.get_by_lower_name("Cooperativa No Existe")
    assert by_lower_missing is None

    # 5. Update
    created.address = "Nueva Dirección 123"
    updated = repo.update(created)
    assert updated.address == "Nueva Dirección 123"

    # 6. List with search and filter
    coop2 = Cooperativa(
        name="Unión Cariamanga",
        ruc="1790011216001",
        is_active=False,
    )
    repo.create(coop2)

    # All
    items, total = repo.list_cooperativas()
    assert total == 2
    assert len(items) == 2

    # Active only
    items_active, total_active = repo.list_cooperativas(is_active=True)
    assert total_active == 1
    assert items_active[0].name == "Cooperativa Loja"

    # Search by name
    items_search, total_search = repo.list_cooperativas(search="Cariamanga")
    assert total_search == 1
    assert items_search[0].name == "Unión Cariamanga"

    # Search by RUC
    items_ruc_search, total_ruc_search = repo.list_cooperativas(search="1104609829")
    assert total_ruc_search == 1
    assert items_ruc_search[0].name == "Cooperativa Loja"

