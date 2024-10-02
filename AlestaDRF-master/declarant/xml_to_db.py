from lxml import etree as et
from declarant.alesta_functions import type_from_xml_name, get_serifikat_date
from .models import *


def start_work_with_xml(fname, xmlfile, user_l):
    """ обработка xml-файлов
        возвращает объект с полем id загруженного файла
        если id==0, то должен быть список messages - с описанием ошибок при обработке xml
    """
    xml_type = type_from_xml_name(fname)
    if xml_type == 'PIAT':
        return piat_to_db(xmlfile, user_l)
    elif xml_type == 'TD':
        return td_to_db(xmlfile, user_l)
    else:
        return {'id': 0, 'messages': [
            'Невозможно обработать XML-файл. Доступны для загрузки только файлы ЭПИ (PIAT) и ТД (TD).']}


def piat_to_db(xmlfile, user_l):
    """
        Загрузка ЭПИ из xml-файла в базу данных
    """
    messages = []

    tree = et.parse(xmlfile)
    root = tree.getroot()
    ns = root.nsmap.copy()

    def only_tag(s):
        """ Убирает namespace из тэга xml-элемента
            на вход может поступать элемент дерева xml и строка тэга с namespace"""
        try:
            _s = s.tag.split('}')[1]  # если на входе объект
            return _s
        except:
            return s.split(':')[1]  # если на входе строка

    def get_node(et, tag, important=False):
        """ Возвращает элемент дерева xml с тэгом tag, у которого родитель et
            important - флаг, указывающий важное поле или же оно может отсутствовать
        """
        if et is not None:
            _ns, _tag = tag.split(':')
            _e = et.find(f'{{{ns[_ns]}}}{_tag}')
            if _e is None:
                if important:
                    messages.append(f'Важно! В XML не найдено поле {only_tag(et)} > {only_tag(tag)}!')
            return _e
        else:
            return None

    def get_nodes(et, tag, important=False):
        """ Возвращает список элементов дерева с тэгом tag, у которого родитель et
            important - флаг, указывающий важное поле или же оно может отсутствовать"""
        if et is not None:
            _ns, _tag = tag.split(':')
            _e = et.findall(f'{{{ns[_ns]}}}{_tag}')
            if _e:
                return _e
            else:
                if important:
                    messages.append(f'Важно! В XML не найдено поле (поля) {only_tag(et.tag)} > {only_tag(tag)}!')
                return []
        else:
            return []

    def get_text_node(node):
        """ Возвращает текст из xml-элемента """
        try:
            return node.text
        except:
            return None

    def get_attr_node(node, attr):
        """ Возвращает значение атрибута attr из xml-элемента """
        try:
            return node.attrib[attr]
        except:
            return None

    def get_text_from_child_node(et, tag, important=False):
        """ Возвращает текст элемент дерева xml с тэгом tag, у которого родитель et
            important - флаг, указывающий важное поле или же оно может отсутствовать
        """
        if et is not None:
            return get_text_node(get_node(et, tag, important=important))
        else:
            return None

    xmlmodel = XMLModel()
    xmlmodel.XmlType = 'PIAT'
    xmlmodel.user = user_l
    xmlmodel.EDocCode = get_text_from_child_node(root, 'csdo:EDocCode')
    xmlmodel.EDocId = get_text_from_child_node(root, 'csdo:EDocId', important=True)
    xmlmodel.EDocDateTime = get_text_from_child_node(root, 'csdo:EDocDateTime', important=True)
    xmlmodel.EDocIndicatorCode = get_text_from_child_node(root, 'casdo:EDocIndicatorCode', important=True)

    # считываем три параметра из xml с одинаковым тэгом
    i = 1
    for _e in get_nodes(root, 'casdo:PreliminaryInformationUsageCode', important=True):
        if i == 1:
            xmlmodel.PreliminaryInformationUsageCode1 = get_text_node(_e)
        elif i == 2:
            xmlmodel.PreliminaryInformationUsageCode2 = get_text_node(_e)
        else:
            xmlmodel.PreliminaryInformationUsageCode3 = get_text_node(_e)
        i += 1

    # пост отправления
    ecp = get_node(root, 'cacdo:PIATEntryCheckPointDetails', important=True)
    xmlmodel.ECP_CustomsOfficeCode = get_text_from_child_node(ecp, 'csdo:CustomsOfficeCode', important=True)
    xmlmodel.ECP_BorderCheckpointName = get_text_from_child_node(ecp, 'csdo:BorderCheckpointName', important=True)
    # end пост отправления

    # декларант ЭПИ
    pi_declarant = get_node(root, 'cacdo:PIDeclarantDetails', important=True)
    xmlmodel.PIDeclarant_SubjectBriefName = get_text_from_child_node(pi_declarant, 'csdo:SubjectBriefName', True)
    xmlmodel.PIDeclarant_TaxpayerId = get_text_from_child_node(pi_declarant, 'csdo:TaxpayerId')

    address = get_node(pi_declarant, 'ccdo:SubjectAddressDetails', important=True)
    xmlmodel.PIDeclarant_UnifiedCountryCode = get_text_from_child_node(address, 'csdo:UnifiedCountryCode', True)
    xmlmodel.PIDeclarant_RegionName = get_text_from_child_node(address, 'csdo:RegionName')
    xmlmodel.PIDeclarant_CityName = get_text_from_child_node(address, 'csdo:CityName', True)
    xmlmodel.PIDeclarant_StreetName = get_text_from_child_node(address, 'csdo:StreetName', True)
    xmlmodel.PIDeclarant_BuildingNumberId = get_text_from_child_node(address, 'csdo:BuildingNumberId')
    xmlmodel.PIDeclarant_RoomNumberId = get_text_from_child_node(address, 'csdo:RoomNumberId')

    xmlmodel.PIDeclarant_RegistrationNumberId = get_text_from_child_node(
        get_node(pi_declarant, 'cacdo:RegisterDocumentIdDetails', important=True),
        'casdo:RegistrationNumberId',
        important=True,
    )
    # end декларант ЭПИ

    main = get_node(root, 'cacdo:PIATMainConsignmentDetails', important=True)  # основная инфа

    # инфа о транспорте
    transport_details = get_node(root, 'cacdo:PIATBorderTransportDetails', important=True)
    xmlmodel.UnifiedTransportModeCode = get_text_from_child_node(transport_details, 'csdo:UnifiedTransportModeCode',
                                                                 True)
    xmlmodel.TransportMeansQuantity = get_text_from_child_node(transport_details, 'casdo:TransportMeansQuantity', True)
    xmlmodel.ContainerIndicator = get_text_from_child_node(transport_details, 'casdo:ContainerIndicator', True)
    xmlmodel.Transport_EqualIndicator = get_text_from_child_node(
        get_node(main, 'cacdo:PITransitTransportMeansDetails'),
        'casdo:EqualIndicator',
    )
    # end инфа о транспорте

    # TIR
    xmlmodel.TIRCarnetIndicator = get_text_from_child_node(main, 'casdo:TIRCarnetIndicator', True)
    tir = get_node(main, 'cacdo:TIRCarnetIdDetails')
    xmlmodel.TIRSeriesId = get_text_from_child_node(tir, 'casdo:TIRSeriesId')
    xmlmodel.TIRId = get_text_from_child_node(tir, 'casdo:TIRId')
    xmlmodel.TIRPageOrdinal = get_text_from_child_node(tir, 'casdo:TIRPageOrdinal')
    xmlmodel.TIRHolderId = get_text_from_child_node(tir, 'casdo:TIRHolderId')
    # end TIR

    xmlmodel.DeclarationKindCode = get_text_from_child_node(main, 'casdo:DeclarationKindCode', True)
    xmlmodel.TransitProcedureCode = get_text_from_child_node(main, 'casdo:TransitProcedureCode', True)
    xmlmodel.TransitFeatureCode = get_text_from_child_node(main, 'casdo:TransitFeatureCode')
    xmlmodel.LoadingListsQuantity = get_text_from_child_node(main, 'casdo:LoadingListsQuantity')
    xmlmodel.LoadingListsPageQuantity = get_text_from_child_node(main, 'casdo:LoadingListsPageQuantity')
    xmlmodel.GoodsQuantity = get_text_from_child_node(main, 'casdo:GoodsQuantity', True)
    xmlmodel.CargoQuantity = get_text_from_child_node(main, 'casdo:CargoQuantity', True)

    # пломбы
    seal = get_node(main, 'cacdo:SealDetails')
    xmlmodel.SealQuantity = get_text_from_child_node(seal, 'casdo:SealQuantity')
    seal_list = []
    for _seal in get_nodes(seal, 'csdo:SealId'):
        seal_list.append(get_text_node(_seal))
    xmlmodel.SealId = ','.join(seal_list)
    # end пломбы

    # пост назначения
    tt = get_node(main, 'cacdo:TransitTerminationDetails', True)
    pto = get_node(tt, 'ccdo:CustomsOfficeDetails', True)
    xmlmodel.TT_CustomsOfficeCode = get_text_from_child_node(pto, 'csdo:CustomsOfficeCode', True)
    xmlmodel.TT_CustomsOfficeName = get_text_from_child_node(pto, 'csdo:CustomsOfficeName', True)
    xmlmodel.TT_CustomsControlZoneId = get_text_from_child_node(tt, 'casdo:CustomsControlZoneId')
    try:
        ucc = Pto.objects.get(CODE=xmlmodel.TT_CustomsOfficeCode)
        if ucc is not None:
            xmlmodel.TT_UnifiedCountryCode = ucc.COUNTRYCODELIT
    except Exception as e:
        messages.append(f'Для поста {xmlmodel.TT_CustomsOfficeCode} не найдена страна в справочнике.')
    # end пост назначения

    consignment = get_node(main, 'cacdo:PIATConsignmentDetails', True)  # общая информация о грузе

    # транспортный документ
    td_doc = get_node(consignment, 'cacdo:PIATTransportDocumentDetails', True)
    xmlmodel.TD_DocKindCode = get_text_from_child_node(td_doc, 'csdo:DocKindCode', True)
    xmlmodel.TD_DocId = get_text_from_child_node(td_doc, 'csdo:DocId', True)
    xmlmodel.TD_DocCreationDate = get_text_from_child_node(td_doc, 'csdo:DocCreationDate', True)
    # end транспортный документ

    # страна отправления
    country = get_node(consignment, 'cacdo:DepartureCountryDetails', True)
    xmlmodel.DepartureCountry_CACountryCode = get_text_from_child_node(country, 'casdo:CACountryCode', True)
    xmlmodel.DepartureCountry_ShortCountryName = get_text_from_child_node(country, 'casdo:ShortCountryName', True)
    # end страна отправления

    # страна назначения
    country = get_node(consignment, 'cacdo:DestinationCountryDetails', True)
    xmlmodel.DestinationCountry_CACountryCode = get_text_from_child_node(country, 'casdo:CACountryCode', True)
    xmlmodel.DestinationCountry_ShortCountryName = get_text_from_child_node(country, 'casdo:ShortCountryName', True)
    # end страна назначения

    # общая стоимость и вес
    inv_value = get_node(consignment, 'casdo:CAInvoiceValueAmount', True)
    xmlmodel.CAInvoiceValueAmount = get_text_node(inv_value)
    xmlmodel.IVA_currencyCode = get_attr_node(inv_value, 'currencyCode')
    gross_mass = get_node(consignment, 'csdo:UnifiedGrossMassMeasure', True)
    xmlmodel.UnifiedGrossMassMeasure = get_text_node(gross_mass)
    xmlmodel.measurementUnitCode = get_attr_node(gross_mass, 'measurementUnitCode')
    # end общая стоимость и вес

    # отправитель
    consignor = get_node(consignment, 'cacdo:PIATConsignorDetails', True)
    xmlmodel.Consignor_SubjectBriefName = get_text_from_child_node(consignor, 'csdo:SubjectBriefName', True)
    xmlmodel.Consignor_TaxpayerId = get_text_from_child_node(consignor, 'csdo:TaxpayerId')

    address = get_node(consignor, 'ccdo:SubjectAddressDetails', important=True)
    xmlmodel.Consignor_UnifiedCountryCode = get_text_from_child_node(address, 'csdo:UnifiedCountryCode', True)
    xmlmodel.Consignor_RegionName = get_text_from_child_node(address, 'csdo:RegionName')
    xmlmodel.Consignor_CityName = get_text_from_child_node(address, 'csdo:CityName', True)
    xmlmodel.Consignor_StreetName = get_text_from_child_node(address, 'csdo:StreetName', True)
    xmlmodel.Consignor_BuildingNumberId = get_text_from_child_node(address, 'csdo:BuildingNumberId')
    xmlmodel.Consignor_RoomNumberId = get_text_from_child_node(address, 'csdo:RoomNumberId')
    # end отправитель

    # получатель
    consignee = get_node(consignment, 'cacdo:PIATConsigneeDetails', True)
    xmlmodel.Consignee_SubjectBriefName = get_text_from_child_node(consignee, 'csdo:SubjectBriefName', True)
    xmlmodel.Consignee_TaxpayerId = get_text_from_child_node(consignee, 'csdo:TaxpayerId')

    address = get_node(consignee, 'ccdo:SubjectAddressDetails', important=True)
    xmlmodel.Consignee_UnifiedCountryCode = get_text_from_child_node(address, 'csdo:UnifiedCountryCode', True)
    xmlmodel.Consignee_RegionName = get_text_from_child_node(address, 'csdo:RegionName')
    xmlmodel.Consignee_CityName = get_text_from_child_node(address, 'csdo:CityName', True)
    xmlmodel.Consignee_StreetName = get_text_from_child_node(address, 'csdo:StreetName', True)
    xmlmodel.Consignee_BuildingNumberId = get_text_from_child_node(address, 'csdo:BuildingNumberId')
    xmlmodel.Consignee_RoomNumberId = get_text_from_child_node(address, 'csdo:RoomNumberId')
    # end получатель

    # декларант процедуры транзита
    transit_decl = get_node(main, 'cacdo:PITransitDeclarantDetails', True)
    xmlmodel.TransitDeclarant_SubjectBriefName = get_text_from_child_node(transit_decl, 'csdo:SubjectBriefName', True)
    xmlmodel.TransitDeclarant_EqualIndicator = get_text_from_child_node(transit_decl, 'casdo:EqualIndicator')
    xmlmodel.TransitDeclarant_TaxpayerId = get_text_from_child_node(transit_decl, 'csdo:TaxpayerId')

    address = get_node(transit_decl, 'ccdo:SubjectAddressDetails', important=True)
    xmlmodel.TransitDeclarant_UnifiedCountryCode = get_text_from_child_node(address, 'csdo:UnifiedCountryCode', True)
    xmlmodel.TransitDeclarant_RegionName = get_text_from_child_node(address, 'csdo:RegionName')
    xmlmodel.TransitDeclarant_CityName = get_text_from_child_node(address, 'csdo:CityName', True)
    xmlmodel.TransitDeclarant_StreetName = get_text_from_child_node(address, 'csdo:StreetName', True)
    xmlmodel.TransitDeclarant_BuildingNumberId = get_text_from_child_node(address, 'csdo:BuildingNumberId')
    xmlmodel.TransitDeclarant_RoomNumberId = get_text_from_child_node(address, 'csdo:RoomNumberId')
    # end декларант процедуры транзита

    # перевозчик по тт еаэс
    union_carrier = get_node(main, 'cacdo:PIUnionCarrierDetails', True)
    xmlmodel.UnionCarrier_SubjectBriefName = get_text_from_child_node(union_carrier, 'csdo:SubjectBriefName', True)
    xmlmodel.UnionCarrier_TaxpayerId = get_text_from_child_node(union_carrier, 'csdo:TaxpayerId')

    address = get_node(union_carrier, 'ccdo:SubjectAddressDetails', important=True)
    xmlmodel.UnionCarrier_UnifiedCountryCode = get_text_from_child_node(address, 'csdo:UnifiedCountryCode', True)
    xmlmodel.UnionCarrier_RegionName = get_text_from_child_node(address, 'csdo:RegionName')
    xmlmodel.UnionCarrier_CityName = get_text_from_child_node(address, 'csdo:CityName', True)
    xmlmodel.UnionCarrier_StreetName = get_text_from_child_node(address, 'csdo:StreetName', True)
    xmlmodel.UnionCarrier_BuildingNumberId = get_text_from_child_node(address, 'csdo:BuildingNumberId')
    xmlmodel.UnionCarrier_RoomNumberId = get_text_from_child_node(address, 'csdo:RoomNumberId')
    # end перевозчик по тт еаэс

    # представитель перевозчика (водитель)
    driver = get_node(union_carrier, 'cacdo:CarrierRepresentativeDetails', True)
    full_name = get_node(driver, 'ccdo:FullNameDetails', True)
    xmlmodel.CarrierRepresentative_FirstName = get_text_from_child_node(full_name, 'csdo:FirstName', True)
    xmlmodel.CarrierRepresentative_LastName = get_text_from_child_node(full_name, 'csdo:LastName', True)
    xmlmodel.CarrierRepresentative_MiddleName = get_text_from_child_node(full_name, 'csdo:MiddleName')
    xmlmodel.CarrierRepresentative_PositionName = get_text_from_child_node(driver, 'csdo:PositionName')

    ident_doc = get_node(driver, 'ccdo:IdentityDocV3Details', True)
    xmlmodel.CarrierRepresentative_UnifiedCountryCode = get_text_from_child_node(ident_doc, 'csdo:UnifiedCountryCode', True)
    xmlmodel.CarrierRepresentative_IdentityDocKindCode = get_text_from_child_node(ident_doc, 'csdo:IdentityDocKindCode', True)
    xmlmodel.CarrierRepresentative_DocId = get_text_from_child_node(ident_doc, 'csdo:DocId', True)
    xmlmodel.CarrierRepresentative_DocCreationDate = get_text_from_child_node(ident_doc, 'csdo:DocCreationDate', True)
    xmlmodel.CarrierRepresentative_DocValidityDate = get_text_from_child_node(ident_doc, 'csdo:DocValidityDate')

    xmlmodel.CarrierRepresentative_RoleCode = get_text_from_child_node(driver, 'casdo:RoleCode')
    # end представитель перевозчика (водитель)

    # перевозчик
    carrier = get_node(root, 'cacdo:PIATCarrierDetails', True)
    xmlmodel.Carrier_SubjectBriefName = get_text_from_child_node(carrier, 'csdo:SubjectBriefName', True)
    xmlmodel.Carrier_TaxpayerId = get_text_from_child_node(carrier, 'csdo:TaxpayerId')

    address = get_node(carrier, 'ccdo:SubjectAddressDetails', important=True)
    xmlmodel.Carrier_UnifiedCountryCode = get_text_from_child_node(address, 'csdo:UnifiedCountryCode', True)
    xmlmodel.Carrier_RegionName = get_text_from_child_node(address, 'csdo:RegionName')
    xmlmodel.Carrier_CityName = get_text_from_child_node(address, 'csdo:CityName', True)
    xmlmodel.Carrier_StreetName = get_text_from_child_node(address, 'csdo:StreetName', True)
    xmlmodel.Carrier_BuildingNumberId = get_text_from_child_node(address, 'csdo:BuildingNumberId')
    xmlmodel.Carrier_RoomNumberId = get_text_from_child_node(address, 'csdo:RoomNumberId')
    # end перевозчик

    try:
        xmlmodel.save()
    except Exception as e:
        messages.append('Не удалось сохранить основную информацию по XML. Ошибка: ' + str(e))
        return {
            'id': 0,
            'messages': messages,
        }

    # перецепки в xml
    for _t in get_nodes(main, 'cacdo:PITranshipmentDetails'):
        transhipment = Transhipment()
        transhipment.CargoOperationKindCode = get_text_from_child_node(_t, 'casdo:CargoOperationKindCode', True)
        transhipment.ContainerIndicator = get_text_from_child_node(_t, 'casdo:ContainerIndicator', True)
        transhipment.CACountryCode = get_text_from_child_node(_t, 'casdo:CACountryCode', True)
        transhipment.ShortCountryName = get_text_from_child_node(_t, 'casdo:ShortCountryName', True)
        transhipment.PlaceName = get_text_from_child_node(_t, 'casdo:PlaceName')
        customs = get_node(_t, 'ccdo:CustomsOfficeDetails')
        transhipment.CustomsOfficeCode = get_text_from_child_node(customs, 'csdo:CustomsOfficeCode')
        transhipment.CustomsOfficeName = get_text_from_child_node(customs, 'csdo:CustomsOfficeName')
        transhipment.xml = xmlmodel

        t_transport = get_node(_t, 'cacdo:TranshipmentTransportDetails', True)
        transhipment.UnifiedTransportModeCode = get_text_from_child_node(t_transport, 'csdo:UnifiedTransportModeCode', True)
        transhipment.RegistrationNationalityCode = get_text_from_child_node(t_transport, 'casdo:RegistrationNationalityCode', True)
        transhipment.TransportMeansQuantity = get_text_from_child_node(t_transport, 'casdo:TransportMeansQuantity', True)

        try:
            transhipment.save()
        except Exception as e:
            messages.append('Не удалось сохранить перецепку/перегрузку в XML. Ошибка: ' + str(e))
            continue

        # транспорт в перецепке
        for _transport in get_nodes(t_transport, 'cacdo:TransportMeansRegistrationIdDetails', True):
            transport_transhipment = TransportTranshipment()
            _ct = get_node(_transport, 'csdo:TransportMeansRegId', True)
            transport_transhipment.TransportMeansRegId = get_text_node(_ct)
            transport_transhipment.countryCode = get_attr_node(_ct, 'countryCode')
            transport_transhipment.TransportTypeCode = get_text_from_child_node(_transport, 'casdo:TransportTypeCode', True)
            transport_transhipment.transhipment_xml = transhipment
            try:
                transport_transhipment.save()
            except Exception as e:
                messages.append('Не удалось сохранить транспорт в перецепке/перегрузке в XML. Ошибка: ' + str(e))
                continue
        # end транспорт в перецепке

        # контейнеры в перецепке
        for _container in get_nodes(_t, 'casdo:ContainerId'):
            container_transhipment = ContainerTranshipment()
            container_transhipment.ContainerId = get_text_node(_container)
            container_transhipment.transhipment_xml = transhipment
            try:
                container_transhipment.save()
            except Exception as e:
                messages.append('Не удалось сохранить контейнер в перецепке/перегрузке в XML. Ошибка: ' + str(e))
                continue
        # end контейнеры в перецепке
    # end перецепки в xml

    # контейнеры в xml
    for _container in get_nodes(consignment, 'cacdo:PIContainerDetails'):
        container_xml = ContainerXML()
        container_xml.ContainerId = get_text_from_child_node(_container, 'casdo:ContainerId', True)
        container_xml.xml = xmlmodel
        try:
            container_xml.save()
        except Exception as e:
            messages.append('Не удалось сохранить контейнер в XML. Ошибка: ' + str(e))
            continue
    # end контейнеры в xml


    # транспорт в xml
    ts_list = []
    # тягач
    transport_xml = TransportXML()
    _transport = get_node(transport_details, 'csdo:TransportMeansRegId', True)
    transport_xml.TransportMeansRegId = get_text_node(_transport)
    transport_xml.countryCode = get_attr_node(_transport, 'countryCode')
    transport_xml.VehicleId = get_text_from_child_node(transport_details, 'csdo:VehicleId', True)
    transport_xml.TransportTypeCode = get_text_from_child_node(transport_details, 'casdo:TransportTypeCode', True)
    transport_xml.VehicleMakeCode = get_text_from_child_node(transport_details, 'csdo:VehicleMakeCode', True)
    transport_xml.VehicleMakeName = get_text_from_child_node(transport_details, 'csdo:VehicleMakeName')
    transport_xml.VehicleModelName = get_text_from_child_node(transport_details, 'casdo:VehicleModelName')
    transport_xml.xml = xmlmodel
    try:
        transport_xml.save()
        ts_list.append(transport_xml.TransportMeansRegId)
    except Exception as e:
        messages.append('Не удалось сохранить тягач. Ошибка: ' + str(e))
    # end тягач

    # прицеп (прицепы)
    for _t in get_nodes(transport_details, 'cacdo:TrailerDetails'):
        transport_xml = TransportXML()
        _transport = get_node(_t, 'csdo:TransportMeansRegId', True)
        transport_xml.TransportMeansRegId = get_text_node(_transport)
        transport_xml.countryCode = get_attr_node(_transport, 'countryCode')
        transport_xml.VehicleId = get_text_from_child_node(_t, 'csdo:VehicleId', True)
        transport_xml.TransportTypeCode = get_text_from_child_node(_t, 'casdo:TransportTypeCode', True)
        transport_xml.VehicleMakeCode = get_text_from_child_node(_t, 'csdo:VehicleMakeCode', True)
        transport_xml.VehicleMakeName = get_text_from_child_node(_t, 'csdo:VehicleMakeName')
        transport_xml.VehicleModelName = get_text_from_child_node(_t, 'casdo:VehicleModelName')
        transport_xml.xml = xmlmodel
        try:
            transport_xml.save()
            ts_list.append(transport_xml.TransportMeansRegId)
        except Exception as e:
            messages.append('Не удалось сохранить прицеп. Ошибка: ' + str(e))
    # end прицеп (прицепы)
    # end транспорт в xml

    # сохраняем список транспортных средств в поле transport_list
    xmlmodel.transport_list = ' / '.join(ts_list)
    try:
        xmlmodel.save(need_refresh=False)
    except Exception as e:
        messages.append(
            'Не удалось сохранить список транспортных средств в основной информации по XML. Ошибка: ' + str(e))
    # end сохраняем список транспортных средств в поле transport_list

    # гарантии в xml
    for _g in get_nodes(main, 'cacdo:TransitGuaranteeDetails', True):
        guarantee = TransitGuarantee()
        guarantee.TransitGuaranteeMeasureCode = get_text_from_child_node(_g, 'casdo:TransitGuaranteeMeasureCode', True)
        _amount = get_node(_g, 'casdo:GuaranteeAmount')
        guarantee.GuaranteeAmount = get_text_node(_amount)
        guarantee.currencyCode = get_attr_node(_amount, 'currencyCode')
        _gc = get_node(_g, 'cacdo:GuaranteeCertificateIdDetails')
        if _gc is not None:
            guarantee.GC_CustomsOfficeCode = get_text_from_child_node(_gc, 'csdo:CustomsOfficeCode', True)
            guarantee.GC_DocCreationDate = get_text_from_child_node(_gc, 'csdo:DocCreationDate', True)
            guarantee.GC_CustomsDocumentId = get_text_from_child_node(_gc, 'casdo:CustomsDocumentId', True)
        _rd = get_node(_g, 'cacdo:RegisterDocumentIdDetails')
        if _rd is not None:
            guarantee.RD_UnifiedCountryCode = get_text_from_child_node(_rd, 'csdo:UnifiedCountryCode', True)
            guarantee.RD_RegistrationNumberId = get_text_from_child_node(_rd, 'casdo:RegistrationNumberId', True)
        guarantee.ES_SubjectBriefName = get_text_from_child_node(_g, 'csdo:SubjectBriefName')
        guarantee.ES_TaxpayerId = get_text_from_child_node(_g, 'csdo:TaxpayerId')
        guarantee.ES_BankId = get_text_from_child_node(_g, 'csdo:BankId')
        guarantee.xml = xmlmodel
        try:
            guarantee.save()
        except Exception as e:
            messages.append('Не удалось сохранить гарантии в XML. Ошибка: ' + str(e))
            continue
    # end гарантии в xml

    # товар и все что в нем
    for _tovar in get_nodes(consignment, 'cacdo:PIATConsignmentItemDetails', True):
        # товар
        cons_item = ConsignmentItem()
        cons_item.ConsignmentItemOrdinal = get_text_from_child_node(_tovar, 'casdo:ConsignmentItemOrdinal', True)
        cons_item.CommodityCode = get_text_from_child_node(_tovar, 'csdo:CommodityCode', True)
        _i = 0
        for _descr in get_nodes(_tovar, 'casdo:GoodsDescriptionText', True):
            if _i == 0:
                cons_item.GoodsDescriptionText = get_text_node(_descr)
            elif _i == 1:
                cons_item.GoodsDescriptionText1 = get_text_node(_descr)
            elif _i == 2:
                cons_item.GoodsDescriptionText2 = get_text_node(_descr)
            else:
                cons_item.GoodsDescriptionText3 = get_text_node(_descr)
            _i += 1
        _gm = get_node(_tovar, 'csdo:UnifiedGrossMassMeasure', True)
        cons_item.UnifiedGrossMassMeasure = get_text_node(_gm)
        cons_item.measurementUnitCode = get_attr_node(_gm, 'measurementUnitCode')

        gm = get_node(_tovar, 'cacdo:GoodsMeasureDetails')
        if gm is not None:
            _gm = get_node(gm, 'casdo:GoodsMeasure', True)
            cons_item.GM_GoodsMeasure = get_text_node(_gm)
            cons_item.GM_measurementUnitCode = get_attr_node(_gm, 'measurementUnitCode')
            cons_item.GM_MeasureUnitAbbreviationCode = get_text_from_child_node(gm, 'casdo:MeasureUnitAbbreviationCode', True)

        gm = get_node(_tovar, 'cacdo:AddGoodsMeasureDetails')
        if gm is not None:
            _gm = get_node(gm, 'casdo:GoodsMeasure', True)
            cons_item.AGM_GoodsMeasure = get_text_node(_gm)
            cons_item.AGM_measurementUnitCode = get_attr_node(_gm, 'measurementUnitCode')
            cons_item.AGM_MeasureUnitAbbreviationCode = get_text_from_child_node(gm, 'casdo:MeasureUnitAbbreviationCode', True)

        _cargo_package = get_node(_tovar, 'cacdo:CargoPackagePalletDetails', True)
        cons_item.PackageAvailabilityCode = get_text_from_child_node(_cargo_package, 'casdo:PackageAvailabilityCode', True)
        cons_item.CargoQuantity = get_text_from_child_node(_cargo_package, 'casdo:CargoQuantity', True)

        _package_details = get_node(_cargo_package, 'cacdo:PackagePalletDetails', True)
        cons_item.CargoPackageInfoKindCode = get_text_from_child_node(_package_details, 'casdo:CargoPackageInfoKindCode', True)
        cons_item.PackageKindCode = get_text_from_child_node(_package_details, 'csdo:PackageKindCode', True)
        cons_item.PackageQuantity = get_text_from_child_node(_package_details, 'csdo:PackageQuantity', True)

        _value = get_node(_tovar, 'casdo:CAValueAmount', True)
        cons_item.CAValueAmount = get_text_node(_value)
        cons_item.currencyCode = get_attr_node(_value, 'currencyCode')
        cons_item.xml = xmlmodel

        try:
            cons_item.save()
        except Exception as e:
            messages.append('Не удалось сохранить товар. Ошибка: ' + str(e))
            continue
        # end товар

        # предшедствующие доки
        for _prec_doc in get_nodes(_tovar, 'cacdo:PIPrecedingDocDetails'):
            preceding_doc = PIPrecedingDocDetails()
            preceding_doc.DocKindCode = get_text_from_child_node(_prec_doc, 'csdo:DocKindCode', True)
            preceding_doc.DocId = get_text_from_child_node(_prec_doc, 'csdo:DocId', True)
            preceding_doc.DocCreationDate = get_text_from_child_node(_prec_doc, 'csdo:DocCreationDate', True)
            preceding_doc.ci = cons_item
            try:
                preceding_doc.save()
            except Exception as e:
                messages.append('Не удалось сохранить предшедствующий документ. Ошибка: ' + str(e))
                continue
        # end предшедствующие доки

        # документы
        for _doc in get_nodes(_tovar, 'cacdo:PIGoodsDocDetails'):
            goods_doc = PIGoodsDocDetails()
            goods_doc.DocKindCode = get_text_from_child_node(_doc, 'csdo:DocKindCode', True)
            goods_doc.DocId = get_text_from_child_node(_doc, 'csdo:DocId', True)
            goods_doc.DocCreationDate = get_text_from_child_node(_doc, 'csdo:DocCreationDate', True)
            goods_doc.ci = cons_item
            try:
                goods_doc.save()
            except Exception as e:
                messages.append('Не удалось сохранить документ для товара. Ошибка: ' + str(e))
                continue
        # end документы

        # контейнеры в товаре
        for _cont in get_nodes(_tovar, 'cacdo:PIContainerDetails'):
            cont_ci = ContainerCI()
            cont_ci.ContainerId = get_text_from_child_node(_cont, 'casdo:ContainerId', True)
            cont_ci.ci = cons_item
            try:
                cont_ci.save()
            except Exception as e:
                messages.append('Не удалось сохранить контейнер для товара. Ошибка: ' + str(e))
                continue
        # end контейнеры в товаре
        # end товар и все что в нем

    return {
        'id': xmlmodel.pk,
        'messages': messages,
    }


