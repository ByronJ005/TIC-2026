import sys
sys.path.insert(0, ".")

from src.core.database import SessionLocal
from src.core.security import hash_password
from src.models.user import DocumentType, User, UserRole
from src.repositories.user_repository import UserRepository


def generate_cedula(prefix_province: str, sequence: int) -> str:
    """Generates a valid Ecuadorian cedula using modulo-10 algorithm."""
    base = f"{prefix_province}{sequence:07d}"
    coefficients = [2, 1, 2, 1, 2, 1, 2, 1, 2]
    total = 0
    for digit_char, coef in zip(base, coefficients):
        val = int(digit_char) * coef
        if val >= 10:
            val -= 9
        total += val
    check_digit = (10 - (total % 10)) % 10
    return f"{base}{check_digit}"


def seed():
    db = SessionLocal()
    user_repo = UserRepository(db)

    print("--- 1. Actualizando usuario existente byronajc50201@hotmail.com ---")
    byron = user_repo.get_by_email("byronajc50201@hotmail.com")
    if byron:
        current_roles = list(byron.roles)
        if UserRole.ADMIN_GENERAL not in current_roles:
            current_roles.append(UserRole.ADMIN_GENERAL)
        if UserRole.PASAJERO not in current_roles:
            current_roles.append(UserRole.PASAJERO)
        byron.roles = current_roles
        db.commit()
        db.refresh(byron)
        print(f"Usuario byronajc50201@hotmail.com actualizado con roles: {[r.value for r in byron.roles]}")
    else:
        # Si no existía, lo creamos directamente
        print("El usuario byronajc50201@hotmail.com no existía en la DB. Creándolo con ADMIN_GENERAL...")
        cedula_byron = generate_cedula("11", 46098)
        new_byron = User(
            document_type=DocumentType.CEDULA,
            document_number=cedula_byron,
            first_name="Byron",
            last_name="AJC",
            email="byronajc50201@hotmail.com",
            hashed_password=hash_password("Password123"),
            is_active=True,
        )
        new_byron.roles = [UserRole.ADMIN_GENERAL, UserRole.PASAJERO]
        user_repo.create(new_byron)
        print(f"Usuario byronajc50201@hotmail.com creado con roles: {[r.value for r in new_byron.roles]}")

    print("\n--- 2. Creando los 6 usuarios solicitados ---")
    users_to_create = [
        {
            "num": 1,
            "first_name": "Admin",
            "last_name": "Cooperativa",
            "email": "admin.coop@terminal.com",
            "password": "Password123",
            "roles": [UserRole.ADMIN_COOPERATIVA, UserRole.PASAJERO],
        },
        {
            "num": 2,
            "first_name": "Secretaria",
            "last_name": "Cooperativa",
            "email": "secretaria.coop@terminal.com",
            "password": "Password124",
            "roles": [UserRole.SECRETARIA_COOPERATIVA, UserRole.PASAJERO],
        },
        {
            "num": 3,
            "first_name": "Pasajero",
            "last_name": "Prueba",
            "email": "pasajero.test@terminal.com",
            "password": "Password125",
            "roles": [UserRole.PASAJERO],
        },
        {
            "num": 4,
            "first_name": "Admin",
            "last_name": "Pasajero",
            "email": "admin.pasajero@terminal.com",
            "password": "Password126",
            "roles": [UserRole.ADMIN_COOPERATIVA, UserRole.PASAJERO],
        },
        {
            "num": 5,
            "first_name": "Carlos",
            "last_name": "Suing",
            "email": "carlos.suing@terminal.com",
            "password": "Password127",
            "roles": [UserRole.PASAJERO],
        },
        {
            "num": 6,
            "first_name": "Maria",
            "last_name": "Secretaria",
            "email": "maria.secretaria@terminal.com",
            "password": "Password128",
            "roles": [UserRole.SECRETARIA_COOPERATIVA, UserRole.PASAJERO],
        },
    ]

    for item in users_to_create:
        email = item["email"]
        existing = user_repo.get_by_email(email)
        if existing:
            existing.first_name = item["first_name"]
            existing.last_name = item["last_name"]
            existing.hashed_password = hash_password(item["password"])
            existing.is_active = True
            existing.roles = item["roles"]
            db.commit()
            db.refresh(existing)
            print(f"[{item['num']}] Usuario {email} ya existía -> actualizado con roles {[r.value for r in existing.roles]}")
        else:
            cedula = generate_cedula("17", 10000 + item["num"])
            new_u = User(
                document_type=DocumentType.CEDULA,
                document_number=cedula,
                first_name=item["first_name"],
                last_name=item["last_name"],
                email=email,
                hashed_password=hash_password(item["password"]),
                is_active=True,
            )
            new_u.roles = item["roles"]
            created = user_repo.create(new_u)
            print(f"[{item['num']}] Usuario creado: {email} | Cédula: {cedula} | Roles: {[r.value for r in created.roles]}")

    db.close()
    print("\n¡Seed completado con éxito!")


if __name__ == "__main__":
    seed()
