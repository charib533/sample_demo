#!/bin/bash

set -e

# Environment variables
ORACLE_HOST="$1"
ORACLE_PORT="$2"
ORACLE_SERVICE="$3"
ORACLE_USER="$4"
ORACLE_PASSWORD="$5"
S3_BUCKET_NAME="$6"
LOCAL_BASE_DIRECTORY="temp_local_directory"

# Create the local base directory if it doesn't exist
mkdir -p $LOCAL_BASE_DIRECTORY

# Oracle connection string
ORACLE_CONN_STRING="$ORACLE_USER/$ORACLE_PASSWORD@(DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)(HOST=$ORACLE_HOST)(PORT=$ORACLE_PORT))(CONNECT_DATA=(SERVICE_NAME=$ORACLE_SERVICE)))"

# Query to fetch file data and hierarchical paths
QUERY="SELECT file_path, file_data FROM your_table"

# Execute the query and process the results
sqlplus -s $ORACLE_CONN_STRING <<EOF | while read file_path file_data; do
SET HEADING OFF
SET FEEDBACK OFF
SET LINESIZE 32767
SET PAGESIZE 0
SET LONG 2000000000
SET LONGCHUNKSIZE 2000000000
SET TRIMSPOOL ON
SET TRIMOUT ON
SET WRAP OFF
SET TERMOUT OFF
$QUERY;
EOF
    # Ensure the directory exists
    local_file_path="$LOCAL_BASE_DIRECTORY/$file_path"
    mkdir -p "$(dirname "$local_file_path")"
    
    # Decode the base64 data and save it locally
    echo "$file_data" | base64 -d > "$local_file_path"

    # Upload the file to S3
    aws s3 cp "$local_file_path" "s3://$S3_BUCKET_NAME/$file_path"
done