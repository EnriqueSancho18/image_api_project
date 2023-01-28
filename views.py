from flask import Blueprint, request, make_response
import base64
import names
import requests
import os
import datetime
import json
import statistics

from . import controller

bp1 = Blueprint('image', __name__, url_prefix='/')
bp2 = Blueprint('images', __name__, url_prefix='/')
bp3 = Blueprint('tags', __name__, url_prefix='/')

@bp1.post('/image')
def post_image():
    min_confidence = int(request.args.get('min_confidence',80))
    
    # Inputs check

    if not request.is_json or 'data' not in request.json:
        return make_response({"description": "You must include the base64 image as a field called data in the body"}, 400)

    data_input = request.json['data']
    response = controller.add_image(data_input,min_confidence)
    return json.dumps(response)

@bp2.get('/images')
def get_images():
    min_date = str(request.args.get('min_date','2022-01-01 00:00:00'))
    max_date = str(request.args.get('max_date','3000-01-01 00:00:00'))
    tags = [i for i in request.args.get('tags','').split(',')]

    response = controller.select_images(min_date,max_date,tags)
    return response

@bp1.get('/image/<image_id>')
def get_image(image_id):
    image_id = int(image_id)

    response = controller.select_image(image_id)
    return response

@bp3.get('/tags')
def get_tags():
    min_date = str(request.args.get('min_date','2022-01-01 00:00:00'))
    max_date = str(request.args.get('max_date','3000-01-01 00:00:00'))

    response = controller.select_tags(min_date,max_date)
    return response    
