from django.shortcuts import render, redirect, get_object_or_404
from datetime import date, timedelta

from .models import Book, Issue
from .forms import IssueForm
from django.contrib.auth.decorators import login_required

# DRF
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework import status
from .serializers import BookSerializer, IssueSerializer


# ================= TEMPLATE VIEWS =================
@login_required
def home(request):
    books = Book.objects.all()
    issues = Issue.objects.all()

    total_books = Book.objects.count()
    available_books = Book.objects.filter(
        quantity__gt=0).count()
    total_issues = Issue.objects.filter(
        return_date=None
    ).count()

    return render(request, 'home.html', {
        'books': books,
        'issues': issues,
        'total_books': total_books,
        'available_books': available_books,
        'total_issues': total_issues,
    })


def issue_book(request):
    form = IssueForm()

    if request.method == 'POST':
        form = IssueForm(request.POST)
        if form.is_valid():
            issue = form.save(commit=False)
            issue.due_date = date.today() + timedelta(days=7)
            issue.save()
            return redirect('issue_book')

    return render(request, 'issue.html', {'form': form})


def return_book(request, issue_id):
    issue = get_object_or_404(Issue, id=issue_id)

    if issue.return_date is None:
        issue.return_date = date.today()
        issue.save()

    return redirect('home')


# ================= API VIEWS =================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_books(request):
    books = Book.objects.all()

    search = request.query_params.get('search', None)
    if search:
        books = books.filter(
            title__icontains=search
        ) | books.filter(
            author__icontains=search
        ) | books.filter(
            category__icontains=search
        )

    available = request.query_params.get('available', None)
    if available:
        books = books.filter(available=True)

    serializer = BookSerializer(books, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_single_book(request, id):
    try:
        book = Book.objects.get(id=id)
        serializer = BookSerializer(book)
        return Response(serializer.data)
    except Book.DoesNotExist:
        return Response(
            {'error': 'Book not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([IsAdminUser])
def create_book(request):
    serializer = BookSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )
    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )


@api_view(['PUT'])
@permission_classes([IsAdminUser])
def update_book(request, id):
    try:
        book = Book.objects.get(id=id)
        serializer = BookSerializer(
            book, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    except Book.DoesNotExist:
        return Response(
            {'error': 'Book not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def delete_book(request, id):
    try:
        book = Book.objects.get(id=id)
        book.delete()
        return Response(
            {'message': 'Book deleted successfully'},
            status=status.HTTP_200_OK
        )
    except Book.DoesNotExist:
        return Response(
            {'error': 'Book not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def issue_book_api(request, id):
    try:
        book = Book.objects.get(id=id)

        if not book.available:
            return Response(
                {'error': 'Book not available'},
                status=status.HTTP_400_BAD_REQUEST
            )

        issue = Issue.objects.create(
            book=book,
            issued_to=request.user,
            issue_date=date.today(),
            due_date=date.today() + timedelta(days=7)
        )

        book.available = False
        book.save()

        return Response({
            'message': 'Book issued successfully',
            'due_date': issue.due_date,
            'issue_id': issue.id
        }, status=status.HTTP_201_CREATED)

    except Book.DoesNotExist:
        return Response(
            {'error': 'Book not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def return_book_api(request, issue_id):
    try:
        issue = Issue.objects.get(id=issue_id)

        if issue.return_date:
            return Response(
                {'error': 'Book already returned'},
                status=status.HTTP_400_BAD_REQUEST
            )

        issue.return_date = date.today()

        # Fine calculation
        fine = 0
        if date.today() > issue.due_date:
            overdue_days = (
                date.today() - issue.due_date
            ).days
            fine = overdue_days * 5  # ₹5 per day

        issue.fine = fine
        issue.save()

        issue.book.available = True
        issue.book.save()

        return Response({
            'message': 'Book returned successfully',
            'fine': f'₹{fine}',
        })

    except Issue.DoesNotExist:
        return Response(
            {'error': 'Issue record not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def borrow_history(request):
    issues = Issue.objects.filter(
        issued_to=request.user)
    serializer = IssueSerializer(issues, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard(request):
    return Response({
        'total_books': Book.objects.count(),
        'available_books': Book.objects.filter(
            available=True).count(),
        'issued_books': Book.objects.filter(
            available=False).count(),
        'overdue_books': Issue.objects.filter(
            return_date=None,
            due_date__lt=date.today()
        ).count(),
    })


# ================= AUTH VIEWS =================

from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    username = request.data.get('username')
    password = request.data.get('password')
    email = request.data.get('email')

    if User.objects.filter(username=username).exists():
        return Response(
            {'error': 'Username already exists'},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = User.objects.create_user(
        username=username,
        password=password,
        email=email,
    )
    is_active=True
    user.save()


    refresh = RefreshToken.for_user(user)

    return Response({
        'message': 'User created successfully',
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    try:
        refresh_token = request.data.get('refresh')
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response(
            {'message': 'Logged out successfully'},
            status=status.HTTP_200_OK
        )
    except Exception:
        return Response(
            {'error': 'Invalid token'},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request):
    user = request.user
    return Response({
        'id': user.id,
        'username': user.username,
        'email': user.email,
    })