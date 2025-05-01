# bookings/templatetags/vite.py
from django import template
from django.conf import settings
import json
import os

register = template.Library()

@register.simple_tag
def vite_asset(asset_name):
    manifest_path = os.path.join(settings.STATIC_ROOT, 'manifest.json')

    try:
        with open(manifest_path, 'r') as manifest_file:
            manifest = json.load(manifest_file)
        asset_file = manifest[asset_name]['file']
        return f'<link rel="stylesheet" href="{settings.STATIC_URL}{asset_file}" />'
    except Exception as e:
        return f'<!-- Vite asset error: {e} -->'

@register.simple_tag
def vite_hmr_client():
    if settings.DEBUG:
        return '<script type="module" src="http://localhost:5173/@vite/client"></script>'
    return ''
