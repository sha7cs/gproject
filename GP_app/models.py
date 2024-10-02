from django.db import models

# Create your models here.

# categories (id, category)
# items (id, name, desc, category_id)
# transactions (id , item, quantity, price, tax, discount, total) we may a column that has costumer id but would be optional only applies for loyalty app users
# costumers (id, firstname, lastname, phone, email) -> only if they have some loyalty system بس كيف نربطه مع الترانزاكشن؟