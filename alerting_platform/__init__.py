# Make PyMySQL act as MySQLdb for Django when using MySQL/MariaDB
try:
    import pymysql
    pymysql.install_as_MySQLdb()
except Exception:
    # PyMySQL not installed or import failed — ignore to avoid crashing dev tools
    pass

# existing celery import (if present)
from .celery import app as celery_app
__all__ = ('celery_app',)