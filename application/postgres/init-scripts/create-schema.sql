CREATE TABLE t_means_of_transport (
    uuid VARCHAR(36) NOT NULL PRIMARY KEY,
    identifier VARCHAR(20) NOT NULL UNIQUE
);

CREATE TABLE t_stations (
    uuid VARCHAR(36) NOT NULL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE t_lines (
    uuid VARCHAR(36) NOT NULL PRIMARY KEY,
    label VARCHAR(5) NOT NULL UNIQUE,
    means_of_transport_uuid VARCHAR(36) NOT NULL,
    terminal_stop_one_uuid VARCHAR(36) NOT NULL,
	terminal_stop_two_uuid VARCHAR(36) NOT NULL,
    CONSTRAINT means_of_transport_fk FOREIGN KEY (means_of_transport_uuid) REFERENCES t_means_of_transport(uuid),
    CHECK (terminal_stop_one_uuid <> terminal_stop_two_uuid),
	CONSTRAINT terminal_stop_one_fk FOREIGN KEY (terminal_stop_one_uuid) REFERENCES t_stations(uuid),
	CONSTRAINT terminal_stop_two_fk FOREIGN KEY (terminal_stop_two_uuid) REFERENCES t_stations(uuid)
);

CREATE TABLE t_edges (
    uuid VARCHAR(36) NOT NULL PRIMARY KEY,
    start_station_uuid VARCHAR(36) NOT NULL,
    end_station_uuid VARCHAR(36) NOT NULL,
    line_uuid VARCHAR(36) NOT NULL,
    distance_min INTEGER NOT NULL,
    CONSTRAINT line_fk FOREIGN KEY (line_uuid) REFERENCES t_lines(uuid) ON DELETE CASCADE,
    CHECK (distance_min > 0),
    CONSTRAINT start_station_fk FOREIGN KEY (start_station_uuid) REFERENCES t_stations(uuid),
    CONSTRAINT end_station_fk FOREIGN KEY (end_station_uuid) REFERENCES t_stations(uuid),
    CHECK (start_station_uuid <> end_station_uuid),
    CONSTRAINT edge_uk UNIQUE(start_station_uuid, end_station_uuid, line_uuid)
);
