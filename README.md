# Analizador de representación de datos

## Enlaces de entrega
- Repositorio: https://github.com/Ahudi23/mi-examen-Joseph-Galdamez
- Video de demostración (máx. 2 min): https://drive.google.com/drive/folders/11Q9zyekOSMUOkd94EtwN6ceD-so7Q2p1?usp=sharing

Aplicación web hecha con **Python 3.12 y Django** que relaciona tres temas de Arquitectura de Computadoras:
sistemas numéricos, codificación de caracteres (UTF-8) y ejecución en contenedores.

## Qué hace

**Formulario 1: número.** Recibe un número y su base de origen (2, 8, 10 o 16) y muestra:

- el valor en decimal, binario, octal y hexadecimal;
- el binario completado con ceros a la izquierda hasta el siguiente límite de byte (8, 16, 24… bits);
- cuántos **bits significativos** y cuántos **bytes** necesita.

Valida que los dígitos pertenezcan a la base elegida y que el valor esté entre 0 y 65 535 (16 bits sin signo).

**Formulario 2: texto.** Acepta hasta 20 caracteres y, para cada uno, muestra el carácter, su código decimal,
su punto de código `U+XXXX`, su valor hexadecimal y sus bytes en UTF-8.

**Mensajes de error** claros para: entrada vacía, dígitos inválidos para la base, valores negativos,
valores fuera de rango, base no permitida y texto de más de 20 caracteres.

## Estructura del proyecto

```
analizador-datos/
├── manage.py
├── requirements.txt          # Django y gunicorn
├── Dockerfile                # python:3.12-slim
├── compose.yaml              # puerto 8000, 256 MB de RAM, 1 CPU
├── evidencia.sh              # genera la evidencia de docker stats
├── config/                   # configuración del proyecto Django (settings, urls, wsgi)
└── representacion/           # la aplicación
    ├── services.py           # lógica pura (conversiones y análisis UTF-8), sin Django
    ├── forms.py              # formularios: validan llamando a services
    ├── views.py              # una vista con los dos formularios
    ├── urls.py
    ├── templates/representacion/index.html
    └── tests/                # test_servicios.py (24 pruebas) y test_vistas.py (10 pruebas)
```

La lógica está separada de Django a propósito: `services.py` solo usa la biblioteca estándar, por lo que
se prueba sin levantar nada. Los formularios solo traducen sus errores a mensajes de pantalla.

## Cómo funciona la conversión

1. Se limpia el texto y se comprueba que no esté vacío ni empiece con `-`.
2. Se revisa carácter por carácter contra los dígitos de la base (`01` para base 2, `0-7` para base 8,
   `0-9` para base 10 y `0-9A-F` para base 16, sin distinguir mayúsculas).
3. Se convierte con `int(texto, base)` y se comprueba el rango 0–65 535.
4. **Bits significativos** = `valor.bit_length()` (el 0 cuenta como 1 bit).
5. **Bytes** = bits significativos redondeados hacia arriba a múltiplo de 8, `(bits + 7) // 8`.
6. El binario se rellena con ceros a la izquierda hasta `bytes × 8` dígitos.

Ejemplo: `256` necesita 9 bits, por lo tanto 2 bytes, y se muestra como `00000001 00000000`.

## Ejecución sin Docker

Requiere Python 3.12.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
DJANGO_DEBUG=1 python manage.py runserver 0.0.0.0:8000
```

Abrir <http://localhost:8000>.

## Pruebas automatizadas

```bash
python manage.py test -v 2
```

Son 34 pruebas en total:

- **Conversiones válidas:** 255 cabe en 1 byte, 256 se ajusta a 16 bits, binario `1010` → `00001010`,
  hexadecimal en minúsculas y mayúsculas, octal, el 0 y el máximo 65 535.
- **Errores:** campo vacío, dígito inválido en base 2, 8 y 16, letras en decimal, negativo,
  65 536 fuera de rango, base no permitida y cadena demasiado larga.
- **UTF-8:** `ñ` → `U+00F1`, decimal 241, bytes `C3 B1`; además `A` (1 byte), `€` (3 bytes) y 😀 (4 bytes).
- **Vistas:** la página carga, la conversión válida y los errores se ven en pantalla, el HTML del texto se escapa.

## Docker

Requiere Docker Engine y el plugin Compose v2 (`docker compose`).

### Construir y ejecutar con Compose

```bash
docker compose up -d --build     # construye la imagen y levanta el contenedor
docker compose ps                # estado del contenedor
docker compose logs -f           # registros de la aplicación
docker compose down              # detener y eliminar el contenedor
```

La aplicación queda en <http://localhost:8000>.

### Alternativa solo con `docker`

```bash
docker build -t analizador-datos:1.0 .
docker run -d --name analizador -p 8000:8000 \
  --memory=256m --memory-swap=256m --cpus=1 \
  analizador-datos:1.0
