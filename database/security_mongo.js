// security_mongo.js
// Creación de usuarios y roles para MongoDB

// Usuario Administrador (en base de datos admin)
db = db.getSiblingDB('admin');
try { db.dropUser("adminUser"); } catch (e) { print("Usuario adminUser no existía o no se pudo borrar: " + e); }
db.createUser(
    {
        user: "adminUser",
        pwd: "adminPassword123",
        roles: [
            { role: "userAdminAnyDatabase", db: "admin" },
            { role: "readWriteAnyDatabase", db: "admin" }
        ]
    }
);

// Cambiar a base de datos del proyecto
db = db.getSiblingDB('ecommerce_db');

// Usuario de Aplicación (Backend)
try { db.dropUser("appUser"); } catch (e) { print("Usuario appUser no existía o no se pudo borrar: " + e); }
db.createUser(
    {
        user: "appUser",
        pwd: "appPassword123",
        roles: [
            { role: "readWrite", db: "ecommerce_db" }
        ]
    }
);

// Usuario Auditor (Solo lectura)
try { db.dropUser("auditorUser"); } catch (e) { print("Usuario auditorUser no existía o no se pudo borrar: " + e); }
db.createUser(
    {
        user: "auditorUser",
        pwd: "auditorPassword123",
        roles: [
            { role: "read", db: "ecommerce_db" }
        ]
    }
);
