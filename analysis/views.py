from django.shortcuts import render, redirect
from django.http import JsonResponse
import pandas as pd
import json  # تم إضافة استيراد JSON
import ast
from django.utils.translation import get_language, activate, gettext_lazy as _
from django.urls import reverse
from firebase_admin import firestore

db = firestore.client()

def get_sales_data():
    """جلب البيانات من Firestore وتحويلها إلى DataFrame"""
    sales_ref = db.collection('Sales_ARS') 
    docs = sales_ref.stream()

    data = []
    for doc in docs:
        record = doc.to_dict()

        # تحويل detailed_orders إلى قائمة فعلية
        try:
            record["detailed_orders"] = json.loads(record["detailed_orders"])
        except (json.JSONDecodeError, TypeError):
            record["detailed_orders"] = []

        data.append(record)

    df = pd.DataFrame(data)
    
    df['business_date'] = pd.to_datetime(df['business_date'], dayfirst=True, errors='coerce')
    df = df.dropna(subset=['business_date', 'total_price'])

    return df

def set_language(request):
    
    language = request.GET.get('language')
    if language:
        activate(language)
        request.session['django_language'] = language 
    next_url = request.META.get('HTTP_REFERER', '/')
    return redirect(next_url) 

def analysis_view(request):
    """تحليل بيانات المبيعات وعرضها في الصفحة"""
    try:
        df = get_sales_data()

        total_sales = df['total_price'].sum()
        total_transactions = len(df)

        # استخراج أفضل منتج مبيعًا
        detailed_orders = df['detailed_orders'].dropna()
        all_items = [item['item'] for order in detailed_orders for item in order]
        best_seller = pd.Series(all_items).value_counts().idxmax() if all_items else "N/A"

        
        monthly_sales = df.groupby(df['business_date'].dt.month)['total_price'].sum().to_dict()

        
        sales_growth_rate = 0
        if len(monthly_sales) >= 2:
            months = sorted(monthly_sales.keys())
            current_month, previous_month = months[-1], months[-2]
            current_sales, previous_sales = monthly_sales[current_month], monthly_sales[previous_month]
            if previous_sales > 0:
                sales_growth_rate = ((current_sales - previous_sales) / previous_sales) * 100

      
        category_sales = {}
        for order in detailed_orders:
            for item in order:
                category = item['category']
                category_sales[category] = category_sales.get(category, 0) + item['quantity']

        context = {
            'total_sales': total_sales,
            'total_transactions': total_transactions,
            'best_seller': best_seller,
            'sales_growth_rate': round(sales_growth_rate, 2),
            'monthly_sales': monthly_sales,
            'category_labels': list(category_sales.keys()),
            'category_data': list(category_sales.values()),
        }

        return render(request, 'analysis/analysis.html', context)
    except Exception as e:
        return render(request, 'analysis/error.html', {'error': str(e)})

def filter_data(request):
    
    try:
        df = get_sales_data()

        filter_type = request.GET.get('filter', 'month')
        selected_month = request.GET.get('month', None)

        sales_data = {}
        if filter_type == 'day' and selected_month:
            try:
                month_number = int(selected_month)
                filtered_df = df[df['business_date'].dt.month == month_number]
                sales_data = filtered_df.groupby(filtered_df['business_date'].dt.day)['total_price'].sum().to_dict()
            except ValueError:
                return JsonResponse({'error': 'Invalid month value'}, status=400)
        elif filter_type == 'month':
            sales_data = df.groupby(df['business_date'].dt.month)['total_price'].sum().to_dict()

        return JsonResponse({'sales': sales_data})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
