import boto3
import streamlit as st
import re
import base64

# Initialize S3 client
s3 = boto3.client(
    "s3",
    aws_access_key_id=st.secrets["AWS_ACCESS_KEY_ID"],
    aws_secret_access_key=st.secrets["AWS_SECRET_ACCESS_KEY"],
    region_name=st.secrets["AWS_REGION"]
)

BUCKET_NAME = st.secrets["AWS_S3_BUCKET"]

def _sanitize_key(file_name: str) -> str:
    base = file_name.rsplit(".", 1)[0]
    return re.sub(r'[^0-9A-Za-z_-]', '_', base) + ".pdf"

def upload_to_s3(file, file_name: str) -> str:
    key = _sanitize_key(file_name)
    s3.upload_fileobj(file, BUCKET_NAME, key, ExtraArgs={"ContentType": "application/pdf"})
    return f"https://{BUCKET_NAME}.s3.{st.secrets['AWS_REGION']}.amazonaws.com/{key}"

def delete_from_s3(file_name: str):
    key = _sanitize_key(file_name)
    s3.delete_object(Bucket=BUCKET_NAME, Key=key)

def fetch_pdf(file_name: str) -> str | None:
    key = _sanitize_key(file_name)
    try:
        response = s3.get_object(Bucket=BUCKET_NAME, Key=key)
        return base64.b64encode(response["Body"].read()).decode()
    except s3.exceptions.NoSuchKey:
        return None
