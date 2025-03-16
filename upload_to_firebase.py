import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd

# 1. تهيئة الاتصال بـ Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate("cafe-data-project-106c5-firebase-adminsdk-fbsvc-13b89a3d8f.json")  
    firebase_admin.initialize_app(cred)

db = firestore.client()

# 2. قراءة ملف Excel
file_path = "Data/event data.xlsx"
df = pd.read_excel(file_path)

# 3. إضافة عمود ID تلقائي إذا ما كان موجود
df.insert(0, "id", range(1, len(df) + 1))

# 4. تجهيز كولكشن Firestore
collection_ref = db.collection("Events_data")

# 5. رفع البيانات مع التعامل مع التاريخ الفاضي NaT
for index, row in df.iterrows():
    event_data = row.to_dict()

    # تحقق من تاريخ gregorian_date وتعامل معه
    if pd.isna(event_data.get('gregorian_date')):
        event_data['gregorian_date'] = None
    else:
        event_data['gregorian_date'] = pd.to_datetime(event_data['gregorian_date']).to_pydatetime()

    doc_ref = collection_ref.document(str(event_data['id']))
    doc_ref.set(event_data)

print("✅ تم رفع جميع بيانات الفعاليات إلى Firebase بنجاح!")

# import firebase_admin
# from firebase_admin import credentials, firestore

# cred = credentials.Certificate("GP/firebase_config/cafe-data-project-106c5-firebase-adminsdk-fbsvc-ffab31fb27.json")
# firebase_admin.initialize_app(cred)

# db = firestore.client()
# print("Firestore connected successfully!")
