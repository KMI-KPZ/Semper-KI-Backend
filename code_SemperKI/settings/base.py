"""
Part of Semper-KI Software

Silvio Weging 2023

Contains: Extention of settings specific for Semper-KI
"""

from code_General.settings.base import CSRF_TRUSTED_ORIGINS, CORS_ALLOWED_ORIGINS, CORS_ORIGIN_WHITELIST

################################################################
CSRF_TRUSTED_ORIGINS.extend(["https://dev.semper-ki.org",
                        "https://semper-ki.org", "https://www.semper-ki.org", "https://backend.semper-ki.org",
                        "https://dev-backend.semper-ki.org"])

CORS_ALLOWED_ORIGINS.extend(["https://dev.semper-ki.org", "https://semper-ki.org", "https://www.semper-ki.org",
                        "https://backend.semper-ki.org", "https://dev-backend.semper-ki.org"])

CORS_ORIGIN_WHITELIST.extend(["https://dev.semper-ki.org", "https://semper-ki.org", "https://www.semper-ki.org",
                         "https://backend.semper-ki.org", "https://dev-backend.semper-ki.org"])
