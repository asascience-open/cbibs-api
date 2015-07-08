-- ListParameters
SELECT
    cbibs.depth_naming(actual_name, elevation) as measurement
FROM cbibs.v_elevations
WHERE
    description = %(stationid)s
    AND organization = %(constellation)s
    -- We don't support depth binned parameters yet
    AND actual_name not in ('current_velocity', 'current_direction')
ORDER BY actual_name;

