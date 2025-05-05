from django.shortcuts import render, get_object_or_404, redirect
from .models import Expense, Category
from .forms import ExpenseForm  # ← 忘れずにインポート！
from django.db.models import Sum
import json
from PIL import Image, ImageOps, ImageFilter
import pytesseract
import os
from django.http import HttpResponse
from django.contrib import messages

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

def receipt_upload(request):
    if request.method == 'POST' and request.FILES['receipt']:
        uploaded_file = request.FILES['receipt']
        image = Image.open(uploaded_file)

        # 画像の前処理
        # グレースケール化
        image = image.convert('L')

        # 二値化（白黒に変換）
        threshold = 150
        image = image.point(lambda p: p > threshold and 255)

        # ノイズ除去
        image = image.filter(ImageFilter.MedianFilter())

        # OCRを実行
        custom_config = r'--oem 3 --psm 6'
        extracted_text = pytesseract.image_to_string(image, lang='jpn', config=custom_config)

        # 結果をテンプレートに渡して表示
        return render(request, 'kakeibo/receipt_upload.html', {
            'extracted_text': extracted_text
        })

    return render(request, 'kakeibo/receipt_upload.html')

def edit_expense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id)
    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            return redirect('index')  # 編集後トップへ戻る
    else:
        form = ExpenseForm(instance=expense)
    return render(request, 'kakeibo/edit.html', {'form': form})

def delete_expense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id)
    if request.method == 'POST':
        expense.delete()
        messages.success(request, '記録を削除しました。')
        return redirect('index')
    return render(request, 'kakeibo/delete.html', {'expense': expense})