```

### Límites de recursos: 256 MB de RAM y 1 CPU

`compose.yaml` los declara con `mem_limit: 256m`, `memswap_limit: 256m` y `cpus: "1.0"`.
Para comprobar que Docker los aplicó:

```bash
docker stats --no-stream analizador
docker inspect -f 'Memory={{.HostConfig.Memory}} NanoCpus={{.HostConfig.NanoCpus}}' analizador
```

- En `docker stats`, la columna `MEM USAGE / LIMIT` debe mostrar un límite de `256MiB`.
- `docker inspect` debe mostrar `Memory=268435456` (256 MiB en bytes) y `NanoCpus=1000000000` (1 CPU).

El script `./evidencia.sh` levanta el contenedor, genera tráfico, ejecuta ambos comandos y guarda la salida
real en `evidencia/docker-stats.txt`.

### Evidencia de `docker stats`

> Pegar aquí la salida real de `docker stats --no-stream analizador` obtenida en la máquina de entrega
> (o enlazar la captura en `evidencia/`).

```
(pendiente: pegar la salida real)
```

## Arquitectura de Von Neumann en esta aplicación

El modelo de Von Neumann describe una computadora con CPU, memoria que guarda **programa y datos juntos**,
entrada/salida y buses que los comunican. La aplicación usa cada parte así:

- **CPU (unidad de control, ALU y registros):** ejecuta el ciclo de instrucción (captar, decodificar, ejecutar)
  sobre el intérprete de Python. La ALU hace las operaciones de la conversión: `int(texto, base)`,
  comparaciones de rango, desplazamientos y divisiones sucesivas al formatear en binario, octal y hexadecimal.
- **Memoria principal (RAM):** guarda a la vez las instrucciones del intérprete, el código de Django y los datos
  de la petición (la cadena escrita, el entero resultante y la lista de caracteres analizados). Ese límite de
  256 MB acota toda esa memoria.
- **Entrada/salida:** el navegador envía el formulario por la red (puerto 8000) y recibe la página HTML;
  la tarjeta de red y el disco, que carga la imagen y el código, son los dispositivos de E/S.
- **Buses:** llevan direcciones, datos y señales de control entre CPU, RAM y dispositivos en cada acceso.
- **Representación de datos:** el valor se guarda como bits; por eso importa cuántos bits significativos y cuántos
  bytes ocupa (1 byte = 8 bits, el tamaño mínimo direccionable) y cómo UTF-8 codifica cada carácter con 1 a 4 bytes.

## Por qué el contenedor comparte el kernel del host

Un contenedor **no es una máquina virtual**: no trae su propio sistema operativo ni su propio kernel.
Es un proceso (o grupo de procesos) del host al que el kernel Linux le aplica dos mecanismos:

- **Namespaces:** le dan una vista aislada de procesos, red, sistema de archivos y nombres de host,
  de modo que dentro del contenedor la aplicación se ve como el proceso 1 de su propio sistema.
- **cgroups:** limitan y contabilizan los recursos que puede usar. Así se aplican los 256 MB de RAM y la 1 CPU.

La imagen `python:3.12-slim` solo aporta el espacio de usuario (bibliotecas, Python y las dependencias);
las llamadas al sistema las atiende el kernel del host. Esto explica que arranque en segundos, ocupe mucha menos
memoria que una VM y que un contenedor Linux necesite un kernel Linux (en Windows o macOS, Docker Desktop
lo obtiene de una máquina virtual ligera).

## Decisiones de diseño

- **Sin base de datos:** la aplicación no guarda nada, por eso `DATABASES = {}`.
- **El 0 usa 1 bit y 1 byte:** hace falta al menos un dígito para representarlo.
- **Sin prefijos:** `0x1F` o `0b101` se rechazan con mensaje claro; se escribe solo `1F` o `101`.
- **Hexadecimal sin relleno:** el relleno a byte se aplica solo al binario, como pide el enunciado.
- **Los espacios cuentan como caracteres** en el análisis de texto, y se muestran como `(espacio)`.
- **`ALLOWED_HOSTS = *`** simplifica la práctica; en un despliegue real se limitaría a los dominios propios.
- **gunicorn** en vez de `runserver` dentro del contenedor, porque `runserver` es solo para desarrollo.

## Guion sugerido para el video (máximo 2 minutos)

1. **Conversión válida** (~25 s): `255` en base 10 y luego `1010` en base 2; señalar el binario ajustado a bytes y bits/bytes.
2. **Error de validación** (~15 s): `102` en base 2, y luego `65536` en base 10.
3. **Texto con ñ** (~20 s): `año`; señalar `U+00F1` y `C3 B1`.
4. **Pruebas** (~20 s): `python manage.py test` terminando en `OK`.
5. **Contenedor en ejecución** (~30 s): `docker compose ps` y `docker stats --no-stream analizador` mostrando el límite de 256 MiB.
