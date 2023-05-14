import imdb
import urllib.request
import base64
from PIL import Image
from io import BytesIO

def getCover(title):
    #init imbdf
    imdb_inst = imdb.IMDb()
    #search movie
    movies = imdb_inst.search_movie(title)
    if len(movies)==0:
        print("No results found.")
        return None
    #movie is first results
    url = None
    for m in movies:
        if m.get("full-size cover url")!=None:
            url = m.get("full-size cover url")
            break
    if url==None:
        return None
    #download image
    data = urllib.request.urlopen(url).read()
    #create pil image
    img = Image.open(BytesIO(data))
    #resize image to speed up, max size 450
    w, h = img.size
    new_h = 450
    new_w = int(w * (450 / h))
    img = img.resize((new_w, new_h))
    #save in buffer to correctly get bits
    buffer = BytesIO()
    img.save(buffer, format="JPEG")
    img_bytes = buffer.getvalue()
    #to base64
    img_base64 = base64.b64encode(img_bytes).decode("utf-8")
    return img_base64