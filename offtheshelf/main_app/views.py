from django.shortcuts import render
from django.http import HttpResponse
import requests, xmltodict, json

# Create your views here.


def index(request):
    response = requests.get('https://www.goodreads.com/search.xml?key={}&q=Ender%27s+Game'.format(key))
    # root = ElementTree.fromstring(response.content)
    # print(root)
    
    data = xmltodict.parse(response.content)
    books = json.dumps(data)
    bo = json.loads(books)
    # print(bo)
    # print(bo["GoodreadsResponse"]["search"]["results"]["work"][0]["average_rating"])
    return render(request, 'index.html')
    # return render(request, 'index.html', {
        # 'msg': data['msg']
    # })

