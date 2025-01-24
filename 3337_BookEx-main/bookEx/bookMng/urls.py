from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('home', views.index, name='index'),
    path('aboutus', views.about_us, name='about_us'),
    path('postbook', views.postbook, name='postbook'),
    path('displaybooks', views.displaybooks, name='displaybooks'),
    path('search/', views.search_books, name='search_books'),
    path('mybooks', views.mybooks, name='mybooks'),
    path('book_detail/<int:book_id>', views.book_detail, name='book_detail'),
    path('book_delete/<int:book_id>', views.book_delete, name='book_delete'),
    path('book_detail/book_favorite/<int:book_id>', views.book_favorite, name='book_favorite'),
    path('book_favorite/<int:book_id>', views.book_favorite, name='book_favorite'),
    path('myfavorites', views.myfavorites, name='myfavorites'),
    # Book rating
    path('book_detail/rating_statistics/<int:book_id>/', views.get_rating_statistics, name='rating_statistics'),
    path('displaybooks/ratebook/<int:book_id>', views.ratebook, name='ratebook'),
]

