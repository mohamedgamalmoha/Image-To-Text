import os
from werkzeug.utils import secure_filename

from web import BASE_DIR


def save_image(image, directory: str = 'images') -> None:
    # Get image`s name & path
    filename = secure_filename(image.filename)
    path = os.path.join(BASE_DIR, directory)
    # Check the existence of the dir, otherwise create it
    if not os.path.exists(path):
        os.makedirs(path)
    # Save the image in local storage
    filedir = os.path.join(path, filename)
    with open(filedir, 'wb') as f:
        f.write(image.read())
