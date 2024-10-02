import os
import django

# Устанавливаем переменную среды, указывающую Django, где находятся настройки проекта
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alestadrf.settings')

# Загружаем настройки Django
django.setup()

import pandas as pd
from models import Structure


def load_data_from_excel(file_path):
    # Читаем данные из файла Excel в DataFrame
    df = pd.read_excel(file_path)

    # Проходимся по каждой строке DataFrame и создаем объекты модели Structure
    for index, row in df.iterrows():
        Structure.objects.create(
            CNKEY=row['CNKEY'],
            LEVEL=row['LEVEL'],
            CN_CODE=row['CN_CODE'],
            NAME_EN=row['NAME_EN'],
            PARENT=row['PARENT'],
            SU=row['SU'],
            SU_Name=row['SU_Name']
        )

if __name__ == "__main__":
    # Путь к файлу Excel
    file_path = 'CN2024_Structure.xlsx'
    load_data_from_excel(file_path)