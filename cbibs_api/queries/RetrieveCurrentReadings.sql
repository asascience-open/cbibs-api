-- RetrieveCurrentReadings
WITH pivot AS (
    SELECT 
        MAX(measure_ts) maxtime,
        o.d_variable_id var_id
    FROM cbibs.f_observation o
    JOIN cbibs.d_station st ON o.d_station_id = st.id
    JOIN cbibs.d_provider pr ON pr.id = st.d_provider_id
    JOIN cbibs.d_variable v ON v.id = o.d_variable_id
    WHERE 
        o.measure_ts at time zone 'UTC' > (current_timestamp - '1 month'::interval)
        AND o.measure_ts at time zone 'UTC' < current_timestamp
        AND st.description = %(station)s
        AND UPPER(pr.organization) = UPPER(%(constellation)s)
        AND v.actual_name not in ('grid_latitude', 'grid_longitude', 'error_count', 'current_velocity', 'current_direction')
    GROUP BY o.d_variable_id
)
SELECT
    cbibs.depth_naming(v.actual_name, l.elevation) AS measurement,
    to_char(
        o.measure_ts AT TIME ZONE 'UTC',
        'YYYY-MM-DD HH:MI:SS'
    ) AS time,
    o.obs_value AS value,
    u.canonical_units AS units
FROM pivot p
JOIN cbibs.f_observation o ON o.measure_ts = p.maxtime
    AND o.d_variable_id = p.var_id
JOIN cbibs.d_location l ON l.id = o.d_location_id
JOIN cbibs.d_station s ON s.id = o.d_station_id
JOIN cbibs.d_provider pr ON pr.id = s.d_provider_id
JOIN cbibs.d_variable v ON v.id = p.var_id
JOIN cbibs.d_units u ON u.id = v.d_units_id
JOIN cbibs.d_qa_code_primary qc ON qc.id = o.d_qa_code_primary_id
WHERE
    s.description = %(station)s
    AND UPPER(pr.organization) = UPPER(%(constellation)s)
    AND qc.qa_code = 1
ORDER BY measurement;
