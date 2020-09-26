from django.shortcuts import render
from django.http import HttpResponse
import requests, xmltodict, json, dotenv
from decouple import config
import os

# Create your views here.


def index(request):
    
    return render(request, 'index.html')
    # return render(request, 'index.html', {
        # 'msg': data['msg']
    # })


def search_results(request):
    if request.method == 'POST':
        search = request.POST.get("search")

        response = requests.get('https://www.goodreads.com/search.xml?key={}&q={}'.format(config('key'), search))
    
        data = xmltodict.parse(response.content)
        books = json.dumps(data)
        bo = json.loads(books)

        searchList = bo["GoodreadsResponse"]["search"]["results"]["work"]
        
        booklist = []

        for i in range(10):
            book = {
                "title": searchList[i]["best_book"]["title"],
                "author": searchList[i]["best_book"]["author"]["name"],
                "img_url": searchList[i]["best_book"]["image_url"]
            }
            booklist.append(book)
            
    return render(request, 'search_results.html', {"booklist": booklist} )
