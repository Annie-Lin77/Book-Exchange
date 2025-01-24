import json

from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404

# Create your views here.
from .models import MainMenu
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseBadRequest
from django.contrib import messages
from .models import Book, Comment

from .forms import BookForm
from django.http import HttpResponseRedirect

from .models import Book

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
    for b in books:
        b.pic_path = b.picture.url[14:]
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

# myfavorites keeps a track of all books that the current user marked.
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


# def book_detail(request, book_id):
#     book = Book.objects.get(id=book_id)
#     book.pic_path = book.picture.url[14:]
#     return render(request,
#                   'bookMng/book_detail.html',
#                   {
#                       'item_list': MainMenu.objects.all(),
#                       'book': book,
#                   })


def book_detail(request, book_id):
    book = get_object_or_404(Book, id=book_id)  # Safely fetch the book
    book.pic_path = book.picture.url[14:]  # Adjust path to the image as needed
    user = request.user

    # Check if the user has favorited the book
    favorited = user.id in json.loads(book.favoritedby) if book.favoritedby else False

    # Fetch existing comments for the book
    comments = book.comments.all()

    if request.method == 'POST':
        # Extract form data
        author = request.POST.get('author').strip()
        content = request.POST.get('content').strip()

        # Validate the comment content
        if author and content:
            # Save the new comment
            Comment.objects.create(book=book, author=author, content=content)
            messages.success(request, 'Your comment has been posted.')
            return redirect('book_detail', book_id=book.id)  # Reload the page with the new comment
        else:
            messages.error(request, 'Both name and comment content are required.')

    return render(request, 'bookMng/book_detail.html', {
        'item_list': MainMenu.objects.all(),
        'book': book,
        'favorited': favorited,
        'comments': comments,  # Pass the comments to the template
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

    return render(request,
                  'bookMng/book_favorite.html',
                  {
                      'item_list': MainMenu.objects.all(),
                      'book': book,
                      'favorited': favorited,
                  })



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


def bookcomment(request, book_id):
    book = get_object_or_404(Book, id=book_id)

    if request.method == 'POST':
        # Retrieve the form data
        author = request.POST.get('author', '').strip()  # Get the author's name
        content = request.POST.get('content','').strip()  # Get the comment content

        # Check if content is provided
        if content.strip():  # Ensure content isn't empty
            # Create and save the new comment
            Comment.objects.create(
                book=book,
                author=author,
                content=content
            )
            messages.success(request, 'Your comment has been posted successfully!')
        else:
            messages.error(request, 'Comment content cannot be empty.')

        # Redirect back to the book detail page to show the comment
        return redirect('book_comment', book_id=book.id)

    # Fetch all comments for this book
    comments = Comment.objects.filter(book=book)

    # Render the page with the comments
    return render(request, 'bookMng/bookcomment.html', {'book': book, 'comments': comments})
