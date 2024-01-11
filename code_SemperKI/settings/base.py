"""
Part of Semper-KI Software

Silvio Weging 2023

Contains: Extention of settings specific for Semper-KI
"""
import os

from main.settings.base import CSRF_TRUSTED_ORIGINS, CORS_ALLOWED_ORIGINS, CORS_ORIGIN_WHITELIST, BASE_DIR, TEMPLATES

###############################################################
CSRF_TRUSTED_ORIGINS.extend(["https://dev.semper-ki.org",
                        "https://semper-ki.org", "https://www.semper-ki.org", "https://backend.semper-ki.org",
                        "https://dev-backend.semper-ki.org", "https://localhost:3000", "https://127.0.0.1:3000", "http://localhost:3000", "http://127.0.0.1:3000"])

CORS_ALLOWED_ORIGINS.extend(["https://dev.semper-ki.org", "https://semper-ki.org", "https://www.semper-ki.org",
                        "https://backend.semper-ki.org", "https://dev-backend.semper-ki.org", "http://localhost:3000", "http://127.0.0.1:3000", "https://localhost:3000", "https://127.0.0.1:3000", 'https://dev-bdt24c5k0meleovv.eu.auth0.com'])

CORS_ORIGIN_WHITELIST.extend(["https://dev.semper-ki.org", "https://semper-ki.org", "https://www.semper-ki.org",
                         "https://backend.semper-ki.org", "https://dev-backend.semper-ki.org", 'http://localhost:3000', 'http://127.0.0.1:3000','https://dev-bdt24c5k0meleovv.eu.auth0.com'])

ADDITIONAL_TEMPLATE_DIR_SEMPER_KI = os.path.join(BASE_DIR, "code_SemperKI", "templates")
TEMPLATES[0]["DIRS"].append(ADDITIONAL_TEMPLATE_DIR_SEMPER_KI)