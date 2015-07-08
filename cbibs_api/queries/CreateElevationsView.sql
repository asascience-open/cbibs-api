-- CreateElevationsView
DROP MATERIALIZED VIEW IF EXISTS cbibs.v_elevations;
CREATE materialized view cbibs.v_elevations as (
    select
        distinct on (o.d_station_id, o.d_variable_id, l.elevation)
        s.description,
        v.actual_name,
        l.elevation,
        pr.organization
    from cbibs.f_observation o
    join cbibs.d_variable v on v.id = o.d_variable_id
    join cbibs.d_location l on l.id = o.d_location_id
    join cbibs.d_station s on s.id = o.d_station_id
    join cbibs.d_provider pr on pr.id = s.d_provider_id
);