def td_to_db(xmlfile, user_l):
    """
        Загрузка ТД из xml-файла в базу данных
    """
    messages = []

    tree = et.parse(xmlfile)
    root = tree.getroot()
    ns = root.nsmap.copy()

    def only_tag(s):
        """ Убирает namespace из тэга xml-элемента
            на вход может поступать элемент дерева xml и строка тэга с namespace"""
        try:
            _s = s.tag.split('}')[1]  # если на входе объект
            return _s
        except:
            return s.split(':')[1]  # если на входе строка

    def get_node(et, tag, important=False):
        """ Возвращает элемент дерева xml с тэгом tag, у которого родитель et
            important - флаг, указывающий важное поле или же оно может отсутствовать
        """
        if et is not None:
            _ns, _tag = tag.split(':')
            _e = et.find(f'{{{ns[_ns]}}}{_tag}')
            if _e is None:
                if important:
                    messages.append(f'Важно! В XML не найдено поле {only_tag(et)} > {only_tag(tag)}!')
            return _e
        else:
            return None

    def get_nodes(et, tag, important=False):
        """ Возвращает список элементов дерева с тэгом tag, у которого родитель et
            important - флаг, указывающий важное поле или же оно может отсутствовать"""
        if et is not None:
            _ns, _tag = tag.split(':')
            _e = et.findall(f'{{{ns[_ns]}}}{_tag}')
            if _e:
                return _e
            else:
                if important:
                    messages.append(f'Важно! В XML не найдено поле (поля) {only_tag(et.tag)} > {only_tag(tag)}!')
                return []
        else:
            return []

    def get_text_node(node):
        """ Возвращает текст из xml-элемента """
        try:
            return node.text
        except:
            return None

    def get_attr_node(node, attr):
        """ Возвращает значение атрибута attr из xml-элемента """
        try:
            return node.attrib[attr]
        except:
            return None

    def get_text_from_child_node(et, tag, important=False):
        """ Возвращает текст элемент дерева xml с тэгом tag, у которого родитель et
            important - флаг, указывающий важное поле или же оно может отсутствовать
        """
        if et is not None:
            return get_text_node(get_node(et, tag, important=important))
        else:
            return None

    xmlmodel = XMLModel()
    xmlmodel.XmlType = 'TD'
    xmlmodel.user = user_l
    xmlmodel.EDocCode = get_text_from_child_node(root, 'csdo:EDocCode')
    xmlmodel.EDocId = get_text_from_child_node(root, 'csdo:EDocId', important=True)
    xmlmodel.EDocDateTime = get_text_from_child_node(root, 'csdo:EDocDateTime', important=True)
    xmlmodel.DeclarationKindCode = get_text_from_child_node(root, 'casdo:DeclarationKindCode', True)
    xmlmodel.TransitProcedureCode = get_text_from_child_node(root, 'casdo:TransitProcedureCode', True)
    xmlmodel.TransitFeatureCode = get_text_from_child_node(root, 'casdo:TransitFeatureCode')
    xmlmodel.EDocIndicatorCode = get_text_from_child_node(root, 'casdo:EDocIndicatorCode', important=True)
    xmlmodel.LoadingListsQuantity = get_text_from_child_node(root, 'casdo:LoadingListsQuantity')
    xmlmodel.LoadingListsPageQuantity = get_text_from_child_node(root, 'casdo:LoadingListsPageQuantity')
    xmlmodel.GoodsQuantity = get_text_from_child_node(root, 'casdo:GoodsQuantity', True)
    xmlmodel.CargoQuantity = get_text_from_child_node(root, 'casdo:CargoQuantity', True)

    # декларант процедуры транзита
    transit_decl = get_node(root, 'cacdo:DeclarantDetails', True)
    xmlmodel.TransitDeclarant_SubjectBriefName = get_text_from_child_node(transit_decl, 'csdo:SubjectBriefName', True)
    xmlmodel.TransitDeclarant_TaxpayerId = get_text_from_child_node(transit_decl, 'csdo:TaxpayerId')

    address = get_node(transit_decl, 'ccdo:SubjectAddressDetails', important=True)
    xmlmodel.TransitDeclarant_UnifiedCountryCode = get_text_from_child_node(address, 'csdo:UnifiedCountryCode', True)
    xmlmodel.TransitDeclarant_RegionName = get_text_from_child_node(address, 'csdo:RegionName')
    xmlmodel.TransitDeclarant_CityName = get_text_from_child_node(address, 'csdo:CityName', True)
    xmlmodel.TransitDeclarant_StreetName = get_text_from_child_node(address, 'csdo:StreetName', True)
    xmlmodel.TransitDeclarant_BuildingNumberId = get_text_from_child_node(address, 'csdo:BuildingNumberId')
    xmlmodel.TransitDeclarant_RoomNumberId = get_text_from_child_node(address, 'csdo:RoomNumberId')
    # end декларант процедуры транзита

    # перевозчик
    carrier = get_node(root, 'cacdo:CarrierDetails', True)
    xmlmodel.Carrier_SubjectBriefName = get_text_from_child_node(carrier, 'csdo:SubjectBriefName', True)
    xmlmodel.Carrier_TaxpayerId = get_text_from_child_node(carrier, 'csdo:TaxpayerId')

    address = get_node(carrier, 'ccdo:SubjectAddressDetails', important=True)
    xmlmodel.Carrier_UnifiedCountryCode = get_text_from_child_node(address, 'csdo:UnifiedCountryCode', True)
    xmlmodel.Carrier_RegionName = get_text_from_child_node(address, 'csdo:RegionName')
    xmlmodel.Carrier_CityName = get_text_from_child_node(address, 'csdo:CityName', True)
    xmlmodel.Carrier_StreetName = get_text_from_child_node(address, 'csdo:StreetName', True)
    xmlmodel.Carrier_BuildingNumberId = get_text_from_child_node(address, 'csdo:BuildingNumberId')
    xmlmodel.Carrier_RoomNumberId = get_text_from_child_node(address, 'csdo:RoomNumberId')
    # end перевозчик

    # представитель перевозчика (водитель)
    driver = get_node(carrier, 'cacdo:CarrierRepresentativeDetails', True)
    full_name = get_node(driver, 'ccdo:FullNameDetails', True)
    xmlmodel.CarrierRepresentative_FirstName = get_text_from_child_node(full_name, 'csdo:FirstName', True)
    xmlmodel.CarrierRepresentative_LastName = get_text_from_child_node(full_name, 'csdo:LastName', True)
    xmlmodel.CarrierRepresentative_MiddleName = get_text_from_child_node(full_name, 'csdo:MiddleName')
    xmlmodel.CarrierRepresentative_PositionName = get_text_from_child_node(driver, 'csdo:PositionName')

    ident_doc = get_node(driver, 'ccdo:IdentityDocV3Details', True)
    xmlmodel.CarrierRepresentative_UnifiedCountryCode = get_text_from_child_node(ident_doc, 'csdo:UnifiedCountryCode', True)
    xmlmodel.CarrierRepresentative_IdentityDocKindCode = get_text_from_child_node(ident_doc, 'csdo:IdentityDocKindCode', True)
    xmlmodel.CarrierRepresentative_DocId = get_text_from_child_node(ident_doc, 'csdo:DocId', True)
    xmlmodel.CarrierRepresentative_DocCreationDate = get_text_from_child_node(ident_doc, 'csdo:DocCreationDate', True)
    xmlmodel.CarrierRepresentative_DocValidityDate = get_text_from_child_node(ident_doc, 'csdo:DocValidityDate')

    xmlmodel.CarrierRepresentative_RoleCode = get_text_from_child_node(driver, 'casdo:RoleCode')
    # end представитель перевозчика (водитель)

    # пломбы
    seal = get_node(root, 'cacdo:SealDetails')
    xmlmodel.SealQuantity = get_text_from_child_node(seal, 'casdo:SealQuantity')
    seal_list = []
    for _seal in get_nodes(seal, 'csdo:SealId'):
        seal_list.append(get_text_node(_seal))
    xmlmodel.SealId = ','.join(seal_list)
    # end пломбы

    # детали о подписывающем представителе
    sign_detail = get_node(root, 'cacdo:SignatoryRepresentativeDetails')
    reg_doc = get_node(sign_detail, 'cacdo:RegisterDocumentIdDetails')
    xmlmodel.SD_RegisterDocumentIdDetails_DocKindCode = get_text_from_child_node(reg_doc, 'csdo:DocKindCode')
    xmlmodel.SD_RegisterDocumentIdDetails_RegistrationNumberId = get_text_from_child_node(reg_doc, 'casdo:RegistrationNumberId')
    contract_r = get_node(sign_detail, 'cacdo:RepresentativeContractDetails')
    xmlmodel.SD_RepresentativeContractDetails_DocKindCode = get_text_from_child_node(contract_r, 'csdo:DocKindCode')
    xmlmodel.SD_RepresentativeContractDetails_DocId = get_text_from_child_node(contract_r, 'csdo:DocId')
    xmlmodel.SD_RepresentativeContractDetails_DocCreationDate = get_text_from_child_node(contract_r, 'csdo:DocCreationDate')
    # end детали о подписывающем представителе

    # подписывающий представитель
    sign_person_detail = get_node(root, 'cacdo:SignatoryPersonV2Details', True)
    person = get_node(sign_person_detail, 'cacdo:SigningDetails', True)
    full_name = get_node(person, 'ccdo:FullNameDetails', True)
    xmlmodel.SP_FirstName = get_text_from_child_node(full_name, 'csdo:FirstName', True)
    xmlmodel.SP_LastName = get_text_from_child_node(full_name, 'csdo:LastName', True)
    xmlmodel.SP_MiddleName = get_text_from_child_node(full_name, 'csdo:MiddleName')
    xmlmodel.SP_PositionName = get_text_from_child_node(person, 'csdo:PositionName')

    ident_doc = get_node(sign_person_detail, 'ccdo:IdentityDocV3Details', True)
    xmlmodel.SP_UnifiedCountryCode = get_text_from_child_node(ident_doc, 'csdo:UnifiedCountryCode', True)
    xmlmodel.SP_IdentityDocKindCode = get_text_from_child_node(ident_doc, 'csdo:IdentityDocKindCode', True)
    xmlmodel.SP_DocId = get_text_from_child_node(ident_doc, 'csdo:DocId', True)
    xmlmodel.SP_DocCreationDate = get_text_from_child_node(ident_doc, 'csdo:DocCreationDate', True)
    xmlmodel.SP_DocValidityDate = get_text_from_child_node(ident_doc, 'csdo:DocValidityDate')

    xmlmodel.SP_QualificationCertificateId = get_text_from_child_node(sign_person_detail, 'casdo:QualificationCertificateId')
    poa = get_node(sign_person_detail, 'cacdo:PowerOfAttorneyDetails')
    xmlmodel.SP_POA_DocKindCode = get_text_from_child_node(poa, 'csdo:DocKindCode')
    xmlmodel.SP_POA_DocId = get_text_from_child_node(poa, 'csdo:DocId')
    xmlmodel.SP_POA_DocCreationDate = get_text_from_child_node(poa, 'csdo:DocCreationDate')
    xmlmodel.SP_POA_DocValidityDate = get_text_from_child_node(poa, 'csdo:DocValidityDate')
    # end подписывающий представитель

    decl_goods = get_node(root, 'cacdo:DeclarationGoodsShipmentDetails', True)
    # страна отправления
    country = get_node(decl_goods, 'cacdo:DepartureCountryDetails', True)
    xmlmodel.DepartureCountry_CACountryCode = get_text_from_child_node(country, 'casdo:CACountryCode', True)
    xmlmodel.DepartureCountry_ShortCountryName = get_text_from_child_node(country, 'casdo:ShortCountryName', True)
    # end страна отправления

    # страна назначения
    country = get_node(decl_goods, 'cacdo:DestinationCountryDetails', True)
    xmlmodel.DestinationCountry_CACountryCode = get_text_from_child_node(country, 'casdo:CACountryCode', True)
    xmlmodel.DestinationCountry_ShortCountryName = get_text_from_child_node(country, 'casdo:ShortCountryName', True)
    # end страна назначения

    # общая стоимость, курс, таможенная стоимость
    inv_value = get_node(decl_goods, 'casdo:CAValueAmount', True)
    xmlmodel.CAInvoiceValueAmount = get_text_node(inv_value)
    xmlmodel.IVA_currencyCode = get_attr_node(inv_value, 'currencyCode')
    exch_rate = get_node(decl_goods, 'casdo:ExchangeRate', True)
    xmlmodel.TD_ExchangeRate = get_text_node(exch_rate)
    xmlmodel.TD_ER_currencyCode = get_attr_node(exch_rate, 'currencyCode')
    xmlmodel.TD_ER_scaleNumber = get_attr_node(exch_rate, 'scaleNumber')
    custom_value = get_node(decl_goods, 'casdo:CustomsValueAmount', True)
    xmlmodel.TD_CustomsValueAmount = get_text_node(custom_value)
    xmlmodel.TD_CV_currencyCode = get_attr_node(custom_value, 'currencyCode')
    # end общая стоимость, курс, таможенная стоимость

    # отправитель
    consignor = get_node(decl_goods, 'cacdo:ConsignorDetails', True)
    xmlmodel.Consignor_SubjectBriefName = get_text_from_child_node(consignor, 'csdo:SubjectBriefName', True)
    xmlmodel.Consignor_TaxpayerId = get_text_from_child_node(consignor, 'csdo:TaxpayerId')

    address = get_node(consignor, 'ccdo:SubjectAddressDetails', important=True)
    xmlmodel.Consignor_UnifiedCountryCode = get_text_from_child_node(address, 'csdo:UnifiedCountryCode', True)
    xmlmodel.Consignor_RegionName = get_text_from_child_node(address, 'csdo:RegionName')
    xmlmodel.Consignor_CityName = get_text_from_child_node(address, 'csdo:CityName', True)
    xmlmodel.Consignor_StreetName = get_text_from_child_node(address, 'csdo:StreetName', True)
    xmlmodel.Consignor_BuildingNumberId = get_text_from_child_node(address, 'csdo:BuildingNumberId')
    xmlmodel.Consignor_RoomNumberId = get_text_from_child_node(address, 'csdo:RoomNumberId')
    # end отправитель

    # получатель
    consignee = get_node(decl_goods, 'cacdo:ConsigneeDetails', True)
    xmlmodel.Consignee_SubjectBriefName = get_text_from_child_node(consignee, 'csdo:SubjectBriefName', True)
    xmlmodel.Consignee_TaxpayerId = get_text_from_child_node(consignee, 'csdo:TaxpayerId')

    address = get_node(consignee, 'ccdo:SubjectAddressDetails', important=True)
    xmlmodel.Consignee_UnifiedCountryCode = get_text_from_child_node(address, 'csdo:UnifiedCountryCode', True)
    xmlmodel.Consignee_RegionName = get_text_from_child_node(address, 'csdo:RegionName')
    xmlmodel.Consignee_CityName = get_text_from_child_node(address, 'csdo:CityName', True)
    xmlmodel.Consignee_StreetName = get_text_from_child_node(address, 'csdo:StreetName', True)
    xmlmodel.Consignee_BuildingNumberId = get_text_from_child_node(address, 'csdo:BuildingNumberId')
    xmlmodel.Consignee_RoomNumberId = get_text_from_child_node(address, 'csdo:RoomNumberId')
    # end получатель

    consignment = get_node(decl_goods, 'cacdo:DeclarationConsignmentDetails', True)  # общая информация о грузе
    # инфа о транспорте
    transport_details = get_node(consignment, 'cacdo:BorderTransportDetails', important=True)
    xmlmodel.UnifiedTransportModeCode = get_text_from_child_node(transport_details, 'csdo:UnifiedTransportModeCode', True)
    xmlmodel.ContainerIndicator = get_text_from_child_node(consignment, 'casdo:ContainerIndicator', True)
    xmlmodel.TransportMeansQuantity = len(get_nodes(
        get_node(consignment, 'cacdo:ArrivalDepartureTransportDetails', True),
        'cacdo:TransportMeansRegistrationIdDetails',
        True)
    )
    # end инфа о транспорте

    # пост отправления
    ecp = get_node(consignment, 'cacdo:BorderCustomsOfficeDetails', important=True)
    xmlmodel.ECP_CustomsOfficeCode = get_text_from_child_node(ecp, 'csdo:CustomsOfficeCode', important=True)
    xmlmodel.ECP_BorderCheckpointName = get_text_from_child_node(ecp, 'csdo:CustomsOfficeName', important=True)
    # end пост отправления

    # пост назначения
    tt = get_node(consignment, 'cacdo:TransitTerminationDetails', True)
    pto = get_node(tt, 'ccdo:CustomsOfficeDetails', True)
    xmlmodel.TT_CustomsOfficeCode = get_text_from_child_node(pto, 'csdo:CustomsOfficeCode', True)
    xmlmodel.TT_CustomsOfficeName = get_text_from_child_node(pto, 'csdo:CustomsOfficeName', True)
    xmlmodel.TT_CustomsControlZoneId = get_text_from_child_node(tt, 'casdo:CustomsControlZoneId')
    ucc = xmlmodel.TT_CustomsOfficeCode[:3]
    if ucc == '112':
        xmlmodel.TT_UnifiedCountryCode = 'BY'
    elif ucc == '051':
        xmlmodel.TT_UnifiedCountryCode = 'AM'
    elif ucc == '398':
        xmlmodel.TT_UnifiedCountryCode = 'KZ'
    elif ucc == '417':
        xmlmodel.TT_UnifiedCountryCode = 'KG'
    else:
        xmlmodel.TT_UnifiedCountryCode = 'RU'
    # end пост назначения

    try:
        xmlmodel.save()
    except Exception as e:
        messages.append('Не удалось сохранить основную информацию по XML. Ошибка: ' + str(e))
        return {
            'id': 0,
            'messages': messages,
        }


    # транспортные средства
    ts_list = []
    transport_details = get_node(consignment, 'cacdo:ArrivalDepartureTransportDetails', True)
    for _t in get_nodes(transport_details, 'cacdo:TransportMeansRegistrationIdDetails'):
        transport_xml = TransportXML()
        _transport = get_node(_t, 'csdo:TransportMeansRegId', True)
        transport_xml.TransportMeansRegId = get_text_node(_transport)
        transport_xml.countryCode = get_attr_node(_transport, 'countryCode')
        transport_xml.DocId = get_text_from_child_node(_t, 'csdo:DocId')
        transport_xml.VehicleId = get_text_from_child_node(_t, 'csdo:VehicleId', True)
        transport_xml.TransportTypeCode = get_text_from_child_node(_t, 'casdo:TransportTypeCode', True)
        transport_xml.VehicleMakeCode = get_text_from_child_node(_t, 'csdo:VehicleMakeCode', True)
        transport_xml.xml = xmlmodel
        try:
            transport_xml.save()
            ts_list.append(transport_xml.TransportMeansRegId)
        except Exception as e:
            messages.append('Не удалось сохранить транспортное средство. Ошибка: ' + str(e))
    # end транспортные средства

    # сохраняем список транспортных средств в поле transport_list
    xmlmodel.transport_list = ' / '.join(ts_list)
    try:
        xmlmodel.save()
    except Exception as e:
        messages.append('Не удалось сохранить список транспортных средств в основной информации по XML. Ошибка: ' + str(e))
    # end сохраняем список транспортных средств в поле transport_list

    # перецепки в xml
    for _t in get_nodes(consignment, 'cacdo:TranshipmentDetails'):
        transhipment = Transhipment()
        transhipment.ContainerIndicator = get_text_from_child_node(_t, 'casdo:ContainerIndicator', True)
        transhipment.CACountryCode = get_text_from_child_node(_t, 'casdo:CACountryCode', True)
        transhipment.ShortCountryName = get_text_from_child_node(_t, 'casdo:ShortCountryName', True)
        transhipment.PlaceName = get_text_from_child_node(_t, 'casdo:PlaceName')
        customs = get_node(_t, 'ccdo:CustomsOfficeDetails')
        transhipment.CustomsOfficeCode = get_text_from_child_node(customs, 'csdo:CustomsOfficeCode')
        transhipment.CustomsOfficeName = get_text_from_child_node(customs, 'csdo:CustomsOfficeName')
        transhipment.xml = xmlmodel

        t_transport = get_node(_t, 'cacdo:TranshipmentTransportDetails', True)
        ts_list = get_nodes(t_transport, 'cacdo:TransportMeansRegistrationIdDetails', True)
        _count_ts = len(ts_list)
        transhipment.TransportMeansQuantity = _count_ts
        if _count_ts > 2:
            transhipment.UnifiedTransportModeCode = 32
        elif _count_ts == 2:
            transhipment.UnifiedTransportModeCode = 31
        else:
            transhipment.UnifiedTransportModeCode = 30

        transhipment.RegistrationNationalityCode = get_attr_node(
            get_node(ts_list[0], 'csdo:TransportMeansRegId'),
            'countryCode'
        )

        try:
            transhipment.save()
        except Exception as e:
            messages.append('Не удалось сохранить перецепку/перегрузку в XML. Ошибка: ' + str(e))
            continue

        # транспорт в перецепке
        for _transport in ts_list:
            transport_transhipment = TransportTranshipment()
            _ct = get_node(_transport, 'csdo:TransportMeansRegId', True)
            transport_transhipment.TransportMeansRegId = get_text_node(_ct)
            transport_transhipment.countryCode = get_attr_node(_ct, 'countryCode')
            transport_transhipment.TransportTypeCode = get_text_from_child_node(_transport, 'casdo:TransportTypeCode', True)
            transport_transhipment.transhipment_xml = transhipment
            try:
                transport_transhipment.save()
            except Exception as e:
                messages.append(
                    'Не удалось сохранить транспорт в перецепке/перегрузке в XML. Ошибка: ' + str(e))
                continue
        # end транспорт в перецепке

        # контейнеры в перецепке
        for _container in get_nodes(_t, 'casdo:ContainerId'):
            container_transhipment = ContainerTranshipment()
            container_transhipment.ContainerId = get_text_node(_container)
            container_transhipment.transhipment_xml = transhipment
            try:
                container_transhipment.save()
            except Exception as e:
                messages.append('Не удалось сохранить контейнер в перецепке/перегрузке в XML. Ошибка: ' + str(e))
                continue
        # end контейнеры в перецепке
    # end перецепки в xml

    # гарантии в xml
    for _g in get_nodes(decl_goods, 'cacdo:TransitGuaranteeDetails', True):
        guarantee = TransitGuarantee()
        guarantee.TransitGuaranteeMeasureCode = get_text_from_child_node(_g, 'casdo:TransitGuaranteeMeasureCode', True)
        _amount = get_node(_g, 'casdo:GuaranteeAmount')
        guarantee.GuaranteeAmount = get_text_node(_amount)
        guarantee.currencyCode = get_attr_node(_amount, 'currencyCode')
        _gc = get_node(_g, 'cacdo:TransitGuaranteeDocDetails')
        if _gc is not None:
            if guarantee.TransitGuaranteeMeasureCode == '03':
                # если в гарантии сертификат, сохраняем его как и в PIAT
                _docid = get_text_from_child_node(_gc, 'csdo:DocId', True).split('/')
                if len(_docid) != 3:
                    messages.append('Не удалось сохранить гарантии в XML. Ошибка: ' + str(e))
                guarantee.GC_CustomsOfficeCode = _docid[0]
                guarantee.GC_DocCreationDate = get_text_from_child_node(_gc, 'csdo:DocCreationDate', True)
                guarantee.GC_CustomsDocumentId = _docid[2]
            else:
                # если указан документ, но тип не 03 - то сохраняем номер и дату
                guarantee.RD_RegistrationNumberId = get_text_from_child_node(_gc, 'csdo:DocId', True)
                guarantee.GC_DocCreationDate = get_text_from_child_node(_gc, 'csdo:DocCreationDate', True)

        guarantee.ES_SubjectBriefName = get_text_from_child_node(_g, 'csdo:SubjectBriefName')
        guarantee.ES_TaxpayerId = get_text_from_child_node(_g, 'csdo:TaxpayerId')
        guarantee.ES_BankId = get_text_from_child_node(_g, 'csdo:BankId')
        guarantee.xml = xmlmodel
        try:
            guarantee.save()
        except Exception as e:
            messages.append('Не удалось сохранить гарантии в XML. Ошибка: ' + str(e))
            continue
    # end гарантии в xml

    # товар и все что в нем
    for _tovar in get_nodes(decl_goods, 'cacdo:DeclarationGoodsItemDetails', True):
        # товар
        cons_item = ConsignmentItem()
        cons_item.ConsignmentItemOrdinal = get_text_from_child_node(_tovar, 'casdo:ConsignmentItemOrdinal', True)
        cons_item.CommodityCode = get_text_from_child_node(_tovar, 'csdo:CommodityCode', True)
        _i = 0
        for _descr in get_nodes(_tovar, 'casdo:GoodsDescriptionText', True):
            if _i == 0:
                cons_item.GoodsDescriptionText = get_text_node(_descr)
            elif _i == 1:
                cons_item.GoodsDescriptionText1 = get_text_node(_descr)
            elif _i == 2:
                cons_item.GoodsDescriptionText2 = get_text_node(_descr)
            else:
                cons_item.GoodsDescriptionText3 = get_text_node(_descr)
            _i += 1
        _gm = get_node(_tovar, 'csdo:UnifiedGrossMassMeasure', True)
        cons_item.UnifiedGrossMassMeasure = get_text_node(_gm)
        cons_item.measurementUnitCode = get_attr_node(_gm, 'measurementUnitCode')

        gm = get_node(_tovar, 'cacdo:GoodsMeasureDetails')
        if gm is not None:
            _gm = get_node(gm, 'casdo:GoodsMeasure', True)
            cons_item.GM_GoodsMeasure = get_text_node(_gm)
            cons_item.GM_measurementUnitCode = get_attr_node(_gm, 'measurementUnitCode')
            cons_item.GM_MeasureUnitAbbreviationCode = get_text_from_child_node(gm, 'casdo:MeasureUnitAbbreviationCode', True)

        cons_item.GoodsTraceabilityCode = get_text_from_child_node(_tovar, 'casdo:GoodsTraceabilityCode')
        cons_item.LicenseGoodsKindCode = get_text_from_child_node(_tovar, 'casdo:LicenseGoodsKindCode')

        gm = get_node(_tovar, 'cacdo:AddGoodsMeasureDetails')
        if gm is not None:
            _gm = get_node(gm, 'casdo:GoodsMeasure', True)
            cons_item.AGM_GoodsMeasure = get_text_node(_gm)
            cons_item.AGM_measurementUnitCode = get_attr_node(_gm, 'measurementUnitCode')
            cons_item.AGM_MeasureUnitAbbreviationCode = get_text_from_child_node(gm, 'casdo:MeasureUnitAbbreviationCode', True)

        _cargo_package = get_node(_tovar, 'cacdo:CargoPackagePalletDetails', True)
        cons_item.CargoQuantity = get_text_from_child_node(_cargo_package, 'casdo:CargoQuantity', True)

        _package_details = get_node(_cargo_package, 'cacdo:PackagePalletDetails', True)
        cons_item.CargoPackageInfoKindCode = get_text_from_child_node(_package_details, 'casdo:CargoPackageInfoKindCode', True)
        cons_item.PackageKindCode = get_text_from_child_node(_package_details, 'csdo:PackageKindCode', True)
        cons_item.PackageQuantity = cons_item.CargoQuantity

        gm = get_node(_tovar, 'cacdo:GoodsTraceabilityMeasureDetails')
        if gm is not None:
            _gm = get_node(gm, 'casdo:GoodsMeasure', True)
            cons_item.TM_GoodsMeasure = get_text_node(_gm)
            cons_item.TM_measurementUnitCode = get_attr_node(_gm, 'measurementUnitCode')
            cons_item.TM_MeasureUnitAbbreviationCode = get_text_from_child_node(gm, 'casdo:MeasureUnitAbbreviationCode', True)

        _value = get_node(_tovar, 'casdo:CAValueAmount', True)
        cons_item.CAValueAmount = get_text_node(_value)
        cons_item.currencyCode = get_attr_node(_value, 'currencyCode')

        _value = get_node(_tovar, 'casdo:CustomsValueAmount', True)
        cons_item.CustomsValueAmount = get_text_node(_value)
        cons_item.CV_currencyCode = get_attr_node(_value, 'currencyCode')

        cons_item.xml = xmlmodel

        try:
            cons_item.save()
        except Exception as e:
            messages.append('Не удалось сохранить товар. Ошибка: ' + str(e))
            continue
        # end товар

        # предшедствующие доки
        for _prec_doc in get_nodes(_tovar, 'cacdo:PrecedingDocDetails'):
            preceding_doc = PIPrecedingDocDetails()
            preceding_doc.DocKindCode = get_text_from_child_node(_prec_doc, 'csdo:DocKindCode', True)
            _doc_detail = get_node(_prec_doc, 'cacdo:CustomsDocIdDetails', True)
            preceding_doc.DocCreationDate = get_text_from_child_node(_doc_detail, 'csdo:DocCreationDate', True)
            preceding_doc.DocId = get_text_from_child_node(_doc_detail, 'csdo:CustomsOfficeCode', True) + '/' + get_serifikat_date(preceding_doc.DocCreationDate) + '/' + get_text_from_child_node(_doc_detail, 'casdo:CustomsDocumentId', True)
            preceding_doc.ConsignmentItemOrdinal = get_text_from_child_node(_prec_doc, 'casdo:ConsignmentItemOrdinal', True)


            preceding_doc.ci = cons_item
            try:
                preceding_doc.save()
            except Exception as e:
                messages.append('Не удалось сохранить предшедствующий документ. Ошибка: ' + str(e))
                continue
        # end предшедствующие доки

        # документы
        for _doc in get_nodes(_tovar, 'cacdo:PresentedDocDetails', True):
            goods_doc = PIGoodsDocDetails()
            goods_doc.DocKindCode = get_text_from_child_node(_doc, 'csdo:DocKindCode', True)
            goods_doc.DocId = get_text_from_child_node(_doc, 'csdo:DocId', True)
            goods_doc.DocCreationDate = get_text_from_child_node(_doc, 'csdo:DocCreationDate', True)
            goods_doc.ci = cons_item
            try:
                goods_doc.save()
                # если 1-ый товар и документ это цмр - сохраним как транспортный документ
                if goods_doc.DocKindCode == '02015' and cons_item.ConsignmentItemOrdinal == '1':
                    # транспортный документ
                    xmlmodel.TD_DocKindCode = goods_doc.DocKindCode
                    xmlmodel.TD_DocId = goods_doc.DocId
                    xmlmodel.TD_DocCreationDate = goods_doc.DocCreationDate
                    # end транспортный документ
                    try:
                        xmlmodel.save()
                    except Exception as e:
                        messages.append('Не удалось сохранить транспортный документ для XML ТД. Ошибка: ' + str(e))
                # ***********************************************************************
            except Exception as e:
                messages.append('Не удалось сохранить документ для товара. Ошибка: ' + str(e))
                continue
        # end документы

        # контейнеры в товаре
        for _cont in get_nodes(_tovar, 'cacdo:ContainerListDetails'):
            cont_ci = ContainerCI()
            cont_ci.ContainerId = get_text_from_child_node(
                get_node(_cont, 'cacdo:ContainerDetails'),
                'casdo:ContainerId',
                True
            )
            cont_ci.ci = cons_item
            try:
                cont_ci.save()
            except Exception as e:
                messages.append('Не удалось сохранить контейнер для товара. Ошибка: ' + str(e))
                continue
        # end контейнеры в товаре
        # end товар и все что в нем

    return {
        'id': xmlmodel.pk,
        'messages': messages,
    }
