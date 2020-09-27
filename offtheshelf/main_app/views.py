from django.shortcuts import render
from django.shortcuts import render
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
# from django.utils.decorators import method_decorator
import requests, xmltodict, json, dotenv
from decouple import config
import os


# Create your views here.


def index(request):
    
    return render(request, 'index.html')
    # return render(request, 'index.html', {
        # 'msg': data['msg']
    # })
def login_view(request):
    if request.method =="POST":
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            u = form.cleaned_data['username']
            p = form.cleaned_data['password']
            user = authenticate(username = u, password = p)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponseRedirect('/user/'+u)
                else:print('The account has been disable YOU SCOUNDREL')
        else:
            print('The username and/or password is incorrect. You are less of a scoundrel')
    else:
        form = AuthenticationForm()
        return render(request, 'login.html', {'form':form})

def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/')

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return HttpResponseRedirect('/user/'+str(user))
        else: 
            return HttpResponse('<h1>Try Again</h1>')
    else:
        form = UserCreationForm()
        return render(request, 'signup.html', {'form': form})
@login_required
def profile(request, username):
    user = User.objects.get(username=username)
    return render(request, 'profile.html', {'username': username})

def search_results(request):
    if request.method == 'POST':
        search = request.POST.get("search")

        response = requests.get('https://www.goodreads.com/search.xml?key={}&q={}'.format(config('key'), search))
    
        data = xmltodict.parse(response.content)
        jsonData = json.dumps(data)
        theData = json.loads(jsonData)
        searchList = theData["GoodreadsResponse"]["search"]["results"]["work"]
        
        
        booklist = []

        for i in range(10):
            book = {
                "title": searchList[i]["best_book"]["title"],
                "author": searchList[i]["best_book"]["author"]["name"],
                "img_url": searchList[i]["best_book"]["image_url"],
                "average_rating": searchList[i]["average_rating"],
                "id": searchList[i]["best_book"]["id"]['#text'],
            }
            booklist.append(book)
            
    return render(request, 'search_results.html', {"booklist": booklist} )


def book_show(request):
    response = requests.get('https://www.goodreads.com/book/show/233093.xml?key={}'.format(config('key')))
    data = xmltodict.parse(response.content)
    jsonData = json.dumps(data)
    theData = json.loads(jsonData)
    book = theData["GoodreadsResponse"]["book"]
    # similar = []
    # for i in range(10):
    #     similar_books = { "similar_books" : book[i]["similar_books"]["book"][6],}
    #     similar.append(similar_books)
    detail = {
        "title": book["title"],
        "description": book["description"],
        "img_url": book["image_url"],
        "average_rating": book["average_rating"],
        # "similar_books": similar_books,
    }
    
    print(jsonData)
    print(book)
    return render(request, 'book_show.html', {"detail": detail})
