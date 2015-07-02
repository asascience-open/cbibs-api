-- CreateSupersets

DROP TABLE IF EXISTS cbibs.d_superset;
DROP TABLE IF EXISTS cbibs.d_superset_group_variable;
DROP TABLE IF EXISTS cbibs.d_superset_group;

CREATE TABLE cbibs.d_superset_group (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL
);

INSERT INTO cbibs.d_superset_group(name) VALUES
    ('water_quality'),
    ('waves'),
    ('meteorology');

CREATE TABLE cbibs.d_superset_group_variable(
    id SERIAL PRIMARY KEY,
    d_superset_group_id INT NOT NULL REFERENCES cbibs.d_superset_group,
    d_variable_id INT NOT NULL REFERENCES cbibs.d_variable
);

INSERT INTO cbibs.d_superset_group_variable(d_superset_group_id, d_variable_id) VALUES
    ((SELECT g.id FROM cbibs.d_superset_group g WHERE g.name = 'water_quality'), (SELECT v.id FROM cbibs.d_variable v WHERE v.actual_name = 'mass_concentration_of_chlorophyll_in_sea_water')),
    ((SELECT g.id FROM cbibs.d_superset_group g WHERE g.name = 'water_quality'), (SELECT v.id FROM cbibs.d_variable v WHERE v.actual_name = 'mass_concentration_of_oxygen_in_sea_water')),
    ((SELECT g.id FROM cbibs.d_superset_group g WHERE g.name = 'water_quality'), (SELECT v.id FROM cbibs.d_variable v WHERE v.actual_name = 'sea_water_salinity')),
    ((SELECT g.id FROM cbibs.d_superset_group g WHERE g.name = 'water_quality'), (SELECT v.id FROM cbibs.d_variable v WHERE v.actual_name = 'sea_water_temperature')),
    ((SELECT g.id FROM cbibs.d_superset_group g WHERE g.name = 'water_quality'), (SELECT v.id FROM cbibs.d_variable v WHERE v.actual_name = 'simple_turbidity')),
    ((SELECT g.id FROM cbibs.d_superset_group g WHERE g.name = 'waves'), (SELECT v.id FROM cbibs.d_variable v WHERE v.actual_name = 'current_average_direction')),
    ((SELECT g.id FROM cbibs.d_superset_group g WHERE g.name = 'waves'), (SELECT v.id FROM cbibs.d_variable v WHERE v.actual_name = 'current_average_velocity')),
    ((SELECT g.id FROM cbibs.d_superset_group g WHERE g.name = 'waves'), (SELECT v.id FROM cbibs.d_variable v WHERE v.actual_name = 'sea_surface_maximum_wave_height')),
    ((SELECT g.id FROM cbibs.d_superset_group g WHERE g.name = 'waves'), (SELECT v.id FROM cbibs.d_variable v WHERE v.actual_name = 'sea_surface_wave_from_direction')),
    ((SELECT g.id FROM cbibs.d_superset_group g WHERE g.name = 'waves'), (SELECT v.id FROM cbibs.d_variable v WHERE v.actual_name = 'sea_surface_wind_wave_period')),
    ((SELECT g.id FROM cbibs.d_superset_group g WHERE g.name = 'waves'), (SELECT v.id FROM cbibs.d_variable v WHERE v.actual_name = 'sea_water_temperature')),
    ((SELECT g.id FROM cbibs.d_superset_group g WHERE g.name = 'meteorology'), (SELECT v.id FROM cbibs.d_variable v WHERE v.actual_name = 'air_pressure')),
    ((SELECT g.id FROM cbibs.d_superset_group g WHERE g.name = 'meteorology'), (SELECT v.id FROM cbibs.d_variable v WHERE v.actual_name = 'air_temperature')),
    ((SELECT g.id FROM cbibs.d_superset_group g WHERE g.name = 'meteorology'), (SELECT v.id FROM cbibs.d_variable v WHERE v.actual_name = 'relative_humidity')),
    ((SELECT g.id FROM cbibs.d_superset_group g WHERE g.name = 'meteorology'), (SELECT v.id FROM cbibs.d_variable v WHERE v.actual_name = 'wind_from_direction')),
    ((SELECT g.id FROM cbibs.d_superset_group g WHERE g.name = 'meteorology'), (SELECT v.id FROM cbibs.d_variable v WHERE v.actual_name = 'wind_speed')),
    ((SELECT g.id FROM cbibs.d_superset_group g WHERE g.name = 'meteorology'), (SELECT v.id FROM cbibs.d_variable v WHERE v.actual_name = 'wind_speed_of_gust'));

CREATE TABLE cbibs.d_superset(
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    d_station_id INT NOT NULL REFERENCES cbibs.d_station,
    d_superset_group_id INT NOT NULL REFERENCES cbibs.d_superset_group
);

