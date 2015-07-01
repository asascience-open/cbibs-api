WITH max_ident AS
    (SELECT MAX(measure_ts) maxtime, o.d_variable_id var_id
         FROM f_observation o
              JOIN d_station st ON o.d_station_id = st.id
              JOIN d_provider pr ON pr.id = st.d_provider_id
         WHERE st.description = %(station)s 
               AND pr.organization = %(constellation)s 
         GROUP BY o.d_variable_id)
SELECT v.actual_name AS measurement,
                          to_char(o.measure_ts AT TIME ZONE 'UTC',
                                  'YYYY-MM-DD HH:MI:SS') AS "time",
                          o.obs_value AS "value", u.netcdf units
      FROM f_observation O
           JOIN max_ident ON o.measure_ts = max_ident.maxtime AND
                             o.d_variable_id = max_ident.var_id
           JOIN d_variable v ON v.id = o.d_variable_id
           JOIN d_units u ON v.d_units_id = u.id;
