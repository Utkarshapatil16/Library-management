from django.contrib import admin

# Register your models here.
from .models import Book,Student,Issue

admin.site.register(Book)
admin.site.register(Student)
admin.site.register(Issue)
