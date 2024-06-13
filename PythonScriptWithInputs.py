import argparse
import cx_Oracle
import boto3
from botocore.exceptions import NoCredentialsError

# Set up argument parser
parser = argparse.ArgumentParser(description="Extract binary files from Oracle DB and upload to S3")
parser.add_argument('--oracle-host', required=True, help='Oracle DB hostname')
parser.add_argument('--oracle-port', required=True, help='Oracle DB port')
parser.add_argument('--oracle-service', required=True, help='Oracle DB service name')
parser.add_argument('--oracle-user', required=True, help='Oracle DB username')
parser.add_argument('--oracle-password', required=True, help='Oracle DB password')
parser.add_argument('--s3-bucket', required=True, help='S3 bucket name')
parser.add_argument('--s3-folder', required=True, help='S3 folder name')

args = parser.parse_args()

# Oracle DB connection details
oracle_dsn = cx_Oracle.makedsn(args.oracle_host, args.oracle_port, service_name=args.oracle_service)
oracle_user = args.oracle_user
oracle_password = args.oracle_password

# AWS S3 details
s3_bucket_name = args.s3_bucket
s3_folder_name = args.s3_folder

# Establish connection to Oracle database
connection = cx_Oracle.connect(user=oracle_user, password=oracle_password, dsn=oracle_dsn)
cursor = connection.cursor()

# Query to get binary data and filenames (assuming you have columns for binary data and filenames)
query = "SELECT filename, filedata FROM your_table"
cursor.execute(query)

# S3 client
s3 = boto3.client('s3')

def upload_to_s3(file_name, data, mime_type):
    try:
        s3.put_object(Bucket=s3_bucket_name, Key=f"{s3_folder_name}/{file_name}", Body=data, ContentType=mime_type)
        print(f"Successfully uploaded {file_name} to {s3_bucket_name}/{s3_folder_name}")
    except NoCredentialsError:
        print("Credentials not available")

for filename, filedata in cursor:
    # Assuming filenames have the correct extensions, you can infer the MIME type
    mime_type = 'application/octet-stream'
    if filename.endswith('.png'):
        mime_type = 'image/png'
    elif filename.endswith('.jpg') or filename.endswith('.jpeg'):
        mime_type = 'image/jpeg'
    elif filename.endswith('.ico'):
        mime_type = 'image/x-icon'
    # Add more conditions as needed

    # Upload to S3
    upload_to_s3(filename, filedata.read(), mime_type)

# Close Oracle connection
cursor.close()
connection.close()