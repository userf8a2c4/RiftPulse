"""Reconstruye la extensión del panel lateral a partir de index.html.
Ejecútelo (o use actualizar-extension.bat) cada vez que cambie la página."""
import json
import os
import re
import struct
import zlib

AQUI = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(AQUI, 'index.html'), encoding='utf-8').read()
m = re.search(r'<script>(.*)</script>', src, re.S)
if not m:
    raise SystemExit('No se encontró el <script> en index.html')
html = src[:m.start()] + '<script src="panel.js"></script>' + src[m.end():]

ext = os.path.join(AQUI, 'extension')
os.makedirs(ext, exist_ok=True)
open(os.path.join(ext, 'panel.html'), 'w', encoding='utf-8').write(html)
open(os.path.join(ext, 'panel.js'), 'w', encoding='utf-8').write(m.group(1))

manifest = {
    "manifest_version": 3,
    "name": "RiftPulse",
    "version": "1.0",
    "description": "Panel lateral con predicciones, copa, historial y Pick'Em de Worlds 2026.",
    "permissions": ["sidePanel"],
    "host_permissions": [
        "https://esports-api.lolesports.com/*", "https://feed.lolesports.com/*",
        "https://ddragon.leagueoflegends.com/*", "https://sb2frontend-altenar2.biahosted.com/*",
        "https://static.lolesports.com/*"
    ],
    "action": {"default_title": "Abrir RiftPulse"},
    "side_panel": {"default_path": "panel.html"},
    "background": {"service_worker": "background.js"},
    "icons": {"128": "icon128.png"}
}
open(os.path.join(ext, 'manifest.json'), 'w', encoding='utf-8').write(json.dumps(manifest, ensure_ascii=False, indent=2))
open(os.path.join(ext, 'background.js'), 'w', encoding='utf-8').write(
    "// Al hacer clic en el ícono de la extensión se abre o cierra el panel lateral.\n"
    "chrome.sidePanel.setPanelBehavior({ openPanelOnActionClick: true }).catch(() => {});\n")


def solid_png(size, rgb):
    def chunk(typ, data):
        c = typ + data
        return struct.pack('>I', len(data)) + c + struct.pack('>I', zlib.crc32(c) & 0xffffffff)
    ihdr = struct.pack('>IIBBBBB', size, size, 8, 2, 0, 0, 0)
    raw = (b'\x00' + bytes(rgb) * size) * size
    return b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', ihdr) + chunk(b'IDAT', zlib.compress(raw)) + chunk(b'IEND', b'')


open(os.path.join(ext, 'icon128.png'), 'wb').write(solid_png(128, (74, 163, 255)))
print('Extensión actualizada en:', ext)
