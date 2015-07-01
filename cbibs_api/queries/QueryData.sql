WITH get_units AS (
    SELECT 
        v.actual_name, 
        u.canonical_units 
    FROM cbibs.d_variable v 
    JOIN cbibs.d_units u ON u.id = v.d_units_id 
    WHERE v.actual_name = %(measurement)s
),
vals_rows AS (
    SELECT 
        measure_ts, 
        obs_value 
    FROM cbibs.f_observation o 
    JOIN cbibs.d_variable v ON v.id = o.d_variable_id 
    JOIN cbibs.d_station st ON st.id = o.d_station_id
    JOIN cbibs.d_provider pr ON pr.id = st.d_provider_id
    WHERE st.description = %(stationid)s 
        AND v.actual_name = %(measurement)s
        AND pr.organization = %(constellation)s 
        AND measure_ts AT TIME ZONE 'UTC' > %(beg_date)s AND  measure_ts AT TIME ZONE 'UTC' < %(end_date)s 
    ORDER BY measure_ts
),
vals_arr AS (
    SELECT 
        array_agg(to_char(measure_ts AT TIME ZONE 'UTC', 'YYYY-MM-DD HH24:MI:SS')) AS time, 
        array_agg(obs_value) AS value 
    FROM vals_rows
)
SELECT 
    row_to_json(t)
FROM (
    SELECT 
        actual_name AS "measurement",
        canonical_units AS "units",
        ( SELECT row_to_json(vals_arr) from vals_arr ) AS "values"
    FROM get_units
) t;
