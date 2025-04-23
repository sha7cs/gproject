import sqlite3
import json
import pandas as pd
import time
import requests
import datetime
import traceback

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.utils.translation import activate
from django.contrib.auth.decorators import login_required
from django.db.models.functions import ExtractMonth

from firebase_admin import firestore
from authentication.decorators import allowed_users, admin_only, unauthenticated_user, approved_user_required

from django.core.cache import cache
from prophet import Prophet
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error

from django.utils.translation import gettext as _
from django.conf import settings

db = firestore.client()

DB_PATH = "sales_data.db"
UPDATE_INTERVAL = 6 * 30 * 24 * 60 * 60  # update every 6 months

# Database Initialization
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

import pandas as pd
import json
import time
import ast

def get_sales_data(profile):
    """
    Load sales data for a specific user profile.
    Will fetch from Firebase or CSV based on profile.
    If neither is available, an error or empty DataFrame will be returned.
    """
    # Check if data needs to be updated (optional, based on last update time)
    if time.time() - get_last_update_time() > UPDATE_INTERVAL:
        if profile.firebase_config:
            # Fetch data from Firebase and store it in SQLite
            fetch_and_store_data_from_firebase(profile.firebase_config)
            # If Firebase is available, data will be fetched and stored in SQLite
            # So we just need to read it from SQLite in both cases

            conn = sqlite3.connect(DB_PATH)  # Connect to the SQLite database
            df = pd.read_sql("SELECT * FROM sales", conn)  # Read the data into a DataFrame
            conn.close()

            # Format the DataFrame as needed
            df['business_date'] = pd.to_datetime(df['business_date'], dayfirst=True, errors='coerce')
            df = df.dropna(subset=['business_date', 'total_price'])
            df['detailed_orders'] = df['detailed_orders'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) and x else [])


            return df
        elif profile.data_file:
            # Fetch data from CSV file (No need to store in SQLite)
            df = pd.read_csv(profile.data_file.path)
            # Process CSV data directly into DataFrame
            df['business_date'] = pd.to_datetime(df['business_date'], dayfirst=True, errors='coerce')
            df = df.dropna(subset=['business_date', 'total_price'])
            df = df.dropna(subset=['business_date', 'total_price'])
            df['detailed_orders'] = df['detailed_orders'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) and x else [])
            return df
        else:
            # Handle case where neither Firebase nor CSV is available
            raise ValueError("No data source available for this user")


def set_language(request):
    language = request.GET.get('language')
    if language:
        activate(language)
        request.session['django_language'] = language
    return redirect(request.META.get('HTTP_REFERER', '/'))

# Analysis View
@login_required
@allowed_users(allowed_roles=['normal_user', 'admins'])
@approved_user_required
def analysis_view(request):
    try:
        profile = UserProfile.objects.get(user=request.user)  # Get the current user's profile
        last_updated = profile.last_updated
        df = get_sales_data(profile)
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
        predicted_january_sales, accuracy = get_prediction(df, profile.user.id, last_updated)
        context = {
            'total_sales': total_sales,
            'total_transactions': total_transactions,
            'best_seller': best_seller,
            'sales_growth_rate': round(sales_growth_rate, 2),
            'monthly_sales': monthly_sales,
            'category_labels': list(category_sales.keys()),
            'category_data': list(category_sales.values()),
            'predicted_sales': predicted_january_sales,
            'prediction_accuracy': accuracy,
        }

        return render(request, 'analysis/analysis.html', context)

    except Exception as e:
        error_message = traceback.format_exc()
        print("Analysis View Error:", error_message)
        return JsonResponse({"error": "Something went wrong. Check Django logs."}, status=500)

# عشان نرسل الداتا ذي للشات 
def user_data(request):
    profile = UserProfile.objects.get(user=request.user)  # Get the current user's profile
    last_updated = profile.last_updated
    df = get_sales_data(profile)
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
    predicted_january_sales, accuracy = get_prediction(df, profile.user.id, last_updated)
    context = {
        'total_sales': total_sales,
        'total_transactions': total_transactions,
        'best_seller': best_seller,
        'sales_growth_rate': round(sales_growth_rate, 2),
        'monthly_sales': monthly_sales,
        'category_labels': list(category_sales.keys()),
        'category_data': list(category_sales.values()),
        'predicted_sales': predicted_january_sales,
        'prediction_accuracy': accuracy,
    }

    return context

