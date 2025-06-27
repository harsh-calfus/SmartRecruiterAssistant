import cloudinary
import cloudinary.uploader
import streamlit as st

cloudinary.config(
    cloud_name=st.secrets["CLOUD_NAME"],
    api_key=st.secrets["CLOUD_API_KEY"],
    api_secret=st.secrets["CLOUD_API_SECRET"]
)

def upload_to_cloudinary(file, file_name):
    result = cloudinary.uploader.upload(file, public_id=file_name, resource_type="raw")
    return result["secure_url"]

def delete_from_cloudinary(file_name):
    cloudinary.uploader.destroy(file_name, resource_type="raw")