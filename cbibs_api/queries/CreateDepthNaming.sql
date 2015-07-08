-- CreateDepthNaming
CREATE OR REPLACE FUNCTION cbibs.depth_naming(actual_name text, elevation double precision) RETURNS text AS $$
BEGIN
    IF elevation < -3 THEN
        RETURN actual_name || '_bottom';
    ELSE
        RETURN actual_name;
    END IF;
END;
$$ LANGUAGE plpgsql;

