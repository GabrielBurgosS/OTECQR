# ============================================================
#  QR Generator – Impronta  |  Instrucciones de build
# ============================================================

## Requisitos previos

- Python 3.9+ (3.11 o 3.12 recomendado)
- pip actualizado: python -m pip install --upgrade pip

## 1. Instalar dependencias

```bash
pip install qrcode[pil] Pillow pywin32 pyinstaller
```

## 2. Compilar el .exe (Windows)

Desde la carpeta del proyecto:

```bash
pyinstaller qr_generator.spec
```

El ejecutable queda en:  `dist/QR_Generator_Impronta.exe`

Es **portátil**: no requiere instalación ni Python en el equipo destino.
Pesa ~20-30 MB (normal para apps Python empaquetadas).

## 3. Opcional – ícono personalizado

1. Convierte el logo a `.ico` (usa https://convertio.co o IrfanView).
2. Coloca el `.ico` en la carpeta del proyecto.
3. En `qr_generator.spec`, descomenta la línea `# icon='icon.ico'`
   y ajusta la ruta.
4. Vuelve a ejecutar `pyinstaller qr_generator.spec`.

## 4. Distribución

Solo necesitas entregar el archivo `.exe` de la carpeta `dist/`.
No hay dependencias externas ni instaladores.

## Notas

- **Logo y colores**: la función `generate_qr()` en `qr_generator.py`
  admite logo opcional (PNG/JPG, redimensionado automáticamente al
  25 % del ancho del QR) y colores personalizados, pero la interfaz
  actual no expone estos controles. Para usarlos, invoca la función
  directamente con los parámetros `logo_path`, `fill_color` y
  `back_color`.
- **Tamaño del QR**: por defecto `box_size=10`. Para imprimir en
  grande, edita la constante en `qr_generator.py` y recompila.
