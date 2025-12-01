-- security_postgres.sql
-- Creación de roles y usuarios para PostgreSQL

-- Rol de Administrador (DBA)
CREATE ROLE admin_role WITH LOGIN PASSWORD 'admin_secure_pass';
ALTER ROLE admin_role SUPERUSER;

-- Rol de Aplicación (Para el backend)
CREATE ROLE app_role WITH LOGIN PASSWORD 'app_secure_pass';
GRANT CONNECT ON DATABASE postgres TO app_role; -- Ajustar nombre de DB si es necesario
GRANT USAGE ON SCHEMA public TO app_role;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_role;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO app_role;

-- Rol de Auditor (Solo lectura)
CREATE ROLE auditor_role WITH LOGIN PASSWORD 'auditor_pass';
GRANT CONNECT ON DATABASE postgres TO auditor_role;
GRANT USAGE ON SCHEMA public TO auditor_role;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO auditor_role;
