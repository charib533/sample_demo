import cx_Oracle
import boto3
from botocore.exceptions import NoCredentialsError

# Oracle DB connection details
oracle_dsn = cx_Oracle.makedsn('hostname', 'port', service_name='service_name')
oracle_user = 'username'
oracle_password = 'password'

# AWS S3 details
s3_bucket_name = 'your-s3-bucket-name'
s3_folder_name = 'your-s3-folder-name'

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