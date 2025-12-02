import subprocess
import os
from datetime import datetime

# Configuración
BACKUP_DIR = "backups"
PG_HOST = os.getenv('PG_HOST', 'localhost')
PG_USER = os.getenv('PG_USER', 'postgres') # Usar usuario con privilegios de backup
PG_DB = os.getenv('PG_DB', 'postgres')
MONGO_HOST = os.getenv('MONGO_HOST', 'localhost')
MONGO_PORT = os.getenv('MONGO_PORT', '27017')
MONGO_DB = os.getenv('MONGO_DB_NAME', 'ecommerce_db')

def create_backup_dir():
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)

def backup_postgres():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{BACKUP_DIR}/pg_backup_{timestamp}.sql"
    
    pg_dump_path = r"C:\Program Files\PostgreSQL\17\bin\pg_dump.exe"
    if not os.path.exists(pg_dump_path):
        pg_dump_path = "pg_dump"
        
    cmd = f'"{pg_dump_path}" -h {PG_HOST} -U {PG_USER} -d {PG_DB} -f {filename}'
    
    print(f"Iniciando backup PostgreSQL: {filename}")
    try:
        subprocess.run(cmd, shell=True, check=True)
        print("Backup PostgreSQL exitoso.")
    except subprocess.CalledProcessError as e:
        print(f"Error en backup PostgreSQL: {e}")

def backup_mongo():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = f"{BACKUP_DIR}/mongo_backup_{timestamp}"

    possible_paths = [
        r"C:\Users\jonat\Downloads\mongodb-database-tools-windows-x86_64-100.13.0\mongodb-database-tools-windows-x86_64-100.13.0\bin\mongodump.exe",
        r"C:\Program Files\MongoDB\Tools\100\bin\mongodump.exe",
        r"C:\Program Files\MongoDB\Server\7.0\bin\mongodump.exe", # Ajustar versión si es necesario
        r"C:\Program Files\MongoDB\Server\6.0\bin\mongodump.exe",
        "mongodump"
    ]
    
    mongodump_path = "mongodump"
    for path in possible_paths:
        if os.path.exists(path) and path.endswith('.exe'):
            mongodump_path = path
            break

    cmd = f'"{mongodump_path}" --host {MONGO_HOST} --port {MONGO_PORT} --db {MONGO_DB} --out {output_dir}'
    
    print(f"Iniciando backup MongoDB: {output_dir}")
    try:
        subprocess.run(cmd, shell=True, check=True)
        print("Backup MongoDB exitoso.")
    except subprocess.CalledProcessError as e:
        print(f"Error en backup MongoDB: {e}")

if __name__ == "__main__":
    create_backup_dir()
    print("--- Iniciando Proceso de Respaldo ---")
    backup_postgres()
    backup_mongo()
    print("--- Proceso Finalizado ---")
