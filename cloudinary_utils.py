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


def upload_to_cloudinary(file, file_name):
    result = cloudinary.uploader.upload(
        file, public_id=file_name, resource_type="raw"
    )
    return result["secure_url"]


def delete_from_cloudinary(file_name):
    cloudinary.uploader.destroy(file_name, resource_type="raw")


def fetch_pdf(file_name):
    url, _ = cloudinary.utils.cloudinary_url(
        file_name, resource_type="raw", type="upload"
    )
    r = requests.get(
        url, auth=(st.secrets["CLOUD_API_KEY"], st.secrets["CLOUD_API_SECRET"])
    )
    if r.status_code == 200:
        return base64.b64encode(r.content).decode()
    else:
        return None
