from django.urls import path
from . import views

urlpatterns = [
    # Template URLs
    path('', views.home, name='home'),
    path('issue/', views.issue_book, name='issue_book'),
    path('return/<int:issue_id>/', views.return_book, name='return_book'),

    # Auth APIs
    path('register/', views.register, name='register'),
    path('logout/', views.logout, name='logout'),
    path('profile/', views.profile, name='profile'),

    # Book APIs
    path('books/', views.get_books, name='get_books'),
    path('books/create/', views.create_book, name='create_book'),
    path('books/<int:id>/', views.get_single_book, name='get_single_book'),
    path('books/<int:id>/update/', views.update_book, name='update_book'),
    path('books/<int:id>/delete/', views.delete_book, name='delete_book'),
    path('books/<int:id>/issue/', views.issue_book_api, name='issue_book_api'),

    # Issue APIs
    path('issues/<int:issue_id>/return/', views.return_book_api, name='return_book_api'),
    path('history/', views.borrow_history, name='borrow_history'),
    path('dashboard/', views.dashboard, name='dashboard'),
]