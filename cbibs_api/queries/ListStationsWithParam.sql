-- ListStationsWithParam
SELECT 
    description
FROM cbibs.v_elevations
WHERE 
    cbibs.depth_naming(actual_name, elevation) = %(parameter)s
    AND organization = %(constellation)s;
