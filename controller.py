from . import models
import base64
import names
import random
import json
import os
import datetime
import statistics
import requests
from imagekitio import ImageKit
from sqlalchemy import create_engine

def add_image(data_input,min_confidence):

    engine = create_engine("mysql+pymysql://mbit:mbit@mi_db:3306/Pictures")

    # Get API credentials from file "credentials.json"

    with open('/image_api/credentials.json', 'r') as f:
 
        json_object = json.load(f)
    
        public_key = json_object['Public Key']
        private_key = json_object['Private Key']
        url_endpoint = json_object['URL-endpoint']
        api_key = json_object['API Key']
        api_secret = json_object['API Secret']


    imagekit = ImageKit(
        public_key,
        private_key,
        url_endpoint
    )

    b64str = data_input
    random_name = names.get_first_name()+str(random.randint(0,100))

    # Upload image to Imagekit

    upload_info = imagekit.upload(file=b64str, file_name=f"{random_name}.jpg")

    imagekit_url = upload_info.url

    # Use Imagga API

    response = requests.get(f"https://api.imagga.com/v2/tags?image_url={imagekit_url}", auth=(api_key, api_secret))

    tags = {
    t["tag"]["en"]:t['confidence']
    for t in response.json()["result"]["tags"]
    if t["confidence"] > min_confidence
    }

    # Delete image from Imagekit

    imagekit.delete_file(file_id=upload_info.file_id)

    # Save image in volume

    bstr = base64.b64decode(b64str)

    with open(f'Imagenes/{random_name}.jpg','wb') as f:
        f.write(bstr)

    absolute_path = os.path.abspath(f'Imagenes/{random_name}.jpg').replace('\\','/')
    current_time = datetime.datetime.now()

    # Insert values into "pictures" and "tags" mysql tables

    with engine.connect() as conn:

        conn.execute(f"""
        INSERT INTO pictures
        (path,date) VALUES ('{absolute_path}','{current_time}')
        """)
        
        result = conn.execute(f"""
        SELECT MAX(id) from pictures
        """)
        columns = result.keys()
        data = [
            dict(zip(columns, row))
            for row in result
        ]

        last_id = data[0]['MAX(id)']
        
        for i in tags:
            conn.execute(f"""
            INSERT INTO tags
            (picture_id,tag,confidence,date) VALUES ({last_id},'{i}',{tags[i]},'{current_time}')
            """)

    # Process the result
            
    response =  {
        
        'id': last_id,
        'size':len(bstr)/1024,
        'date':current_time.strftime('%Y-%m-%d %H:%M:%S'),
        'tags': [
            {
                'tag':i,
                'confidence':tags[i]
            }
                for i in tags
            ],
        'data':b64str
    }

    return json.dumps(response)


def select_images(min_date,max_date,tags):

    engine = create_engine("mysql+pymysql://mbit:mbit@mi_db:3306/Pictures")

    # Extract values from "pictures" and "tags" mysql tables

    with engine.connect() as conn:

        result = conn.execute(f"""
        SELECT P.id, P.path, P.date, GROUP_CONCAT(T.tag) as tags
        FROM tags T INNER JOIN pictures P
        ON T.picture_id = P.id
        WHERE P.date BETWEEN '{min_date}' and '{max_date}'
        GROUP BY P.id
        """)

        columns = result.keys()
        data = [
            dict(zip(columns, row))
            for row in result
        ] 

    # Process the result

    for i in data:
        with open(i['path'], mode='rb') as img:
            b64_2 = base64.b64encode(img.read()).decode()
            bstr_2 = base64.b64decode(b64_2)
        i['path']=len(bstr_2)/1024

    processed_result1 =  [
        {
            'id':i['id'],
            'size': i['path'],
            'date':i['date'].strftime('%Y-%m-%d %H:%M:%S'),
            'tags':[
                l
                for l in i['tags'].split(',')
            ]
        }

        for i in data
    ]
        
    if tags[0]=='':
        
        return processed_result1
    
    else:
        
        processed_result2 = []
        for i in processed_result1:
            if all([item in i['tags'] for item in tags]):
                processed_result2.append(i)
                
        return processed_result2 

   
def select_image(image_id):

    engine = create_engine("mysql+pymysql://mbit:mbit@mi_db:3306/Pictures")

    # Extract values from "pictures" and "tags" mysql tables

    with engine.connect() as conn:

        result = conn.execute(f"""
        SELECT P.id, P.path, P.date, GROUP_CONCAT(T.tag) as tags, GROUP_CONCAT(T.confidence) as confidence
        FROM tags T INNER JOIN pictures P
        ON T.picture_id = P.id
        WHERE P.id = {image_id}
        GROUP BY P.id
        """)

        columns = result.keys()
        data = [
            dict(zip(columns, row))
            for row in result
        ]

    # Process the result
            
    for i in data:
        with open(i['path'], mode='rb') as img:
            b64_2 = base64.b64encode(img.read()).decode()
            bstr_2 = base64.b64decode(b64_2)
        i['path']=len(bstr_2)/1024 

    processed_result =  [
    {
        'id':i['id'],
        'size': i['path'],
        'date':i['date'].strftime('%Y-%m-%d %H:%M:%S'),
        'tags':[
            {
                'tag':t,
                'confidence':float(i['confidence'].split(',')[int(i['tags'].split(',').index(t))])
            }
            for t in i['tags'].split(',')
        ],
        'data':b64_2
    }

    for i in data
    ]
    
    return json.dumps(processed_result)

def select_tags(min_date,max_date):

    engine = create_engine("mysql+pymysql://mbit:mbit@mi_db:3306/Pictures")

    # Extract values from "pictures" and "tags" mysql tables

    with engine.connect() as conn:

        result = conn.execute(f"""
        SELECT P.id, GROUP_CONCAT(T.tag) as tags, GROUP_CONCAT(T.confidence) as confidence
        FROM tags T INNER JOIN pictures P
        ON T.picture_id = P.id
        WHERE P.date BETWEEN '{min_date}' and '{max_date}'
        GROUP BY P.id
        """)

        columns = result.keys()
        data = [
            dict(zip(columns, row))
            for row in result
        ] 

    # Process the result
        
    unique_tags = set([
    t
    for i in data
    for t in i['tags'].split(',')
    ])   

    respuesta = [{
    
    'tag':u,
    'confidence':[],
    }
    for u in unique_tags
    ]
    
    for i in data:
        for t in unique_tags:
            if t in i['tags'].split(','):
                for r in respuesta:
                    if r['tag']==t:
                        r['confidence'].append(float(i['confidence'].split(',')[int(i['tags'].split(',').index(t))]))
                        r['n_images']=len(r['confidence'])
                        r['min_confidence']=min(r['confidence'])
                        r['max_confidence']=max(r['confidence'])
                        r['mean_confidence']=statistics.mean(r['confidence'])
    
    return respuesta