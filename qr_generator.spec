# qr_generator.spec
# Ejecutar con: pyinstaller qr_generator.spec

import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Incluye todos los submódulos de qrcode (evita ImportError en runtime)
hiddenimports = (
    collect_submodules('qrcode') +
    collect_submodules('PIL') +
    [
        'qrcode.image.pil',
        'qrcode.image.base',
        'pkg_resources.py2_warn',
        # Portapapeles Windows
        'win32clipboard',
        'win32con',
        'pywintypes',
    ]
)

a = Analysis(
    ['qr_generator.py'],
    pathex=[],
    binaries=[],
    datas=collect_data_files('qrcode'),
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'numpy', 'scipy', 'pandas', 'wx', 'PyQt5'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='QR_Generator_Impronta',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,      # Sin ventana de consola (modo GUI puro)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # icon='icon.ico',  # Descomentar y apuntar a un .ico para ícono personalizado
)
