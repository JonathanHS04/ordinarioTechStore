# Sistema Híbrido de E-commerce
**Proyecto Final - Bases de Datos Avanzadas**

## Descripción
Sistema de comercio electrónico que utiliza una arquitectura híbrida:
- **PostgreSQL**: Gestión de pedidos, usuarios y pagos (datos transaccionales)
- **MongoDB**: Catálogo de productos y logs (datos flexibles)
- **Python Flask**: Interfaz web y lógica de negocio

## Características Implementadas
✅ Transacciones distribuidas (Saga Pattern)
✅ Control de concurrencia optimista
✅ Seguridad (Usuarios y roles en ambas BD)
✅ Scripts de respaldo automatizados
✅ Conexión remota habilitada
✅ Índices y optimización de consultas

## Estructura del Proyecto
```
ordinario/
├── app/
│   ├── app.py              # Aplicación Flask principal
│   ├── db_manager.py       # Gestor de conexiones y transacciones
│   └── templates/          # Plantillas HTML
├── database/
│   ├── init_postgres.sql   # Inicialización PostgreSQL
│   ├── init_mongo.js       # Inicialización MongoDB
│   ├── security_postgres.sql
│   └── security_mongo.js
├── ops/
│   └── backup_script.py    # Script de respaldo
├── documentation.md        # Documentación completa del proyecto
├── verify_system.py        # Script de verificación
└── requirements.txt
```

## Instalación y Configuración

### Prerrequisitos
- Python 3.9+
- PostgreSQL 14+
- MongoDB 5+

### Pasos de Instalación

1. **Clonar/Descargar el proyecto**

2. **Instalar dependencias de Python**
```powershell
python -m venv venv
.\venv\Scripts\pip install -r requirements.txt
```

3. **Inicializar PostgreSQL**
```powershell
psql -U postgres -f database/init_postgres.sql
psql -U postgres -f database/security_postgres.sql
```

4. **Inicializar MongoDB**
```powershell
mongosh database/init_mongo.js
mongosh database/security_mongo.js
```

5. **Ejecutar la aplicación**
```powershell
.\venv\Scripts\python app/app.py
```

6. **Abrir en el navegador**
```
http://127.0.0.1:5000
```

## Uso del Sistema

### Navegación
- **Inicio**: Catálogo de productos (MongoDB)
- **Pedidos**: Historial de órdenes (PostgreSQL)

### Realizar una Compra
1. Seleccionar cantidad del producto
2. Hacer clic en "Comprar"
3. El sistema verifica stock en MongoDB
4. Crea el pedido en PostgreSQL
5. Actualiza el inventario en MongoDB

### Verificación del Sistema
Ejecutar el script de verificación:
```powershell
.\venv\Scripts\python verify_system.py
```

## Respaldo de Datos
Ejecutar el script de respaldo:
```powershell
python ops/backup_script.py
```

Esto generará:
- `backups/pg_backup_YYYYMMDD_HHMMSS.sql`
- `backups/mongo_backup_YYYYMMDD_HHMMSS/`

## Documentación Completa
Ver [documentation.md](documentation.md) para:
- Contexto y reglas de negocio
- Diseño de bases de datos
- Diccionario de datos
- Estrategia de respaldo
- Manual de usuario detallado

## Autores
Proyecto desarrollado para la materia de Bases de Datos Avanzadas por Jonathan Hillman Sánchez y Daniel Sandoval Castañeda
