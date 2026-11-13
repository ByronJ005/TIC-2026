import pytest
from fastapi import HTTPException
from src.models.user import DocumentType, User, UserRole
from src.repositories.user_repository import UserRepository
from src.schemas.cooperativa_schemas import (
    CooperativaCreate,
    CooperativaEstadoUpdate,
    CooperativaUpdate,
)
from src.services.cooperativa_service import (
    CODE_COOPERATIVA_INACTIVA,
    ERROR_COOPERATIVA_INACTIVE,
    ERROR_COOPERATIVA_NOT_FOUND,
    ERROR_NAME_DUPLICATED,
    ERROR_RUC_DUPLICATED,
    CooperativaService,
)
from src.services.logo_storage_service import (
    ERROR_LOGO_INVALID_TYPE,
    ERROR_LOGO_SIZE_EXCEEDED,
    JPEG_MAGIC,
    PNG_MAGIC,
    RIFF_MAGIC,
    WEBP_MAGIC,
    LogoStorageService,
)


@pytest.fixture
def admin_user(db_session):
    user_repo = UserRepository(db_session)
    return user_repo.create(
        User(
            document_type=DocumentType.CEDULA,
            document_number="1104609829",
            first_name="Admin",
            last_name="General",
            email="admin@terminal.ec",
            hashed_password="hash",
            is_active=True,
            roles=[UserRole.ADMIN_GENERAL],
        )
    )


def test_cooperativa_service_create_and_duplicates(db_session, admin_user):
    service = CooperativaService(db_session)

    # CP-46: Registrar cooperativa con datos válidos
    create_dto = CooperativaCreate(
        name="Cooperativa Loja",
        ruc="1104609829001",
        address="Terminal Terrestre Loja",
        phone="0987654321",
        email="info@cooploja.ec",
    )
    res = service.create_cooperativa(create_dto, current_user=admin_user)
    assert res.id is not None
    assert res.name == "Cooperativa Loja"
    assert res.is_active is True

    # CP-49: Validar unicidad del RUC
    dup_ruc_dto = CooperativaCreate(
        name="Otra Cooperativa",
        ruc="1104609829001",
    )
    with pytest.raises(HTTPException) as exc:
        service.create_cooperativa(dup_ruc_dto, current_user=admin_user)
    assert exc.value.status_code == 400
    assert ERROR_RUC_DUPLICATED in exc.value.detail

    # CP-50: Validar unicidad del Nombre (insensible a mayúsculas)
    dup_name_dto = CooperativaCreate(
        name="cooperativa loja",
        ruc="1790011216001",
    )
    with pytest.raises(HTTPException) as exc:
        service.create_cooperativa(dup_name_dto, current_user=admin_user)
    assert exc.value.status_code == 400
    assert ERROR_NAME_DUPLICATED in exc.value.detail


def test_cooperativa_service_update_and_immutability(db_session, admin_user):
    service = CooperativaService(db_session)
    created = service.create_cooperativa(
        CooperativaCreate(
            name="Coop Cariamanga",
            ruc="1104609829001",
            address="Oficina 1",
        ),
        current_user=admin_user,
    )

    # CP-55: Actualizar información de cooperativa
    update_dto = CooperativaUpdate(
        name="Coop Unión Cariamanga",
        address="Oficina 2 Modificada",
        phone="0999999999",
    )
    updated = service.update_cooperativa(created.id, update_dto, current_user=admin_user)
    assert updated.name == "Coop Unión Cariamanga"
    assert updated.address == "Oficina 2 Modificada"
    assert updated.phone == "0999999999"
    # CP-57: RUC remains inmutable
    assert updated.ruc == "1104609829001"


def test_cooperativa_service_deactivate_and_concurrency(db_session, admin_user):
    service = CooperativaService(db_session)
    coop = service.create_cooperativa(
        CooperativaCreate(name="Coop Sur", ruc="1104609829001"),
        current_user=admin_user,
    )

    # CP-58: Desactivar cooperativa (baja lógica)
    deactivated = service.update_estado(
        coop.id, CooperativaEstadoUpdate(is_active=False), current_user=admin_user
    )
    assert deactivated.is_active is False

    # CP-60: Intentar editar una cooperativa desactivada desde otra sesión
    with pytest.raises(HTTPException) as exc:
        service.update_cooperativa(
            coop.id,
            CooperativaUpdate(address="Nueva Dirección"),
            current_user=admin_user,
        )
    assert exc.value.status_code == 409
    assert exc.value.detail["code"] == CODE_COOPERATIVA_INACTIVA
    assert exc.value.detail["message"] == ERROR_COOPERATIVA_INACTIVE

    # CP-59: Reactivar cooperativa
    activated = service.update_estado(
        coop.id, CooperativaEstadoUpdate(is_active=True), current_user=admin_user
    )
    assert activated.is_active is True

    # After activation, editing is allowed again
    res = service.update_cooperativa(
        coop.id,
        CooperativaUpdate(address="Dirección Reactivada"),
        current_user=admin_user,
    )
    assert res.address == "Dirección Reactivada"


def test_logo_storage_service(tmp_path):
    storage = LogoStorageService(
        upload_dir=str(tmp_path),
        max_size_bytes=1024 * 1024,  # 1 MB
    )

    # 1. Valid PNG
    valid_png_bytes = PNG_MAGIC + b"\x00" * 50
    url = storage.save_logo_file(valid_png_bytes)
    assert url.startswith("/static/logos/")
    assert url.endswith(".png")

    # 2. Valid JPG
    valid_jpg_bytes = JPEG_MAGIC + b"\x00" * 50
    url_jpg = storage.save_logo_file(valid_jpg_bytes, previous_logo_url=url)
    assert url_jpg.endswith(".jpg")

    # 3. Valid WEBP
    valid_webp_bytes = RIFF_MAGIC + b"\x00\x00\x00\x00" + WEBP_MAGIC + b"\x00" * 50
    url_webp = storage.save_logo_file(valid_webp_bytes)
    assert url_webp.endswith(".webp")

    # 4. Invalid file type (e.g. text/exe/pdf)
    fake_bytes = b"NOT AN IMAGE FILE AT ALL"
    with pytest.raises(HTTPException) as exc:
        storage.save_logo_file(fake_bytes)
    assert exc.value.status_code == 400
    assert ERROR_LOGO_INVALID_TYPE in exc.value.detail

    # 5. Exceeded size
    huge_bytes = PNG_MAGIC + b"\x00" * (1024 * 1024 + 1)
    with pytest.raises(HTTPException) as exc:
        storage.save_logo_file(huge_bytes)
    assert exc.value.status_code == 400
    assert ERROR_LOGO_SIZE_EXCEEDED in exc.value.detail

