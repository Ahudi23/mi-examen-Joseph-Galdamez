"""Lógica de negocio del Analizador de representación de datos.

Este módulo no depende de Django: son funciones puras que reciben texto y
devuelven diccionarios. Eso permite probarlas de forma aislada y mantener las
vistas y formularios delgados.
"""

import unicodedata

# Bases permitidas y los dígitos válidos de cada una (en mayúsculas).
BASES = {2: "binaria", 8: "octal", 10: "decimal", 16: "hexadecimal"}
DIGITOS = "0123456789ABCDEF"

VALOR_MINIMO = 0
VALOR_MAXIMO = 65_535  # 2**16 - 1: lo que cabe en 16 bits sin signo
MAX_LONGITUD_NUMERO = 64  # evita procesar cadenas absurdamente largas
MAX_CARACTERES_TEXTO = 20


class ErrorDeEntrada(ValueError):
    """Entrada del usuario inválida; el mensaje está listo para mostrarse."""


def _lista_legible(elementos):
    return ", ".join(f"'{e}'" for e in elementos)


def _miles(numero):
    """65535 -> '65 535' (separador de miles con espacio)."""
    return f"{numero:,}".replace(",", " ")


def convertir_a_entero(texto, base):
    """Valida `texto` contra `base` y lo convierte a entero (0 a 65 535)."""
    if base not in BASES:
        raise ErrorDeEntrada("La base de origen debe ser 2, 8, 10 o 16.")

    texto = (texto or "").strip()
    if not texto:
        raise ErrorDeEntrada("Ingrese un número: el campo no puede estar vacío.")

    if texto.startswith("-"):
        raise ErrorDeEntrada(
            "No se permiten valores negativos: este analizador trabaja con "
            f"enteros sin signo entre {VALOR_MINIMO} y {_miles(VALOR_MAXIMO)}."
        )

    if len(texto) > MAX_LONGITUD_NUMERO:
        raise ErrorDeEntrada(
            f"El número es demasiado largo (máximo {MAX_LONGITUD_NUMERO} dígitos)."
        )

    permitidos = DIGITOS[:base]
    invalidos = []
    for caracter in texto.upper():
        if caracter not in permitidos and caracter not in invalidos:
            invalidos.append(caracter)
    if invalidos:
        raise ErrorDeEntrada(
            f"Dígito(s) no válido(s) para la base {base} ({BASES[base]}): "
            f"{_lista_legible(invalidos)}. "
            f"Dígitos permitidos: {_lista_legible(permitidos)}."
        )

    valor = int(texto, base)
    if valor > VALOR_MAXIMO:
        raise ErrorDeEntrada(
            f"El valor {_miles(valor)} (decimal) está fuera de rango: debe estar "
            f"entre {VALOR_MINIMO} y {_miles(VALOR_MAXIMO)}."
        )
    return valor


def agrupar_en_bytes(binario):
    """'0000000100000000' -> '00000001 00000000' (solo para mostrar)."""
    return " ".join(binario[i : i + 8] for i in range(0, len(binario), 8))


def representar_numero(valor):
    """Devuelve todas las representaciones y el tamaño de `valor`.

    - bits significativos: posiciones desde el 1 más a la izquierda; el 0
      se cuenta como 1 bit (convención: hace falta al menos un dígito).
    - bytes: bits significativos redondeados hacia arriba a múltiplos de 8.
    - binario ajustado: el binario completado con ceros a la izquierda hasta
      el siguiente límite de byte (8, 16, 24... bits).
    """
    bits = max(1, valor.bit_length())
    bytes_necesarios = (bits + 7) // 8
    binario = format(valor, f"0{bytes_necesarios * 8}b")
    return {
        "decimal": str(valor),
        "binario": binario,
        "binario_agrupado": agrupar_en_bytes(binario),
        "octal": format(valor, "o"),
        "hexadecimal": format(valor, "X"),
        "bits": bits,
        "bytes": bytes_necesarios,
        "bits_ajustados": bytes_necesarios * 8,
    }


def convertir_numero(texto, base):
    """Atajo: valida, convierte y representa en un solo paso."""
    return representar_numero(convertir_a_entero(texto, base))


def _visible(caracter):
    """Texto seguro para mostrar caracteres invisibles o de control."""
    if caracter == " ":
        return "(espacio)"
    if caracter == "\t":
        return "(tabulador)"
    if caracter == "\n":
        return "(salto de línea)"
    if unicodedata.category(caracter).startswith("C"):
        return "(control)"
    return caracter


def analizar_texto(texto):
    """Analiza hasta 20 caracteres y devuelve una fila por carácter."""
    if texto is None or not texto.strip():
        raise ErrorDeEntrada("Ingrese un texto: el campo no puede estar vacío.")

    if len(texto) > MAX_CARACTERES_TEXTO:
        raise ErrorDeEntrada(
            f"El texto tiene {len(texto)} caracteres; el máximo permitido es "
            f"{MAX_CARACTERES_TEXTO}."
        )

    filas = []
    total_bytes = 0
    for caracter in texto:
        codigo = ord(caracter)
        en_utf8 = caracter.encode("utf-8")
        total_bytes += len(en_utf8)
        filas.append(
            {
                "caracter": _visible(caracter),
                "decimal": codigo,
                "punto_codigo": f"U+{codigo:04X}",
                "hexadecimal": f"{codigo:X}",
                "bytes_utf8": " ".join(f"{b:02X}" for b in en_utf8),
                "cantidad_bytes": len(en_utf8),
                "nombre": unicodedata.name(caracter, ""),
            }
        )
    return {
        "filas": filas,
        "total_caracteres": len(texto),
        "total_bytes": total_bytes,
    }
