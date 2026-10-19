# Analizador de representación de datos

## Enlaces de entrega

- **Repositorio:** https://github.com/Ahudi23/mi-examen-Joseph-Galdamez
- **Video de demostración:** https://drive.google.com/drive/folders/11Q9zyekOSMUOkd94EtwN6ceD-so7Q2p1?usp=sharing

## Descripción

Aplicación web desarrollada con Python 3.12 y Django para trabajar con sistemas numéricos y codificación de caracteres UTF-8. También se ejecuta en Docker con límites de memoria y CPU.

La aplicación tiene dos formularios:

- **Conversión de números:** recibe un número en base 2, 8, 10 o 16 y muestra su equivalente en decimal, binario, octal y hexadecimal. También indica los bits significativos y los bytes necesarios.
- **Análisis de texto:** muestra cada carácter, su código decimal, su punto de código Unicode y su representación en hexadecimal y UTF-8.

El formulario de números acepta valores entre 0 y 65 535. El formulario de texto permite hasta 20 caracteres. Ambos muestran mensajes cuando los datos ingresados no son válidos.

## Estructura del proyecto

```
analizador-datos/
├── manage.py
├── requirements.txt
├── Dockerfile
├── compose.yaml
├── evidencia.sh
├── config/
└── representacion/
    ├── services.py
    ├── forms.py
    ├── views.py
    ├── urls.py
    ├── templates/representacion/index.html
    └── tests/
        ├── test_servicios.py
        └── test_vistas.py
```

El archivo `services.py` contiene las conversiones y el análisis de UTF-8. `forms.py` valida los datos, mientras que `views.py` se encarga de mostrar los formularios y sus resultados.

## Conversión de números

La aplicación verifica que los dígitos correspondan a la base seleccionada y que el número esté dentro del rango permitido.

Para calcular los bits significativos se utiliza `bit_length()`. La cantidad de bytes se obtiene redondeando los bits al siguiente múltiplo de ocho. Después, el número binario se completa con ceros a la izquierda.

Por ejemplo, el número decimal `256` necesita 9 bits y ocupa 2 bytes:

```
00000001 00000000
```

No se aceptan prefijos como `0x` o `0b`; se debe ingresar únicamente el número.

## Análisis de texto

El formulario procesa textos de hasta 20 caracteres y muestra los datos de cada carácter.

Por ejemplo, la letra `ñ` tiene estos valores:

- Código decimal: `241`
- Unicode: `U+00F1`
- Bytes UTF-8: `C3 B1`

También se pueden analizar caracteres que utilizan más de un byte, como `€` y `😀`.

## Ejecución sin Docker

Se necesita Python 3.12.

```
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
DJANGO_DEBUG=1 python manage.py runserver 0.0.0.0:8000
```

Luego, abrir http://localhost:8000.

## Pruebas

Para ejecutar las pruebas automatizadas:

```
python manage.py test -v 2
```

El proyecto incluye 34 pruebas: 24 para los servicios y 10 para las vistas.

Se prueban las conversiones entre bases, los límites numéricos, los datos inválidos y la codificación UTF-8. También se comprueba que las vistas respondan correctamente y que el contenido del texto se muestre de forma segura en HTML.

## Ejecución con Docker

Se requiere Docker Engine y Docker Compose v2.

Para construir y ejecutar la aplicación:

```
docker compose up -d --build
docker compose ps
docker compose logs -f
```

La aplicación queda disponible en http://localhost:8000.

Para detenerla:

```
docker compose down
```

### Límites de recursos

El contenedor está configurado con 256 MiB de memoria RAM y una CPU.

Para revisar los recursos utilizados:

```
docker stats --no-stream analizador
docker inspect -f 'Memory={{.HostConfig.Memory}} NanoCpus={{.HostConfig.NanoCpus}}' analizador
```

Los valores esperados en la configuración son:

```
Memory=268435456 NanoCpus=1000000000
```

El archivo `evidencia.sh` permite ejecutar las comprobaciones y guardar sus resultados en `evidencia/docker-stats.txt`.

### Evidencia de Docker

Salida registrada durante la ejecución:

```
CONTAINER ID   NAME        CPU %   MEM USAGE / LIMIT
70f06e8031d0   analizador  0.01%   74.83MiB / 256MiB
```

Configuración de recursos:

```
Memory=268435456 NanoCpus=1000000000
```

El contenedor se encontraba en ejecución durante la comprobación. La lectura de memoria y CPU corresponde al momento en que se ejecutó `docker stats`.

## Arquitectura de Von Neumann

La aplicación permite relacionar los componentes del modelo de Von Neumann con el funcionamiento de un programa.

- **CPU:** ejecuta las instrucciones de Python y las operaciones utilizadas para convertir los números.
- **Memoria RAM:** almacena el código en ejecución y los datos que se procesan en cada solicitud.
- **Entrada y salida:** el navegador envía los formularios y recibe los resultados mediante HTTP.
- **Buses:** permiten la comunicación entre el procesador, la memoria y los dispositivos.
- **Representación de datos:** los números se almacenan en forma binaria y los caracteres se representan mediante codificaciones como UTF-8.

## Contenedores y kernel

Docker permite ejecutar la aplicación dentro de un contenedor sin instalar todas sus dependencias directamente en el sistema anfitrión.

El contenedor utiliza el kernel del sistema anfitrión. Los _namespaces_ aíslan recursos como los procesos y la red, mientras que los _cgroups_ permiten controlar el uso de CPU y memoria.

La imagen `python:3.12-slim` incluye Python y los componentes necesarios para ejecutar la aplicación. En este proyecto, los límites configurados son 256 MiB de RAM y una CPU.
