import os, secrets
from PIL import Image
from flask import current_app

def save_picture(form_picture):
    filename, file_extension = os.path.splitext(form_picture.filename)
    
    random_hex = secrets.token_hex(8)

    # # This line is to save the file so that s3 know where to extract it
    # form_picture.save(filename)

    # s3.upload_file(
    #     Bucket = BUCKET_NAME,
    #     Filename= filename,
    #     Key = random_hex + file_extension
    # )

    # # Remove the file after uploading
    # os.remove(filename)
    # return random_hex + file_extension
    
    picture_fn = random_hex + file_extension
    picture_path = os.path.join(current_app.root_path, 'static/uploads', picture_fn)
    output_size = (250, 250)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn
    