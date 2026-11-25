import pytest
from decimal import Decimal
from pydantic import ValidationError
from src.schemas.validators import (
    ERROR_LOCALITY_NAME_EMPTY,
    ERROR_LOCALITY_NAME_TOO_LONG,
    ERROR_ROUTE_DESCRIPTION_TOO_LONG,
    ERROR_ROUTE_DISTANCE_INVALID,
    ERROR_ROUTE_NAME_SUFFIX_TOO_LONG,
    ERROR_ROUTE_ORIGIN_DESTINATION_SAME,
    ERROR_ROUTE_STOP_DUPLICATED,
    ERROR_ROUTE_STOP_EQUALS_ORIGIN_OR_DESTINATION,
    ERROR_ROUTE_TIME_INVALID,
    get_locality_name_error,
    get_route_description_error,
    get_route_distance_error,
    get_route_name_suffix_error,
    get_route_time_error,
    normalize_locality_name,
)
from src.schemas.locality_schemas import LocalityCreate
from src.schemas.route_schemas import RouteCreate, RouteStopInput, RouteUpdate


def test_normalize_locality_name():
    assert normalize_locality_name("  Loja   ") == "Loja"
    assert normalize_locality_name("Santo   Domingo   de los Tsáchilas") == "Santo Domingo de los Tsáchilas"
    assert normalize_locality_name("") == ""
    assert normalize_locality_name(None) == ""


def test_locality_name_validation():
    assert get_locality_name_error("Quito") is None
    assert get_locality_name_error("   ") == ERROR_LOCALITY_NAME_EMPTY
    assert get_locality_name_error("A" * 101) == ERROR_LOCALITY_NAME_TOO_LONG

    loc = LocalityCreate(name="  Cuenca  ")
    assert loc.name == "Cuenca"

    with pytest.raises(ValidationError) as exc:
        LocalityCreate(name="   ")
    assert ERROR_LOCALITY_NAME_EMPTY in str(exc.value)


def test_route_name_suffix_and_description():
    assert get_route_name_suffix_error(None) is None
    assert get_route_name_suffix_error("Vía Cuenca") is None
    assert get_route_name_suffix_error("A" * 31) == ERROR_ROUTE_NAME_SUFFIX_TOO_LONG

    assert get_route_description_error(None) is None
    assert get_route_description_error("Ruta directa") is None
    assert get_route_description_error("A" * 101) == ERROR_ROUTE_DESCRIPTION_TOO_LONG


def test_route_distance_validation():
    assert get_route_distance_error(10.5) is None
    assert get_route_distance_error(Decimal("100.25")) is None
    assert get_route_distance_error(0) == ERROR_ROUTE_DISTANCE_INVALID
    assert get_route_distance_error(-5) == ERROR_ROUTE_DISTANCE_INVALID
    assert get_route_distance_error("abc") == ERROR_ROUTE_DISTANCE_INVALID


def test_route_time_validation():
    assert get_route_time_error(60) is None
    assert get_route_time_error(1439) is None
    assert get_route_time_error(0) == ERROR_ROUTE_TIME_INVALID
    assert get_route_time_error(-10) == ERROR_ROUTE_TIME_INVALID
    assert get_route_time_error(1440) is None
    assert get_route_time_error(3000) is None
    assert get_route_time_error(6000) == ERROR_ROUTE_TIME_INVALID
    assert get_route_time_error("xyz") == ERROR_ROUTE_TIME_INVALID


def test_route_create_schema_valid():
    route_in = RouteCreate(
        origin_id=1,
        destination_id=2,
        name_suffix="Vía Cuenca",
        distance_km=Decimal("450.50"),
        estimated_time_minutes=480,
        description="Ruta interprovincial",
        stops=[
            RouteStopInput(locality_id=3, stop_order=1),
            RouteStopInput(locality_id=4, stop_order=2),
        ],
    )
    assert route_in.origin_id == 1
    assert route_in.destination_id == 2
    assert route_in.name_suffix == "Vía Cuenca"
    assert len(route_in.stops) == 2


def test_route_create_schema_same_origin_destination():
    with pytest.raises(ValidationError) as exc:
        RouteCreate(
            origin_id=1,
            destination_id=1,
            distance_km=Decimal("100"),
            estimated_time_minutes=120,
        )
    assert ERROR_ROUTE_ORIGIN_DESTINATION_SAME in str(exc.value)


def test_route_create_schema_stop_equals_origin_or_destination():
    with pytest.raises(ValidationError) as exc:
        RouteCreate(
            origin_id=1,
            destination_id=2,
            distance_km=Decimal("100"),
            estimated_time_minutes=120,
            stops=[RouteStopInput(locality_id=1, stop_order=1)],
        )
    assert ERROR_ROUTE_STOP_EQUALS_ORIGIN_OR_DESTINATION in str(exc.value)

    with pytest.raises(ValidationError) as exc:
        RouteCreate(
            origin_id=1,
            destination_id=2,
            distance_km=Decimal("100"),
            estimated_time_minutes=120,
            stops=[RouteStopInput(locality_id=2, stop_order=1)],
        )
    assert ERROR_ROUTE_STOP_EQUALS_ORIGIN_OR_DESTINATION in str(exc.value)


def test_route_create_schema_duplicated_stops():
    with pytest.raises(ValidationError) as exc:
        RouteCreate(
            origin_id=1,
            destination_id=2,
            distance_km=Decimal("100"),
            estimated_time_minutes=120,
            stops=[
                RouteStopInput(locality_id=3, stop_order=1),
                RouteStopInput(locality_id=3, stop_order=2),
            ],
        )
    assert ERROR_ROUTE_STOP_DUPLICATED in str(exc.value)
