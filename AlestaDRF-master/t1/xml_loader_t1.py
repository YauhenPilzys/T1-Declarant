from .models import *
from datetime import datetime
import json
from decimal import Decimal
from django.contrib.auth.models import User





def generate_lrn(user_id):
    current_time = datetime.now()
    date_part = current_time.strftime("%Y%m%d")
    time_part = current_time.strftime("%H%M")
    user_id_part = str(user_id).zfill(3)
    return f"LT{date_part}{time_part}{user_id_part}"


def prepare_guid(s):
    t = s.replace('-', '')
    return t[0:8] + '-' + t[8:12] + '-' + t[12:16] + '-' + t[16:20] + '-' + t[20:]


def new_xml_load(s, user_l):
    """
    Создаем новую запись и сохраняем туда данные из json.
    @param s: json с данными
    @param user_l: пользователь
    @return: id созданного xml и сообщения, собранные при записи в БД
    """

    messages = []
    warnings = []
    xmlmodel = t1_xml()  # Основная таблица XML
    xmlmodel.user = user_l  # пользователь, который загрузил данные
    xmlmodel.date_time = datetime.now()  # Установим текущее время для поля date_time
    xmlmodel.LRN = generate_lrn(user_l.id)  # Генерация номера декларации LRN

    try:
        y = json.loads(s)
    except json.JSONDecodeError as e:
        messages.append(f'Ошибка при декодировании JSON: {e}')
        return {
            'id': 0,
            'messages': messages,
            'warnings': warnings,
        }

    if not isinstance(y, dict):
        messages.append('Ошибка: JSON не преобразован в словарь.')
        return {
            'id': 0,
            'messages': messages,
            'warnings': warnings,
        }

    # Заполнение полей основной таблицы t1_xml
    xmlmodel.SynIdeMES1 = y["SynIdeMES1"]  # Идентификатор синтаксиса
    xmlmodel.SynVerNumMES2 = y["SynVerNumMES2"]  # Версия синтаксиса
    xmlmodel.MesSenMES3 = y["MesSenMES3"]  # Отправитель сообщения
    xmlmodel.MesRecMES6 = y["MesRecMES6"]  # Получатель сообщения
    xmlmodel.DatOfPreMES9 = datetime.now().strftime("%y%m%d")  # Формат: YYMMDD  дата ( ставится автоматически)
    xmlmodel.TimOfPreMES10 = datetime.now().strftime("%H%M")   # Формат: HHMM время (ставится автоматически)
    xmlmodel.IntConRefMES11 = y["IntConRefMES11"]  # Внутренний контрольный референс должен формироваться LTДАТАВРЕМЯ
    xmlmodel.MesIdeMES19 = y["MesIdeMES19"]  # Идентификатор сообщения делается равным полю LRN автоматически
    xmlmodel.MesTypMES20 = y["MesTypMES20"]  # Тип сообщения

    xmlmodel.RefNumHEA4 = y.get("RefNumHEA4", None)  # Номер документа декларации
    xmlmodel.TypOfDecHEA24 = y.get("TypOfDecHEA24")  # Тип декларации
    xmlmodel.CouOfDesCodHEA30 = y["CouOfDesCodHEA30"]  # Код страны назначения
    xmlmodel.PlaOfLoaCodHEA46 = y["PlaOfLoaCodHEA46"]  # Код места загрузки
    xmlmodel.CouOfDisCodHEA55 = y["CouOfDisCodHEA55"]  # Код страны выгрузки
    xmlmodel.InlTraModHEA75 = y["InlTraModHEA75"]  # Внутренний транспортный модуль (грузовой - 30)
    xmlmodel.IdeOfMeaOfTraAtDHEA78 = y["IdeOfMeaOfTraAtDHEA78"]  # Идентификатор транспортного средства на отгрузке
    xmlmodel.NatOfMeaOfTraAtDHEA80 = y["NatOfMeaOfTraAtDHEA80"]  # Национальность транспортного средства на отгрузке
    xmlmodel.IdeOfMeaOfTraCroHEA85 = y["IdeOfMeaOfTraCroHEA85"]  # Идентификатор транспортного средства на границе
    xmlmodel.NatOfMeaOfTraCroHEA87 = y["NatOfMeaOfTraCroHEA87"]  # Национальность транспортного средства на границе
    xmlmodel.ConIndHEA96 = y["ConIndHEA96"]  # Индикатор контейнера
    xmlmodel.ConNum = y["ConNum"]  # Номер контейнера (если применимо)
    xmlmodel.DiaLanIndAtDepHEA254 = y["DiaLanIndAtDepHEA254"]  # Индикатор языка на отгрузке
    xmlmodel.NCTSAccDocHEA601LNG = y["NCTSAccDocHEA601LNG"]  # Язык оформления таможенных документов
    xmlmodel.TotNumOfIteHEA305 = y["TotNumOfIteHEA305"]  # Общее количество товара
    xmlmodel.TotNumOfPacHEA306 = y["TotNumOfPacHEA306"]  # Общее количество упаковок
    xmlmodel.TotGroMasHEA307 = y["TotGroMasHEA307"]  # Общая масса брутто
    xmlmodel.TraChaMetOfPayHEA1 = y["TraChaMetOfPayHEA1"]  # Метод оплаты перевозки
    xmlmodel.SecHEA358 = y["SecHEA358"]  # (неизвестно что)
    xmlmodel.CodPlUnHEA357 = y["CodPlUnHEA357"]  # Код места доставки

    # Информация о поручителе
    xmlmodel.NamPC17 = y.get("NamPC17")
    xmlmodel.StrAndNumPC122 = y.get("StrAndNumPC122")
    xmlmodel.PosCodPC123 = y.get("PosCodPC123")
    xmlmodel.CitPC124 = y.get("CitPC124")
    xmlmodel.CouPC125 = y.get("CouPC125")
    xmlmodel.NADLNGPC = y.get("NADLNGPC")
    xmlmodel.TINPC159 = y.get("TINPC159")


    # Информация о отправителе
    xmlmodel.NamCO17 = y.get("NamCO17")
    xmlmodel.StrAndNumCO122 = y.get("StrAndNumCO122")
    xmlmodel.PosCodCO123 = y.get("PosCodCO123")
    xmlmodel.CitCO124 = y.get("CitCO124")
    xmlmodel.CouCO125 = y.get("CouCO125")

    # Информация о получателе
    xmlmodel.NamCE17 = y.get("NamCE17")
    xmlmodel.StrAndNumCE122 = y.get("StrAndNumCE122")
    xmlmodel.PosCodCE123 = y.get("PosCodCE123")
    xmlmodel.CitCE124 = y.get("CitCE124")
    xmlmodel.CouCE125 = y.get("CouCE125")
    xmlmodel.NADLNGCE = y.get("NADLNGCE")


    # Заполнение данных таможни отправления
    xmlmodel.RefNumEPT1 = y.get("RefNumEPT1") #Номер таможни отправления

    # Заполнение данных таможни отправления
    xmlmodel.RefNumEST1 = y.get("RefNumEST1")  # Номер таможни назначения

    # Информация о представителе
    xmlmodel.NamREP5 = y.get("NamREP5")  # Имя представителя
    xmlmodel.RepCapREP18 = y.get("RepCapREP18")  # наверное должность представителя
    xmlmodel.RepCapREP18LNG = y.get("RepCapREP18LNG")  # язык


    # Заполнение данных гарантии в таблице t1_xml
    xmlmodel.GuaTypGUA1 = y.get("GuaTypGUA1")  # Тип гарантии
    xmlmodel.GuaRefNumGRNREF1 = y.get("GuaRefNumGRNREF1") # Номер счета гарантии
    xmlmodel.AccCodREF6 = y.get("AccCodREF6")  # Код доступа
    xmlmodel.ANotValForOthConPLIM2 = y.get("NotValForOthConPLIM2")  # Код страны откуда гарантия

    # Информация о транспортной компании ASSTRA (перевозчик)
    xmlmodel.NamCARTRA121 = y.get("NamCARTRA121")  # Название транспортной компании
    xmlmodel.StrAndNumCARTRA254 = y.get("StrAndNumCARTRA254")  # Адрес (улица и номер)
    xmlmodel.PosCodCARTRA121 = y.get("PosCodCARTRA121")  # Почтовый индекс
    xmlmodel.CitCARTRA789 = y.get("CitCARTRA789")  # Город
    xmlmodel.CouCodCARTRA587 = y.get("CouCodCARTRA587")  # Код страны
    xmlmodel.NADCARTRA121 = y.get("NADCARTRA121")  # Где заренистрирована ТК или язык хз

    # Информация о отправителе для этого груза ASSTRA  <TRACORSEC037>
    xmlmodel.NamTRACORSEC041 = y.get("NamTRACORSEC041")  # Название второго перевозчика
    xmlmodel.StrNumTRACORSEC043 = y.get("StrNumTRACORSEC043")  # Адрес
    xmlmodel.PosCodTRACORSEC042 = y.get("PosCodTRACORSEC042")  # Индекс
    xmlmodel.CitTRACORSEC038 = y.get("CitTRACORSEC038")  # Город
    xmlmodel.CouCodTRACORSEC039 = y.get("CouCodTRACORSEC039")  # Код страны
    xmlmodel.TRACORSEC037LNG = y.get("TRACORSEC037LNG")  # Язык

    # Информация об получателе для этого груза
    xmlmodel.NameTRACONSEC033 = y.get("NameTRACONSEC033")  # Название получателя
    xmlmodel.StrNumTRACONSEC035 = y.get("StrNumTRACONSEC035")  # Адрес  (улица и номер)
    xmlmodel.PosCodTRACONSEC034 = y.get("PosCodTRACONSEC034")  # Почтовый индекс
    xmlmodel.CitTRACONSEC030 = y.get("CitTRACONSEC030")  # Город
    xmlmodel.CouCodTRACONSEC031 = y.get("CouCodTRACONSEC031")  # Код страны
    xmlmodel.TRACONSEC029LNG = y.get("TRACONSEC029LNG")  # Язык

    # Заполнение информации о декларанте кто подает Т1 (БРОКЕР)
    xmlmodel.NamNFO101 = y.get("NamNFO101")  # Название
    xmlmodel.StrNumNFO103 = y.get("StrNumNFO103")  # Адрес (улица и номер)
    xmlmodel.PosCodNFO105 = y.get("PosCodNFO105")  # Почтовый индекс
    xmlmodel.CitNFO104 = y.get("CitNFO104")  # Город
    xmlmodel.CounNFO102 = y.get("CounNFO102")  # Код страны
    xmlmodel.NADLNGNFO = y.get("NADLNGNFO")  # Язык
    xmlmodel.TinNFO100 = y.get("TinNFO100")  # Налоговый идентификационный номер плательщика

    try:
        xmlmodel.save()  # Сохранение основной записи в таблице t1_xml
    except Exception as e:
        messages.append(f'Ошибка при сохранении данных в t1_xml: {e}')
        return {
            'id': 0,
            'messages': messages,
            'warnings': warnings,
        }

    # Создание записей для связанных моделей Product, Document, Pre_Document, Routes
    for product_data in y.get("products", []):
        product = Product(
            t1_xml=xmlmodel,
            IteNumGDS7=product_data.get("IteNumGDS7"),
            ComCodTarCodGDS10=product_data.get("ComCodTarCodGDS10"),
            GooDesGDS23=product_data.get("GooDesGDS23"),
            GroMasGDS46=product_data.get("GroMasGDS46"),
            MarNumOfPacGS21=product_data.get("MarNumOfPacGS21"),
            MarNumOfPacGS21LNG=product_data.get("MarNumOfPacGS21LNG"),
            KinOfPacGS23=product_data.get("KinOfPacGS23"),
            NumOfPacGS24=product_data.get("NumOfPacGS24"),
        )

        try:
            product.save()
        except Exception as e:
            warnings.append(f'Ошибка при сохранении данных в Product: {e}')
            continue

        # Создание связанных записей Document для каждого товара
        for document_data in product_data.get("documents", []):
            document = Document(
                Product=product,
                DocTypDC21=document_data.get("DocTypDC21"),
                DocRefDC23=document_data.get("DocRefDC23"),
                DocRefDCLNG=document_data.get("DocRefDCLNG"),
                ComOfInfDC25=document_data.get("ComOfInfDC25"),
                ComOfInfDC25LNG=document_data.get("ComOfInfDC25LNG"),
            )

            try:
                document.save()
            except Exception as e:
                warnings.append(f'Ошибка при сохранении данных в Document: {e}')
                continue

        # Создание связанных записей Pre_Document для каждого товара
        for pre_document_data in product_data.get("pre_documents", []):
            pre_document = Pre_Document(
                Product=product,
                PreDocTypAR21=pre_document_data.get("PreDocTypAR21"),
                PreDocRefAR26=pre_document_data.get("PreDocRefAR26"),
                PreDocRefLNG=pre_document_data.get("PreDocRefLNG"),
                # ComOfInfDC25=pre_document_data.get("ComOfInfDC25"),
                # ComOfInfDC25LNG=pre_document_data.get("ComOfInfDC25LNG"),
            )

            try:
                pre_document.save()
            except Exception as e:
                warnings.append(f'Ошибка при сохранении данных в Pre_Document: {e}')
                continue

    # Создание записей для маршрутов (Routes)
    for route_data in y.get("routes", []):
        route = Routes(
            t1_xml=xmlmodel,
            CouOfRouCodITI1=route_data.get("CouOfRouCodITI1"),
        )

        try:
            route.save()
        except Exception as e:
            warnings.append(f'Ошибка при сохранении данных в Routes: {e}')
            continue

    # Возвращаем результат выполнения функции
    messages.append('Данные успешно сохранены.')
    return {
        'id': xmlmodel.id,
        'messages': messages,
        'warnings': warnings,
    }


def update_t1_xml_load(s, user_l, xml_id):
    """
    Создаем новую запись и сохраняем туда данные из json.
    Если создание прошло успешно, удаляем xml со старым id.
    @param s: json с данными
    @param user_l: пользователь
    @param xml_id: id xml файла на замену
    @return: id созданного xml и сообщения, собранные при записи в БД
    """

    m = new_xml_load(s, user_l)

    if m['id']:
        t1_xml.objects.filter(pk=xml_id).delete()
        return m
    else:
        m['messages'].append('НЕ УДАЛОСЬ ОБНОВИТЬ XML!')
        return {
            'id': None,
            'messages': m['messages'],
            'warnings': m['warnings'],
        }