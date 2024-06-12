import os
import boto3
import cx_Oracle

# Environment variables
oracle_dsn = cx_Oracle.makedsn(
    os.getenv('ORACLE_HOST'), 
    os.getenv('ORACLE_PORT'), 
    service_name=os.getenv('ORACLE_SERVICE')
)
oracle_user = os.getenv('ORACLE_USER')
oracle_password = os.getenv('ORACLE_PASSWORD')
s3_bucket_name = os.getenv('S3_BUCKET_NAME')

# Local base directory for temporary files
local_base_directory = 'temp_local_directory'
os.makedirs(local_base_directory, exist_ok=True)

# AWS S3 client
s3 = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
)

# Connect to Oracle database
connection = cx_Oracle.connect(oracle_user, oracle_password, oracle_dsn)
cursor = connection.cursor()

# Query to fetch file data and hierarchical paths
query = "SELECT file_path, file_data FROM your_table"

cursor.execute(query)
for file_path, file_data in cursor:
    # Ensure the directory exists
    local_file_path = os.path.join(local_base_directory, file_path)
    os.makedirs(os.path.dirname(local_file_path), exist_ok=True)

    # Save file locally
    with open(local_file_path, 'wb') as file:
        file.write(file_data.read())

    # Upload the file to S3
    s3.upload_file(local_file_path, s3_bucket_name, file_path)

# Clean up
cursor.close()
connection.close()