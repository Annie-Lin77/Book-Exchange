import json

from django.contrib.auth.decorators import login_required
from django.db.models import Q, Avg

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.contrib import messages
# Create your views here.
from bookMng.models import MainMenu

from .forms import BookForm, RatingForm
from django.http import HttpResponseRedirect

from .models import Book, BookRating

from django.views.generic.edit import CreateView
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy


def index(request):
    return render(request,
                  'bookMng/index.html',
                  {
                      'item_list': MainMenu.objects.all()
                  })


def about_us(request):
    return render(request,
                  'bookMng/about_us.html',
                  {'item_list': MainMenu.objects.all()
                   })


def search_books(request):
    # Get search query from URL parameters
    query = request.GET.get('q', '')

    if query:
        # Filter books that match either book name or username
        books = Book.objects.filter(
            Q(name__icontains=query) |
            Q(username__username__icontains=query)
        )
    else:
        # If no query, show all books
        books = Book.objects.all()

    # calvin: gonna add the favorite stuff to your code
    user = request.user

    # Process picture paths (following your project's convention)
    for b in books:
        b.pic_path = b.picture.url[14:]
        # calvin: this is part of the favorites stuff (52-54)
        favorited_users = json.loads(b.favoritedby) if b.favoritedby else []
        b.is_favorited = user.id in favorited_users

    return render(request,
                  'bookMng/search_books.html',
                  {
                      'item_list': MainMenu.objects.all(),
                      'books': books,
                      'query': query,
                  })


def postbook(request):
    submitted = False
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():

            # form.save()
            book = form.save(commit=False)
            try:
                book.username = request.user
            except Exception:
                pass
            book.save()

            return HttpResponseRedirect('/postbook?submitted=True')
    else:
        form = BookForm()
        if 'submitted' in request.GET:
            submitted = True

    return render(request,
                  'bookMng/postbook.html',
                  {
                      'form': form,
                      'item_list': MainMenu.objects.all(),
                      'submitted': submitted
                  })


def displaybooks(request):
    books = Book.objects.all()
    user = request.user

    for b in books:
        b.pic_path = b.picture.url[14:]
        favorited_users = json.loads(b.favoritedby) if b.favoritedby else []
        b.is_favorited = user.id in favorited_users
        b.user_rating = b.get_user_rating(user)
        b.update_avg_rating()

        #b.user_rating = user_ratings_dict.get(b.id, None)
    return render(request,
                  'bookMng/displaybooks.html',
                  {
                      'item_list': MainMenu.objects.all(),
                      'books': books,
                  })


def mybooks(request):
    books = Book.objects.filter(username=request.user)
    for b in books:
        b.pic_path = b.picture.url[14:]
    return render(request,
                  'bookMng/mybooks.html',
                  {
                      'item_list': MainMenu.objects.all(),
                      'books': books,
                  })


# myfavorites keeps a track of all books that the current user mar  ked.
def myfavorites(request):
    # filters all user favorited books
    user = request.user
    # books = Book.objects.filter(favoritedby(user)) #error
    books = [book for book in Book.objects.all() if user.id in json.loads(book.favoritedby)]

    for b in books:
        b.pic_path = b.picture.url[14:]
    return render(request,
                  'bookMng/myfavorites.html',
                  {
                      'item_list': MainMenu.objects.all(),
                      'books': books,
                  })


def book_detail(request, book_id):
    book = Book.objects.get(id=book_id)
    book.pic_path = book.picture.url[14:]
    user = request.user


    favorited = user.id in json.loads(book.favoritedby) if book.favoritedby else False

    return render(request,
                  'bookMng/book_detail.html',
                  {
                      'item_list': MainMenu.objects.all(),
                      'book': book,
                      'favorited': favorited,

                  })


# adds user to list of favorites for a book
def book_favorite(request, book_id):
    book = Book.objects.get(id=book_id)
    user = request.user

    # load the current list of favorited users
    favorited_users = json.loads(book.favoritedby)

    if user.id not in favorited_users:
        favorited_users.append(user.id)
        favorited = True
    else:
        favorited_users.remove(user.id)
        favorited = False

    book.favoritedby = json.dumps(favorited_users)
    book.save()

    next_url = request.GET.get('next', 'book_detail')

    if next_url == 'book_detail':
        return redirect('book_detail', book_id=book.id)
    elif next_url == 'myfavorites':
        return redirect('myfavorites')
    else:
        return redirect('myfavorites')


def book_unfavorite(request, book_id):
    book = Book.objects.get(id=book_id)
    user = request.user

    # Load the current list of favorited users
    favorited_users = json.loads(book.favoritedby) if book.favoritedby else []

    # Remove the user from the list of favorited users if they are in it
    if user.id in favorited_users:
        favorited_users.remove(user.id)

    # Update the book's favoritedby field
    book.favoritedby = json.dumps(favorited_users)
    book.save()

    # Redirect the user back to the My Favorites page
    return redirect('myfavorites')


def book_delete(request, book_id):
    book = Book.objects.get(id=book_id)
    book.delete()
    return render(request,
                  'bookMng/book_delete.html',
                  {
                      'item_list': MainMenu.objects.all(),
                  })


class Register(CreateView):
    template_name = 'registration/register.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('register-success')

    def form_valid(self, form):
        form.save()
        return HttpResponseRedirect(self.success_url)


#rate book
#view to handle rating a book
@login_required
def ratebook(request, book_id):
    # Get the book object
    book = get_object_or_404(Book, id=book_id)
    # Check if the user has already rated the book
    book_rating = BookRating.objects.filter(book=book, user=request.user).first()
    # Handle rating submission (POST request)
    if request.method == "POST":

        new_rating = int(request.POST.get('rating', 0))
        if book_rating:
            # Update the existing rating if the user has already rated the book
            book_rating.rating = new_rating
            book_rating.save()
            messages.success(request, "Your rating has been updated!")
        else:
            # Create a new rating if the user hasn't rated the book yet
            BookRating.objects.create(book=book, user=request.user, rating=new_rating)
            messages.success(request, "Your rating has been submitted!")

        return redirect('displaybooks')
    # Render the page, passing the current rating if available
    context = {
        'book': book,
        'user_rating': book_rating.rating if book_rating else None,
    }
    return render(request, 'bookMng/ratebook.html', context)



# Gets user rating
def get_user_rating(request, book_id):
    # must get current user
    user = request.user
    book = get_object_or_404(Book, id=book_id)

    # Ensure user is logged in
    if not user.is_authenticated:
        return redirect('login')

    # To get the user's rating for the book
    book_rating = BookRating.objects.filter(book=book, user=user).first()
    user_rating = book_rating.rating if book_rating else None

    context = {
        'item_list': MainMenu.objects.all(),
        'book': book,
        'user_rating': user_rating,  # Current user's rating
        'avg_rating': book.avg_rating,
        'number_of_ratings': book.number_of_ratings,
    }
    return render(request, 'bookMng/displaybooks.html', context)


#Gets the ratings for a book
def get_rating_statistics(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    #All Ratings for Given Book
    ratings = BookRating.objects.filter(book=book)

    user_ratings = [
        (rating.user.username, rating.rating) for rating in ratings
    ]

    # Recalculate average and number of ratings to ensure accuracy
    book.update_avg_rating()
    context = {
        'book': book,
        'user_ratings': user_ratings,
        'avg_rating': f"{book.avg_rating:.1f}",
        'number_of_ratings': book.number_of_ratings,
        'item_list': MainMenu.objects.all(),
    }
    return render(request, 'bookMng/rating_statistics.html', context)
