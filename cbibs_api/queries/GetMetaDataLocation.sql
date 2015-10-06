-- GetMetaDataLocation
SELECT
    l.latitude,
    l.longitude
FROM cbibs.d_station s
JOIN cbibs.d_location l on l.id = s.d_location_id
JOIN cbibs.d_provider pr ON pr.id = s.d_provider_id
WHERE
    UPPER(pr.organization) = UPPER(%(constellation)s)
    AND s.description = %(station)s
LIMIT 1;

