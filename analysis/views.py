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
from authentication_app.decorators import allowed_users, admin_only, unauthenticated_user, approved_user_required

from prophet import Prophet
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error


db = firestore.client()

DB_PATH = "sales_data.db"
UPDATE_INTERVAL = 365 * 24 * 60 * 60  # update every year

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

def get_sales_data():
    if time.time() - get_last_update_time() > UPDATE_INTERVAL:
        fetch_and_store_data()
    
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM sales", conn)
    conn.close()

    df['business_date'] = pd.to_datetime(df['business_date'], dayfirst=True, errors='coerce')
    df = df.dropna(subset=['business_date', 'total_price'])
    df['detailed_orders'] = df['detailed_orders'].apply(lambda x: json.loads(x) if x else [])
    return df

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
            'predicted_sales': predicted_january_sales,
            'prediction_accuracy': accuracy,
        }

        return render(request, 'analysis/analysis.html', context)

    except Exception as e:
        error_message = traceback.format_exc()
        print("Analysis View Error:", error_message)
        return JsonResponse({"error": "Something went wrong. Check Django logs."}, status=500)

def filter_data(request):
    try:
        df = get_sales_data()
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

            detailed_orders = df['detailed_orders'].dropna()
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

# Prediction (Hybrid Model)
conn = sqlite3.connect(DB_PATH)
df = pd.read_sql("SELECT business_date, total_price FROM sales", conn)
conn.close()

df['business_date'] = pd.to_datetime(df['business_date'], dayfirst=True, errors='coerce')
df = df.dropna(subset=['business_date', 'total_price'])

# Get holidays from API
API_KEY = 'AjYi7mqOuumRPwEbkpEG9A7SjTZIczMz'
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

event_dates = get_events()

# Monthly Aggregation
monthly_sales = df.resample('MS', on='business_date')['total_price'].sum().reset_index()
monthly_sales = monthly_sales.rename(columns={'business_date': 'ds', 'total_price': 'y'})
monthly_sales['has_event'] = monthly_sales['ds'].dt.date.apply(
    lambda d: 1 if any(event.month == d.month for event in event_dates) else 0
)

# Prophet Forecast
model = Prophet(weekly_seasonality=False, yearly_seasonality=True, changepoint_prior_scale=0.4)
model.fit(monthly_sales[['ds', 'y']])
future = model.make_future_dataframe(periods=1, freq='MS')
forecast = model.predict(future)[['ds', 'yhat']]

# Merge predictions
merged = pd.merge(monthly_sales, forecast, on='ds', how='left')
merged['month'] = merged['ds'].dt.month
merged['year'] = merged['ds'].dt.year
merged['yhat_lag1'] = merged['yhat'].shift(1)
merged = merged.dropna()

features = ['month', 'year', 'yhat', 'yhat_lag1', 'has_event']

# Train/Test Split
train_data = merged[merged['ds'] < '2024-11-01']
test_data = merged[(merged['ds'] >= '2024-11-01') & (merged['ds'] <= '2024-12-01')]

X_train = train_data[features]
y_train = train_data['y']
X_test = test_data[features]
y_test = test_data['y']

# Train Random Forest
rf_model = RandomForestRegressor(n_estimators=1000, max_depth=20, random_state=42)
rf_model.fit(X_train, y_train)

# Evaluate
y_pred = rf_model.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)
avg_actual = y_test.mean()
accuracy = round(100 - ((mae / avg_actual) * 100), 2)
mae = round(mae, 2)

# Predict January 2025
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


print("\n Hybrid Model Forecast (Monthly):")
print(f" Accuracy for Nov + Dec 2024: {accuracy}%")
print(f"MAE: {mae} SAR")
print(f" January 2025 Total Sales Prediction: {predicted_january_sales} SAR")

#check if there is overfiting (احذفه بعدين)
train_pred = rf_model.predict(X_train)
train_mae = mean_absolute_error(y_train, train_pred)
train_accuracy = round(100 - ((train_mae / y_train.mean()) * 100), 2)

print(f"Train Accuracy: {train_accuracy}%")
print(f"Train MAE: {round(train_mae, 2)} SAR")
train_pred = rf_model.predict(X_train)
train_mae = mean_absolute_error(y_train, train_pred)
train_accuracy = round(100 - ((train_mae / y_train.mean()) * 100), 2)

print("\n Training Performance:")
print(f" Training Accuracy: {train_accuracy}%")
print(f" Training MAE: {round(train_mae, 2)} SAR")
