SELECT
    DISTINCT ON (o.measure_ts, measurement, l.elevation)
    o.measure_ts AT TIME ZONE 'UTC' as measure_ts,
    cbibs.depth_naming(v.actual_name, l.elevation) as measurement,
    o.obs_value,
    u.canonical_units,
    qc.qa_code as primary_qc
FROM cbibs.f_observation o
JOIN cbibs.d_variable v ON v.id=o.d_variable_id
JOIN cbibs.d_units u ON u.id = v.d_units_id
JOIN cbibs.d_location l ON l.id = o.d_location_id
JOIN cbibs.d_station s ON s.id = o.d_station_id
JOIN cbibs.d_provider pr ON pr.id = s.d_provider_id
JOIN cbibs.d_qa_code_primary qc ON qc.id = o.d_qa_code_primary_id
WHERE
    s.description = %(station)s
    AND o.measure_ts > %(start_date)s
    AND UPPER(pr.organization) = UPPER(%(constellation)s);

