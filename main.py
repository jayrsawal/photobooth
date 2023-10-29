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

border_px = 50

left_crop = (border_px, border_px, 762, 1150)
right1_crop = (812, border_px, 1256, 735)
right2_crop = (1306, border_px, 1750, 735)

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
@route('/photos/<groupId>/<photoName>')
def serve_collage_files(groupId, photoName):
    filePath = os.path.join('./photos/', groupId)
    return static_file(photoName, filePath)

@route('/upload/<groupId>')
@enable_cors
def upload(groupId):
    root_dir = "photos/"+groupId
    
    filename = collage(root_dir, [photo for photo in os.listdir(root_dir) if photo != f"{groupId}.png" and "png" in photo])
    filepath = "/photos/" + groupId + "/" + filename
    
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
    result = subprocess.run([r"./lumix_focusshot.exe", filePath, filename], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    data = ""
    if result.returncode:
        processedPath = result.stdout.decode(sys.stdout.encoding).strip().replace("\"", "").replace("\\\\\\\\", "\\\\")
        
        while not os.path.isfile(processedPath):
            time.sleep(0.5)

        with Image.open(processedPath) as f:
            img = f.convert("RGB").rotate(-90, expand=True)
            img = img.resize((1200,1800))
            with BytesIO() as b:
                img.save(b, format="JPEG")
                img_str = base64.b64encode(b.getvalue())    
                data = bytes("data:image/jpeg;base64,", encoding='utf-8') + img_str
    
    return data

def collage(root_dir, files):
    numFiles = len(files)
    
    bg = Image.open("templates/collage2-3.png").convert("RGBA")
    if numFiles == 1:
        bg = Image.open("templates/collage2-1.png").convert("RGBA")

    collage = Image.new("RGBA", bg.size)
    
    if numFiles == 1:
        with open(os.path.join(root_dir, files[0]), "rb") as raw_img:
            img = Image.open(raw_img).convert("RGBA").rotate(-90, expand=True)
            crop = (border_px, border_px, collage.size[0]-border_px, collage.size[1]-border_px)
            dim = (crop[2]-crop[0], crop[3]-crop[1])
            cropped = img.resize(dim)
            collage.paste(cropped, (crop[0],crop[1]))
            img.close()

    else:
        paste_three(collage, root_dir, files)
               
    collage.paste(bg, (0, 0), bg)
    bg.close()

    filename = files[0].split(".")[0] + ".png"
    collage.save(os.path.join(root_dir, filename))
    collage.close()
    return filename

def paste_three(collage, root_dir, files):
    numFiles = len(files)
    for i in range(numFiles):
        f = files[i]
        with open(os.path.join(root_dir, f), "rb") as raw_img:
            img = Image.open(raw_img).convert("RGBA").rotate(-90, expand=True)
            crop = left_crop
            if i == 1:
                crop = right1_crop
            elif i == 2:
                crop = right2_crop

            dim = (crop[2]-crop[0], crop[3]-crop[1])
            cropped = img.resize(dim)
            collage.paste(cropped, (crop[0], crop[1]))
            img.close()

def fit(img, new_width, new_height):
    return ImageOps.fit(img, (new_width, new_height), method = 0, bleed = 0.0, centering = (0.5, 0.5))

run(host='localhost', port=8080, debug=True)