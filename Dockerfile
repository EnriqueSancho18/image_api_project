FROM python:3.11

COPY requirements.txt /tmp/

RUN pip3 install -r /tmp/requirements.txt

COPY __init__.py /image_api/
COPY controller.py /image_api/
COPY models.py /image_api/
COPY views.py /image_api/
COPY credentials.json /image_api/

EXPOSE 80

CMD waitress-serve --port=80 --call 'image_api:create_app'
