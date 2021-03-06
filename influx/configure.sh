#!/bin/bash

# Discord


for DB_NAME in trade_api characters;
    do
        echo "Create $DB_NAME DB"
        influx -execute "CREATE DATABASE $DB_NAME"
        echo "Create $DB_NAME DB policies"
        influx -execute "ALTER RETENTION POLICY autogen ON $DB_NAME DURATION 3d REPLICATION 1 SHARD DURATION 1d DEFAULT"
        influx -execute "CREATE RETENTION POLICY a_week ON $DB_NAME DURATION 7d REPLICATION 1 SHARD DURATION 1d"
        influx -execute "CREATE RETENTION POLICY a_month ON $DB_NAME DURATION 31d REPLICATION 1 SHARD DURATION 1d"
        influx -execute "CREATE RETENTION POLICY a_year ON $DB_NAME DURATION 52w REPLICATION 1 SHARD DURATION 1w"
        influx -execute "CREATE RETENTION POLICY forever ON $DB_NAME DURATION inf REPLICATION 1 SHARD DURATION 1w"
        echo "Create $DB_NAME CQs"
        influx -execute "CREATE CONTINUOUS QUERY \"cq_10s\" ON \"$DB_NAME\" BEGIN SELECT mean(*),min(*),max(*) INTO \"$DB_NAME\".\"a_week\".:MEASUREMENT FROM /.*/ GROUP BY time(10s),* END"
        influx -execute "CREATE CONTINUOUS QUERY \"cq_1min\" ON \"$DB_NAME\" BEGIN SELECT mean(*),min(*),max(*) INTO \"$DB_NAME\".\"a_month\".:MEASUREMENT FROM /.*/ GROUP BY time(1m),* END"
        influx -execute "CREATE CONTINUOUS QUERY \"cq_10min\" ON \"$DB_NAME\" BEGIN SELECT mean(*),min(*),max(*) INTO \"$DB_NAME\".\"a_year\".:MEASUREMENT FROM /.*/ GROUP BY time(10m),* END"
        influx -execute "CREATE CONTINUOUS QUERY \"cq_1hr\" ON \"$DB_NAME\" BEGIN SELECT mean(*),min(*),max(*) INTO \"$DB_NAME\".\"forever\".:MEASUREMENT FROM /.*/ GROUP BY time(1h),* END"
    done