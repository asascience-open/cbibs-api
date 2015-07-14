SELECT COUNT(*) 
FROM cbibs.f_observation o 
JOIN cbibs.d_variable v ON v.id = o.d_variable_id 
JOIN cbibs.d_station st ON st.id = o.d_station_id
JOIN cbibs.d_provider pr ON pr.id = st.d_provider_id
WHERE st.description = %(station)s 
    AND v.actual_name = %(measurement)s
    AND UPPER(pr.organization) = UPPER(%(constellation)s)
    AND measure_ts AT TIME ZONE 'UTC' > %(beg_date)s AND  measure_ts AT TIME ZONE 'UTC' < %(end_date)s;
