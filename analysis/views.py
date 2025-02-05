from django.shortcuts import render
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
import ast
from django.http import JsonResponse


file_path = "Data/filtered_data.csv"     
df = pd.read_csv(file_path)

df['business_date'] = pd.to_datetime(df['business_date'], errors='coerce')
df = df.dropna(subset=['business_date', 'total_price'])

def analysis_view(request):
    try:
       
        total_sales = df['total_price'].sum()
        total_transactions = len(df)

       
        detailed_orders = df['detailed_orders'].dropna().apply(ast.literal_eval)
        all_items = [item['item'] for order in detailed_orders for item in order]
        best_seller = pd.Series(all_items).value_counts().idxmax()

       
        monthly_sales = df.groupby(df['business_date'].dt.month)['total_price'].sum()
        
        plt.figure(figsize=(6, 4))
        if not monthly_sales.empty:
            monthly_sales.plot(kind='bar', color='skyblue')
        plt.title('Monthly Sales')
        plt.xlabel('Month')
        plt.ylabel('Total Sales')
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        monthly_chart = base64.b64encode(buffer.getvalue()).decode('utf-8')
        buffer.close()

        
        category_sales = {}
        for order in detailed_orders:
            for item in order:
                category = item['category']
                category_sales[category] = category_sales.get(category, 0) + item['quantity']
        
        
        plt.figure(figsize=(6, 4))
        category_df = pd.DataFrame.from_dict(category_sales, orient='index', columns=['quantity'])
        category_df['percentage'] = (category_df['quantity'] / category_df['quantity'].sum()) * 100
        category_df['percentage'].plot(kind='pie', autopct='%1.1f%%')
        plt.title('Category Sales Percentage')
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        category_chart = base64.b64encode(buffer.getvalue()).decode('utf-8')
        buffer.close()

        
        context = {
            'total_sales': total_sales,
            'total_transactions': total_transactions,
            'best_seller': best_seller,
            'monthly_chart': monthly_chart,
            'category_chart': category_chart,
        }

        return render(request, 'analysis/analysis.html', context)
    except Exception as e:
        return HttpResponse(f"Error: {e}")

def filter_data(request):
    filter_type = request.GET.get('filter', 'month')  

    if filter_type == 'day':
        sales_data = df.groupby(df['business_date'].dt.day)['total_price'].sum()
    elif filter_type == 'year':
        sales_data = df.groupby(df['business_date'].dt.year)['total_price'].sum()
    else: 
        sales_data = df.groupby(df['business_date'].dt.month)['total_price'].sum()

    sales_chart = sales_data.to_dict()
    return JsonResponse({'sales_chart': sales_chart})
