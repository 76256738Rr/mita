"""Captura pantallas de la plataforma MITA para el manual de usuario."""

import os
import sys
from pathlib import Path

import django

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mita_platform.settings')
django.setup()

from playwright.sync_api import sync_playwright  # noqa: E402

from mita_engine.models import Expediente  # noqa: E402

BASE_URL = os.environ.get('MITA_SCREENSHOT_URL', 'http://127.0.0.1:8888')
OUT_DIR = BASE / 'docs' / 'manual-usuario' / 'pantallas'
PASSWORD = 'mita2026'

activo = Expediente.objects.filter(folio='MITA-DEMO-2026-ACTIVO').first()
dictaminado = Expediente.objects.filter(folio='MITA-DEMO-2026-DICTAMINADO').first()

CAPTURAS = [
    {'file': '01-login.png', 'path': '/login/', 'login': None},
    {'file': '02-dashboard.png', 'path': '/', 'login': 'analista'},
    {'file': '03-bandeja.png', 'path': '/bandeja/', 'login': 'analista'},
    {'file': '04-expedientes.png', 'path': '/expedientes/', 'login': 'analista'},
    {'file': '05-expediente-nuevo.png', 'path': '/expedientes/nuevo/', 'login': 'dependencia'},
    {
        'file': '06-expediente-paso6.png',
        'path': f'/expedientes/{activo.pk}/' if activo else '/expedientes/',
        'login': 'investigador',
    },
    {
        'file': '07-expediente-dictaminado.png',
        'path': f'/expedientes/{dictaminado.pk}/' if dictaminado else '/expedientes/',
        'login': 'auditor',
    },
    {'file': '08-proceso-operativo.png', 'path': '/proceso/', 'login': 'analista'},
    {'file': '09-base-conocimiento.png', 'path': '/base-datos/', 'login': 'analista'},
    {'file': '10-mapa-geoespacial.png', 'path': '/mapa/', 'login': 'analista'},
    {'file': '11-metodologia.png', 'path': '/metodologia/', 'login': 'analista'},
    {'file': '12-proyecto-demo.png', 'path': '/proyecto/', 'login': 'analista'},
    {'file': '13-perfiles-sni.png', 'path': '/sni/', 'login': 'investigador'},
    {'file': '14-dictamenes.png', 'path': '/dictamenes/', 'login': 'admin'},
    {'file': '15-reportes.png', 'path': '/reportes/', 'login': 'auditor'},
]


def login_as(page, username):
    page.goto(f'{BASE_URL}/login/')
    form = page.locator(f'form.role-card input[name="username"][value="{username}"]').locator('xpath=ancestor::form')
    form.locator('button[type="submit"]').click()
    page.wait_for_load_state('networkidle')


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    current_user = None

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1440, 'height': 900}, locale='es-MX')
        page = context.new_page()

        for cap in CAPTURAS:
            username = cap['login']
            if username and username != current_user:
                login_as(page, username)
                current_user = username
            elif not username and current_user:
                context.clear_cookies()
                current_user = None

            page.goto(f'{BASE_URL}{cap["path"]}')
            page.wait_for_load_state('networkidle')
            page.wait_for_timeout(400)
            target = OUT_DIR / cap['file']
            page.screenshot(path=str(target), full_page=True)
            print(f'OK {target.name}')

        browser.close()

    print(f'Capturas guardadas en {OUT_DIR}')


if __name__ == '__main__':
    main()
