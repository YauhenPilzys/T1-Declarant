import requests
import hashlib
import logging

from .models import TreeTnved, Tnved, Excise
from django.conf import settings

logger2 = logging.getLogger(__name__)
logger2.setLevel(logging.INFO)

# настройка обработчика и форматировщика для logger2
handler2 = logging.FileHandler(f"{__name__}.log", mode='a')
formatter2 = logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s")

# добавление форматировщика к обработчику
handler2.setFormatter(formatter2)
# добавление обработчика к логгеру
logger2.addHandler(handler2)


def start_session():
    session_key = ''
    res = requests.get('https://www.tws.by/tws/api/r0')
    if res:
        logger2.info('R0 - ок.')
        json = res.json()
        token_r0 = json['Token']
        temp_string = token_r0 + settings.TWS_API_KEY
        hash256 = hashlib.sha256(temp_string.encode('utf-8')).hexdigest()
        params = dict(VirtualOfficeID=settings.TWS_OFFICE_ID, Token=token_r0, Hash=hash256)
        res = requests.get('https://www.tws.by/tws/api/r1', params=params)
        if res:
            logger2.info('R1 - ok.')
            session_key = res.json()['SessionKey']
        else:
            logger2.info('R1 - error.')
    else:
        logger2.info('R0 - error.')
    return session_key


def stop_session(session_key=''):
    if session_key:
        params = dict(SessionKey=session_key)
        res = requests.get('https://www.tws.by/tws/api/rE', params=params)
        if res:
            logger2.info('Session completed successfully.')
        else:
            logger2.info('Error closing session.')


def update_tnved():
    session_key = start_session()
    if session_key:
        logger2.info('Start TreeTnvedUpdate!')
        params = dict(SessionKey=session_key)
        res_tree = requests.get('https://www.tws.by/tws/api/r2', params=params)
        if res_tree:
            logger2.info('Tree_tnved json received successfully.')
        else:
            logger2.info('Failed to get tree_tnved json.')


        res_tnved = requests.get('https://www.tws.by/tws/api/r3', params=params)
        if res_tnved:
           logger2.info('Tnved json received successfully.')
        else:
           logger2.info('Failed to get Tnved json.')

        if res_tree and res_tnved:  # получили данные по обеим таблицам, значит можно обновляться
            # очищаем таблицы
            Tnved.objects.all().delete()
            TreeTnved.objects.all().delete()
            Excise.objects.all().delete()

            # заполняем дерево кодов
            logger2.info('Start save tree_tnved.')
            tree = res_tree.json()['Tree']
            noparent_list = []      # список записей, у которых не установился родитель
            for t in tree:
                # создаем, заполняем список объектами TreeTnved
                if t['ParentID']:
                    try:
                        parent = TreeTnved.objects.get(pk=t['ParentID'])
                    except:
                        parent = None
                        noparent_list.append({"ID": t['ID'], "ParentID": t['ParentID']})
                        logger2.error(f"ERROR. id - {t['ID']}, parent - {t['ParentID']}, name - {t['Name']}")
                else:
                    parent = None

                # преобразуем код, чтоб был без пробелов
                tmp = t['Code']
                if tmp.find('РАЗДЕЛ') == -1:
                    n_code = tmp.replace(' ', '')
                else:
                    n_code = tmp

                tt_object = TreeTnved(
                        id=t['ID'],
                        ParentID=parent,
                        Name=t['Name'],
                        Code=n_code,
                        DateFrom=t['DateFrom'],
                        DateTo=t['DateTo'],
                    )

                # сохраняем данные в таблицу TreeTnved
                try:
                    tt_object.save()
                except:
                    logger2.error(f"NOT SAVE. id - {t['ID']}, parent - {t['ParentID']}, name - {t['Name']}")

            # устанавливаем родителей для тех записей, которые изначально не установились
            for t in noparent_list:
                TreeTnved.objects.filter(pk=t['ID']).update(ParentID=t['ParentID'])

            logger2.info('Tree_tnved saved.')
            logger2.info('Start save tnved.')

            # заполняем подробную таблицу с кодами
            tnved = res_tnved.json()['Tnved']
            for t in tnved:
                # создаем, заполняем список объектами Tnved
                if t['TreeID']:
                    try:
                        key_tree = TreeTnved.objects.get(pk=t['TreeID'])
                    except:
                        key_tree = None
                        logger2.error(f"id - {t['ID']}, tree - {t['TreeID']}, name - {t['Name']}")
                else:
                    key_tree = None

                tt_object = Tnved(
                    id=t['ID'],
                    TreeID=key_tree,
                    Name=t['Name'],
                    Code=t['Code'].replace(' ', ''),
                    TariffText=t.get('TariffText'),
                    TariffAdvalor=t.get('TariffAdvalor'),
                    TariffSpecific=t.get('TariffSpecific'),
                    TariffSpecificCurrency=t.get('TariffSpecificCurrency'),
                    TariffSpecificMeasureAmount=t.get('TariffSpecificMeasureAmount'),
                    TariffSpecificMeasureUnit=t.get('TariffSpecificMeasureUnit'),
                    TariffSpecificAddedToAdvalor=t.get('TariffSpecificAddedToAdvalor'),
                    AdditionalMeasureUnit=t.get('AdditionalMeasureUnit'),
                    Ad=t.get('Ad'),
                    Sp=t.get('Sp'),
                    Ex=t.get('Ex'),
                    Ip=t.get('Ip'),
                    F=t.get('F'),
                    Ta=t.get('Ta'),
                    DateFrom=t['DateFrom'],
                    DateTo=t['DateTo'],
                )

                # сохраняем данные в таблицу Tnved
                try:
                    tt_object.save()
                    # если для товара указаны акцизы - загружаем и их
                    if tt_object.Ex:
                        params = dict(SessionKey=session_key, Code=tt_object.Code)
                        res_ex = requests.get('https://www.tws.by/tws/api/r12', params=params)
                        if res_ex:
                            for re in res_ex.json()['Excises']:
                                exc_obj = Excise(
                                    TnvedID=tt_object,
                                    Name=re['Name'],
                                    DateFrom=re['DateFrom'],
                                    DateTo=re['DateTo'],
                                    Rate=re['Rate'],
                                    Currency=re['Currency'],
                                    Amount=re['Amount'],
                                    MeasureUnit=re['MeasureUnit'],
                                )
                                exc_obj.save()
                except:
                    logger2.error(f"NOT SAVE. id - {t['ID']}, tree - {t['TreeID']}, name - {t['Name']}")

            logger2.info('Tnved saved.')

        stop_session(session_key)
    return {'result': 'ok'}
