#!/bin/sh
rm -rf data/*
if [ ! -d /data/databases/discover.db ]; then {
    read dataset_id dataset_version < <(echo $(curl -s 'https://api.blackfynn.io/discover/datasets/doi/'"${DOI}"'' | jq -r '.id,.version'))
    aws s3 cp s3://blackfynn-discover-use1/"$dataset_id"/"$dataset_version"/metadata . --request-payer requester --recursive;
    python3 parse_data.py
    neo4j-admin import @args.txt
    neo4j-admin set-initial-password test

    chown -R neo4j:neo4j /data

} fi
