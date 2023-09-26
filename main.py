import base64
import json
import time
import calendar
import subprocess
import os
import sys

from bottle import route, post, run, static_file, request, response
from PIL import Image, ImageOps
from io import BytesIO

default_width = 1470
default_height = 827
left_edge_w = 320
right_edge_w = 322

left_dim = (658, 862)
right_dim = (524, 390)

left_crop = (156, 174, 814, 1036)
right1_crop = (1080, 178, 1604, 565)
right2_crop = (1080, 650, 1602, 1040)
right1_crop_alt = (963, 168, 1623, 1030)

# the decorator
def enable_cors(fn):
    def _enable_cors(*args, **kwargs):
        # set CORS headers
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'

        if request.method != 'OPTIONS':
            # actual request; reply with the actual response
            return fn(*args, **kwargs)

    return _enable_cors

#Hosts html file which will be invoked from browser.
@route('/')
def serve_static_file():
    filePath = './public_html/'
    return static_file("index.html", filePath)

#Hosts html file which will be invoked from browser.
@route('/public_html/<staticFile>')
def serve_static_file(staticFile):
    filePath = './public_html/'
    return static_file(staticFile, filePath)

#host css files which will be invoked implicitly by your html files.
@route('/public_html/css/<cssFile>')
def serve_css_files(cssFile):
    filePath = './public_html/styles/'
    return static_file(cssFile, filePath)

# host js files which will be invoked implicitly by your html files.
@route('/public_html/js/<jsFile>')
def serve_js_files(jsFile):
    filePath = './public_html/scripts/'
    return static_file(jsFile, filePath)

# host js files which will be invoked implicitly by your html files.
@route('/photos/collages/<photoName>')
def serve_collage_files(photoName):
    filePath = './photos/collages/'
    return static_file(photoName, filePath)

@route('/upload/<groupId>')
@enable_cors
def upload(groupId):
    root_dir = "photos/"+groupId
    
    filename = collage(root_dir, os.listdir(root_dir))   
    filepath = "/photos/collages/" + filename
    
    return {
        "photo_url": filepath,
        "group_id": groupId
    }
    
@route('/photo/<groupId>/<photoId>')
@enable_cors
def photo(groupId, photoId):
    root_dir = "photos/"+groupId
    if not os.path.exists(root_dir):
        os.makedirs(root_dir)
        
    filename = groupId + ".raw." + photoId + ".png"
    filePath = os.path.abspath(root_dir)
    result = subprocess.run([r"./lumix_oneshot.exe", filePath, filename], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    data = ""
    if result.returncode:
        processedPath = result.stdout.decode(sys.stdout.encoding).strip().replace("\"", "").replace("\\\\\\\\", "\\\\")
        
        with Image.open(processedPath) as f:
            img = f.convert("RGB")
        
            with BytesIO() as b:
                img.save(b, format="JPEG")
                img_str = base64.b64encode(b.getvalue())    
                data = bytes("data:image/jpeg;base64,", encoding='utf-8') + img_str
    
    return data

def collage(root_dir, files):
    numFiles = len(files)
    bg = Image.open("photos/collage3.png").convert("RGB")
    if numFiles == 1:
        bg = Image.open("photos/collage1.png").convert("RGB")
    elif numFiles == 2:
        bg = Image.open("photos/collage2.png").convert("RGB")

    for i in range(numFiles):
        f = files.pop()
        with Image.open(os.path.join(root_dir,f)).convert("RGB") as img:
            dim = right_dim
            crop = right2_crop
            if i == 0:
                dim = left_dim
                crop = left_crop
            elif i == 1:
                crop = right1_crop
                if numFiles == 2:
                    dim = left_dim
                    crop = right1_crop_alt

            cropped = fit(img, dim[0], dim[1])
            bg.paste(cropped, (crop[0], crop[1]))

    filename = f.split(".")[0] + ".collage.png"
    bg.save("photos/collages/" + filename)
    bg.close()
    return filename

def fit(img, new_width, new_height):
    return ImageOps.fit(img, (new_width, new_height), method = 0, bleed = 0.0, centering = (0.5, 0.5))

run(host='localhost', port=8080, debug=True)