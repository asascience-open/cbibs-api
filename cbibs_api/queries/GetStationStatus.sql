SELECT 
    sm.status
FROM cbibs.d_station_metadata sm
JOIN cbibs.d_station s ON s.id = sm.d_station_id
JOIN cbibs.d_provider pr ON pr.id = s.d_provider_id
WHERE 
    s.description = %(station)s
    AND pr.organization = %(constellation)s
ORDER BY end_eff_ts
LIMIT 1;
