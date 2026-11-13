import pytest
from src.schemas.validators import (
    ERROR_COOP_NAME_EMPTY,
    ERROR_COOP_NAME_INVALID_CHARS,
    ERROR_COOP_NAME_TOO_LONG,
    ERROR_RUC_INVALID_ALGORITHM,
    ERROR_RUC_LENGTH_OR_FORMAT,
    get_cooperativa_name_error,
    get_ruc_error,
    validate_cooperativa_name,
    validate_ruc,
)


class TestRucValidator:
    # 1. RUC Persona Natural (based on valid cedula 1104609829 + 001)
    def test_valid_ruc_natural_person(self):
        ruc = "1104609829001"
        assert validate_ruc(ruc) is True
        assert get_ruc_error(ruc) is None

    # 2. RUC Sociedad Privada (third digit 9)
    # Province: 17, 3rd digit: 9. Digits: 1790011219001
    # Check sum for 179001121:
    # 1*4 + 7*3 + 9*2 + 0*7 + 0*6 + 1*5 + 1*4 + 2*3 + 1*2 = 4 + 21 + 18 + 0 + 0 + 5 + 4 + 6 + 2 = 60
    # 60 % 11 = 5 => verifier = 11 - 5 = 6 => 10th digit is 6.
    # 1790011216001
    def test_valid_ruc_private_society(self):
        # 1790011216001
        ruc = "1790011216001"
        assert validate_ruc(ruc) is True
        assert get_ruc_error(ruc) is None

    # 3. RUC Sociedad Pública (third digit 6)
    # Province: 17, 3rd digit: 6.
    # Coefficients: [3, 2, 7, 6, 5, 4, 3, 2]
    # Digits: 1760001550001
    # 1*3 + 7*2 + 6*7 + 0*6 + 0*5 + 0*4 + 1*3 + 5*2 = 3 + 14 + 42 + 0 + 0 + 0 + 3 + 10 = 72
    # 72 % 11 = 6 => verifier = 11 - 6 = 5 => 9th digit is 5.
    # 1760001550001
    def test_valid_ruc_public_society(self):
        ruc = "1760001550001"
        assert validate_ruc(ruc) is True
        assert get_ruc_error(ruc) is None

    # 4. Longitud inválida (menos o más de 13 dígitos)
    def test_empty_ruc(self):
        assert validate_ruc("") is False
        assert get_ruc_error("") == "El RUC es obligatorio"
        assert get_ruc_error("   ") == "El RUC es obligatorio"

    @pytest.mark.parametrize("invalid_len_ruc", ["1104618214", "110461821400", "110461821400100"])
    def test_invalid_length_ruc(self, invalid_len_ruc):
        assert validate_ruc(invalid_len_ruc) is False
        assert get_ruc_error(invalid_len_ruc) == ERROR_RUC_LENGTH_OR_FORMAT

    # 5. Caracteres no numéricos
    @pytest.mark.parametrize("non_numeric_ruc", ["110461821400A", "11046182-4001", "11046 8214001"])
    def test_non_numeric_ruc(self, non_numeric_ruc):
        assert validate_ruc(non_numeric_ruc) is False
        assert get_ruc_error(non_numeric_ruc) == ERROR_RUC_LENGTH_OR_FORMAT

    # 6. Provincia inválida (00, 25, 99)
    @pytest.mark.parametrize("invalid_prov_ruc", ["0004618214001", "2504618214001", "9904618214001"])
    def test_invalid_province_ruc(self, invalid_prov_ruc):
        assert validate_ruc(invalid_prov_ruc) is False
        assert get_ruc_error(invalid_prov_ruc) == ERROR_RUC_INVALID_ALGORITHM

    # 7. Dígito verificador inválido
    def test_invalid_verifier_digit_ruc(self):
        # 1104609829001 has verifier 9. If we change it to 8:
        invalid_ruc = "1104609828001"
        assert validate_ruc(invalid_ruc) is False
        assert get_ruc_error(invalid_ruc) == ERROR_RUC_INVALID_ALGORITHM

    # 8. Establecimiento en 000
    def test_invalid_establishment_ruc(self):
        ruc_zero_est = "1104609829000"
        assert validate_ruc(ruc_zero_est) is False
        assert get_ruc_error(ruc_zero_est) == ERROR_RUC_INVALID_ALGORITHM


class TestCooperativaNameValidator:
    def test_valid_cooperativa_names(self):
        valid_names = [
            "Cooperativa Loja",
            "Coop. Unión Cariamanga 2",
            "Trans-Esmeraldas Express",
            "O'Higgins Bus 100",
            "Cooperativa N° 1 del Sur",  # If no ° then simple number
            "Línea 24 - San Cristóbal",
        ]
        assert validate_cooperativa_name("Cooperativa Loja") is True
        assert validate_cooperativa_name("Trans-Esmeraldas") is True
        assert validate_cooperativa_name("O'Higgins Bus") is True
        assert validate_cooperativa_name("Coop 24 de Mayo") is True

    def test_name_empty_or_whitespace(self):
        assert validate_cooperativa_name("") is False
        assert get_cooperativa_name_error("") == ERROR_COOP_NAME_EMPTY
        assert validate_cooperativa_name("   ") is False
        assert get_cooperativa_name_error("   ") == ERROR_COOP_NAME_EMPTY

    def test_name_invalid_symbols(self):
        # Symbols like @, #, $, %, &, ! are not allowed
        invalid_names = [
            "Cooperativa @ Loja",
            "Coop #1",
            "Trans_Loja",  # Underscore not allowed, only hyphen
            "Cooperativa <script>",
        ]
        for name in invalid_names:
            assert validate_cooperativa_name(name) is False
            assert get_cooperativa_name_error(name) == ERROR_COOP_NAME_INVALID_CHARS

    def test_name_length_limit(self):
        name_100 = "A" * 100
        assert validate_cooperativa_name(name_100) is True
        assert get_cooperativa_name_error(name_100) is None

        name_101 = "A" * 101
        assert validate_cooperativa_name(name_101) is False
        assert get_cooperativa_name_error(name_101) == ERROR_COOP_NAME_TOO_LONG
