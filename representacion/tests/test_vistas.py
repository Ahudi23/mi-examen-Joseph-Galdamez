"""Pruebas de integración: formularios + vista + plantilla (cliente de pruebas de Django)."""

from django.test import SimpleTestCase
from django.urls import reverse


class VistaIndexTests(SimpleTestCase):
    def setUp(self):
        self.url = reverse("index")

    def enviar_numero(self, numero, base):
        return self.client.post(self.url, {"accion": "numero", "numero": numero, "base": base})

    def enviar_texto(self, texto):
        return self.client.post(self.url, {"accion": "texto", "texto": texto})

    def test_get_muestra_ambos_formularios(self):
        r = self.client.get(self.url)
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Convertir un número")
        self.assertContains(r, "Analizar un texto")

    def test_conversion_valida_muestra_las_cuatro_bases(self):
        r = self.enviar_numero("255", 10)
        self.assertContains(r, "11111111")  # binario
        self.assertContains(r, "377")  # octal
        self.assertContains(r, "FF")  # hexadecimal
        self.assertContains(r, "Bytes necesarios")

    def test_binario_se_completa_a_16_bits_en_pantalla(self):
        r = self.enviar_numero("100000000", 2)  # 256 decimal
        self.assertContains(r, "00000001 00000000")

    def test_digito_invalido_muestra_error_claro(self):
        r = self.enviar_numero("102", 2)
        self.assertContains(r, "no válido")
        self.assertNotContains(r, "Bytes necesarios")

    def test_valor_fuera_de_rango_muestra_error(self):
        r = self.enviar_numero("65536", 10)
        self.assertContains(r, "fuera de rango")

    def test_valor_negativo_y_vacio_muestran_error(self):
        self.assertContains(self.enviar_numero("-1", 10), "negativos")
        self.assertContains(self.enviar_numero("", 10), "vacío")

    def test_base_no_permitida_se_rechaza(self):
        r = self.enviar_numero("10", 3)
        self.assertNotContains(r, "Bytes necesarios")
        self.assertContains(r, "alert")

    def test_texto_con_enie_muestra_utf8(self):
        r = self.enviar_texto("ñ")
        self.assertContains(r, "U+00F1")
        self.assertContains(r, "C3 B1")
        self.assertContains(r, "241")

    def test_texto_de_mas_de_20_caracteres_muestra_error(self):
        r = self.enviar_texto("a" * 21)
        self.assertContains(r, "máximo permitido")

    def test_html_en_el_texto_se_escapa(self):
        r = self.enviar_texto("<b>")
        self.assertNotContains(r, "<b></td>")
        self.assertContains(r, "&lt;")
