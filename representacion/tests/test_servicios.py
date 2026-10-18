"""Pruebas de la lógica pura (sin Django): conversiones, errores y UTF-8."""

import unittest

from representacion.services import (
    ErrorDeEntrada,
    analizar_texto,
    convertir_a_entero,
    convertir_numero,
)


class ConversionesValidasTests(unittest.TestCase):
    def test_decimal_255_cabe_en_un_byte(self):
        r = convertir_numero("255", 10)
        self.assertEqual(r["decimal"], "255")
        self.assertEqual(r["binario"], "11111111")
        self.assertEqual(r["octal"], "377")
        self.assertEqual(r["hexadecimal"], "FF")
        self.assertEqual((r["bits"], r["bytes"]), (8, 1))

    def test_decimal_256_se_ajusta_a_16_bits(self):
        r = convertir_numero("256", 10)
        self.assertEqual(r["bits"], 9)  # 100000000
        self.assertEqual(r["bytes"], 2)
        self.assertEqual(r["binario"], "0000000100000000")
        self.assertEqual(r["binario_agrupado"], "00000001 00000000")

    def test_binario_se_completa_al_byte(self):
        r = convertir_numero("1010", 2)
        self.assertEqual(r["decimal"], "10")
        self.assertEqual(r["binario"], "00001010")
        self.assertEqual((r["bits"], r["bytes"]), (4, 1))

    def test_hexadecimal_acepta_minusculas_y_mayusculas(self):
        self.assertEqual(convertir_a_entero("ff", 16), 255)
        self.assertEqual(convertir_a_entero("FF", 16), 255)
        self.assertEqual(convertir_a_entero("1a3", 16), 419)

    def test_octal_a_decimal(self):
        self.assertEqual(convertir_a_entero("377", 8), 255)

    def test_cero_usa_un_bit_y_un_byte(self):
        r = convertir_numero("0", 10)
        self.assertEqual(r["binario"], "00000000")
        self.assertEqual((r["bits"], r["bytes"]), (1, 1))

    def test_maximo_65535_ocupa_16_bits(self):
        r = convertir_numero("65535", 10)
        self.assertEqual(r["binario"], "1" * 16)
        self.assertEqual(r["hexadecimal"], "FFFF")
        self.assertEqual((r["bits"], r["bytes"]), (16, 2))


class ErroresDeNumeroTests(unittest.TestCase):
    def assertError(self, texto, base, fragmento):
        with self.assertRaises(ErrorDeEntrada) as contexto:
            convertir_a_entero(texto, base)
        self.assertIn(fragmento, str(contexto.exception))

    def test_entrada_vacia(self):
        self.assertError("", 10, "vacío")
        self.assertError("   ", 10, "vacío")

    def test_digito_invalido_en_binario(self):
        self.assertError("1021", 2, "'2'")

    def test_digito_invalido_en_octal(self):
        self.assertError("789", 8, "base 8")

    def test_letra_invalida_en_hexadecimal(self):
        self.assertError("1G", 16, "'G'")

    def test_letras_en_decimal(self):
        self.assertError("12a", 10, "'A'")

    def test_valor_negativo(self):
        self.assertError("-5", 10, "negativos")

    def test_fuera_de_rango_por_uno(self):
        self.assertError("65536", 10, "fuera de rango")

    def test_fuera_de_rango_en_hexadecimal(self):
        self.assertError("10000", 16, "fuera de rango")

    def test_base_no_permitida(self):
        self.assertError("10", 3, "2, 8, 10 o 16")

    def test_cadena_demasiado_larga(self):
        self.assertError("1" * 65, 2, "demasiado largo")


class AnalisisDeTextoTests(unittest.TestCase):
    def test_enie_ocupa_dos_bytes_en_utf8(self):
        fila = analizar_texto("ñ")["filas"][0]
        self.assertEqual(fila["caracter"], "ñ")
        self.assertEqual(fila["decimal"], 241)
        self.assertEqual(fila["punto_codigo"], "U+00F1")
        self.assertEqual(fila["hexadecimal"], "F1")
        self.assertEqual(fila["bytes_utf8"], "C3 B1")

    def test_ascii_ocupa_un_byte(self):
        fila = analizar_texto("A")["filas"][0]
        self.assertEqual(
            (fila["decimal"], fila["punto_codigo"], fila["bytes_utf8"]),
            (65, "U+0041", "41"),
        )

    def test_euro_ocupa_tres_bytes_y_emoji_cuatro(self):
        self.assertEqual(analizar_texto("€")["filas"][0]["bytes_utf8"], "E2 82 AC")
        emoji = analizar_texto("😀")["filas"][0]
        self.assertEqual(emoji["punto_codigo"], "U+1F600")
        self.assertEqual(emoji["bytes_utf8"], "F0 9F 98 80")

    def test_total_de_bytes_de_una_palabra(self):
        r = analizar_texto("año")  # a=1, ñ=2, o=1
        self.assertEqual((r["total_caracteres"], r["total_bytes"]), (3, 4))

    def test_el_espacio_cuenta_como_caracter(self):
        r = analizar_texto("a b")
        self.assertEqual(r["total_caracteres"], 3)
        self.assertEqual(r["filas"][1]["caracter"], "(espacio)")

    def test_texto_vacio(self):
        with self.assertRaises(ErrorDeEntrada):
            analizar_texto("")
        with self.assertRaises(ErrorDeEntrada):
            analizar_texto("    ")

    def test_limite_de_20_caracteres(self):
        self.assertEqual(analizar_texto("a" * 20)["total_caracteres"], 20)
        with self.assertRaises(ErrorDeEntrada) as contexto:
            analizar_texto("a" * 21)
        self.assertIn("máximo", str(contexto.exception))


if __name__ == "__main__":
    unittest.main()
