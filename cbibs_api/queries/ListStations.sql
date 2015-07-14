-- Lists descriptions of stations
SELECT 
    st.description 
FROM d_station st 
JOIN d_provider pr ON pr.id = st.d_provider_id 
WHERE UPPER(organization) = UPPER(:constellation);
