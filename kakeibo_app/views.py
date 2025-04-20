from django.shortcuts import render, redirect
from .models import Expense
from .forms import ExpenseForm  # ← 忘れずにインポート！
from django.db.models import Sum
import json

def index(request):
    expenses = Expense.objects.all().order_by('-date')
    total_income = expenses.filter(income=True).aggregate(Sum('amount'))['amount__sum'] or 0
    total_expense = expenses.filter(income=False).aggregate(Sum('amount'))['amount__sum'] or 0
    balance = total_income - total_expense

    context = {
        'expenses': expenses,
        'total_income': total_income,
        'total_expense': total_expense,
        'balance': balance
    }
    return render(request, 'kakeibo/index.html', context)

def add_expense(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')  # 登録完了後にトップへ戻る
    else:
        form = ExpenseForm()
    return render(request, 'kakeibo/add_expense.html', {'form': form})

def stats(request):
    # カテゴリごとの支出（支出のみをフィルター）
    category_data = (
        Expense.objects.filter(income=False)
        .values('category__name')
        .annotate(total=Sum('amount'))
        .order_by('-total')
    )

    labels = [item['category__name'] for item in category_data]
    data = [float(item['total']) for item in category_data]

    context = {
        'labels': json.dumps(labels),
        'data': json.dumps(data),
    }
    return render(request, 'kakeibo/stats.html', context)