def filter_data(request):
    try:
        profile = UserProfile.objects.get(user=request.user)  # Get the current user's profile
        df = get_sales_data(profile)
        filter_type = request.GET.get('filter', 'month')
        selected_month = request.GET.get('month', None)

        if filter_type == 'day' and selected_month:
            month_number = int(selected_month)
            filtered_df = df[df['business_date'].dt.month == month_number]
            sales_data = filtered_df.groupby(filtered_df['business_date'].dt.day)['total_price'].sum().to_dict()

            detailed_orders = filtered_df['detailed_orders'].dropna()
            category_sales = {}
            for order in detailed_orders:
                for item in order:
                    category = item['category']
                    quantity = item['quantity']
                    category_sales[category] = category_sales.get(category, 0) + quantity

        else:
            sales_data = df.groupby(df['business_date'].dt.month)['total_price'].sum().to_dict()

            detailed_orders =                 df['detailed_orders'].dropna()
            category_sales = {}
            for order in detailed_orders:
                for item in order:
                    category = item['category']
                    quantity = item['quantity']
                    category_sales[category] = category_sales.get(category, 0) + quantity
                    

        return JsonResponse({
            'sales': sales_data,
            'category_labels': list(category_sales.keys()),
            'category_data': list(category_sales.values())
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# # Prediction (Hybrid Model)
# conn = sqlite3.connect(DB_PATH)
# df = pd.read_sql("SELECT business_date, total_price FROM sales", conn)
# conn.close()

# df['business_date'] = pd.to_datetime(df['business_date'], dayfirst=True, errors='coerce')
# df = df.dropna(subset=['business_date', 'total_price'])

# Get holidays from API
API_KEY = settings.CALENDARIFIC_API_KEY
YEAR = datetime.datetime.today().year

def get_events():
    url = f"https://calendarific.com/api/v2/holidays?&api_key={API_KEY}&country=SA&year={YEAR}"
    response = requests.get(url)
    data = response.json()
    dates = []

    if 'response' in data and 'holidays' in data['response']:
        for h in data['response']['holidays']:
            dates.append(pd.to_datetime(h['date']['iso']).date())

    manual_dates = [
        f"{YEAR}-10-01", f"{YEAR}-03-21", f"{YEAR}-06-21",
        f"{YEAR}-07-30", f"{YEAR}-10-04"
    ]
    for date in manual_dates:
        d = pd.to_datetime(date).date()
        if d not in dates:
            dates.append(d)

    return dates


def get_prediction(df, user_id, last_updated):  # you’ll need to pass request.user.id or profile.user.id
    cache_key = f"user_prediction_{user_id}"
    cached_data = cache.get(cache_key)

    if cached_data and cached_data['last_updated'] == last_updated:
        return cached_data['result'], cached_data['accuracy']  # Return (prediction, accuracy) from cache

    if len(df) < 60:  # Safety check: minimum ~2 months of data
        return ("Data too small to generate accurate prediction", 0)

    try:
        event_dates = get_events()

        # Prepare data
        monthly_sales = df.resample('MS', on='business_date')['total_price'].sum().reset_index()
        if len(monthly_sales) < 3:
            return _("Not enough monthly data for prediction", 0)

        monthly_sales = monthly_sales.rename(columns={'business_date': 'ds', 'total_price': 'y'})
        monthly_sales['has_event'] = monthly_sales['ds'].dt.date.apply(
            lambda d: 1 if any(event.month == d.month for event in event_dates) else 0
        )

        # Prophet Forecast
        model = Prophet(weekly_seasonality=False, yearly_seasonality=True, changepoint_prior_scale=0.4)
        model.fit(monthly_sales[['ds', 'y']])
        future = model.make_future_dataframe(periods=1, freq='MS')
        forecast = model.predict(future)[['ds', 'yhat']]

        # Merge for ML
        merged = pd.merge(monthly_sales, forecast, on='ds', how='left')
        merged['month'] = merged['ds'].dt.month
        merged['year'] = merged['ds'].dt.year
        merged['yhat_lag1'] = merged['yhat'].shift(1)
        merged = merged.dropna()

        if merged.shape[0] < 3:
            return _("Insufficient data after merging", 0)

        features = ['month', 'year', 'yhat', 'yhat_lag1', 'has_event']

        # Train/Test Split
        train_data = merged[merged['ds'] < '2024-11-01']
        test_data = merged[(merged['ds'] >= '2024-11-01') & (merged['ds'] <= '2024-12-01')]

        if train_data.empty or test_data.empty:
            return _("Not enough data for training/testing split", 0)

        X_train = train_data[features]
        y_train = train_data['y']
        X_test = test_data[features]
        y_test = test_data['y']

        # Random Forest
        rf_model = RandomForestRegressor(n_estimators=1000, max_depth=20, random_state=42)
        rf_model.fit(X_train, y_train)

        # Accuracy
        y_pred = rf_model.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)
        avg_actual = y_test.mean() if y_test.mean() != 0 else 1
        accuracy = round(100 - ((mae / avg_actual) * 100), 2)
        accuracy = max(0, min(accuracy, 100))

        # Predict January
        january_ds = pd.to_datetime('2025-01-01')
        has_event_jan = 1 if any(event.month == 1 for event in event_dates) else 0
        last_yhat = forecast.iloc[-2]['yhat']
        next_yhat = forecast.iloc[-1]['yhat']

        january_features = pd.DataFrame([{
            'month': 1,
            'year': 2025,
            'yhat': next_yhat,
            'yhat_lag1': last_yhat,
            'has_event': has_event_jan
        }])

        predicted_january_sales = round(rf_model.predict(january_features)[0], 2)

        # Cache result for 1 day (86400 seconds)
        cache.set(cache_key, {
            'result': predicted_january_sales,
            'accuracy': accuracy,
            'last_updated': last_updated,
        }, timeout=86400)

        return predicted_january_sales, accuracy

    except Exception as e:
        print("Prediction error:", str(e))
        return ("Prediction error", 0)



init_db()

#################
from django.shortcuts import render
from django.http import HttpResponse
import pandas as pd
import tempfile
from django.template.loader import render_to_string
from weasyprint import HTML
from authentication.models import UserProfile 
from django.core.exceptions import ObjectDoesNotExist
import ast
from .templatetags import filters

import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
import base64

def generate_pie_chart(category_sales):
    """Generate a pie chart for category sales distribution with labels."""
    if not category_sales:
        return None  # No chart if no data

    categories, values = zip(*category_sales.items())  

    fig, ax = plt.subplots(figsize=(5,3), facecolor='#1E1E1E')  # Dark background
    colors = ['#2E2E2E', '#595959', '#8C8C8C', '#BFBFBF', '#D9D9D9']  # Shades of black/grey  

    wedges, texts, autotexts = ax.pie(
        values, labels=None, autopct='%1.1f%%', startangle=140, 
        colors=colors[:len(categories)], textprops={'color': 'white'}
    )
    
    # Improve label visibility
    for text in texts:
        text.set_color('white')
    for autotext in autotexts:
        autotext.set_color('white')

    # Add a legend outside the chart for clarity
    ax.legend(wedges, categories, title="Categories", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1), fontsize=10)
    ax.set_facecolor('#1E1E1E')

    # Save figure to a BytesIO object
    pie_image = BytesIO()
    plt.savefig(pie_image, format='png', bbox_inches='tight', transparent=True)
    plt.close(fig)
    pie_image.seek(0)

    return pie_image



