from django.shortcuts import render
from django.http import JsonResponse,HttpResponseRedirect
import pandas as pd
import ast
from django. utils.translation import get_language, activate 
from django.utils.translation import gettext_lazy as _
from django. utils.translation import get_language, activate
from django.urls import reverse
from django.shortcuts import redirect


file_path = "Data/Sales_ARS.csv"
df = pd.read_csv(file_path)
df['business_date'] = pd.to_datetime(df['business_date'], dayfirst=True, errors='coerce')
df = df.dropna(subset=['business_date', 'total_price'])


def set_language(request):
    language = request.GET['language']
    if language:
        activate(language)
        request.session['django_language'] = language 
    next_url = request.META.get('HTTP_REFERER', '/')
    return redirect(next_url) 


def analysis_view(request):
    try:
        total_sales = df['total_price'].sum()
        total_transactions = len(df)

        detailed_orders = df['detailed_orders'].dropna().apply(ast.literal_eval)
        all_items = [item['item'] for order in detailed_orders for item in order]
        best_seller = pd.Series(all_items).value_counts().idxmax()

        monthly_sales = df.groupby(df['business_date'].dt.month)['total_price'].sum().to_dict()

     
        if len(monthly_sales) >= 2:
            months = sorted(monthly_sales.keys())
            current_month = months[-1]
            previous_month = months[-2]
            current_sales = monthly_sales[current_month]
            previous_sales = monthly_sales[previous_month]
            sales_growth_rate = ((current_sales - previous_sales) / previous_sales) * 100
        else:
            sales_growth_rate = 0

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
    filter_type = request.GET.get('filter', 'month')
    selected_month = request.GET.get('month', None)

    if filter_type == 'day' and selected_month:
        month_number = int(selected_month)
        filtered_df = df[df['business_date'].dt.month == month_number]
        sales_data = filtered_df.groupby(filtered_df['business_date'].dt.day)['total_price'].sum().to_dict()
    elif filter_type == 'month':
        sales_data = df.groupby(df['business_date'].dt.month)['total_price'].sum().to_dict()
    else:
        sales_data = {}

    return JsonResponse({'sales': sales_data})