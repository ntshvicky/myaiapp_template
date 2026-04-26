# Install PyMySQL as MySQLdb replacement only when using MySQL engine
import os
if os.environ.get("DATABASE_ENGINE", "sqlite").lower() == "mysql":
    try:
        import pymysql
        pymysql.install_as_MySQLdb()
    except ImportError:
        pass
