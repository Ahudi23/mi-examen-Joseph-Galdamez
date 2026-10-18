from django.shortcuts import render

from .forms import NumeroForm, TextoForm


def index(request):
    """Una sola página con dos formularios; `accion` indica cuál se envió."""
    form_numero = NumeroForm()
    form_texto = TextoForm()
    resultado = None
    analisis = None

    if request.method == "POST":
        accion = request.POST.get("accion")
        if accion == "numero":
            form_numero = NumeroForm(request.POST)
            if form_numero.is_valid():
                resultado = form_numero.resultado
        elif accion == "texto":
            form_texto = TextoForm(request.POST)
            if form_texto.is_valid():
                analisis = form_texto.analisis

    return render(
        request,
        "representacion/index.html",
        {
            "form_numero": form_numero,
            "form_texto": form_texto,
            "resultado": resultado,
            "analisis": analisis,
        },
    )
