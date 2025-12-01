# Documentación del Proyecto: Sistema Híbrido de E-commerce

## 1. Contexto y Reglas de Negocio
**Contexto:**
El sistema es una plataforma de comercio electrónico diseñada para manejar un alto volumen de productos y transacciones seguras. Utiliza una arquitectura híbrida para aprovechar lo mejor de dos mundos: la integridad transaccional de las bases de datos relacionales (PostgreSQL) y la flexibilidad de esquema de las bases de datos NoSQL (MongoDB).

**Reglas de Negocio:**
1.  **Inventario:** El stock de productos se gestiona en MongoDB. No se puede vender un producto sin stock.
2.  **Pedidos:** Los pedidos se registran en PostgreSQL para garantizar consistencia financiera.
3.  **Transacciones:** La creación de un pedido implica una transacción distribuida: se debe reservar stock en MongoDB y crear el registro de pedido en PostgreSQL. Si una falla, la otra debe revertirse (o no completarse).
4.  **Usuarios:** Existen roles de Administrador (gestión total), Cliente (compras) y Auditor (solo lectura).

## 2. Tecnología Utilizada
*   **Base de Datos Relacional:** PostgreSQL 14+
    *   *Justificación:* Manejo robusto de transacciones ACID, integridad referencial para pedidos y pagos.
*   **Base de Datos No Relacional:** MongoDB 5+
    *   *Justificación:* Esquema flexible para atributos de productos variados, alta velocidad de lectura para el catálogo.
*   **Lenguaje de Programación:** Python 3.9+
    *   *Framework:* Flask (Web)
    *   *Drivers:* `psycopg2` (PostgreSQL), `pymongo` (MongoDB)

## 3. Diseño de Bases de Datos y Concurrencia

### PostgreSQL (Relacional)
*   **Tablas:** `users`, `orders`, `order_items`, `payments`.
*   **Mitigación de Concurrencia:** Se utiliza el nivel de aislamiento por defecto (Read Committed). Para operaciones críticas de saldo o inventario (si estuviera aquí), se usarían bloqueos de fila (`FOR UPDATE`).

### MongoDB (No Relacional)
*   **Colecciones:** `products`, `reviews`, `audit_logs`.
*   **Mitigación de Concurrencia:** Se utiliza **Optimistic Locking** y operaciones atómicas.
    *   *Ejemplo:* Al reducir stock, la consulta busca `{ _id: ..., stock: { $gte: cantidad } }`. Si otro usuario compró el último ítem milisegundos antes, la condición `$gte` fallará y la actualización retornará 0 documentos modificados, permitiendo a la aplicación manejar el error sin inconsistencias.

## 4. Diccionario de Datos (Resumen)

### PostgreSQL - Tabla `orders`
| Campo | Tipo | Descripción |
|-------|------|-------------|
| order_id | SERIAL (PK) | Identificador único del pedido |
| user_id | INT (FK) | ID del usuario que compra |
| total_amount | DECIMAL | Monto total de la compra |
| status | VARCHAR | Estado: pending, paid, shipped |

### MongoDB - Colección `products`
| Campo | Tipo | Descripción |
|-------|------|-------------|
| _id | ObjectId | Identificador único |
| name | String | Nombre del producto |
| price | Double | Precio unitario |
| stock | Int | Cantidad disponible |
| attributes | Object | Objeto anidado con detalles variables |

## 5. Diseño y Justificación de Respaldo Remoto
**Estrategia:**
Se implementa un script en Python (`ops/backup_script.py`) que ejecuta `pg_dump` y `mongodump`.
*   **Justificación:** Permite automatizar la tarea mediante CRON (Linux) o Task Scheduler (Windows).
*   **Respaldo Remoto:** Los archivos generados se deben enviar a un servidor de almacenamiento seguro (ej. AWS S3 o un servidor FTP dedicado) para cumplir con la regla de "3-2-1" (3 copias, 2 medios, 1 fuera del sitio). El script actual guarda en local, pero es trivialmente extensible para subir el archivo resultante a la nube usando `boto3` o `scp`.

## 6. Manual de Usuario
1.  **Instalación:**
    *   Instalar Python, PostgreSQL y MongoDB.
    *   Ejecutar `pip install -r requirements.txt`.
    *   Inicializar BDs con los scripts en `/database`.
2.  **Ejecución:**
    *   Correr `.\venv\Scripts\python app/app.py`.
    *   Abrir navegador en `http://localhost:5000`.
3.  **Uso:**
    *   **Ver Productos:** Página de inicio.
    *   **Comprar:** Ingresar cantidad y clic en "Comprar". Si hay stock, se procesa.
    *   **Ver Pedidos:** Ir a la pestaña "Pedidos" para ver el historial transaccional.
