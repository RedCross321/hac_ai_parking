from app.database import Base, engine
from app.models import TestCamera, TestSnapshot  # Импортируйте ваши новые модели
# Если модели лежат в другом файле, поправьте путь импорта выше

def init_db():
    print("Создание таблиц в БД...")
    # Создаются все таблицы, унаследованные от Base
    Base.metadata.create_all(bind=engine)
    print("✓ Таблицы успешно созданы!")

if __name__ == "__main__":
    init_db()