import sqlite3
import json
import pandas as pd
import time
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.utils.translation import activate
from firebase_admin import firestore
from authentication_app.decorators import allowed_users, admin_only, unauthenticated_user,approved_user_required
from django.contrib.auth.decorators import login_required

db = firestore.client()

DB_PATH = "sales_data.db"
UPDATE_INTERVAL = 365 * 24 * 60 * 60  #update every year

def init_db():
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            business_date TEXT,
            total_price REAL,
            detailed_orders TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS metadata (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')
    conn.commit()
    conn.close()

def get_last_update_time():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM metadata WHERE key = 'last_update'")
    result = cursor.fetchone()
    conn.close()
    return float(result[0]) if result else 0

def set_last_update_time():
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("REPLACE INTO metadata (key, value) VALUES ('last_update', ?)", (str(time.time()),))
    conn.commit()
    conn.close()

def fetch_and_store_data():
    
    sales_ref = db.collection('Sales_ARS')
    docs = sales_ref.stream()
    
    data = []
    for doc in docs:
        record = doc.to_dict()
        try:
            record["detailed_orders"] = json.dumps(json.loads(record["detailed_orders"].replace("'", '"')))
        except json.JSONDecodeError:
            record["detailed_orders"] = "[]"
        
        data.append((record['business_date'], record['total_price'], record['detailed_orders']))
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM sales")  
    cursor.executemany("INSERT INTO sales (business_date, total_price, detailed_orders) VALUES (?, ?, ?)", data)
    conn.commit()
    conn.close()
    set_last_update_time()

def get_sales_data():

    if time.time() - get_last_update_time() > UPDATE_INTERVAL:
        fetch_and_store_data()
    
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM sales", conn)
    conn.close()
    
    df['business_date'] = pd.to_datetime(df['business_date'], errors='coerce')
    df = df.dropna(subset=['business_date', 'total_price'])
    df['detailed_orders'] = df['detailed_orders'].apply(lambda x: json.loads(x) if x else [])
    return df

def set_language(request):
    language = request.GET.get('language')
    if language:
        activate(language)
        request.session['django_language'] = language 
    return redirect(request.META.get('HTTP_REFERER', '/'))

@login_required
@allowed_users(allowed_roles=['normal_user','admins'])
@approved_user_required
def analysis_view(request):
    try:
        df = get_sales_data()
        total_sales = df['total_price'].sum()
        total_transactions = len(df)
        
        detailed_orders = df['detailed_orders'].dropna()
        all_items = [item['item'] for order in detailed_orders for item in order]
        best_seller = pd.Series(all_items).value_counts().idxmax() if all_items else None
        
        monthly_sales = df.groupby(df['business_date'].dt.month)['total_price'].sum().to_dict()
        
        if len(monthly_sales) >= 2:
            months = sorted(monthly_sales.keys())
            sales_growth_rate = ((monthly_sales[months[-1]] - monthly_sales[months[-2]]) / monthly_sales[months[-2]]) * 100
        else:
            sales_growth_rate = 0
        
        category_sales = {}
        for order in detailed_orders:
            for item in order:
                category_sales[item['category']] = category_sales.get(item['category'], 0) + item['quantity']
        
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
        
        if filter_type == 'day' and selected_month:
            month_number = int(selected_month)
            filtered_df = df[df['business_date'].dt.month == month_number]
            sales_data = filtered_df.groupby(filtered_df['business_date'].dt.day)['total_price'].sum().to_dict()
        else:
            sales_data = df.groupby(df['business_date'].dt.month)['total_price'].sum().to_dict()
        
        return JsonResponse({'sales': sales_data})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


init_db()