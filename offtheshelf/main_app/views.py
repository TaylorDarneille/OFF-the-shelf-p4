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
        title = (bo["GoodreadsResponse"]["search"]["results"]["work"][0]["best_book"]["title"])

    return render(request, 'search_results.html', { 'title': title })

