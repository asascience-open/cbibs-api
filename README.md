# cbibs-api
Chesapeake Bay Interpretive Buoy System Public API


## Migrating Database Changes

You'll need to run "CreateSupersets.sql" on the database you wish to use the API with.


```
REFRESH MATERIALIZED VIEW cbibs.v_elevations;
```
