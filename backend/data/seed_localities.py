"""Carga el catálogo inicial: python -m data.seed_localities (desde backend)."""

import json
import unicodedata
from pathlib import Path

from sqlalchemy.orm import Session
from src.core.database import engine
from src.repositories.locality_repository import LocalityRepository
from src.schemas.locality_schemas import LocalityCreate
from src.services.locality_service import LocalityService

CATALOG_READ_LIMIT = 10000

def clave(nombre: str) -> str:
    normalizado = unicodedata.normalize("NFD", " ".join(nombre.split()).casefold())
    return "".join(caracter for caracter in normalizado if not unicodedata.combining(caracter))


def seed_localities() -> tuple[int, int]:
    catalogo = json.loads(Path(__file__).with_name("localities_loja.json").read_text(encoding="utf-8"))
    datos = [LocalityCreate(name=nombre) for grupo in catalogo["groups"] for nombre in grupo["names"]]
    claves = [clave(dato.name) for dato in datos]
    excluidas = {clave(nombre) for nombre in catalogo["excluded"]}
    if len(claves) != len(set(claves)) or excluidas.intersection(claves):
        raise ValueError("El catálogo contiene duplicados o localidades excluidas")

    creadas = 0
    with engine.begin() as conexion:
        # Los commits del repositorio liberan savepoints dentro de esta transacción.
        with Session(bind=conexion, join_transaction_mode="create_savepoint") as session:
            repository = LocalityRepository(session)
            existentes = repository.search_localities(is_active=None, limit=CATALOG_READ_LIMIT)
            if len(existentes) >= CATALOG_READ_LIMIT:
                raise ValueError("Revise el límite de lectura antes de cargar un catálogo mayor")
            conocidas = {clave(localidad.name) for localidad in existentes}
            service = LocalityService(session)
            for dato in datos:
                identificador = clave(dato.name)
                if identificador in conocidas:
                    continue
                _, creada = service.get_or_create(dato)
                creadas += int(creada)
                conocidas.add(identificador)
    return creadas, len(datos) - creadas


if __name__ == "__main__":
    creadas, existentes = seed_localities()
    print(f"Carga confirmada: {creadas} creadas; {existentes} ya existentes.")
