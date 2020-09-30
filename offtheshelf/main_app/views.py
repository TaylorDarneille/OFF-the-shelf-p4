from django.shortcuts import render
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
                    return HttpResponseRedirect('/user/'+str(user))
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
            return HttpResponseRedirect('/')
        else: 
            return HttpResponse('<h1>Try Again</h1>')
    else:
        form = UserCreationForm()
        return render(request, 'signup.html', {'form': form})

######################### Profile #########################   
     
@login_required
def profile(request, username):
    if request.method == "POST":
        delete_comment = request.POST.get("delete_comment")
        if delete_comment:
            Comment.objects.filter(id=delete_comment).delete()
        else:
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
    comments = Comment.objects.filter(user=user)
    return render(request, 'profile.html', {'username': username, 'wishlists': wishlists, "comments": comments})

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
        # print(searchList[0])
    return render(request, 'search_results.html', {"booklist": booklist} )

######################### Book Show #########################

def book_show(request, id):
    if request.method == 'POST':
        content = request.POST.get("content")
        id = request.POST.get("id")
        user = request.user
        title = request.POST.get("title")

        Comment.objects.create(
            content=content,
            book_id = id,
            user = user,
            title = title
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
        unwanted_tags = ['<br />', '<b>', '</b>', '<i>', '</i>', '<em>', '</em>']
        for i in unwanted_tags:
            if i in txt:
                txt = ''.join(txt.split(i))
        return(txt)

    # check if book description exist
    description = book["description"]
    if description: # clean description if it exits
        description = clean_text(book["description"])
    else:
        description = ''
    
    # check if author is a dictionary
    author_type = type(book["authors"]["author"])
    if author_type is dict:
        author = book["authors"]["author"]["name"]
        author_link = book["authors"]["author"]["link"]
    else:
        author = book["authors"]["author"][0]["name"]
        author_link = book["authors"]["author"][0]["link"]

    detail = {
        "title": book["title"],
        "author": author,
        "author_link": author_link,
        "description": description,
        "img_url": book["image_url"],
        "average_rating": book["average_rating"],
        "id": book["id"],
        "isbn": book["isbn"]
    }

    def clean_title(txt):
        if '(' in txt:
            txt = txt.split('(')
            return(txt[0])
        else:
            return(txt)



    
    title = clean_title(detail["title"])
    omdb_response = requests.get('http://www.omdbapi.com/?t={}&apikey={}'.format(title, config('omdb_key')))
    movie_data = json.loads(omdb_response.content)
    search_key = "Writer"
    movie_writers = [val for key, val in movie_data.items() if search_key in key] 
    # print("Values for substring keys : " + str(movie_writers))
    # book_writer = detail.author

    # def book_author(book_writers):
    #     if '(novel)' in movie_writers or '(book)' in movie_writers == book_writers:
    #         print('true')
    #         return True
    #     else:
    #         print('false')
    #         return False

    def book_author(writer):
        ls = ['novel', 'book', 'based on the  by']
        theWriter = []
        for i in range(len(ls)):
            if ls[i] in writer:
                writer = ''.join(writer.split(ls[i]))
        writer = writer.split(',')
        for i in writer:
            if '()' in i:
                theWriter = i.split(' (')
        return (theWriter[0])

    print(book_author(movie_data['Writer']))
    # print(movie_data['Writer'])
    # print(movie_data)
    if "Title" in movie_data:
        movie = {
            "title": movie_data["Title"],
            "year": movie_data["Year"],
            "director": movie_data["Director"],
            "writer": movie_data["Writer"],
            "poster": movie_data["Poster"],
            "imdbRating": movie_data["imdbRating"]
        }
    else: 
        movie = "No movie based on this book yet."
    
    


    for i in range(6):
        similar_books = {
            "id": book["similar_books"]["book"][i]["id"],
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
    
class CommentUpdate(UpdateView):
    model = Comment
    fields = ['content']
    # user = request.user
    # success_url = '/user/'
    def form_valid(self, form): 
        self.object = form.save(commit=False) 
        self.object.save()
        user = self.object.user.username
        return HttpResponseRedirect('/user/' + user)

# def handler404(request):
#     return render(request, '404.html', status=404)
# def handler500(request):
#     return render(request, '500.html', status=500)

