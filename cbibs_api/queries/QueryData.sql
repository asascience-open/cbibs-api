SELECT
    to_char(measure_ts AT TIME ZONE 'UTC', 'YYYY-MM-DD HH24:MI:SS') as time,
    obs_value as value,
    cbibs.depth_naming(v.actual_name, l.elevation) as measurement,
    u.canonical_units as units
FROM cbibs.f_observation o
JOIN cbibs.d_station s ON s.id = o.d_station_id
JOIN cbibs.d_location l ON l.id = o.d_location_id
JOIN cbibs.d_variable v on v.id = o.d_variable_id
JOIN cbibs.d_units u ON u.id = v.d_units_id
JOIN cbibs.d_provider pr ON pr.id = s.d_provider_id
JOIN cbibs.d_qa_code_primary qc ON qc.id = o.d_qa_code_primary_id
WHERE 
    measure_ts AT TIME ZONE 'UTC' > %(beg_date)s
    AND measure_ts AT TIME ZONE 'UTC' < %(end_date)s
    AND s.description = %(station)s
    AND UPPER(pr.organization) = UPPER(%(constellation)s)
    AND v.actual_name = %(measurement)s
    AND NOT (qc.qa_code = ANY ('{3,4}'))
ORDER BY measure_ts;
