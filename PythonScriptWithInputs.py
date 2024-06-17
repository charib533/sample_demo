import argparse
import cx_Oracle
import boto3
import base64
from botocore.exceptions import NoCredentialsError

mime_types = {
    "js": "text/javascript",
    "dataservice": "text/javascript",
    "html": "text/html",
    "htm": "text/html",
    "ftl": "text/plain",
    "bsh": "text/plain",
    "css": "text/css",
    "png": "image/png",
    "eot": "application/vnd.ms-fontobject",
    "ttf": "application/x-font-ttf",
    "woff": "application/x-font-woff",
    "woff2": "application/x-font-woff",
    "gif": "image/gif",
    "ico": "image/x-icon",
    "svg": "image/svg+xml",
    "xml": "application/xml",
    "jpg": "image/jpeg",
    "swf": "application/x-shockwave-flash",
    "fla": "application/x-shockwave-flash",
    "otf": "application/x-font-otf",
    "map": "application/x-navimap",
    "doc": "application/msword",
    "dot": "application/msword",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "xls": "application/vnd.ms-excel",
    "xlt": "application/vnd.ms-excel",
    "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "ppt": "application/vnd.ms-powerpoint",
    "pot": "application/vnd.ms-powerpoint",
    "pps": "application/vnd.ms-powerpoint",
    "ppa": "application/vnd.ms-powerpoint",
    "txt": "text/plain"
}

# S3 client
s3 = boto3.client('s3')

def upload_to_s3(file_name, data, mime_type):
    try:
        s3.put_object(Bucket=s3_bucket_name, Key=f"{file_name}", Body=data, ContentType=mime_type)
        print(f"Successfully uploaded {file_name} to {s3_bucket_name}/{s3_folder_name}")
    except NoCredentialsError:
        print("Credentials not available")

def get_file_extension(filename):
    dot_index = filename.rindex(".") if "." in filename else 0
    return filename[dot_index+1:]


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

try:
    cursor = connection.cursor()
    # Query to get binary data and filenames
    eapp_query = f"SELECT content_name, content FROM uuidb.ui_content WHERE content_name like '{s3_folder_name}/%' AND content_type = 'CURRENT' order by last_modified_date desc"
    cursor.execute(eapp_query)
    for content_name, content in cursor:
        # Assuming filenames have the correct extensions, you can infer the MIME type
        mime_type = 'text/html'
        file_extension = get_file_extension(content_name)
        if file_extension.lower() in mime_types:
            mime_type = mime_types[file_extension.lower()]
            s3_content = base64.b64decode(content.read())
            upload_to_s3(content_name, s3_content, mime_type)
        else:
            mime_type = "text/plain"
            upload_to_s3(content_name, content.read(), mime_type)
        
finally:
    # Close Oracle connection
    print("finally block running...!")
    cursor.close()
    connection.close()


