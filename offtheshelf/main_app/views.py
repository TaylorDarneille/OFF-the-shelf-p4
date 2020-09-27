from django.shortcuts import render
from django.shortcuts import render
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .forms import  CommentForm
from .models import Comment
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


# Create your views here.
@method_decorator(login_required, name='dispatch')
class CommentCreate(CreateView):
    model = Comment
    fields = ['content']

    ## how to pass in book id to post a comment

    def form_valid(self, form):
        # This lets us catch the PK, if we didn't do this we'd have no way of accessing this pk from this CRUD right here
        self.object = form.save(commit=False) # Don't post to DB until I say so, this is the form validation
        self.object.user = self.request.user
        user = self.object.user
        self.object.save() # This gives us access to the PK through the self.object
        return HttpResponseRedirect('/user/'+str(user.username))



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


def book_show(request, book_id):
    comment = Comment.objects.all()
    response = requests.get('https://www.goodreads.com/book/show/{}.xml?key={}'.format(book_id, config('key')))
    data = xmltodict.parse(response.content)
    jsonData = json.dumps(data)
    theData = json.loads(jsonData)
    book = theData["GoodreadsResponse"]["book"]
    similar = []
    buyLinks = []
    for i in range(10):
        similar_books = {
            "title" : book["similar_books"]["book"][i]["title"],
            "image_url": book["similar_books"]["book"][i]["image_url"]
        }
        similar.append(similar_books)
    for i in range(10):
        buy_links = {
            "name" : book["buy_links"]["buy_link"][i]["name"],
            "link" : book["buy_links"]["buy_link"][i]["link"]
        }
        buyLinks.append(buy_links)
    # print(similar)
    detail = {
        "title": book["title"],
        "description": book["description"],
        "img_url": book["image_url"],
        "average_rating": book["average_rating"],
        "id": book["id"],
        # "similar_books": similar_books,
    }

    
    # print(jsonData)
    # print(book)
    # print(similar)
    return render(request, 'book_show.html', {"detail": detail, "similar": similar, "buyLinks": buyLinks, "comment":comment})

# @method_decorator(login_required, name='dispatch')
# class CommentCreate(CreateView, pk):
#     model = Comment
#     fields = ['content']

#     def form_valid(self, form):
#         # This lets us catch the PK, if we didn't do this we'd have no way of accessing this pk from this CRUD right here
#         self.object = form.save(commit=False) # Don't post to DB until I say so, this is the form validation
#         self.object.user = self.request.user
#         user = self.object.user
#         self.object.save() # This gives us access to the PK through the self.object
#         return HttpResponseRedirect('/user/'+str(user.username))

