import decimal
import json
import logging
from datetime import date
from copy import deepcopy
from .models import *

# Вывод родительских связей в кодах товара
def get_structure_code_description(s):
    """
    Возвращает полное описание кода ТНВЭД по таблице и по дереву.
    @param s: код ТНВЭД
    @return: список с узлами, в котором введенный ТНВЭД - последний
    """
    all_result = []

    try:
        # Находим запись по заданному коду
        item = Structure.objects.get(CN_CODE=s)
    except Structure.DoesNotExist:
        return {'result': []}

    # Добавляем информацию о текущем элементе в результат
    all_result.append({
        'code': item.CN_CODE,
        'name': item.NAME_EN,
    })

    parent_key = item.PARENT

    # Пока у текущего элемента есть родительский элемент
    while parent_key:
        try:
            # Убираем десятичную часть перед сравнением
            parent_key = parent_key.split('.')[0]
            # Находим родительский элемент по его ключу
            parent_item = Structure.objects.get(CNKEY=parent_key)
        except Structure.DoesNotExist:
            break

        # Добавляем информацию о родительском элементе в результат
        all_result.append({
            'code': parent_item.CN_CODE,
            'name': parent_item.NAME_EN,
        })

        # Обновляем parent_key для следующей итерации
        parent_key = parent_item.PARENT

    # Результат нужно перевернуть, чтобы элементы шли от корня к листьям
    return {'result': all_result[::-1]}