INSERT INTO cbibs.d_superset(name, d_station_id, d_superset_group_id) VALUES
    ('WQP', (SELECT s.id FROM cbibs.d_station s WHERE s.description = 'PL'), (SELECT g.id FROM cbibs.d_superset_group g WHERE g.name='water_quality')),
    ('OP', (SELECT s.id FROM cbibs.d_station s WHERE s.description = 'PL'), (SELECT g.id FROM cbibs.d_superset_group g WHERE g.name='waves')),
    ('METP', (SELECT s.id FROM cbibs.d_station s WHERE s.description = 'PL'), (SELECT g.id FROM cbibs.d_superset_group g WHERE g.name='meteorology')),
    ('WQJ', (SELECT s.id FROM cbibs.d_station s WHERE s.description = 'J'), (SELECT g.id FROM cbibs.d_superset_group g WHERE g.name='water_quality')),
    ('OJ', (SELECT s.id FROM cbibs.d_station s WHERE s.description = 'J'), (SELECT g.id FROM cbibs.d_superset_group g WHERE g.name='waves')),
    ('METJ', (SELECT s.id FROM cbibs.d_station s WHERE s.description = 'J'), (SELECT g.id FROM cbibs.d_superset_group g WHERE g.name='meteorology')),
    ('WQPA', (SELECT s.id FROM cbibs.d_station s WHERE s.description = 'SN'), (SELECT g.id FROM cbibs.d_superset_group g WHERE g.name='water_quality')),
    ('OPA', (SELECT s.id FROM cbibs.d_station s WHERE s.description = 'SN'), (SELECT g.id FROM cbibs.d_superset_group g WHERE g.name='waves')),
    ('METPA', (SELECT s.id FROM cbibs.d_station s WHERE s.description = 'SN'), (SELECT g.id FROM cbibs.d_superset_group g WHERE g.name='meteorology')),
    ('WQSP', (SELECT s.id FROM cbibs.d_station s WHERE s.description = 'SR'), (SELECT g.id FROM cbibs.d_superset_group g WHERE g.name='water_quality')),
    ('OSP', (SELECT s.id FROM cbibs.d_station s WHERE s.description = 'SR'), (SELECT g.id FROM cbibs.d_superset_group g WHERE g.name='waves')),
    ('METSP', (SELECT s.id FROM cbibs.d_station s WHERE s.description = 'SR'), (SELECT g.id FROM cbibs.d_superset_group g WHERE g.name='meteorology')),
    ('WQHDG', (SELECT s.id FROM cbibs.d_station s WHERE s.description = 'S'), (SELECT g.id FROM cbibs.d_superset_group g WHERE g.name='water_quality')),
    ('OHDG', (SELECT s.id FROM cbibs.d_station s WHERE s.description = 'S'), (SELECT g.id FROM cbibs.d_superset_group g WHERE g.name='waves')),
    ('METHDG', (SELECT s.id FROM cbibs.d_station s WHERE s.description = 'S'), (SELECT g.id FROM cbibs.d_superset_group g WHERE g.name='meteorology')),
    ('WQEQ', (SELECT s.id FROM cbibs.d_station s WHERE s.description = 'N'), (SELECT g.id FROM cbibs.d_superset_group g WHERE g.name='water_quality')),
    ('OEQ', (SELECT s.id FROM cbibs.d_station s WHERE s.description = 'N'), (SELECT g.id FROM cbibs.d_superset_group g WHERE g.name='waves')),
    ('METEQ', (SELECT s.id FROM cbibs.d_station s WHERE s.description = 'N'), (SELECT g.id FROM cbibs.d_superset_group g WHERE g.name='meteorology')),
    ('WQAN', (SELECT s.id FROM cbibs.d_station s WHERE s.description = 'AN'), (SELECT g.id FROM cbibs.d_superset_group g WHERE g.name='water_quality')),
    ('OAN', (SELECT s.id FROM cbibs.d_station s WHERE s.description = 'AN'), (SELECT g.id FROM cbibs.d_superset_group g WHERE g.name='waves')),
    ('METAN', (SELECT s.id FROM cbibs.d_station s WHERE s.description = 'AN'), (SELECT g.id FROM cbibs.d_superset_group g WHERE g.name='meteorology')),
    ('WQUP', (SELECT s.id FROM cbibs.d_station s WHERE s.description = 'UP'), (SELECT g.id FROM cbibs.d_superset_group g WHERE g.name='water_quality')),
    ('OUP', (SELECT s.id FROM cbibs.d_station s WHERE s.description = 'UP'), (SELECT g.id FROM cbibs.d_superset_group g WHERE g.name='waves')),
    ('METUP', (SELECT s.id FROM cbibs.d_station s WHERE s.description = 'UP'), (SELECT g.id FROM cbibs.d_superset_group g WHERE g.name='meteorology')),
    ('WQGR', (SELECT s.id FROM cbibs.d_station s WHERE s.description = 'GR'), (SELECT g.id FROM cbibs.d_superset_group g WHERE g.name='water_quality')),
    ('OGR', (SELECT s.id FROM cbibs.d_station s WHERE s.description = 'GR'), (SELECT g.id FROM cbibs.d_superset_group g WHERE g.name='waves')),
    ('METGR', (SELECT s.id FROM cbibs.d_station s WHERE s.description = 'GR'), (SELECT g.id FROM cbibs.d_superset_group g WHERE g.name='meteorology'));
