from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.
class Book(models.Model):
    title= models.CharField(max_length=100)
    author= models.CharField(max_length=100)
    quantity =models.IntegerField()
    def __str__(self):
         return self.title

class Student(models.Model):
    name = models.CharField(max_length=100)
    email =models.EmailField()
    def __str__(self):
        return self.name

class Issue(models.Model):
    student = models.ForeignKey(Student,on_delete=models.CASCADE)
    book = models.ForeignKey(Book,on_delete=models.CASCADE)
    issue_date = models.DateField(auto_now_add=True)
    return_date = models.DateField(null=True,blank=True)

    def save(self,*args,**kwargs):
        if not self.pk:
            if self.book.quantity >0:
               self.book.quantity -=1
               self.book.save()
            else:
                raise ValueError("Book out of stock")
        super().save(*args,**kwargs)

    def __str__(self):
        return f"{self.student} - {self.book}"

@receiver(post_save,sender=Issue)
def reduce_book_quantity(sender,instance,created,**kwargs):
    if created:
        print("Signal triggered")
        book= instance.book
        if book.quantity>0:
            book.quantity -=1
            book.save()

