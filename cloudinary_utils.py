import re
import cloudinary
import cloudinary.uploader
import cloudinary.api
import streamlit as st
import base64
import requests

cloudinary.config(
    cloud_name=st.secrets["CLOUD_NAME"],
    api_key=st.secrets["CLOUD_API_KEY"],
    api_secret=st.secrets["CLOUD_API_SECRET"],
)

def _sanitize_public_id(file_name: str) -> str:
    # Remove file extension, replace invalid chars with underscore
    base = file_name.rsplit(".", 1)[0]
    return re.sub(r'[^0-9A-Za-z_-]', '_', base)

def upload_to_cloudinary(file, file_name: str) -> str:
    public_id = _sanitize_public_id(file_name)
    result = cloudinary.uploader.upload(
        file,
        public_id=public_id,
        resource_type="raw"
    )
    return result["secure_url"]

def delete_from_cloudinary(file_name: str):
    public_id = _sanitize_public_id(file_name)
    cloudinary.uploader.destroy(public_id, resource_type="raw")

def fetch_pdf(file_name: str) -> str | None:
    public_id = _sanitize_public_id(file_name)
    url, _ = cloudinary.utils.cloudinary_url(
        public_id, resource_type="raw", type="upload"
    )
    r = requests.get(
        url,
        auth=(st.secrets["CLOUD_API_KEY"], st.secrets["CLOUD_API_SECRET"])
    )
    if r.status_code == 200:
        return base64.b64encode(r.content).decode()
    return None
