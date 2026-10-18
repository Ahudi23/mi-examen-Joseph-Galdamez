"""Formularios: validan la entrada llamando a la lógica de `services`."""

from django import forms

from .services import (
    BASES,
    ErrorDeEntrada,
    analizar_texto,
    convertir_numero,
)


class NumeroForm(forms.Form):
    # required=False: la validación de "vacío" la hace el servicio, para
    # mostrar siempre el mismo mensaje claro en español.
    numero = forms.CharField(
        label="Número",
        required=False,
        widget=forms.TextInput(
            attrs={"placeholder": "Ej.: 255, 1010, FF", "autocomplete": "off"}
        ),
    )
    base = forms.TypedChoiceField(
        label="Base de origen",
        choices=[(b, f"{b} — {nombre}") for b, nombre in BASES.items()],
        coerce=int,
        initial=10,
    )

    resultado = None  # se llena en clean() si todo es válido

    def clean(self):
        datos = super().clean()
        base = datos.get("base")
        if base is None:  # el error de la base ya quedó registrado
            return datos
        try:
            self.resultado = convertir_numero(datos.get("numero", ""), base)
        except ErrorDeEntrada as error:
            self.add_error("numero", str(error))
        return datos


class TextoForm(forms.Form):
    # strip=False: los espacios del principio/final también son caracteres.
    texto = forms.CharField(
        label="Texto (hasta 20 caracteres)",
        required=False,
        strip=False,
        widget=forms.TextInput(
            attrs={"placeholder": "Ej.: año, ¡Hola!, €", "autocomplete": "off"}
        ),
    )

    analisis = None

    def clean(self):
        datos = super().clean()
        try:
            self.analisis = analizar_texto(datos.get("texto", ""))
        except ErrorDeEntrada as error:
            self.add_error("texto", str(error))
        return datos
