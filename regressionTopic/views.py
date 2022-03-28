from django.shortcuts import render
from bs4 import BeautifulSoup
import urllib.request
import requests
import tensorflow as tf
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
import pickle
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed
import time


def get_url_status(url):  # checks status for each url in list urls
    try:
        r = requests.get(url)
    except Exception as e:
        return False
    return True


#
#
model = tf.keras.models.load_model("nlp.h5")
tokenizer = pickle.load(open("tokenizer.pickle", "rb"))


def getContent(url):
    page = urllib.request.urlopen(url)
    soup = BeautifulSoup(page, "html.parser")
    content = soup.findAll('p')
    if content != None:
        return " ".join([p.text for p in content])
    return ""


# Create your views here.
def home_view(request):
    dic = {0: 'the-gioi',
           1: 'du-lich',
           2: 'the-thao',
           3: 'giao-duc',
           4: 'giai-tri',
           5: 'phap-luat',
           6: 'khoa-hoc',
           7: 'suc-khoe',
           8: 'kinh-doanh',
           9: 'oto-xe-may'}

    template_name = "index.html"
    l = []
    urls = request.POST.get("duongdan")

    if urls != None and urls.strip() != '':
        urls = urls.split('\n')
        a = []
        ak = ""
        index = 0
        print(len(urls))
        t0 = time.time()

        maxparalell = 30
        urlsnew = []
        with ThreadPoolExecutor(max_workers=min(maxparalell, len(urls))) as executor:
            future_to_url = {}
            for url in urls:
                url = url.strip()
                if url != '' and url != None and get_url_status(url):
                    future_to_url[executor.submit(getContent, url)] = url

            for future in as_completed(future_to_url):
                urlsnew.append(future_to_url[future])
                a.append(future.result())

        urls = urlsnew
        print(len(urls))
        print("Time =====", time.time() - t0)

        if len(urls) > 0:
            a = np.array(a).reshape(-1,)
            a = tokenizer.texts_to_sequences(a)
            a = pad_sequences(a, maxlen=2029)
            ak = model.predict(a)

            for ii in ak:
                t = [[[],[]],"",""]
                for i in range(len(ii)):
                    t[0][0][0:0] = [dic[i]]
                    t[0][1][0:0] = [ii[i]]
                t[1] = f'Link{index+1}'
                t[2] = urls[index]
                l.append(t)
                index += 1

    context = {
        'check': urls!=None and len(urls)>0,
        'l': l,
        'urls': urls
    }
    return render(request, template_name, context)