from django.shortcuts import render
from django.shortcuts import render
from django.views.generic.edit import CreateView, UpdateView, DeleteView
# from .forms import  CommentForm
from .models import Comment, Wishlist
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
import requests, xmltodict, json, dotenv
from decouple import config
import os



# class WishlistDelete(DeleteView):
#     model = Wishlist
#     success_url = '/profile'
######################### Index #########################
def index(request):    
    return render(request, 'index.html')

######################### Login #########################
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

######################### Logout #########################
def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/')

######################### Signup #########################
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

######################### Profile #########################        
@login_required
def profile(request, username):
    if request.method == "POST":
        delete = request.POST.get("delete")
        if delete:
            Wishlist.objects.filter(book_id=delete).delete()
        else:
            title = request.POST.get("title")
            id = request.POST.get("id")
            img_url = request.POST.get("image")
            user = request.user 

            exist = Wishlist.objects.filter(book_id=id)
            if exist:
                pass
            else:
                Wishlist.objects.create(
                    title = title,
                    book_id = id,
                    img_url = img_url,
                    user = user
                )
    user = User.objects.get(username=username)
    wishlists = Wishlist.objects.filter(user=user)
    return render(request, 'profile.html', {'username': username, 'wishlists': wishlists})

######################### Search Result #########################
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

######################### Book Show #########################
def book_show(request, id):
    if request.method == 'POST':
        content = request.POST.get("content")
        id = request.POST.get("id")
        user = request.user

        Comment.objects.create(
            content=content,
            book_id = id,
            user = user
        )

    comments = Comment.objects.filter(book_id=id)
    response = requests.get('https://www.goodreads.com/book/show/{}.xml?key={}'.format(id, config('key')))
    data = xmltodict.parse(response.content)
    jsonData = json.dumps(data)
    theData = json.loads(jsonData)
    book = theData["GoodreadsResponse"]["book"]
    similar = []
    buyLinks = []

    def clean_text(txt):
        newTxt = ''.join(txt.split('<br />'))
        newTxt = ''.join(newTxt.split('<b>'))
        newTxt = ''.join(newTxt.split('</b>'))
        newTxt = ''.join(newTxt.split('<i>'))
        newTxt = ''.join(newTxt.split('</i>'))
        return(newTxt)
    
    detail = {
        "title": book["title"],
        "description": clean_text(book["description"]),
        "img_url": book["image_url"],
        "average_rating": book["average_rating"],
        "id": book["id"],
    }

    for i in range(10):
        buy_links = {
            "name" : book["buy_links"]["buy_link"][i]["name"],
            "link" : book["buy_links"]["buy_link"][i]["link"]
        }
        buyLinks.append(buy_links)

    for i in range(10):
        similar_books = {
            "title" : book["similar_books"]["book"][i]["title"],
            "image_url": book["similar_books"]["book"][i]["image_url"]
        }
        similar.append(similar_books)
        
    return render(request, 'book_show.html', {
        "detail": detail,
        "similar": similar,
        "buyLinks": buyLinks,
        "comments":comments,
    })



