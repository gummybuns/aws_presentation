"""
Build zip file used to update the deploy
"""
import os
import base64

def build_package():
    # Install dependencies
    os.system("rm -rf ./function.zip")

    # Add app code to zip file
    os.system("zip -g function.zip -r lambda_function.py")
    os.system("zip -g function.zip -r __init__.py")

    # Encode Zip file
    zip_file = open("function.zip", "rb")
    try:
        return zip_file.read()
    finally:
        zip_file.close()
