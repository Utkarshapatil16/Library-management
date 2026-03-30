from django.shortcuts import render,redirect,get_object_or_404
from django.utils import timezone
# Create your views here.
from .models import Book,Issue
from .forms import IssueForm
from django.contrib.auth.decorators import login_required
from datetime import date ,timedelta


@login_required
def home(request):
    issues = Issue.objects.all()
    query = request.GET.get('q')

    if query:
        books = Book.objects.filter(title__icontains=query)
    else:
        books = Book.objects.all()
        issues =Issue.objects.all()
        for issue in issues:
         if issue.return_date and issue.due_date:
            if issue.return_date > issue.due_date:
                days_late = (issue.return_date - issue.due_date).days
                issue.fine = days_late*10
            else:
                issue.fine =0
        else:
            issue.fine=0

    total_books = Book.objects.count()
    issued_books = Issue.objects.filter(return_date__isnull=True).count()
    available_books = total_books - issued_books
    return render(request,'home.html',{'books':books,'issues' : issues,'total_books':total_books,
           'issued_books':issued_books,'available_books':available_books})

def issue_book(request):
    form = IssueForm()
    if request.method == 'POST':
       form = IssueForm(request.POST)
       if form.is_valid():
           issue = form.save(commit=False)
           issue.due_date = date.today()+ timedelta(days=7)
           form.save()
           return redirect('issue_book')
       else:
        form = IssueForm()
    return render(request,'issue.html',{'form':form})

def return_book(request , issue_id):
    issue = get_object_or_404(Issue,id=issue_id)
    if issue.return_date is None:
        issue.return_date = date.today()

        book = issue.book
        book.quantity += 1
        book.save()

        issue.save()

    return redirect('home')