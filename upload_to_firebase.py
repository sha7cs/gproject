import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd


if not firebase_admin._apps:
    cred = credentials.Certificate("cafe-data-project-106c5-firebase-adminsdk-fbsvc-bf14c05a88.json")  # استبدل بالمسار الصحيح
    firebase_admin.initialize_app(cred)


db = firestore.client()


file_path = "Data/Sales_ARS.csv"
df = pd.read_csv(file_path)

if "id" not in df.columns:
    df.insert(0, "id", range(1, len(df) + 1))


collection_ref = db.collection("Sales_ARS")  


for _, row in df.iterrows():
    doc_id = str(row["id"])  
    doc_ref = collection_ref.document(doc_id)


    if not doc_ref.get().exists:
        doc_ref.set(row.to_dict())  

print("✅ البيانات أُضيفت إلى Firestore بنجاح بدون تكرار!")

