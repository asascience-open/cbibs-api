-- ListParameters
WITH groups AS (
    SELECT
        DISTINCT ON (s.description, svs.d_variable_id)
        s.description,
        svs.d_variable_id
    FROM cbibs.d_sensor_variable_station svs
    JOIN cbibs.d_station s ON s.id = svs.d_station_id
    JOIN cbibs.d_provider pr ON pr.id = s.d_provider_id
    WHERE s.description='J'
        AND pr.organization = 'CBIBS'
)
SELECT
    v.actual_name
FROM cbibs.d_variable v
JOIN groups g ON v.id=g.d_variable_id;
