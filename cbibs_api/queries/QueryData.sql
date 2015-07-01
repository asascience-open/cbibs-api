WITH get_units AS (SELECT v.actual_name, u.canonical_units FROM d_variable v JOIN d_units u ON u.id = v.d_units_id WHERE v.actual_name = %(measurement)s),
vals_rows AS (SELECT measure_ts, obs_value FROM f_observation o JOIN d_variable v ON v.id = o.d_variable_id JOIN d_station st ON st.id = o.d_station_id           JOIN d_provider pr ON pr.id = st.d_provider_id
    WHERE st.description = %(stationid)s AND v.actual_name = %(measurement)s
    AND pr.organization = %(constellation)s AND measure_ts BETWEEN %(beg_date)s AND %(end_date)s ORDER BY measure_ts                                                    ),
vals_arr AS (select array_agg(to_char(measure_ts AT TIME ZONE 'UTC', 'YYYY-MM-DD HH24:MI:SS')) AS time, array_agg(obs_value) AS value FROM vals_rows)         SELECT json_build_object('measurement', actual_name, 'units', canonical_units, 'values', (SELECT row_to_json(vals_arr) FROM vals_arr)) FROM get_units;
