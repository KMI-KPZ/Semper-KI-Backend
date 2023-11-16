"""
Part of Semper-KI Software

Silvio Weging 2023

Contains: Extention of settings specific for Semper-KI
"""

################################################################
CSRF_TRUSTED_ORIGINS.append("https://dev.semper-ki.org",
                        "https://semper-ki.org", "https://www.semper-ki.org", "https://backend.semper-ki.org",
                        "https://dev-backend.semper-ki.org")

CORS_ALLOWED_ORIGINS.append("https://dev.semper-ki.org", "https://semper-ki.org", "https://www.semper-ki.org",
                        "https://backend.semper-ki.org", "https://dev-backend.semper-ki.org")

CORS_ORIGIN_WHITELIST.append("https://dev.semper-ki.org", "https://semper-ki.org", "https://www.semper-ki.org",
                         "https://backend.semper-ki.org", "https://dev-backend.semper-ki.org")