-- GetMetaDataLocation
SELECT
    l.latitude,
    l.longitude
FROM cbibs.f_observation o
JOIN cbibs.d_location l on l.id = o.d_location_id
JOIN cbibs.d_location_type lt on lt.id = o.d_location_type_id
JOIN cbibs.d_station s ON s.id = o.d_station_id
JOIN cbibs.d_provider pr ON pr.id = s.d_provider_id
JOIN cbibs.d_qa_code_primary qc ON qc.id = o.d_qa_code_primary_id
WHERE
    UPPER(pr.organization) = UPPER(%(constellation)s)
    AND s.description = %(station)s
    AND lt.location_type = 'Observed Latitude, Longitude, Station Elevation'
    AND qc.qa_code = 1
ORDER BY measure_ts
LIMIT 1;

