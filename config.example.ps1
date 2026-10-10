# BookShop configuration example (MIG-RULE-010).
# Copy this file OUTSIDE the repository, replace the placeholder values, then dot-source it
# before running scripts\start.ps1, for example:   . $HOME\bookshop-config.ps1
# Never commit real secrets.

# Data directory (database, covers, logs). Must exist and be writable; keep it outside the repository.
$env:BOOKSHOP_DATA_DIR = Join-Path $HOME 'bookshop-data'

# Session signing key: at least 32 random bytes. Generate one with:
#   .venv\Scripts\python.exe -c "import secrets; print(secrets.token_hex(32))"
# The service refuses to start while this placeholder is still here.
$env:BOOKSHOP_SECRET_KEY = 'replace-with-64-hex-chars-from-python-secrets-token-hex-32'

# Listen address and port. Keep 127.0.0.1 unless you really need LAN access (COMP-001).
$env:BOOKSHOP_HOST = '127.0.0.1'
$env:BOOKSHOP_PORT = '8080'

# Only for the one-time "init-db"; set it in the console instead of this file if possible,
# and remove it afterwards. It must not be 123456.
# $env:BOOKSHOP_ADMIN_PASSWORD = '<choose an admin password>'
