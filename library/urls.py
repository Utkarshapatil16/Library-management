from django.urls import path
from . import views

urlpatterns = [
    path('',views.home,name='home'),
    path('issue/',views.issue_book,name='issue_book'),
    path('return/<int:issue_id>/',views.return_book,name='return_book'),
]