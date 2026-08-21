#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.database import DatabaseManager

def create_table():
    db = DatabaseManager()
    print(f"MySQL ready: {db.mysql_ready}")
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS adulto_cuidador (
        id INT AUTO_INCREMENT PRIMARY KEY,
        id_adulto INT NOT NULL,
        id_cuidador INT NOT NULL,
        fecha_vinculo DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        activo TINYINT(1) NOT NULL DEFAULT 1,
        observaciones TEXT NULL,
        UNIQUE KEY uk_adulto_cuidador (id_adulto, id_cuidador),
        CONSTRAINT fk_adulto_cuidador_adulto FOREIGN KEY (id_adulto) REFERENCES adulto_mayor(id) ON DELETE CASCADE,
        CONSTRAINT fk_adulto_cuidador_cuidador FOREIGN KEY (id_cuidador) REFERENCES cuidador(id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    result = db.ejecutar_mysql(create_table_sql)
    print(f"Table creation result: {result}")
    # Check if table exists
    tables = db.ejecutar_mysql("SHOW TABLES LIKE 'adulto_cuidador'")
    print(f"Table exists: {tables}")
    return True

if __name__ == "__main__":
    create_table()