def generate_line_chart(monthly_sales):
    """Generate a better sales growth chart with proper labels and colors."""
    if len(monthly_sales) < 2:
        print("⚠ Not enough data for a line chart!")
        return None

    months = sorted(monthly_sales.keys())  # X-axis (e.g., 10, 11)
    sales = [monthly_sales[m] for m in months]  # Y-axis values

    fig, ax = plt.subplots(figsize=(5, 3), facecolor='white')

    # Line plot with visible markers
    ax.plot(
        months, sales, marker='o', linestyle='-', color='black', linewidth=2.5, 
        markerfacecolor='darkgray', markeredgecolor='black', markersize=6, label='Monthly Sales'
    )

    # Explicitly set x-axis labels
    ax.set_xticks(months)
    ax.set_xticklabels([f"Month {m}" for m in months], fontsize=10, fontweight="bold")

    # Explicitly set y-axis labels (ensuring even spacing)
    min_sales, max_sales = min(sales), max(sales)
    y_ticks = np.linspace(min_sales, max_sales, num=5)  # Create 5 evenly spaced ticks
    ax.set_yticks(y_ticks)
    ax.set_yticklabels([f"${int(y)}" for y in y_ticks], fontsize=10)

    # Labels & Title
    ax.set_xlabel("Month", fontsize=10, fontweight='bold')
    ax.set_ylabel("Sales ($)", fontsize=10, fontweight='bold')
    ax.set_title("Sales Growth Over Time", fontsize=12, fontweight='bold')

    # Grid & Legend
    ax.grid(True, linestyle="--", alpha=0.6, color="gray")
    ax.legend(fontsize=9, facecolor="lightgray", edgecolor="black")

    # Save to memory
    line_image = BytesIO()
    plt.savefig(line_image, format='png', bbox_inches='tight', dpi=100)
    plt.close(fig)
    line_image.seek(0)

    return line_image


