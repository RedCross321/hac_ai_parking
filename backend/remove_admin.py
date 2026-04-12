import sys
import os
sys.path.insert(0, os.getcwd())   # добавляем текущую папку в пути импорта

from app.database import SessionLocal
from app.models import User

db = SessionLocal()
admin = db.query(User).filter(User.is_admin == True).first()
if admin:
    db.delete(admin)
    db.commit()
    print(f"✅ Администратор {admin.email} удалён.")
else:
    print("⚠️ Администратор не найден.")
db.close()