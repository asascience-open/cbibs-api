-- Lists descriptions of stations
SELECT 
    st.description id, 
    st.site_name cn 
FROM 
    cbibs.d_station st 
JOIN cbibs.d_provider pr ON pr.id = st.d_provider_id 
WHERE organization = %(constellation)s ORDER BY 1;
