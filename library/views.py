from django.shortcuts import render,redirect,get_object_or_404
from django.utils import timezone
# Create your views here.
from .models import Book,Issue
from .forms import IssueForm

def home(request):
    books=Book.objects.all()
    issues = Issue.objects.all()
    query = request.GET.get('q')

    if query:
        books = Book.objects.filter(title__icontains=query)
    else:
        books = Book.objects.all()
        issues =Issue.objects.all()

    return render(request,'home.html',{'books':books,'issues' : issues})

def issue_book(request):
    form = IssueForm()
    if request.method == 'POST':
       form = IssueForm(request.POST)
       if form.is_valid():
           form.save()
           return redirect('issue_book')
       else:
        form = IssueForm()
    return render(request,'issue.html',{'form':form})

def return_book(request , issue_id):
    issue = get_object_or_404(Issue,id=issue_id)
    if issue.return_date is None:
        issue.return_date = timezone.now()

        book = issue.book
        book.quantity += 1
        book.save()

        issue.save()

    return redirect('home')