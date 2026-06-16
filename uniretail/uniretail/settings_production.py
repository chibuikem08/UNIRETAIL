"""
Production settings — extend base settings.
Usage: set DJANGO_SETTINGS_MODULE=uniretail.settings_production
"""
from .settings import *

DEBUG = False

ALLOWED_HOSTS = [
    'yourdomain.com',
    'www.yourdomain.com',
    # Add your server IP or domain here
]

# Security headers
SECURE_BROWSER_XSS_FILTER       = True
SECURE_CONTENT_TYPE_NOSNIFF     = True
X_FRAME_OPTIONS                 = 'DENY'
SECURE_SSL_REDIRECT             = True
SESSION_COOKIE_SECURE           = True
CSRF_COOKIE_SECURE              = True

# Static files served by WhiteNoise (already configured)
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
