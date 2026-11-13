-- Esquema del demostrador (PostgreSQL / Supabase).
-- Generado desde demostrador/models.py: si cambian los modelos, se regenera.
-- Uso: pegar en el SQL Editor de Supabase y ejecutar una sola vez.
-- La aplicación también crea las tablas al arrancar si no existen.

CREATE TABLE IF NOT EXISTS t_configuracion (
	codigo VARCHAR(20) NOT NULL, 
	usa_cache BOOLEAN NOT NULL, 
	usa_mirror BOOLEAN NOT NULL, 
	id BIGINT GENERATED ALWAYS AS IDENTITY, 
	uuid UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	deleted_at TIMESTAMP WITH TIME ZONE, 
	PRIMARY KEY (id), 
	UNIQUE (codigo), 
	UNIQUE (uuid)
);

CREATE TABLE IF NOT EXISTS t_lista_paquete (
	version VARCHAR(20) NOT NULL, 
	descripcion VARCHAR(200) NOT NULL, 
	id BIGINT GENERATED ALWAYS AS IDENTITY, 
	uuid UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	deleted_at TIMESTAMP WITH TIME ZONE, 
	PRIMARY KEY (id), 
	UNIQUE (version), 
	UNIQUE (uuid)
);

CREATE TABLE IF NOT EXISTS t_sesion (
	configuracion_id BIGINT NOT NULL, 
	lista_paquete_id BIGINT NOT NULL, 
	n_estaciones INTEGER NOT NULL, 
	es_calentamiento BOOLEAN NOT NULL, 
	entorno VARCHAR(20) NOT NULL, 
	salidas_origen INTEGER NOT NULL, 
	sincronizacion_mirror INTEGER NOT NULL, 
	bytes_salida BIGINT, 
	iniciada_en TIMESTAMP WITH TIME ZONE NOT NULL, 
	id BIGINT GENERATED ALWAYS AS IDENTITY, 
	uuid UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	deleted_at TIMESTAMP WITH TIME ZONE, 
	PRIMARY KEY (id), 
	CONSTRAINT ck_sesion_n CHECK (n_estaciones BETWEEN 1 AND 30), 
	FOREIGN KEY(configuracion_id) REFERENCES t_configuracion (id) ON DELETE RESTRICT, 
	FOREIGN KEY(lista_paquete_id) REFERENCES t_lista_paquete (id) ON DELETE RESTRICT, 
	UNIQUE (uuid)
);

CREATE TABLE IF NOT EXISTS t_observacion (
	sesion_id BIGINT NOT NULL, 
	estacion INTEGER NOT NULL, 
	segundos NUMERIC(10, 4) NOT NULL, 
	aciertos INTEGER NOT NULL, 
	errores INTEGER NOT NULL, 
	id BIGINT GENERATED ALWAYS AS IDENTITY, 
	uuid UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	deleted_at TIMESTAMP WITH TIME ZONE, 
	PRIMARY KEY (id), 
	CONSTRAINT uq_observacion_sesion_estacion UNIQUE (sesion_id, estacion), 
	CONSTRAINT ck_observacion_segundos CHECK (segundos > 0), 
	CONSTRAINT ck_observacion_estacion CHECK (estacion >= 1), 
	FOREIGN KEY(sesion_id) REFERENCES t_sesion (id) ON DELETE RESTRICT, 
	UNIQUE (uuid)
);

CREATE INDEX IF NOT EXISTS ix_t_observacion_sesion_id ON t_observacion (sesion_id);

-- Seguridad: RLS activo y sin políticas. La API pública de Supabase no ve
-- estas tablas; solo entra la aplicación con DATABASE_URL.
ALTER TABLE t_configuracion ENABLE ROW LEVEL SECURITY;
ALTER TABLE t_lista_paquete ENABLE ROW LEVEL SECURITY;
ALTER TABLE t_sesion ENABLE ROW LEVEL SECURITY;
ALTER TABLE t_observacion ENABLE ROW LEVEL SECURITY;