def sales_report_pdf(request):
    """Generates a PDF report from sales analysis data."""
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        user_file = user_profile.data_file

        if not user_file:
            return HttpResponse("User has not uploaded a CSV file.", status=400)

        df = pd.read_csv(user_file.path)
        df['business_date'] = pd.to_datetime(df['business_date'], errors='coerce', dayfirst=True)

        # ✅ New: Handle selected months from modal
        selected_months = request.GET.getlist('months')
        if selected_months:
            selected_months = [int(month) for month in selected_months]
            df = df[df['business_date'].dt.month.isin(selected_months)]

        else:
            # Fallback to full range if no selection
            start_date = request.GET.get('start_date')
            end_date = request.GET.get('end_date')

            if start_date and end_date:
                start_date = pd.to_datetime(start_date)
                end_date = pd.to_datetime(end_date)
            else:
                start_date = df['business_date'].min()
                end_date = df['business_date'].max()

            df = df[(df['business_date'] >= start_date) & (df['business_date'] <= end_date)]

        if df.empty:
            return HttpResponse("No data available for the selected range.", status=400)

        total_sales = df['total_price'].sum()
        total_transactions = len(df)

        detailed_orders = df['detailed_orders'].dropna()
        all_items = []

        for order in detailed_orders:
            try:
                order_items = ast.literal_eval(order)
                for item in order_items:
                    all_items.append(item['item'])
            except (ValueError, SyntaxError) as e:
                print(f"Error parsing detailed_orders: {e}")

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
            try:
                order_items = ast.literal_eval(order)
                for item in order_items:
                    category = item['category']
                    category_sales[category] = category_sales.get(category, 0) + item['quantity']
            except (ValueError, SyntaxError) as e:
                print(f"Error parsing detailed_orders: {e}")

        category_chart = generate_pie_chart(category_sales)
        growth_chart = generate_line_chart(monthly_sales)

        import base64
        category_chart2 = base64.b64encode(category_chart.read()).decode() if category_chart else ""
        growth_chart2 = base64.b64encode(growth_chart.read()).decode() if growth_chart else ""

        context = {
            'cafe_name': user_profile.cafe_name,
            'total_sales': total_sales,
            'total_transactions': total_transactions,
            'best_seller': best_seller,
            'sales_growth_rate': round(sales_growth_rate, 2),
            'monthly_sales': monthly_sales,
            'category_info': list(zip(category_sales.keys(), category_sales.values())),
            'start_date': df['business_date'].min().strftime('%Y-%m-%d') if not selected_months else '',
            'end_date': df['business_date'].max().strftime('%Y-%m-%d') if not selected_months else '',
            'category_chart': category_chart2,
            'growth_chart': growth_chart2,
        }

        html_string = render_to_string('analysis/pdf_template.html', context)

        with tempfile.NamedTemporaryFile(delete=True) as temp_pdf:
            HTML(string=html_string).write_pdf(temp_pdf.name)
            temp_pdf.seek(0)
            pdf_data = temp_pdf.read()

        response = HttpResponse(pdf_data, content_type="application/pdf")
        response["Content-Disposition"] = "inline; filename=sales_report.pdf"
        return response

    except Exception as e:
        return HttpResponse(f"Error generating PDF: {str(e)}", status=500)
