-- ListParameters
SELECT
    cbibs.depth_naming(actual_name, elevation) as measurement
FROM cbibs.v_elevations
WHERE
    description = %(station)s
    AND UPPER(organization) = UPPER(%(constellation)s)
    -- We don't support depth binned parameters yet
    AND actual_name not in ('current_velocity', 'current_direction', 'error_count', 'grid_latitude', 'grid_longitude')
ORDER BY actual_name;

