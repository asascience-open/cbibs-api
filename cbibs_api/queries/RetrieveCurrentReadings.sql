WITH pivot AS (
    SELECT 
        MAX(measure_ts) maxtime,
        MIN(l.elevation) elevation,
        o.d_variable_id var_id
    FROM cbibs.f_observation o
    JOIN cbibs.d_station st ON o.d_station_id = st.id
    JOIN cbibs.d_provider pr ON pr.id = st.d_provider_id
    JOIN cbibs.d_location l ON l.id = o.d_location_id
    JOIN cbibs.d_variable v ON v.id = o.d_variable_id
    WHERE 
        o.measure_ts at time zone 'UTC' > (current_timestamp - '1 month'::interval)
        AND o.measure_ts at time zone 'UTC' < current_timestamp
        AND st.description = %(station)s
        AND pr.organization = %(constellation)s
        AND v.actual_name not in ('grid_latitude', 'grid_longitude', 'error_count')
    GROUP BY o.d_variable_id
)
SELECT
    v.actual_name AS measurement,
    to_char(
        o.measure_ts AT TIME ZONE 'UTC',
        'YYYY-MM-DD HH:MI:SS'
    ) AS "time",
    o.obs_value AS "value",
    u.netcdf units
FROM pivot p
JOIN cbibs.d_location l ON l.elevation = p.elevation
JOIN cbibs.f_observation o ON o.measure_ts = p.maxtime
    AND o.d_variable_id = p.var_id
    AND o.d_location_id = l.id
JOIN cbibs.d_station s ON s.id = o.d_station_id
JOIN cbibs.d_provider pr ON pr.id = s.d_provider_id
JOIN cbibs.d_variable v ON v.id = p.var_id
JOIN cbibs.d_units u ON u.id = v.d_units_id
WHERE
    s.description = %(station)s
    AND pr.organization = %(constellation)s
ORDER BY measurement;
