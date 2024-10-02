from .models import *
from datetime import datetime
import json

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
    xmlmodel = XMLModel()
    xmlmodel.user = user_l  # пользователь, который загрузил данные
    try:
        user_org = UserOrg.objects.get(user=user_l)
    except Exception as e:
        messages.append('Пользователь не привязан к организации. Сообщите администратору. Ошибка: ' + str(e))
        return {
            'id': 0,
            'messages': messages,
            'warnings': warnings,
        }


    y = json.loads(s)
    xmlmodel.XmlType = y["radioType"]   # тип PIAT или TD
    if xmlmodel.XmlType == 'PIAT':
        xmlmodel.EDocCode = 'R.042'
    if xmlmodel.XmlType == 'TD':
        xmlmodel.EDocCode = 'R.036'

    xmlmodel.EDocId = prepare_guid(y["EDocId"])             # GUID
    xmlmodel.EDocDateTime = datetime.strptime(y["EDocDateTime"], '%d.%m.%Y %H:%M')   # дата и время составления
    xmlmodel.EDocIndicatorCode = y["EDocIndicatorCode"]     # индикатор документа
    xmlmodel.ECP_CustomsOfficeCode = y["ECP_CustomsOfficeCode"]         # код поста отправления
    xmlmodel.ECP_BorderCheckpointName = y["ECP_BorderCheckpointName"].upper()   # наименование поста отправления

    # таможенный представитель
    # пока оставляю данные АЛЕСТА-ТРАНЗИТ
    # в дальнейшем хранить данные в отдельной таблице
    xmlmodel.PIDeclarant_SubjectBriefName = user_org.org.SubjectBriefName
    xmlmodel.PIDeclarant_TaxpayerId = user_org.org.TaxpayerId
    xmlmodel.PIDeclarant_UnifiedCountryCode = user_org.org.UnifiedCountryCode
    xmlmodel.PIDeclarant_RegionName = user_org.org.RegionName
    xmlmodel.PIDeclarant_CityName = user_org.org.CityName
    xmlmodel.PIDeclarant_StreetName = user_org.org.StreetName
    xmlmodel.PIDeclarant_BuildingNumberId = user_org.org.BuildingNumberId
    xmlmodel.PIDeclarant_RoomNumberId = user_org.org.RoomNumberId
    xmlmodel.PIDeclarant_RegistrationNumberId = user_org.org.RegistrationNumberId

    xmlmodel.UnifiedTransportModeCode = y["UnifiedTransportModeCode"]   # код транпорта
    xmlmodel.ContainerIndicator = y["ContainerIndicator"]               # индикатор контейнера
    xmlmodel.TransportMeansQuantity = len(y["Transport"])
    xmlmodel.Transport_EqualIndicator = '1'

    if y.get("TIRSeriesId", ''):
        xmlmodel.TIRCarnetIndicator = y["TIRCarnetIndicator"]
    else:
        xmlmodel.TIRCarnetIndicator = '0'
    if y.get("TIRSeriesId", ''):    # жду добавления
        xmlmodel.TIRSeriesId = y["TIRSeriesId"].upper()
    if y.get("TIRId", ''):
        xmlmodel.TIRId = y["TIRId"]
    if y.get("TIRPageOrdinal", ''):
        xmlmodel.TIRPageOrdinal = int(y["TIRPageOrdinal"])
    if y.get("TIRHolderId", ''):
        xmlmodel.TIRHolderId = y["TIRHolderId"].upper()

    xmlmodel.DeclarationKindCode = y["DeclarationKindCode"].upper()
    xmlmodel.TransitProcedureCode = y["TransitProcedureCode"].upper()
    xmlmodel.TransitFeatureCode = y["TransitFeatureCode"].upper()

    if y.get("warrantySpecification", ''):
        xmlmodel.LoadingListsQuantity = int(y["warrantySpecification"])
    if y.get("warrantySpecification2", ''):
        xmlmodel.LoadingListsPageQuantity = int(y["warrantySpecification2"])
    xmlmodel.GoodsQuantity = len(y["Goods"])
    if y.get("CargoQuantity", ''):
        xmlmodel.CargoQuantity = int(y["CargoQuantity"])
    else:
        warnings.append(f'Не найдено общее количество мест.')
    if y.get("SealQuantity", ''):
        xmlmodel.SealQuantity = int(y["SealQuantity"])
    xmlmodel.SealId = y["SealId"].upper()

    xmlmodel.TT_CustomsOfficeCode = y["TT_CustomsOfficeCode"]
    xmlmodel.TT_CustomsOfficeName = y["TT_CustomsOfficeName"].upper()
    xmlmodel.TT_CustomsControlZoneId = y["TT_CustomsControlZoneId"].upper()   # жду добавления
    try:
        ucc = Pto.objects.get(CODE=xmlmodel.TT_CustomsOfficeCode)
        if ucc is not None:
            xmlmodel.TT_UnifiedCountryCode = ucc.COUNTRYCODELIT
    except Exception as e:
        warnings.append(f'Для поста {xmlmodel.TT_CustomsOfficeCode} не найдена страна в справочнике.')
    if y.get("TD_DocKindCode", ''):
        xmlmodel.TD_DocKindCode = y["TD_DocKindCode"]  # жду добавления
    if y.get("TD_DocId", ''):
        xmlmodel.TD_DocId = y["TD_DocId"].upper()   # жду добавления
    if y.get("TD_DocCreationDate", ''):
        xmlmodel.TD_DocCreationDate = datetime.strptime(y["TD_DocCreationDate"], '%d.%m.%Y').date()  # жду добавления

    xmlmodel.DepartureCountry_CACountryCode = y["DepartureCountry_CACountryCode"]            # код страны отправления
    xmlmodel.DepartureCountry_ShortCountryName = y["DepartureCountry_ShortCountryName"].upper()      # страна отправления

    xmlmodel.DestinationCountry_CACountryCode = y["DestinationCountry_CACountryCode"]        # код страны назначения
    xmlmodel.DestinationCountry_ShortCountryName = y["DestinationCountry_ShortCountryName"].upper()  # страна назначения

    if y.get("CAInvoiceValueAmount", ''):
        xmlmodel.CAInvoiceValueAmount = float(y["CAInvoiceValueAmount"])
    else:
        warnings.append(f'Не найдена общая стоимость товаров.')
    xmlmodel.IVA_currencyCode = y["IVA_currencyCode"].upper()

    # отправитель
    xmlmodel.Consignor_SubjectBriefName = y["Consignor_SubjectBriefName"].upper()
    xmlmodel.Consignor_TaxpayerId = y["Consignor_TaxpayerId"]
    xmlmodel.Consignor_UnifiedCountryCode = y["Consignor_UnifiedCountryCode"].upper()
    xmlmodel.Consignor_RegionName = y["Consignor_RegionName"].upper()
    xmlmodel.Consignor_CityName = y["Consignor_CityName"].upper()
    xmlmodel.Consignor_StreetName = y["Consignor_StreetName"].upper()
    xmlmodel.Consignor_BuildingNumberId = y["Consignor_BuildingNumberId"].upper()
    xmlmodel.Consignor_RoomNumberId = y["Consignor_RoomNumberId"].upper()

    # получатель
    xmlmodel.Consignee_SubjectBriefName = y["Consignee_SubjectBriefName"].upper()
    xmlmodel.Consignee_TaxpayerId = y["Consignee_TaxpayerId"]
    xmlmodel.Consignee_UnifiedCountryCode = y["Consignee_UnifiedCountryCode"].upper()
    xmlmodel.Consignee_RegionName = y["Consignee_RegionName"].upper()
    xmlmodel.Consignee_CityName = y["Consignee_CityName"].upper()
    xmlmodel.Consignee_StreetName = y["Consignee_StreetName"].upper()
    xmlmodel.Consignee_BuildingNumberId = y["Consignee_BuildingNumberId"].upper()
    xmlmodel.Consignee_RoomNumberId = y["Consignee_RoomNumberId"].upper()

    # декларант
    xmlmodel.TransitDeclarant_EqualIndicator = '0'
    xmlmodel.TransitDeclarant_SubjectBriefName = y["TransitDeclarant_SubjectBriefName"].upper()
    xmlmodel.TransitDeclarant_TaxpayerId = y["TransitDeclarant_TaxpayerId"]
    xmlmodel.TransitDeclarant_UnifiedCountryCode = y["TransitDeclarant_UnifiedCountryCode"].upper()
    xmlmodel.TransitDeclarant_RegionName = y["TransitDeclarant_RegionName"].upper()
    xmlmodel.TransitDeclarant_CityName = y["TransitDeclarant_CityName"].upper()
    xmlmodel.TransitDeclarant_StreetName = y["TransitDeclarant_StreetName"].upper()
    xmlmodel.TransitDeclarant_BuildingNumberId = y["TransitDeclarant_BuildingNumberId"].upper()
    xmlmodel.TransitDeclarant_RoomNumberId = y["TransitDeclarant_RoomNumberId"].upper()

    # перевозчик (заполняем данными с декларанта)
    xmlmodel.Carrier_SubjectBriefName = y["TransitDeclarant_SubjectBriefName"].upper()
    xmlmodel.Carrier_TaxpayerId = y["TransitDeclarant_TaxpayerId"]
    xmlmodel.Carrier_UnifiedCountryCode = y["TransitDeclarant_UnifiedCountryCode"].upper()
    xmlmodel.Carrier_RegionName = y["TransitDeclarant_RegionName"].upper()
    xmlmodel.Carrier_CityName = y["TransitDeclarant_CityName"].upper()
    xmlmodel.Carrier_StreetName = y["TransitDeclarant_StreetName"].upper()
    xmlmodel.Carrier_BuildingNumberId = y["TransitDeclarant_BuildingNumberId"].upper()
    xmlmodel.Carrier_RoomNumberId = y["TransitDeclarant_RoomNumberId"].upper()

    # ПЕРЕВОЗЧИК ПО ТТ ЕАЭС
    if y["Carrier_SubjectBriefName"]:
        xmlmodel.UnionCarrier_SubjectBriefName = y["Carrier_SubjectBriefName"].upper()
        xmlmodel.UnionCarrier_TaxpayerId = y["Carrier_TaxpayerId"]
        xmlmodel.UnionCarrier_UnifiedCountryCode = y["Carrier_UnifiedCountryCode"].upper()
        xmlmodel.UnionCarrier_RegionName = y["Carrier_RegionName"].upper()
        xmlmodel.UnionCarrier_CityName = y["Carrier_CityName"].upper()
        xmlmodel.UnionCarrier_StreetName = y["Carrier_StreetName"].upper()
        xmlmodel.UnionCarrier_BuildingNumberId = y["Carrier_BuildingNumberId"].upper()
        xmlmodel.UnionCarrier_RoomNumberId = y["Carrier_RoomNumberId"].upper()
    else:
        xmlmodel.UnionCarrier_SubjectBriefName = y["TransitDeclarant_SubjectBriefName"].upper()
        xmlmodel.UnionCarrier_TaxpayerId = y["TransitDeclarant_TaxpayerId"]
        xmlmodel.UnionCarrier_UnifiedCountryCode = y["TransitDeclarant_UnifiedCountryCode"].upper()
        xmlmodel.UnionCarrier_RegionName = y["TransitDeclarant_RegionName"].upper()
        xmlmodel.UnionCarrier_CityName = y["TransitDeclarant_CityName"].upper()
        xmlmodel.UnionCarrier_StreetName = y["TransitDeclarant_StreetName"].upper()
        xmlmodel.UnionCarrier_BuildingNumberId = y["TransitDeclarant_BuildingNumberId"].upper()
        xmlmodel.UnionCarrier_RoomNumberId = y["TransitDeclarant_RoomNumberId"].upper()


    # водитель
    xmlmodel.CarrierRepresentative_FirstName = y["CarrierRepresentative_FirstName"].upper()
    xmlmodel.CarrierRepresentative_MiddleName = y["CarrierRepresentative_MiddleName"].upper()
    xmlmodel.CarrierRepresentative_LastName = y["CarrierRepresentative_LastName"].upper()
    xmlmodel.CarrierRepresentative_PositionName = y["CarrierRepresentative_PositionName"].upper()
    xmlmodel.CarrierRepresentative_UnifiedCountryCode = y["CarrierRepresentative_UnifiedCountryCode"].upper()
    xmlmodel.CarrierRepresentative_IdentityDocKindCode = y["CarrierRepresentative_IdentityDocKindCode"].upper()
    xmlmodel.CarrierRepresentative_DocId = y["CarrierRepresentative_DocId"].upper()
    if y.get("CarrierRepresentative_DocCreationDate", ''):
        xmlmodel.CarrierRepresentative_DocCreationDate = datetime.strptime(y["CarrierRepresentative_DocCreationDate"], '%d.%m.%Y')
    if y.get("CarrierRepresentative_DocValidityDate", ''):
        xmlmodel.CarrierRepresentative_DocValidityDate = datetime.strptime(y["CarrierRepresentative_DocValidityDate"], '%d.%m.%Y')
    xmlmodel.CarrierRepresentative_RoleCode = '1'

    if y.get("TD_ExchangeRate", ''):
        xmlmodel.TD_ExchangeRate = float(y["TD_ExchangeRate"])
    xmlmodel.TD_ER_currencyCode = y["IVA_currencyCode"]
    xmlmodel.TD_ER_scaleNumber = y["TD_ER_scaleNumber"]
    if y["TD_CustomsValueAmount"]:
        xmlmodel.TD_CustomsValueAmount = float(y["TD_CustomsValueAmount"])
    else:
        if xmlmodel.XmlType == 'TD':
            warnings.append(f'Не найдена общая таможенная стоимость товаров для ТД.')

    xmlmodel.TD_CV_currencyCode = 'BYN'

    # жду добавления веса брутто всех товаров
    if y.get("UnifiedGrossMassMeasure", ''):
        xmlmodel.UnifiedGrossMassMeasure = float(y["UnifiedGrossMassMeasure"])
        xmlmodel.measurementUnitCode = '166'

    # принципал (физ. лицо), доверенность, аттестат, контакт
    if xmlmodel.SP_DocId:   # если указан номер паспорта, то загружаем из соотв. полей
        xmlmodel.SP_LastName = y["SP_LastName"].upper()
        xmlmodel.SP_FirstName = y["SP_FirstName"].upper()
        xmlmodel.SP_MiddleName = y["SP_MiddleName"].upper()
        xmlmodel.SP_PositionName = y["SP_PositionName"].upper()
        xmlmodel.SP_UnifiedCountryCode = y["SP_UnifiedCountryCode"].upper()
        xmlmodel.SP_IdentityDocKindCode = y["SP_IdentityDocKindCode"].upper()
        xmlmodel.SP_DocId = y["SP_DocId"].upper()
        if y.get("SP_DocCreationDate", ''):
            xmlmodel.SP_DocCreationDate = datetime.strptime(y["SP_DocCreationDate"], '%d.%m.%Y')
        if y.get("SP_DocValidityDate", ''):
            xmlmodel.SP_DocValidityDate = datetime.strptime(y["SP_DocValidityDate"], '%d.%m.%Y')
    else:      # если номер паспорта не указан, загружаем информацию из водителя
        xmlmodel.SP_FirstName = y["CarrierRepresentative_FirstName"].upper()
        xmlmodel.SP_MiddleName = y["CarrierRepresentative_MiddleName"].upper()
        xmlmodel.SP_LastName = y["CarrierRepresentative_LastName"].upper()
        xmlmodel.SP_PositionName = y["CarrierRepresentative_PositionName"].upper()
        xmlmodel.SP_UnifiedCountryCode = y["CarrierRepresentative_UnifiedCountryCode"].upper()
        xmlmodel.SP_IdentityDocKindCode = y["CarrierRepresentative_IdentityDocKindCode"].upper()
        xmlmodel.SP_DocId = y["CarrierRepresentative_DocId"].upper()
        if y.get("CarrierRepresentative_DocCreationDate", ''):
            xmlmodel.SP_DocCreationDate = datetime.strptime(
                y["CarrierRepresentative_DocCreationDate"], '%d.%m.%Y')
        if y.get("CarrierRepresentative_DocValidityDate", ''):
            xmlmodel.SP_DocValidityDate = datetime.strptime(
                y["CarrierRepresentative_DocValidityDate"], '%d.%m.%Y')

    xmlmodel.SP_QualificationCertificateId = y["SP_QualificationCertificateId"].upper()
    xmlmodel.SP_POA_DocKindCode = '11004'
    xmlmodel.SP_POA_DocId = y["SP_POA_DocId"].upper()
    if y.get("SP_POA_DocCreationDate", ''):
        xmlmodel.SP_POA_DocCreationDate = datetime.strptime(y["SP_POA_DocCreationDate"], '%d.%m.%Y')
        if xmlmodel.SP_POA_DocCreationDate > datetime.now():
            messages.append('Дата начала действия доверенности больше чем сегодня!')
    if y.get("SP_POA_DocValidityDate", ''):
        xmlmodel.SP_POA_DocValidityDate = datetime.strptime(y["SP_POA_DocValidityDate"], '%d.%m.%Y')
        if xmlmodel.SP_POA_DocValidityDate < datetime.now():
            messages.append('Доверенность уже не действует!')

    xmlmodel.CD_CommunicationChannelCode = 'TE'
    xmlmodel.CD_CommunicationChannelName = 'ТЕЛЕФОН'
    xmlmodel.CD_CommunicationChannelId = user_org.org.Phone

    try:
        xmlmodel.save()
    except Exception as e:
        messages.append('Не удалось сохранить основную информацию по XML. Ошибка: ' + str(e))
        return {
            'id': 0,
            'messages': messages,
            'warnings': warnings,
        }

    doc_flag = False
    tmp_doc_id = ''
    tmp_doc_kindcode = ''
    tmp_doc_date = ''


    # товары в xml
    items_list = y["Goods"]
    items_list_keys = sorted(list(items_list.keys()))
    count = 0
    for _i in items_list_keys:
        i = items_list[_i]
        item = ConsignmentItem()
        count += 1
        item.ConsignmentItemOrdinal = count
        item.CommodityCode = i["CommodityCode"]
        s = i["GoodsDescriptionText"].upper()
        if len(s) > 250:
            t = s[0:250]
            s = s[250:]
        else:
            t = s
            s = ''
        item.GoodsDescriptionText = t
        if len(s) > 250:
            t = s[0:250]
            s = s[250:]
        else:
            t = s
            s = ''
        item.GoodsDescriptionText1 = t
        if len(s) > 250:
            t = s[0:250]
            s = s[250:]
        else:
            t = s
            s = ''
        item.GoodsDescriptionText2 = t
        if len(s) > 250:
            t = s[0:250]
            s = s[250:]
        else:
            t = s
            s = ''
        item.GoodsDescriptionText3 = t

        if i["UnifiedGrossMassMeasure"]:
            item.UnifiedGrossMassMeasure = float(i["UnifiedGrossMassMeasure"])
        else:
            messages.append(f'Не найден вес товара под номером {count}.')
        item.measurementUnitCode = '166'    # вес всегда в кг приходит
        # GoodsMeasureDetails
        item.GM_measurementUnitCode = i["GM_measurementUnitCode"]
        item.GM_MeasureUnitAbbreviationCode = i["GM_MeasureUnitAbbreviationCode"]
        if i["GM_GoodsMeasure"]:
            item.GM_GoodsMeasure = float(i["GM_GoodsMeasure"])
        else:
            if item.GM_measurementUnitCode:
                messages.append(f'Для товара №{count} не указано количество в доп. единицах, хотя код доп.единиц указан.')
        # AddGoodsMeasureDetails
        item.AGM_measurementUnitCode = i["AGM_measurementUnitCode"]
        item.AGM_MeasureUnitAbbreviationCode = i["AGM_MeasureUnitAbbreviationCode"]
        if i["AGM_GoodsMeasure"]:
            item.AGM_GoodsMeasure = float(i["AGM_GoodsMeasure"])
        else:
            if item.AGM_measurementUnitCode:
                messages.append(f'Для товара №{count} не указано количество в доп. единицах, хотя код доп.единиц указан.')
        # CargoPackagePalletDetails
        item.PackageAvailabilityCode = i["PackageAvailabilityCode"]
        if i["CargoQuantity"]:
            item.CargoQuantity = int(i["CargoQuantity"])
        else:
            messages.append(f'Для товара №{count} не указано количество грузовых мест.')
        item.CargoPackageInfoKindCode = i["CargoPackageInfoKindCode"]
        item.PackageKindCode = i["PackageKindCode"]
        if i["PackageQuantity"]:
            item.PackageQuantity = int(i["PackageQuantity"])
        else:
            if xmlmodel.XmlType == 'PIAT':
                messages.append(f'Для товара №{count} не указано количество упаковок.')
        # стоимость
        if i["CAValueAmount"]:
            item.CAValueAmount = float(i["CAValueAmount"])
        else:
            messages.append(f'Для товара №{count} не указана стоимость.')
        item.currencyCode = i["currencyCode"]

        # поля только в ТД
        item.GoodsTraceabilityCode = i["GoodsTraceabilityCode"]
        item.LicenseGoodsKindCode = i["LicenseGoodsKindCode"]
        # кол-во отслеживаемого товара
        item.TM_measurementUnitCode = i["TM_measurementUnitCode"]
        item.TM_MeasureUnitAbbreviationCode = i["TM_MeasureUnitAbbreviationCode"]
        if i["TM_GoodsMeasure"]:
            item.TM_GoodsMeasure = float(i["TM_GoodsMeasure"])
        else:
            if xmlmodel.XmlType == 'TD':
                if i["TM_measurementUnitCode"]:
                    messages.append(f'Для товара №{count} не указано количество в доп. единицах (отслеж. товар), хотя код доп.единиц указан.')
        # таможенная стоимость
        if i["CustomsValueAmount"]:
            item.CustomsValueAmount = float(i["CustomsValueAmount"])
        else:
            if xmlmodel.XmlType == 'TD':
                messages.append(f'Для товара №{count} не указана таможенная стоимость.')
        item.CV_currencyCode = 'BYN'   # таможенная стоимость в BYN всегда

        item.xml = xmlmodel
        try:
            item.save()
        except Exception as e:
            messages.append('Не удалось сохранить товар в XML. Ошибка: ' + str(e))
            continue

        tmp = i["AddInfo"]

        # документы в товаре
        item_doc_dict = tmp["Doc"]
        #item_doc_keys = sorted(list(item_doc_dict.keys()))
        item_doc_keys = item_doc_dict["PIGoodsDocDetails"]
        for idoc in item_doc_keys:
            #idoc = item_doc_dict[_idoc]
            item_doc = PIGoodsDocDetails()
            item_doc.DocKindCode = idoc["DocKindCode"]
            item_doc.DocId = idoc["DocId"].upper()
            item_doc.DocCreationDate = datetime.strptime(idoc["DocCreationDate"], '%d.%m.%Y').date()
            item_doc.ci = item
            try:
                item_doc.save()
                if tmp_doc_kindcode != '02015':
                    if not doc_flag:
                        tmp_doc_kindcode = item_doc.DocKindCode
                        tmp_doc_id = item_doc.DocId
                        tmp_doc_date = item_doc.DocCreationDate
                        doc_flag = True
                    else:
                        if item_doc.DocKindCode == '02015':
                            tmp_doc_kindcode = item_doc.DocKindCode
                            tmp_doc_id = item_doc.DocId
                            tmp_doc_date = item_doc.DocCreationDate
                # заполнение и сохранение транспортного документа
            except Exception as e:
                messages.append('Не удалось сохранить документ в товаре. Ошибка: ' + str(e))
                continue

        # предшедствующие документы в товаре
        item_pdoc_dict = tmp["Previous"]
        #item_pdoc_keys = sorted(list(item_pdoc_dict.keys()))
        item_pdoc_keys = item_pdoc_dict["PIPrecedingDocDetails"]
        for ipdoc in item_pdoc_keys:
            #ipdoc = item_pdoc_dict[_ipdoc]
            item_pdoc = PIPrecedingDocDetails()
            item_pdoc.DocKindCode = ipdoc["DocKindCode"]
            item_pdoc.DocId = ipdoc["DocId"].upper()
            item_pdoc.DocCreationDate = datetime.strptime(ipdoc["DocCreationDate"], '%d.%m.%Y').date()
            if ipdoc["ConsignmentItemOrdinal"]:
                item_pdoc.ConsignmentItemOrdinal = ipdoc["ConsignmentItemOrdinal"]
            else:
                if xmlmodel.XmlType == 'TD':
                    messages.append(f'Для товара №{count} не указан номер товара в предшедствующем документе.')

            item_pdoc.ci = item
            try:
                item_pdoc.save()
            except Exception as e:
                messages.append('Не удалось сохранить предшедствующий документ в товаре. Ошибка: ' + str(e))
                continue

        # контейнеры в товаре
        item_cont_dict = tmp["Cont"]
        #item_cont_keys = sorted(list(item_cont_dict.keys()))
        item_cont_keys = item_cont_dict["ContainerCI"]
        for ic in item_cont_keys:
            #ic = item_cont_dict[_ic]
            item_cont = ContainerCI()
            item_cont.ContainerId = ic["ContainerId"]
            item_cont.ci = item
            try:
                item_cont.save()
            except Exception as e:
                messages.append('Не удалось сохранить контейнер в товаре. Ошибка: ' + str(e))
                continue

    # перецепки в xml
    reload_list = y["Reload"]
    reload_list_keys = sorted(list(reload_list.keys()))
    for _r in reload_list_keys:
        r = reload_list[_r]
        reload = Transhipment()
        if r.get("CargoOperationKindCode", ''):
            reload.CargoOperationKindCode = r["CargoOperationKindCode"]
        if r.get("ContainerIndicator", ''):
            reload.ContainerIndicator = r["ContainerIndicator"]
        reload.CACountryCode = r["CACountryCode"].upper()
        reload.ShortCountryName = r["ShortCountryName"].upper()
        if r.get("PlaceName", ''):
            reload.PlaceName = r["PlaceName"].upper()
        if r.get("CustomsOfficeCode", ''):
            reload.CustomsOfficeCode = r["CustomsOfficeCode"]
        if r.get("CustomsOfficeName", ''):
            reload.CustomsOfficeName = r["CustomsOfficeName"].upper()
        if r.get("UnifiedTransportModeCode", ''):
            reload.UnifiedTransportModeCode = r["UnifiedTransportModeCode"]
        tmp = r["AddInfo"]
        temp_dict = tmp["Trans"]
        #temp_dict_keys = sorted(list(temp_dict.keys()))
        temp_dict_keys = temp_dict["TransportTranshipment"]
        reload.TransportMeansQuantity = int(len(temp_dict_keys))
        _t = temp_dict_keys[0]
        reload.RegistrationNationalityCode = _t["CountryCode"]
        reload.xml = xmlmodel

        try:
            reload.save()
        except Exception as e:
            messages.append('Не удалось сохранить перецепку в XML. Ошибка: ' + str(e))
            continue

        # транспорт в перецепке
        tmp = r["AddInfo"]
        reload_ts_dict = tmp["Trans"]
        #reload_ts_keys = sorted(list(reload_ts_dict.keys()))
        reload_ts_keys = reload_ts_dict["TransportTranshipment"]
        for rts in reload_ts_keys:
            #rts = reload_ts_dict[_rts]
            reload_ts = TransportTranshipment()
            reload_ts.TransportMeansRegId = rts["TransportMeansRegId"]
            reload_ts.countryCode = rts["CountryCode"]
            reload_ts.TransportTypeCode = rts["TransportTypeCode"]
            reload_ts.transhipment_xml = reload
            try:
                reload_ts.save()
            except Exception as e:
                messages.append('Не удалось сохранить транспорт в перецепке в XML. Ошибка: ' + str(e))
                continue

        # контейнеры в перецепке
        tmp = r["AddInfo"]
        reload_cont_dict = tmp["Cont"]
        #reload_cont_keys = sorted(list(reload_cont_dict.keys()))
        reload_cont_keys = reload_cont_dict["ContainerTranshipment"]
        for rc in reload_cont_keys:
            #rc = reload_cont_dict[_rc]
            reload_cont = ContainerTranshipment()
            reload_cont.ContainerId = rc["ContainerId"]
            reload_cont.transhipment_xml = reload
            try:
                reload_cont.save()
            except Exception as e:
                messages.append('Не удалось сохранить контейнер в перецепке в XML. Ошибка: ' + str(e))
                continue

    # транспорт в xml
    ts_list_tmp = []
    ts_list = y["Transport"]
    ts_list_keys = sorted(list(ts_list.keys()))
    for _ts in ts_list_keys:
        ts = ts_list[_ts]
        ts_xml = TransportXML()
        ts_xml.TransportMeansRegId = ts.get("TransportMeansRegId", "").upper()
        if not ts_xml.TransportMeansRegId:
            messages.append('Не найден номер транспортного средства.')
        ts_xml.countryCode = ts.get("countryCode", "").upper()
        if not ts_xml.countryCode:
            messages.append('Не найдена страна регистрации транспортного средства.')
        ts_xml.VehicleId = ts.get("VehicleId", "").upper()
        if not ts_xml.VehicleId:
            messages.append('Не найден VIN транспортного средства.')
        ts_xml.TransportTypeCode = ts.get("TransportTypeCode", "")
        if not ts_xml.TransportTypeCode:
            messages.append('Не найден код типа транспортного средства.')
        ts_xml.VehicleMakeCode = ts.get("VehicleMakeCode", "")
        if not ts_xml.VehicleMakeCode:
            messages.append('Не найден код марки транспортного средства.')
        ts_xml.VehicleMakeName = ts.get("VehicleMakeName", "")
        ts_xml.VehicleModelName = ts.get("VehicleModelName", "")
        ts_xml.DocId = ts.get("DocId", "").upper()
        if not ts_xml.DocId:
            warnings.append('Не найден номер техпаспорта .')
        ts_xml.xml = xmlmodel
        try:
            ts_xml.save()
            ts_list_tmp.append(ts_xml.TransportMeansRegId)
        except Exception as e:
            messages.append('Не удалось сохранить транспортное средство в XML. Ошибка: ' + str(e))
            continue

    # сохраняем список транспортных средств в поле transport_list
    xmlmodel.transport_list = ' / '.join(ts_list_tmp)
    try:
        xmlmodel.save()
    except Exception as e:
        messages.append('Не удалось сохранить список транспортных средств в основной информации по XML. Ошибка: ' + str(e))
    # end сохраняем список транспортных средств в поле transport_list

    # сохраняем транспортный документ (CMR или первый в списке документов в 1м товаре)
    xmlmodel.TD_DocKindCode = tmp_doc_kindcode
    xmlmodel.TD_DocId = tmp_doc_id
    xmlmodel.TD_DocCreationDate = tmp_doc_date
    try:
        xmlmodel.save()
    except Exception as e:
        messages.append('Не удалось сохранить транспортный документ по XML. Ошибка: ' + str(e))
    # end сохраняем транспортный документ (CMR или первый в списке документов в 1м товаре)

    # гарантии в xml
    garant = y["Warranty"]
    garant_keys = sorted(list(garant.keys()))
    for _g in garant_keys:
        g = garant[_g]
        guarantee = TransitGuarantee()
        guarantee.TransitGuaranteeMeasureCode = g["TransitGuaranteeMeasureCode"]
        if g.get("GuaranteeAmount", ''):
            guarantee.GuaranteeAmount = float(g["GuaranteeAmount"])
        else:
            warnings.append(f'Не указана сумма гарантии.')
        # guarantee.currencyCode =
        # секция для номера сертификата
        if g.get("GC_CUstomsDocumentId", ''):
            t = g["GC_CUstomsDocumentId"].split('/')
            if len(t) == 3:
                guarantee.GC_CustomsOfficeCode = t[0]
                date_format = '%d%m%y'
                guarantee.GC_DocCreationDate = datetime.strptime(t[1], date_format)
                guarantee.GC_CustomsDocumentId = t[2]
            else:
                messages.append(f'Не верный формат номера сертификата: {g["GC_CUstomsDocumentId"]}.')
        # секция для подтверждающего документа
        if g.get("RD_UnifiedCountryCode", ''):
            guarantee.RD_UnifiedCountryCode = g["RD_UnifiedCountryCode"].upper()
        if g.get("RD_RegistrationNumberId", ''):
            guarantee.RD_RegistrationNumberId = g["RD_RegistrationNumberId"].upper()
        # секция для таможенного сопровождения
        if g.get("ES_SubjectBriefName", ''):
            guarantee.ES_SubjectBriefName = g["ES_SubjectBriefName"].upper()
        if g.get("ES_TaxpayerId", ''):
            guarantee.ES_TaxpayerId = g["ES_TaxpayerId"].upper()
        if g.get("ES_BankId", ''):
            guarantee.ES_BankId = g["ES_BankId"].upper()
        guarantee.xml = xmlmodel
        try:
            guarantee.save()
        except Exception as e:
            messages.append('Не удалось сохранить гарантию в XML. Ошибка: ' + str(e))
            continue

    return {
        'id': xmlmodel.pk,
        'messages': messages,
        'warnings': warnings,
    }


def update_xml_load(s, user_l, xml_id):
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
        XMLModel.objects.filter(pk=xml_id).delete()
        return m
    else:
        m['messages'].append('НЕ УДАЛОСЬ ОБНОВИТЬ XML!')
        return {
            'id': None,
            'messages': m['messages'],
            'warnings': m['warnings'],
        }
