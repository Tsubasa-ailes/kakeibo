from django.db import models

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Expense(models.Model):
    date = models.DateField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    income = models.BooleanField(default=False)  # Trueなら収入、Falseなら支出

    def __str__(self):
        return f"{self.date} - {self.description} - {self.amount}円"