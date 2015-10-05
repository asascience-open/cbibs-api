WITH supersets AS (
    SELECT
        sup.name,
        v.id as var_id,
        sup.d_station_id
    FROM cbibs.d_superset sup
    JOIN cbibs.d_superset_group sg ON sg.id=sup.d_superset_group_id
    JOIN cbibs.d_station s on s.id=sup.d_station_id
    JOIN cbibs.d_superset_group_variable sgv ON sgv.d_superset_group_id=sg.id
    JOIN cbibs.d_variable v on v.id=sgv.d_variable_id
    WHERE sup.name = %(superset)s
),
max_ident AS (
    SELECT
        MAX(measure_ts) maxtime,
        o.d_variable_id var_id
    FROM cbibs.f_observation o
    JOIN supersets sup ON sup.var_id = o.d_variable_id
        AND sup.d_station_id = o.d_station_id
    GROUP BY o.d_variable_id
)
SELECT 
    DISTINCT ON (v.actual_name, o.measure_ts, o.obs_value)
    v.actual_name AS measurement,
    to_char(
        o.measure_ts AT TIME ZONE 'UTC',
        'YYYY-MM-DD HH:MI:SS'
    ) AS "time",
    o.obs_value AS "value"
FROM cbibs.f_observation o
JOIN max_ident i ON i.maxtime = o.measure_ts
    AND i.var_id = o.d_variable_id
JOIN supersets sup ON sup.d_station_id = o.d_station_id
    AND sup.var_id = o.d_variable_id
JOIN cbibs.d_variable v ON v.id = o.d_variable_id
JOIN cbibs.d_station s ON s.id = o.d_station_id
JOIN cbibs.d_units u ON v.d_units_id = u.id;
