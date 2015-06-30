SELECT st.description
    FROM d_station_variable_ob_stats sv
         JOIN d_station st ON st.id = sv.d_station_id
         JOIN d_provider pr ON pr.id = st.d_provider_id
         JOIN d_variable v ON v.id = sv.d_variable_id
    WHERE pr.organization = %(constellation)s AND
          v.actual_name = %(parameter)s;
