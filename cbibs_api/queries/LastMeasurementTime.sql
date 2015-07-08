SELECT 
    measure_ts AT TIME ZONE 'UTC' 
FROM cbibs.f_observation o
JOIN cbibs.d_variable v ON v.id = o.d_variable_id
JOIN cbibs.d_station st ON st.id = o.d_station_id
JOIN cbibs.d_provider pr ON pr.id = st.d_provider_id
WHERE st.description = %(station)s 
    AND v.actual_name = %(measurement)s
    AND pr.organization = %(constellation)s
ORDER BY measure_ts DESC
LIMIT 1;
