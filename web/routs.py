import time
import platform

import pytesseract
from PIL import Image
from flask import request, url_for
from flask_restful import Resource
from flask_jwt_extended import jwt_required, create_access_token

from web import db, SAVE_IMAGE
from web.utils import save_image
from web.status import HTTPStatus
from web.models import User, user_exists
from web.forms import SignupForm, LoginForm


if platform.system() == 'Windows':
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


class LoginAPI(Resource):
    form_cls = LoginForm

    def post(self):
        form = self.form_cls(request.form)
        if form.validate():
            email, password = form.email.data, form.password.data
            user = user_exists(email=email, password=password)
            if not user:
                return {'message': 'Invalid email or password'}, HTTPStatus.UNAUTHORIZED
            access_token = create_access_token(identity=user.email)
            user_info = user.as_dict()
            user_info.update({'access_token': access_token})
            return user_info, HTTPStatus.OK
        return {'message': form.form_errors}, HTTPStatus.BAD_REQUEST


class SignupAPI(Resource):
    form_cls = SignupForm

    def post(self):
        form = self.form_cls(request.form)
        if form.validate():
            email, password = form.email.data, form.password.data
            user = user_exists(email=email, password=password)
            if user:
                return {'message': 'Email already exists'}, HTTPStatus.CONFLICT
            user = User.create_user(**form.as_dict())
            db.session.add(user)
            db.session.commit()
            return {'message': 'User has successfully created', 'login': url_for('login', _external=True)}, HTTPStatus.CREATED
        return {'message': form.errors}, HTTPStatus.OK


class ExtractTextAPI(Resource):

    @jwt_required()
    def post(self):
        # Parse the request to get the uploaded image file
        image = request.files.get('image', None)
        if image is None:
            return {'message': 'Image field is required'}, HTTPStatus.BAD_REQUEST
        # Save image
        if SAVE_IMAGE:
            save_image(image)
        # Open the image using Pillow
        image = Image.open(image)
        # Start time of extraction
        start_time = time.monotonic()
        # Extract text from the image using pytesseract
        text = pytesseract.image_to_string(image)
        # End time of extraction
        end_time = time.monotonic()
        # Get confidence values for each character
        confidences = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)['conf']
        # Calculate average confidence value
        avg_confidence = sum([c for c in confidences if c != -1]) / len([c for c in confidences if c != -1])
        # Get HOCR output from OCR
        hocr = pytesseract.image_to_pdf_or_hocr(image, extension='hocr')
        response = {
            'text': text,  # the extracted text
            'num_words': len(text.split()),  # the number of words in the extracted text
            'num_chars': len(text),  # the number of characters in the extracted text
            'image_size': f'{image.width}x{image.height}',  # the size of the input image
            'language': pytesseract.get_languages()[0],  # the language used for OCR
            'avg_confidence': avg_confidence,  # the average confidence value for the recognized characters
            'image_format': image.format,  # the format of the input image
            'dpi': image.info.get('dpi'),  # the DPI (dots per inch) of the input image, if available
            'extraction_time': end_time - start_time,  # Time needed for extraction
            'hocr': hocr.decode('utf-8') if hocr else None  # the HOCR output, if available
        }
        # Return the response JSON response
        return response, HTTPStatus.OK
