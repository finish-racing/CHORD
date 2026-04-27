DO $$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'chord') THEN
      CREATE ROLE chord LOGIN PASSWORD 'change_me';
   END IF;
END $$;

SELECT 'CREATE DATABASE chord OWNER chord'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'chord')\gexec
