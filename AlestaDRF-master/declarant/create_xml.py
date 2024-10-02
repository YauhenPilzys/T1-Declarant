import datetime
from io import BytesIO

from .alesta_functions import dt_to_xml_format
from .models import *
from lxml.builder import ElementMaker
import lxml.etree as etree
from lxml.builder import E

import logging

code_list = {
    'country': '2021',
    'ts': '2004',
    'ts_type': '2024',
    'ts_make': '2025',
    'measure': '2016',
    'doc_type': '2009',
    'currency': '2022',
    'pack': '2013',
    'guarantee': '2017',
    'doc_kind': '2053',
}

logger2 = logging.getLogger(__name__)
logger2.setLevel(logging.INFO)

# настройка обработчика и форматировщика для logger2
handler2 = logging.FileHandler(f"{__name__}.log", mode='a')
formatter2 = logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s")

# добавление форматировщика к обработчику
handler2.setFormatter(formatter2)
# добавление обработчика к логгеру
logger2.addHandler(handler2)


def xml_from_db(xml_id, flag_file=False):
    """
    Выгружаем xml из базы данных. Результат: текст с содержимым xml или файл (зависит от параметра flag_file).
    Тип (эпи или тд) определяется на основе поля в БД.
    """
    xml_model = XMLModel.objects.get(pk=xml_id)
    nsmap_obj = NsMap.objects.filter(xml_type=xml_model.XmlType, date_end__gte=datetime.date.today())

    xml_nsmap = dict(
        zip(
            list(nsmap_obj.values_list("name_field", flat=True)),
            list(nsmap_obj.values_list("text_field", flat=True))
        )
    )

    def addE(parent, pref, tag, value, **kwargs):
        """
            Добавляем в элемент parent элемент вида <pref:tag kwargs>value</pref:tag>
        """
        if value is not None:
            if type(value) != 'str':
                value = str(value)
        if (value is not None) and (value != ''):
            parent.append(E(
                etree.QName(xml_nsmap[pref], tag),
                value,
                kwargs
            ))

    try:
        schemaLocation = xml_nsmap.pop('schemaLocation')
    except:
        logger2.error('В таблице nsmap не найден действующий атрибут schemaLocation!')

    NS = ElementMaker(nsmap=xml_nsmap)
    sl = str(etree.QName(xml_nsmap['xsi'], "schemaLocation"))
    d = dict(zip([sl], [schemaLocation]))

    if xml_model.XmlType == 'PIAT':
        # формирование ЭПИ
        my_doc = NS(
            etree.QName(xml_nsmap['atpi'], "AutoPreliminaryInformation"),
            **d,
        )
        addE(my_doc, 'csdo', 'EDocCode', xml_model.EDocCode)
        addE(my_doc, 'csdo', 'EDocId', xml_model.EDocId)
        addE(my_doc, 'csdo', 'EDocDateTime', dt_to_xml_format(xml_model.EDocDateTime))
        addE(my_doc, 'casdo', 'EDocIndicatorCode', xml_model.EDocIndicatorCode)
        addE(my_doc, 'casdo', 'PreliminaryInformationUsageCode', xml_model.PreliminaryInformationUsageCode1)
        addE(my_doc, 'casdo', 'PreliminaryInformationUsageCode', xml_model.PreliminaryInformationUsageCode2)
        addE(my_doc, 'casdo', 'PreliminaryInformationUsageCode', xml_model.PreliminaryInformationUsageCode3)

        # пто отправления
        ptoin = E(etree.QName(xml_nsmap['cacdo'], 'PIATEntryCheckPointDetails'))
        addE(ptoin, 'csdo', 'CustomsOfficeCode', xml_model.ECP_CustomsOfficeCode)
        addE(ptoin, 'csdo', 'BorderCheckpointName', xml_model.ECP_BorderCheckpointName)
        my_doc.append(ptoin)
        # END пто отправления

        # декларант ПИ
        pideclarant = E(etree.QName(xml_nsmap['cacdo'], 'PIDeclarantDetails'))
        addE(pideclarant, 'csdo', 'SubjectBriefName', xml_model.PIDeclarant_SubjectBriefName)
        addE(pideclarant, 'csdo', 'TaxpayerId', xml_model.PIDeclarant_TaxpayerId)

        address = E(etree.QName(xml_nsmap['ccdo'], 'SubjectAddressDetails'))
        addE(address, 'csdo', 'AddressKindCode', '1')
        addE(address, 'csdo', 'UnifiedCountryCode', xml_model.PIDeclarant_UnifiedCountryCode,
             codeListId=code_list['country'])
        addE(address, 'csdo', 'RegionName', xml_model.PIDeclarant_RegionName)
        addE(address, 'csdo', 'CityName', xml_model.PIDeclarant_CityName)
        addE(address, 'csdo', 'StreetName', xml_model.PIDeclarant_StreetName)
        addE(address, 'csdo', 'BuildingNumberId', xml_model.PIDeclarant_BuildingNumberId)
        addE(address, 'csdo', 'RoomNumberId', xml_model.PIDeclarant_RoomNumberId)
        pideclarant.append(address)

        regdoc = E(etree.QName(xml_nsmap['cacdo'], 'RegisterDocumentIdDetails'))
        addE(regdoc, 'casdo', 'RegistrationNumberId', xml_model.PIDeclarant_RegistrationNumberId)
        pideclarant.append(regdoc)

        addE(pideclarant, 'casdo', 'EqualIndicator', '0')
        my_doc.append(pideclarant)
        # END декларант ПИ

        # тс на границе
        border_ts = E(etree.QName(xml_nsmap['cacdo'], 'PIATBorderTransportDetails'))
        ts = TransportXML.objects.filter(xml=xml_model)
        addE(
            border_ts,
            'csdo',
            'UnifiedTransportModeCode',
            xml_model.UnifiedTransportModeCode,
            codeListId=code_list['ts']
        )
        count_ts = xml_model.TransportMeansQuantity
        if (count_ts is None) or (count_ts == ''):
            count_ts = len(ts)
        addE(border_ts, 'casdo', 'TransportMeansQuantity', count_ts)
        addE(border_ts, 'casdo', 'ContainerIndicator', xml_model.ContainerIndicator)
        for i in range(count_ts):
            if i == 0:  # тягач
                parent_elem = border_ts
            else:  # прицеп
                trailer = E(etree.QName(xml_nsmap['cacdo'], 'TrailerDetails'))
                parent_elem = trailer
            addE(
                parent_elem,
                'csdo',
                'TransportMeansRegId',
                ts[i].TransportMeansRegId,
                countryCodeListId=code_list['country'],
                countryCode=ts[i].countryCode
            )
            addE(parent_elem, 'csdo', 'VehicleId', ts[i].VehicleId)
            addE(
                parent_elem,
                'casdo',
                'TransportTypeCode',
                ts[i].TransportTypeCode,
                codeListId=code_list['ts_type']
            )
            addE(
                parent_elem,
                'csdo',
                'VehicleMakeCode',
                ts[i].VehicleMakeCode,
                codeListId=code_list['ts_make']
            )
            addE(parent_elem, 'csdo', 'VehicleMakeName', ts[i].VehicleMakeName)
            addE(parent_elem, 'casdo', 'VehicleModelName', ts[i].VehicleModelName)

            if i != 0:
                border_ts.append(trailer)
        my_doc.append(border_ts)
        # END тс на границе

        # блок main
        main = E(etree.QName(xml_nsmap['cacdo'], 'PIATMainConsignmentDetails'))

        # инфа о TIR
        addE(main, 'casdo', 'TIRCarnetIndicator', xml_model.TIRCarnetIndicator)
        if xml_model.TIRCarnetIndicator == '1':
            tir = E(etree.QName(xml_nsmap['cacdo'], 'TIRCarnetIdDetails'))
            addE(tir, 'casdo', 'TIRSeriesId', xml_model.TIRSeriesId)
            addE(tir, 'casdo', 'TIRId', xml_model.TIRId)
            addE(tir, 'casdo', 'TIRPageOrdinal', xml_model.TIRPageOrdinal)
            addE(tir, 'casdo', 'TIRHolderId', xml_model.TIRHolderId)
            main.append(tir)
        # END инфа о TIR

        addE(main, 'casdo', 'DeclarationKindCode', xml_model.DeclarationKindCode)
        addE(main, 'casdo', 'TransitProcedureCode', xml_model.TransitProcedureCode)
        addE(main, 'casdo', 'TransitFeatureCode', xml_model.TransitFeatureCode)
        addE(main, 'casdo', 'LoadingListsQuantity', xml_model.LoadingListsQuantity)
        addE(main, 'casdo', 'LoadingListsPageQuantity', xml_model.LoadingListsPageQuantity)
        addE(main, 'casdo', 'GoodsQuantity', xml_model.GoodsQuantity)
        addE(main, 'casdo', 'CargoQuantity', xml_model.CargoQuantity)

        # пломбы
        if (xml_model.SealQuantity != 0) and (xml_model.SealQuantity is not None):
            seal = E(etree.QName(xml_nsmap['cacdo'], 'SealDetails'))
            addE(seal, 'casdo', 'SealQuantity', str(xml_model.SealQuantity))
            for _s in xml_model.SealId.split(','):
                addE(seal, 'csdo', 'SealId', _s)
            main.append(seal)
        # END пломбы

        # транспортные средства (транзит)
        ts_tranzit = E(etree.QName(xml_nsmap['cacdo'], 'PITransitTransportMeansDetails'))
        addE(ts_tranzit, 'casdo', 'EqualIndicator', xml_model.Transport_EqualIndicator)
        addE(
            ts_tranzit,
            'csdo',
            'UnifiedTransportModeCode',
            xml_model.UnifiedTransportModeCode,
            codeListId=code_list['ts']
        )
        count_ts = xml_model.TransportMeansQuantity
        if (count_ts is None) or (count_ts == ''):
            count_ts = len(ts)
        addE(ts_tranzit, 'casdo', 'TransportMeansQuantity', count_ts)
        for i in range(count_ts):
            parent_elem = E(etree.QName(xml_nsmap['cacdo'], 'TransportMeansRegistrationIdDetails'))
            addE(
                parent_elem,
                'csdo',
                'TransportMeansRegId',
                ts[i].TransportMeansRegId,
                countryCodeListId=code_list['country'],
                countryCode=ts[i].countryCode
            )
            addE(parent_elem, 'csdo', 'VehicleId', ts[i].VehicleId)
            addE(
                parent_elem,
                'casdo',
                'TransportTypeCode',
                ts[i].TransportTypeCode,
                codeListId=code_list['ts_type']
            )
            addE(
                parent_elem,
                'csdo',
                'VehicleMakeCode',
                ts[i].VehicleMakeCode,
                codeListId=code_list['ts_make']
            )
            ts_tranzit.append(parent_elem)

        main.append(ts_tranzit)
        # END транспортные средства (транзит)

        # пто назначения
        tt = E(etree.QName(xml_nsmap['cacdo'], 'TransitTerminationDetails'))

        customs = E(etree.QName(xml_nsmap['ccdo'], 'CustomsOfficeDetails'))
        addE(customs, 'csdo', 'CustomsOfficeCode', xml_model.TT_CustomsOfficeCode)
        addE(customs, 'csdo', 'CustomsOfficeName', xml_model.TT_CustomsOfficeName)
        tt.append(customs)

        addE(tt, 'casdo', 'CustomsControlZoneId', xml_model.TT_CustomsControlZoneId)
        main.append(tt)
        # END пто назначения

        # перецепки
        transhipment = Transhipment.objects.filter(xml=xml_model)
        for _t in transhipment:
            tr_elem = E(etree.QName(xml_nsmap['cacdo'], 'PITranshipmentDetails'))
            addE(tr_elem, 'casdo', 'CargoOperationKindCode', _t.CargoOperationKindCode)
            addE(tr_elem, 'casdo', 'ContainerIndicator', _t.ContainerIndicator)
            addE(
                tr_elem,
                'casdo',
                'CACountryCode',
                _t.CACountryCode,
                codeListId=code_list['country']
            )
            addE(tr_elem, 'casdo', 'ShortCountryName', _t.ShortCountryName)
            addE(tr_elem, 'casdo', 'PlaceName', _t.PlaceName)

            if ((_t.CustomsOfficeCode is not None) and (_t.CustomsOfficeCode != '')) or (
                    (_t.CustomsOfficeName is not None) and (_t.CustomsOfficeName != '')):
                customs = E(etree.QName(xml_nsmap['ccdo'], 'CustomsOfficeDetails'))
                addE(customs, 'csdo', 'CustomsOfficeCode', _t.CustomsOfficeCode)
                addE(customs, 'csdo', 'CustomsOfficeName', _t.CustomsOfficeName)
                tr_elem.append(customs)

            # транспорт в перецепке
            transhipment_ts = TransportTranshipment.objects.filter(transhipment_xml=_t)
            if len(transhipment_ts) > 0:
                tr_ts_elem = E(etree.QName(xml_nsmap['cacdo'], 'TranshipmentTransportDetails'))
                addE(
                    tr_ts_elem,
                    'csdo',
                    'UnifiedTransportModeCode',
                    _t.UnifiedTransportModeCode,
                    codeListId=code_list['ts']
                )
                addE(
                    tr_ts_elem,
                    'casdo',
                    'RegistrationNationalityCode',
                    _t.RegistrationNationalityCode,
                    codeListId=code_list['country']
                )
                addE(tr_ts_elem, 'casdo', 'TransportMeansQuantity', _t.TransportMeansQuantity)

                for _ts in transhipment_ts:
                    parent_elem = E(etree.QName(xml_nsmap['cacdo'], 'TransportMeansRegistrationIdDetails'))
                    addE(
                        parent_elem,
                        'csdo',
                        'TransportMeansRegId',
                        _ts.TransportMeansRegId,
                        countryCodeListId=code_list['country'],
                        countryCode=_ts.countryCode
                    )
                    addE(
                        parent_elem,
                        'casdo',
                        'TransportTypeCode',
                        _ts.TransportTypeCode,
                        codeListId=code_list['ts_type']
                    )
                    tr_ts_elem.append(parent_elem)

                tr_elem.append(tr_ts_elem)
            # END транспорт в перецепке

            # контейнеры в перецепке
            containers = ContainerTranshipment.objects.filter(transhipment_xml=_t)
            if len(containers) > 0:
                for _c in containers:
                    addE(tr_elem, 'casdo', 'ContainerId', _c.ContainerId)
            # END контейнеры в перецепке

            main.append(tr_elem)
        # end перецепки

        # блок consigment
        consigment = E(etree.QName(xml_nsmap['cacdo'], 'PIATConsignmentDetails'))

        # транспортный документ
        transport_doc = E(etree.QName(xml_nsmap['cacdo'], 'PIATTransportDocumentDetails'))
        addE(
            transport_doc,
            'csdo',
            'DocKindCode',
            xml_model.TD_DocKindCode,
            codeListId=code_list['doc_type']
        )
        addE(transport_doc, 'csdo', 'DocId', xml_model.TD_DocId)
        addE(transport_doc, 'csdo', 'DocCreationDate', xml_model.TD_DocCreationDate)
        consigment.append(transport_doc)
        # END транспортный документ

        addE(consigment, 'casdo', 'CargoQuantity', xml_model.CargoQuantity)

        # страна отправления
        сountry = E(etree.QName(xml_nsmap['cacdo'], 'DepartureCountryDetails'))
        addE(
            сountry,
            'casdo',
            'CACountryCode',
            xml_model.DepartureCountry_CACountryCode,
            codeListId=code_list['country']
        )
        addE(сountry, 'casdo', 'ShortCountryName', xml_model.DepartureCountry_ShortCountryName)
        consigment.append(сountry)
        # END страна отправления

        # страна назначения
        сountry = E(etree.QName(xml_nsmap['cacdo'], 'DestinationCountryDetails'))
        addE(
            сountry,
            'casdo',
            'CACountryCode',
            xml_model.DestinationCountry_CACountryCode,
            codeListId=code_list['country']
        )
        addE(сountry, 'casdo', 'ShortCountryName', xml_model.DestinationCountry_ShortCountryName)
        consigment.append(сountry)
        # END страна назначения

        # общая стоимость
        addE(
            consigment,
            'casdo',
            'CAInvoiceValueAmount',
            xml_model.CAInvoiceValueAmount,
            currencyCodeListId=code_list['currency'],
            currencyCode=xml_model.IVA_currencyCode
        )

        # общий вес
        addE(
            consigment,
            'csdo',
            'UnifiedGrossMassMeasure',
            xml_model.UnifiedGrossMassMeasure,
            measurementUnitCodeListId=code_list['measure'],
            measurementUnitCode=xml_model.measurementUnitCode
        )

        # отправитель
        consignor = E(etree.QName(xml_nsmap['cacdo'], 'PIATConsignorDetails'))
        addE(consignor, 'csdo', 'SubjectBriefName', xml_model.Consignor_SubjectBriefName)
        addE(consignor, 'csdo', 'TaxpayerId', xml_model.Consignor_TaxpayerId)

        address = E(etree.QName(xml_nsmap['ccdo'], 'SubjectAddressDetails'))
        addE(address, 'csdo', 'AddressKindCode', '1')
        addE(address, 'csdo', 'UnifiedCountryCode', xml_model.Consignor_UnifiedCountryCode,
             codeListId=code_list['country'])
        addE(address, 'csdo', 'RegionName', xml_model.Consignor_RegionName)
        addE(address, 'csdo', 'CityName', xml_model.Consignor_CityName)
        addE(address, 'csdo', 'StreetName', xml_model.Consignor_StreetName)
        addE(address, 'csdo', 'BuildingNumberId', xml_model.Consignor_BuildingNumberId)
        addE(address, 'csdo', 'RoomNumberId', xml_model.Consignor_RoomNumberId)
        consignor.append(address)

        consigment.append(consignor)
        # END отправитель

        # получатель
        consignee = E(etree.QName(xml_nsmap['cacdo'], 'PIATConsigneeDetails'))
        addE(consignee, 'csdo', 'SubjectBriefName', xml_model.Consignee_SubjectBriefName)
        addE(consignee, 'csdo', 'TaxpayerId', xml_model.Consignee_TaxpayerId)

        address = E(etree.QName(xml_nsmap['ccdo'], 'SubjectAddressDetails'))
        addE(address, 'csdo', 'AddressKindCode', '1')
        addE(address, 'csdo', 'UnifiedCountryCode', xml_model.Consignee_UnifiedCountryCode,
             codeListId=code_list['country'])
        addE(address, 'csdo', 'RegionName', xml_model.Consignee_RegionName)
        addE(address, 'csdo', 'CityName', xml_model.Consignee_CityName)
        addE(address, 'csdo', 'StreetName', xml_model.Consignee_StreetName)
        addE(address, 'csdo', 'BuildingNumberId', xml_model.Consignee_BuildingNumberId)
        addE(address, 'csdo', 'RoomNumberId', xml_model.Consignee_RoomNumberId)
        consignee.append(address)

        consigment.append(consignee)
        # END получатель

        # контейнеры в XML
        cont_xml = ContainerXML.objects.filter(xml=xml_model)
        if len(cont_xml) > 0:
            for _c in cont_xml:
                cont = E(etree.QName(xml_nsmap['cacdo'], 'PIContainerDetails'))
                addE(cont, 'casdo', 'ContainerId', _c.ContainerId)
                consigment.append(cont)
        # END контейнеры в XML

        # товары
        consigment_items = ConsignmentItem.objects.filter(xml=xml_model)
        if len(consigment_items) > 0:
            for _ci in consigment_items:
                cons_item = E(etree.QName(xml_nsmap['cacdo'], 'PIATConsignmentItemDetails'))
                addE(cons_item, 'casdo', 'ConsignmentItemOrdinal', _ci.ConsignmentItemOrdinal)
                addE(cons_item, 'csdo', 'CommodityCode', _ci.CommodityCode)
                addE(cons_item, 'casdo', 'GoodsDescriptionText', _ci.GoodsDescriptionText)
                addE(cons_item, 'casdo', 'GoodsDescriptionText', _ci.GoodsDescriptionText1)
                addE(cons_item, 'casdo', 'GoodsDescriptionText', _ci.GoodsDescriptionText2)
                addE(cons_item, 'casdo', 'GoodsDescriptionText', _ci.GoodsDescriptionText3)
                addE(
                    cons_item,
                    'csdo',
                    'UnifiedGrossMassMeasure',
                    _ci.UnifiedGrossMassMeasure,
                    measurementUnitCodeListId=code_list['measure'],
                    measurementUnitCode=_ci.measurementUnitCode,
                )

                if (_ci.GM_GoodsMeasure is not None) and (_ci.GM_GoodsMeasure != ''):
                    gm = E(etree.QName(xml_nsmap['cacdo'], 'GoodsMeasureDetails'))
                    addE(
                        gm,
                        'casdo',
                        'GoodsMeasure',
                        _ci.GM_GoodsMeasure,
                        measurementUnitCodeListId=code_list['measure'],
                        measurementUnitCode=_ci.GM_measurementUnitCode,
                    )
                    addE(gm, 'casdo', 'MeasureUnitAbbreviationCode', _ci.GM_MeasureUnitAbbreviationCode)
                    cons_item.append(gm)

                if (_ci.AGM_GoodsMeasure is not None) and (_ci.AGM_GoodsMeasure != ''):
                    gm = E(etree.QName(xml_nsmap['cacdo'], 'AddGoodsMeasureDetails'))
                    addE(
                        gm,
                        'casdo',
                        'GoodsMeasure',
                        _ci.AGM_GoodsMeasure,
                        measurementUnitCodeListId=code_list['measure'],
                        measurementUnitCode=_ci.AGM_measurementUnitCode,
                    )
                    addE(gm, 'casdo', 'MeasureUnitAbbreviationCode', _ci.AGM_MeasureUnitAbbreviationCode)
                    cons_item.append(gm)

                # упаковка и места
                cargo_package = E(etree.QName(xml_nsmap['cacdo'], 'CargoPackagePalletDetails'))
                addE(cargo_package, 'casdo', 'PackageAvailabilityCode', _ci.PackageAvailabilityCode)
                addE(cargo_package, 'casdo', 'CargoQuantity', _ci.CargoQuantity)

                package_details = E(etree.QName(xml_nsmap['cacdo'], 'PackagePalletDetails'))
                addE(package_details, 'casdo', 'CargoPackageInfoKindCode', _ci.CargoPackageInfoKindCode)
                addE(
                    package_details,
                    'csdo',
                    'PackageKindCode',
                    _ci.PackageKindCode,
                    codeListId=code_list['pack']
                )
                addE(package_details, 'csdo', 'PackageQuantity', _ci.PackageQuantity)
                cargo_package.append(package_details)

                cons_item.append(cargo_package)
                # END упаковка и места

                # контейнеры в товаре
                cont_ci = ContainerCI.objects.filter(ci=_ci)
                if len(cont_ci) > 0:
                    for _c in cont_ci:
                        cont = E(etree.QName(xml_nsmap['cacdo'], 'PIContainerDetails'))
                        addE(cont, 'casdo', 'ContainerId', _c.ContainerId)
                        cons_item.append(cont)
                # END контейнеры в товаре

                addE(
                    cons_item,
                    'casdo',
                    'CAValueAmount',
                    _ci.CAValueAmount,
                    currencyCodeListId=code_list['currency'],
                    currencyCode=_ci.currencyCode,
                )

                # предшедствующие документы
                doc = PIPrecedingDocDetails.objects.filter(ci=_ci)
                if len(doc) > 0:
                    for _d in doc:
                        doc_item = E(etree.QName(xml_nsmap['cacdo'], 'PIPrecedingDocDetails'))
                        addE(
                            doc_item,
                            'csdo',
                            'DocKindCode',
                            _d.DocKindCode,
                            codeListId=code_list['doc_type']
                        )
                        addE(doc_item, 'csdo', 'DocId', _d.DocId)
                        addE(doc_item, 'csdo', 'DocCreationDate', _d.DocCreationDate)
                        cons_item.append(doc_item)
                # END предшедствующие документы

                # документы
                doc = PIGoodsDocDetails.objects.filter(ci=_ci)
                if len(doc) > 0:
                    for _d in doc:
                        doc_item = E(etree.QName(xml_nsmap['cacdo'], 'PIGoodsDocDetails'))
                        addE(
                            doc_item,
                            'csdo',
                            'DocKindCode',
                            _d.DocKindCode,
                            codeListId=code_list['doc_type']
                        )
                        addE(doc_item, 'csdo', 'DocId', _d.DocId)
                        addE(doc_item, 'csdo', 'DocCreationDate', _d.DocCreationDate)
                        cons_item.append(doc_item)
                # END документы

                consigment.append(cons_item)
        # END товары

        main.append(consigment)
        # END блок consigment

        # гарантии
        guarantee_list = TransitGuarantee.objects.filter(xml=xml_model)
        if len(guarantee_list) > 0:
            for _g in guarantee_list:
                tg_item = E(etree.QName(xml_nsmap['cacdo'], 'TransitGuaranteeDetails'))
                addE(
                    tg_item,
                    'casdo',
                    'TransitGuaranteeMeasureCode',
                    _g.TransitGuaranteeMeasureCode,
                    codeListId=code_list['guarantee']
                )
                addE(
                    tg_item,
                    'casdo',
                    'GuaranteeAmount',
                    _g.GuaranteeAmount,
                    currencyCodeListId=code_list['currency'],
                    currencyCode=_g.currencyCode
                )
                if (_g.GC_CustomsDocumentId is not None) and (_g.GC_CustomsDocumentId != ''):
                    sert = E(etree.QName(xml_nsmap['cacdo'], 'GuaranteeCertificateIdDetails'))
                    addE(sert, 'csdo', 'CustomsOfficeCode', _g.GC_CustomsOfficeCode)
                    addE(sert, 'csdo', 'DocCreationDate', _g.GC_DocCreationDate)
                    addE(sert, 'casdo', 'CustomsDocumentId', _g.GC_CustomsDocumentId)
                    tg_item.append(sert)

                if (_g.RD_RegistrationNumberId is not None) and (_g.RD_RegistrationNumberId != ''):
                    reg_doc = E(etree.QName(xml_nsmap['cacdo'], 'RegisterDocumentIdDetails'))
                    addE(
                        reg_doc,
                        'csdo',
                        'UnifiedCountryCode',
                        _g.RD_UnifiedCountryCode,
                        codeListId=code_list['country']
                    )
                    addE(reg_doc, 'casdo', 'RegistrationNumberId', _g.RD_RegistrationNumberId)
                    tg_item.append(reg_doc)
                addE(tg_item, 'csdo', 'SubjectBriefName', _g.ES_SubjectBriefName)
                addE(tg_item, 'csdo', 'TaxpayerId', _g.ES_TaxpayerId)
                addE(tg_item, 'csdo', 'BankId', _g.ES_BankId)

                main.append(tg_item)
        # END гарантии

        # декларант транзита
        tr_decl = E(etree.QName(xml_nsmap['cacdo'], 'PITransitDeclarantDetails'))
        addE(tr_decl, 'csdo', 'SubjectBriefName', xml_model.TransitDeclarant_SubjectBriefName)
        addE(tr_decl, 'csdo', 'TaxpayerId', xml_model.TransitDeclarant_TaxpayerId)

        address = E(etree.QName(xml_nsmap['ccdo'], 'SubjectAddressDetails'))
        addE(address, 'csdo', 'AddressKindCode', '1')
        addE(address, 'csdo', 'UnifiedCountryCode', xml_model.TransitDeclarant_UnifiedCountryCode,
             codeListId=code_list['country'])
        addE(address, 'csdo', 'RegionName', xml_model.TransitDeclarant_RegionName)
        addE(address, 'csdo', 'CityName', xml_model.TransitDeclarant_CityName)
        addE(address, 'csdo', 'StreetName', xml_model.TransitDeclarant_StreetName)
        addE(address, 'csdo', 'BuildingNumberId', xml_model.TransitDeclarant_BuildingNumberId)
        addE(address, 'csdo', 'RoomNumberId', xml_model.TransitDeclarant_RoomNumberId)
        tr_decl.append(address)

        addE(tr_decl, 'casdo', 'EqualIndicator', xml_model.TransitDeclarant_EqualIndicator)
        main.append(tr_decl)
        # END декларант транзита

        # перевозчик по ТТ ЕАЭС
        union_carrier = E(etree.QName(xml_nsmap['cacdo'], 'PIUnionCarrierDetails'))
        addE(union_carrier, 'csdo', 'SubjectBriefName', xml_model.UnionCarrier_SubjectBriefName)
        addE(union_carrier, 'csdo', 'TaxpayerId', xml_model.UnionCarrier_TaxpayerId)

        address = E(etree.QName(xml_nsmap['ccdo'], 'SubjectAddressDetails'))
        addE(address, 'csdo', 'AddressKindCode', '1')
        addE(address, 'csdo', 'UnifiedCountryCode', xml_model.UnionCarrier_UnifiedCountryCode,
             codeListId=code_list['country'])
        addE(address, 'csdo', 'RegionName', xml_model.UnionCarrier_RegionName)
        addE(address, 'csdo', 'CityName', xml_model.UnionCarrier_CityName)
        addE(address, 'csdo', 'StreetName', xml_model.UnionCarrier_StreetName)
        addE(address, 'csdo', 'BuildingNumberId', xml_model.UnionCarrier_BuildingNumberId)
        addE(address, 'csdo', 'RoomNumberId', xml_model.UnionCarrier_RoomNumberId)
        union_carrier.append(address)

        # представитель перевозчика (водитель)
        driver = E(etree.QName(xml_nsmap['cacdo'], 'CarrierRepresentativeDetails'))

        fullname = E(etree.QName(xml_nsmap['ccdo'], 'FullNameDetails'))
        addE(fullname, 'csdo', 'FirstName', xml_model.CarrierRepresentative_FirstName)
        addE(fullname, 'csdo', 'MiddleName', xml_model.CarrierRepresentative_MiddleName)
        addE(fullname, 'csdo', 'LastName', xml_model.CarrierRepresentative_LastName)
        driver.append(fullname)

        addE(driver, 'csdo', 'PositionName', xml_model.CarrierRepresentative_PositionName)

        identity_doc = E(etree.QName(xml_nsmap['ccdo'], 'IdentityDocV3Details'))
        addE(
            identity_doc,
            'csdo',
            'UnifiedCountryCode',
            xml_model.CarrierRepresentative_UnifiedCountryCode,
            codeListId=code_list['country']
        )
        addE(identity_doc, 'csdo', 'IdentityDocKindCode', xml_model.CarrierRepresentative_IdentityDocKindCode)
        addE(identity_doc, 'csdo', 'DocId', xml_model.CarrierRepresentative_DocId)
        addE(identity_doc, 'csdo', 'DocCreationDate', xml_model.CarrierRepresentative_DocCreationDate)
        addE(identity_doc, 'csdo', 'DocValidityDate', xml_model.CarrierRepresentative_DocValidityDate)
        driver.append(identity_doc)

        addE(driver, 'casdo', 'RoleCode', xml_model.CarrierRepresentative_RoleCode)
        union_carrier.append(driver)
        # END представитель перевозчика (водитель)

        main.append(union_carrier)
        # END перевозчик по ТТ ЕАЭС

        my_doc.append(main)
        # END блок main

        # перевозчик
        carrier = E(etree.QName(xml_nsmap['cacdo'], 'PIATCarrierDetails'))
        addE(carrier, 'csdo', 'SubjectBriefName', xml_model.Carrier_SubjectBriefName)
        addE(carrier, 'csdo', 'TaxpayerId', xml_model.Carrier_TaxpayerId)

        address = E(etree.QName(xml_nsmap['ccdo'], 'SubjectAddressDetails'))
        addE(address, 'csdo', 'AddressKindCode', '1')
        addE(address, 'csdo', 'UnifiedCountryCode', xml_model.Carrier_UnifiedCountryCode,
             codeListId=code_list['country'])
        addE(address, 'csdo', 'RegionName', xml_model.Carrier_RegionName)
        addE(address, 'csdo', 'CityName', xml_model.Carrier_CityName)
        addE(address, 'csdo', 'StreetName', xml_model.Carrier_StreetName)
        addE(address, 'csdo', 'BuildingNumberId', xml_model.Carrier_BuildingNumberId)
        addE(address, 'csdo', 'RoomNumberId', xml_model.Carrier_RoomNumberId)
        carrier.append(address)

        my_doc.append(carrier)
        # END перевозчик
        # END формирование ЭПИ

    if xml_model.XmlType == 'TD':
        # формирование ТД
        my_doc = NS(
            etree.QName(xml_nsmap['gd'], "GoodsDeclaration"),
            **d
        )
        addE(my_doc, 'csdo', 'EDocCode', xml_model.EDocCode)
        addE(my_doc, 'csdo', 'EDocId', xml_model.EDocId)
        addE(my_doc, 'csdo', 'EDocDateTime', dt_to_xml_format(xml_model.EDocDateTime))
        addE(my_doc, 'casdo', 'DeclarationKindCode', xml_model.DeclarationKindCode)
        addE(my_doc, 'casdo', 'TransitProcedureCode', xml_model.TransitProcedureCode)
        addE(my_doc, 'casdo', 'TransitFeatureCode', xml_model.TransitFeatureCode)
        addE(my_doc, 'casdo', 'EDocIndicatorCode', xml_model.EDocIndicatorCode)

        count_item = xml_model.GoodsQuantity
        if (count_item - 1) % 3 == 0:
            count_page = 1 + (count_item - 1) // 3
        else:
            count_page = 2 + (count_item - 1) // 3
        addE(my_doc, 'csdo', 'PageQuantity', count_page)
        addE(my_doc, 'casdo', 'LoadingListsQuantity', xml_model.LoadingListsQuantity)
        addE(my_doc, 'casdo', 'LoadingListsPageQuantity', xml_model.LoadingListsPageQuantity)
        addE(my_doc, 'casdo', 'GoodsQuantity', xml_model.GoodsQuantity)
        addE(my_doc, 'casdo', 'CargoQuantity', xml_model.CargoQuantity)

        # декларант
        tr_decl = E(etree.QName(xml_nsmap['cacdo'], 'DeclarantDetails'))
        addE(tr_decl, 'csdo', 'SubjectBriefName', xml_model.TransitDeclarant_SubjectBriefName)
        addE(tr_decl, 'csdo', 'TaxpayerId', xml_model.TransitDeclarant_TaxpayerId)

        address = E(etree.QName(xml_nsmap['ccdo'], 'SubjectAddressDetails'))
        addE(address, 'csdo', 'UnifiedCountryCode', xml_model.TransitDeclarant_UnifiedCountryCode,
             codeListId=code_list['country'])
        addE(address, 'csdo', 'RegionName', xml_model.TransitDeclarant_RegionName)
        addE(address, 'csdo', 'CityName', xml_model.TransitDeclarant_CityName)
        addE(address, 'csdo', 'StreetName', xml_model.TransitDeclarant_StreetName)
        addE(address, 'csdo', 'BuildingNumberId', xml_model.TransitDeclarant_BuildingNumberId)
        addE(address, 'csdo', 'RoomNumberId', xml_model.TransitDeclarant_RoomNumberId)
        tr_decl.append(address)

        my_doc.append(tr_decl)
        # END декларант

        # основная секция о партии товаров

        shipment = E(etree.QName(xml_nsmap['cacdo'], 'DeclarationGoodsShipmentDetails'))

        # страна отправления
        сountry = E(etree.QName(xml_nsmap['cacdo'], 'DepartureCountryDetails'))
        addE(
            сountry,
            'casdo',
            'CACountryCode',
            xml_model.DepartureCountry_CACountryCode,
            codeListId=code_list['country']
        )
        addE(сountry, 'casdo', 'ShortCountryName', xml_model.DepartureCountry_ShortCountryName)
        shipment.append(сountry)
        # END страна отправления

        # страна назначения
        сountry = E(etree.QName(xml_nsmap['cacdo'], 'DestinationCountryDetails'))
        addE(
            сountry,
            'casdo',
            'CACountryCode',
            xml_model.DestinationCountry_CACountryCode,
            codeListId=code_list['country']
        )
        addE(сountry, 'casdo', 'ShortCountryName', xml_model.DestinationCountry_ShortCountryName)
        shipment.append(сountry)
        # END страна назначения

        # общая стоимость
        addE(
            shipment,
            'casdo',
            'CAValueAmount',
            xml_model.CAInvoiceValueAmount,
            currencyCodeListId=code_list['currency'],
            currencyCode=xml_model.IVA_currencyCode
        )

        # курс валюты
        addE(
            shipment,
            'casdo',
            'ExchangeRate',
            xml_model.TD_ExchangeRate,
            scaleNumber=xml_model.TD_ER_scaleNumber,
            currencyCodeListId=code_list['currency'],
            currencyCode=xml_model.TD_ER_currencyCode
        )

        # отправитель
        consignor = E(etree.QName(xml_nsmap['cacdo'], 'ConsignorDetails'))
        addE(consignor, 'csdo', 'SubjectBriefName', xml_model.Consignor_SubjectBriefName)
        addE(consignor, 'csdo', 'TaxpayerId', xml_model.Consignor_TaxpayerId)

        address = E(etree.QName(xml_nsmap['ccdo'], 'SubjectAddressDetails'))
        addE(address, 'csdo', 'UnifiedCountryCode', xml_model.Consignor_UnifiedCountryCode,
             codeListId=code_list['country'])
        addE(address, 'csdo', 'RegionName', xml_model.Consignor_RegionName)
        addE(address, 'csdo', 'CityName', xml_model.Consignor_CityName)
        addE(address, 'csdo', 'StreetName', xml_model.Consignor_StreetName)
        addE(address, 'csdo', 'BuildingNumberId', xml_model.Consignor_BuildingNumberId)
        addE(address, 'csdo', 'RoomNumberId', xml_model.Consignor_RoomNumberId)
        consignor.append(address)

        shipment.append(consignor)
        # END отправитель

        # получатель
        consignee = E(etree.QName(xml_nsmap['cacdo'], 'ConsigneeDetails'))
        addE(consignee, 'csdo', 'SubjectBriefName', xml_model.Consignee_SubjectBriefName)
        addE(consignee, 'csdo', 'TaxpayerId', xml_model.Consignee_TaxpayerId)

        address = E(etree.QName(xml_nsmap['ccdo'], 'SubjectAddressDetails'))
        addE(address, 'csdo', 'UnifiedCountryCode', xml_model.Consignee_UnifiedCountryCode,
             codeListId=code_list['country'])
        addE(address, 'csdo', 'RegionName', xml_model.Consignee_RegionName)
        addE(address, 'csdo', 'CityName', xml_model.Consignee_CityName)
        addE(address, 'csdo', 'StreetName', xml_model.Consignee_StreetName)
        addE(address, 'csdo', 'BuildingNumberId', xml_model.Consignee_BuildingNumberId)
        addE(address, 'csdo', 'RoomNumberId', xml_model.Consignee_RoomNumberId)
        consignee.append(address)

        shipment.append(consignee)
        # END получатель

        # таможенная стоимость
        addE(
            shipment,
            'casdo',
            'CustomsValueAmount',
            xml_model.TD_CustomsValueAmount,
            currencyCodeListId=code_list['currency'],
            currencyCode=xml_model.TD_CV_currencyCode
        )

        # инфа о транспорте, перецепках, пост отправления/назначения
        consignment = E(etree.QName(xml_nsmap['cacdo'], 'DeclarationConsignmentDetails'))
        addE(consignment, 'casdo', 'ContainerIndicator', xml_model.ContainerIndicator)

        # транспорт
        border_ts = E(etree.QName(xml_nsmap['cacdo'], 'BorderTransportDetails'))
        addE(
            border_ts,
            'csdo',
            'UnifiedTransportModeCode',
            xml_model.UnifiedTransportModeCode,
            codeListId=code_list['ts']
        )
        consignment.append(border_ts)

        arrival_ts = E(etree.QName(xml_nsmap['cacdo'], 'ArrivalDepartureTransportDetails'))
        ts = TransportXML.objects.filter(xml=xml_model)
        count_ts = xml_model.TransportMeansQuantity
        if (count_ts is None) or (count_ts == ''):
            count_ts = len(ts)
        for i in range(count_ts):
            parent_elem = E(etree.QName(xml_nsmap['cacdo'], 'TransportMeansRegistrationIdDetails'))
            addE(
                parent_elem,
                'csdo',
                'TransportMeansRegId',
                ts[i].TransportMeansRegId,
                countryCodeListId=code_list['country'],
                countryCode=ts[i].countryCode
            )
            addE(parent_elem, 'csdo', 'DocId', ts[i].DocId)
            addE(parent_elem, 'csdo', 'VehicleId', ts[i].VehicleId)
            addE(
                parent_elem,
                'casdo',
                'TransportTypeCode',
                ts[i].TransportTypeCode,
                codeListId=code_list['ts_type']
            )
            addE(
                parent_elem,
                'csdo',
                'VehicleMakeCode',
                ts[i].VehicleMakeCode,
                codeListId=code_list['ts_make']
            )
            arrival_ts.append(parent_elem)

        consignment.append(arrival_ts)
        # END транспорт

        # перецепки
        transhipment = Transhipment.objects.filter(xml=xml_model)
        for _t in transhipment:
            tr_elem = E(etree.QName(xml_nsmap['cacdo'], 'TranshipmentDetails'))
            addE(tr_elem, 'casdo', 'ContainerIndicator', _t.ContainerIndicator)
            addE(
                tr_elem,
                'casdo',
                'CACountryCode',
                _t.CACountryCode,
                codeListId=code_list['country']
            )
            addE(tr_elem, 'casdo', 'ShortCountryName', _t.ShortCountryName)
            addE(tr_elem, 'casdo', 'PlaceName', _t.PlaceName)

            if ((_t.CustomsOfficeCode is not None) and (_t.CustomsOfficeCode != '')) or (
                    (_t.CustomsOfficeName is not None) and (_t.CustomsOfficeName != '')):
                customs = E(etree.QName(xml_nsmap['ccdo'], 'CustomsOfficeDetails'))
                addE(customs, 'csdo', 'CustomsOfficeCode', _t.CustomsOfficeCode)
                addE(customs, 'csdo', 'CustomsOfficeName', _t.CustomsOfficeName)
                tr_elem.append(customs)

            # транспорт в перецепке
            transhipment_ts = TransportTranshipment.objects.filter(transhipment_xml=_t)
            if len(transhipment_ts) > 0:
                tr_ts_elem = E(etree.QName(xml_nsmap['cacdo'], 'TranshipmentTransportDetails'))

                for _ts in transhipment_ts:
                    parent_elem = E(etree.QName(xml_nsmap['cacdo'], 'TransportMeansRegistrationIdDetails'))
                    addE(
                        parent_elem,
                        'csdo',
                        'TransportMeansRegId',
                        _ts.TransportMeansRegId,
                        countryCodeListId=code_list['country'],
                        countryCode=_ts.countryCode
                    )
                    addE(
                        parent_elem,
                        'casdo',
                        'TransportTypeCode',
                        _ts.TransportTypeCode,
                        codeListId=code_list['ts_type']
                    )
                    tr_ts_elem.append(parent_elem)

                tr_elem.append(tr_ts_elem)
            # END транспорт в перецепке

            # контейнеры в перецепке
            containers = ContainerTranshipment.objects.filter(transhipment_xml=_t)
            if len(containers) > 0:
                for _c in containers:
                    addE(tr_elem, 'casdo', 'ContainerId', _c.ContainerId)
            # END контейнеры в перецепке

            consignment.append(tr_elem)
        # end перецепки

        # пто отправления
        ptoin = E(etree.QName(xml_nsmap['cacdo'], 'BorderCustomsOfficeDetails'))
        addE(ptoin, 'csdo', 'CustomsOfficeCode', xml_model.ECP_CustomsOfficeCode)
        addE(ptoin, 'csdo', 'CustomsOfficeName', xml_model.ECP_BorderCheckpointName)
        consignment.append(ptoin)
        # END пто отправления

        # пто назначения
        tt = E(etree.QName(xml_nsmap['cacdo'], 'TransitTerminationDetails'))

        customs = E(etree.QName(xml_nsmap['ccdo'], 'CustomsOfficeDetails'))
        addE(customs, 'csdo', 'CustomsOfficeCode', xml_model.TT_CustomsOfficeCode)
        addE(customs, 'csdo', 'CustomsOfficeName', xml_model.TT_CustomsOfficeName)
        addE(
            customs,
            'csdo',
            'UnifiedCountryCode',
            xml_model.TT_UnifiedCountryCode,
            codeListId=code_list['country']
        )
        tt.append(customs)

        addE(tt, 'casdo', 'CustomsControlZoneId', xml_model.TT_CustomsControlZoneId)
        consignment.append(tt)
        # END пто назначения

        shipment.append(consignment)
        # END инфа о транспорте, перецепках, пост отправления/назначения

        # информация о товаре
        consigment_items = ConsignmentItem.objects.filter(xml=xml_model)
        if len(consigment_items) > 0:
            for _ci in consigment_items:
                cons_item = E(etree.QName(xml_nsmap['cacdo'], 'DeclarationGoodsItemDetails'))
                addE(cons_item, 'casdo', 'ConsignmentItemOrdinal', _ci.ConsignmentItemOrdinal)
                addE(cons_item, 'csdo', 'CommodityCode', _ci.CommodityCode)
                addE(cons_item, 'casdo', 'GoodsDescriptionText', _ci.GoodsDescriptionText)
                addE(cons_item, 'casdo', 'GoodsDescriptionText', _ci.GoodsDescriptionText1)
                addE(cons_item, 'casdo', 'GoodsDescriptionText', _ci.GoodsDescriptionText2)
                addE(cons_item, 'casdo', 'GoodsDescriptionText', _ci.GoodsDescriptionText3)
                addE(
                    cons_item,
                    'csdo',
                    'UnifiedGrossMassMeasure',
                    _ci.UnifiedGrossMassMeasure,
                    measurementUnitCodeListId=code_list['measure'],
                    measurementUnitCode=_ci.measurementUnitCode,
                )

                if (_ci.GM_GoodsMeasure is not None) and (_ci.GM_GoodsMeasure != ''):
                    gm = E(etree.QName(xml_nsmap['cacdo'], 'GoodsMeasureDetails'))
                    addE(
                        gm,
                        'casdo',
                        'GoodsMeasure',
                        _ci.GM_GoodsMeasure,
                        measurementUnitCodeListId=code_list['measure'],
                        measurementUnitCode=_ci.GM_measurementUnitCode,
                    )
                    addE(gm, 'casdo', 'MeasureUnitAbbreviationCode', _ci.GM_MeasureUnitAbbreviationCode)
                    cons_item.append(gm)

                if _ci.ConsignmentItemOrdinal == 1:
                    page_number = 1
                else:
                    page_number = (_ci.ConsignmentItemOrdinal + 1) // 3 + 1

                addE(cons_item, 'casdo', 'PageOrdinal', page_number)
                addE(cons_item, 'casdo', 'GoodsTraceabilityCode', _ci.GoodsTraceabilityCode)
                addE(cons_item, 'casdo', 'LicenseGoodsKindCode', _ci.LicenseGoodsKindCode)

                if (_ci.AGM_GoodsMeasure is not None) and (_ci.AGM_GoodsMeasure != ''):
                    gm = E(etree.QName(xml_nsmap['cacdo'], 'AddGoodsMeasureDetails'))
                    addE(
                        gm,
                        'casdo',
                        'GoodsMeasure',
                        _ci.AGM_GoodsMeasure,
                        measurementUnitCodeListId=code_list['measure'],
                        measurementUnitCode=_ci.AGM_measurementUnitCode,
                    )
                    addE(gm, 'casdo', 'MeasureUnitAbbreviationCode', _ci.AGM_MeasureUnitAbbreviationCode)
                    cons_item.append(gm)

                # упаковка и места
                cargo_package = E(etree.QName(xml_nsmap['cacdo'], 'CargoPackagePalletDetails'))
                addE(cargo_package, 'casdo', 'CargoQuantity', _ci.CargoQuantity)

                package_details = E(etree.QName(xml_nsmap['cacdo'], 'PackagePalletDetails'))
                addE(package_details, 'casdo', 'CargoPackageInfoKindCode', _ci.CargoPackageInfoKindCode)
                addE(
                    package_details,
                    'csdo',
                    'PackageKindCode',
                    _ci.PackageKindCode,
                    codeListId=code_list['pack']
                )
                cargo_package.append(package_details)

                cons_item.append(cargo_package)
                # END упаковка и места

                # контейнеры в товаре
                cont_ci = ContainerCI.objects.filter(ci=_ci)
                if len(cont_ci) > 0:
                    for _c in cont_ci:
                        cont_list = E(etree.QName(xml_nsmap['cacdo'], 'ContainerListDetails'))
                        cont = E(etree.QName(xml_nsmap['cacdo'], 'ContainerDetails'))
                        addE(cont, 'casdo', 'ContainerId', _c.ContainerId)
                        cont_list.append(cont)
                        cons_item.append(cont_list)
                # END контейнеры в товаре

                if _ci.TM_GoodsMeasure is not None:
                    tm = E(etree.QName(xml_nsmap['cacdo'], 'GoodsTraceabilityMeasureDetails'))
                    addE(
                        tm,
                        'casdo',
                        'GoodsMeasure',
                        _ci.TM_GoodsMeasure,
                        measurementUnitCodeListId=code_list['measure'],
                        measurementUnitCode=_ci.TM_measurementUnitCode
                    )
                    addE(tm, 'casdo', 'MeasureUnitAbbreviationCode', _ci.TM_MeasureUnitAbbreviationCode)
                    cons_item.append(tm)

                addE(
                    cons_item,
                    'casdo',
                    'CAValueAmount',
                    _ci.CAValueAmount,
                    currencyCodeListId=code_list['currency'],
                    currencyCode=_ci.currencyCode,
                )

                addE(
                    cons_item,
                    'casdo',
                    'CustomsValueAmount',
                    _ci.CustomsValueAmount,
                    currencyCodeListId=code_list['currency'],
                    currencyCode=_ci.CV_currencyCode,
                )

                # предшедствующие документы
                doc = PIPrecedingDocDetails.objects.filter(ci=_ci)
                if len(doc) > 0:
                    counter = 1
                    for _d in doc:
                        doc_item = E(etree.QName(xml_nsmap['cacdo'], 'PrecedingDocDetails'))
                        addE(doc_item, 'casdo', 'LineId', counter)
                        addE(
                            doc_item,
                            'csdo',
                            'DocKindCode',
                            _d.DocKindCode,
                            codeListId=code_list['doc_type']
                        )
                        doc_details = E(etree.QName(xml_nsmap['cacdo'], 'CustomsDocIdDetails'))
                        if _d.DocKindCode == '09013':
                            di = _d.DocId.split('/')
                            if len(di) == 3:
                                addE(doc_details, 'csdo', 'CustomsOfficeCode', di[0])
                                addE(doc_details, 'csdo', 'DocCreationDate', _d.DocCreationDate)
                                addE(doc_details, 'casdo', 'CustomsDocumentId', di[2])
                            else:
                                addE(doc_details, 'csdo', 'DocCreationDate', _d.DocCreationDate)
                                addE(doc_details, 'casdo', 'CustomsDocumentId', _d.DocId)
                        else:
                            addE(doc_details, 'csdo', 'DocCreationDate', _d.DocCreationDate)
                            addE(doc_details, 'casdo', 'CustomsDocumentId', _d.DocId)

                        doc_item.append(doc_details)
                        addE(doc_item, 'casdo', 'ConsignmentItemOrdinal', _d.ConsignmentItemOrdinal)
                        cons_item.append(doc_item)
                        counter += 1
                # END предшедствующие документы

                # документы
                doc = PIGoodsDocDetails.objects.filter(ci=_ci)
                if len(doc) > 0:
                    for _d in doc:
                        doc_item = E(etree.QName(xml_nsmap['cacdo'], 'PresentedDocDetails'))
                        addE(
                            doc_item,
                            'csdo',
                            'DocKindCode',
                            _d.DocKindCode,
                            codeListId=code_list['doc_type']
                        )
                        addE(doc_item, 'csdo', 'DocId', _d.DocId)
                        addE(doc_item, 'csdo', 'DocCreationDate', _d.DocCreationDate)
                        cons_item.append(doc_item)
                # END документы

                shipment.append(cons_item)
        # END информация о товаре

        # информация о гарантах
        guarantee_list = TransitGuarantee.objects.filter(xml=xml_model)
        if len(guarantee_list) > 0:
            for _g in guarantee_list:
                tg_item = E(etree.QName(xml_nsmap['cacdo'], 'TransitGuaranteeDetails'))
                addE(
                    tg_item,
                    'casdo',
                    'TransitGuaranteeMeasureCode',
                    _g.TransitGuaranteeMeasureCode,
                    codeListId=code_list['guarantee']
                )
                addE(
                    tg_item,
                    'casdo',
                    'GuaranteeAmount',
                    _g.GuaranteeAmount,
                    currencyCodeListId=code_list['currency'],
                    currencyCode=_g.currencyCode
                )
                if (_g.GC_CustomsDocumentId is not None) and (_g.GC_CustomsDocumentId != ''):
                    sert = E(etree.QName(xml_nsmap['cacdo'], 'TransitGuaranteeDocDetails'))
                    addE(
                        sert,
                        'csdo',
                        'DocId',
                        _g.GC_CustomsOfficeCode + '/' + _g.GC_DocCreationDate.strftime(
                            "%d%m%y") + '/' + _g.GC_CustomsDocumentId)
                    addE(sert, 'csdo', 'DocCreationDate', _g.GC_DocCreationDate)
                    tg_item.append(sert)
                elif (_g.RD_RegistrationNumberId is not None) and (_g.RD_RegistrationNumberId != ''):
                    reg_doc = E(etree.QName(xml_nsmap['cacdo'], 'TransitGuaranteeDocDetails'))
                    addE(reg_doc, 'csdo', 'DocId', _g.RD_RegistrationNumberId)
                    addE(reg_doc, 'csdo', 'DocCreationDate', _g.GC_DocCreationDate)
                    tg_item.append(reg_doc)
                addE(tg_item, 'csdo', 'SubjectBriefName', _g.ES_SubjectBriefName)
                addE(tg_item, 'csdo', 'TaxpayerId', _g.ES_TaxpayerId)
                addE(tg_item, 'csdo', 'BankId', _g.ES_BankId)

                shipment.append(tg_item)
        # END информация о гарантах

        my_doc.append(shipment)
        # END основная секция о партии товаров

        # перевозчик
        carrier = E(etree.QName(xml_nsmap['cacdo'], 'CarrierDetails'))
        addE(carrier, 'csdo', 'SubjectBriefName', xml_model.Carrier_SubjectBriefName)
        addE(carrier, 'csdo', 'TaxpayerId', xml_model.Carrier_TaxpayerId)

        address = E(etree.QName(xml_nsmap['ccdo'], 'SubjectAddressDetails'))
        addE(address, 'csdo', 'UnifiedCountryCode', xml_model.Carrier_UnifiedCountryCode,
             codeListId=code_list['country'])
        addE(address, 'csdo', 'RegionName', xml_model.Carrier_RegionName)
        addE(address, 'csdo', 'CityName', xml_model.Carrier_CityName)
        addE(address, 'csdo', 'StreetName', xml_model.Carrier_StreetName)
        addE(address, 'csdo', 'BuildingNumberId', xml_model.Carrier_BuildingNumberId)
        addE(address, 'csdo', 'RoomNumberId', xml_model.Carrier_RoomNumberId)
        carrier.append(address)

        # водитель
        driver = E(etree.QName(xml_nsmap['cacdo'], 'CarrierRepresentativeDetails'))
        fullname = E(etree.QName(xml_nsmap['ccdo'], 'FullNameDetails'))
        addE(fullname, 'csdo', 'FirstName', xml_model.CarrierRepresentative_FirstName)
        addE(fullname, 'csdo', 'MiddleName', xml_model.CarrierRepresentative_MiddleName)
        addE(fullname, 'csdo', 'LastName', xml_model.CarrierRepresentative_LastName)
        driver.append(fullname)

        addE(driver, 'csdo', 'PositionName', xml_model.CarrierRepresentative_PositionName)

        identity_doc = E(etree.QName(xml_nsmap['ccdo'], 'IdentityDocV3Details'))
        addE(
            identity_doc,
            'csdo',
            'UnifiedCountryCode',
            xml_model.CarrierRepresentative_UnifiedCountryCode,
            codeListId=code_list['country']
        )
        addE(
            identity_doc,
            'csdo',
            'IdentityDocKindCode',
            xml_model.CarrierRepresentative_IdentityDocKindCode,
            codeListId=code_list['doc_kind']
        )
        addE(identity_doc, 'csdo', 'DocId', xml_model.CarrierRepresentative_DocId)
        addE(identity_doc, 'csdo', 'DocCreationDate', xml_model.CarrierRepresentative_DocCreationDate)
        addE(identity_doc, 'csdo', 'DocValidityDate', xml_model.CarrierRepresentative_DocValidityDate)
        driver.append(identity_doc)

        addE(driver, 'casdo', 'RoleCode', xml_model.CarrierRepresentative_RoleCode)
        carrier.append(driver)
        # END водитель

        my_doc.append(carrier)
        # END перевозчик

        # пломбы
        if xml_model.SealId is not None:
            _seals = xml_model.SealId.split(',')
            seal = E(etree.QName(xml_nsmap['cacdo'], 'SealDetails'))
            addE(seal, 'casdo', 'SealQuantity', len(_seals))
            for _s in _seals:
                addE(seal, 'csdo', 'SealId', _s)
            my_doc.append(seal)
            # END пломбы

            # сведения об аттестате и договоре
            if (xml_model.SD_RegisterDocumentIdDetails_RegistrationNumberId is not None) or (
                    xml_model.SD_RepresentativeContractDetails_DocId is not None):
                srd = E(etree.QName(xml_nsmap['cacdo'], 'SignatoryRepresentativeDetails'))
                if xml_model.SD_RegisterDocumentIdDetails_RegistrationNumberId is not None:
                    reg_doc = E(etree.QName(xml_nsmap['cacdo'], 'RegisterDocumentIdDetails'))
                    addE(
                        reg_doc,
                        'csdo',
                        'DocKindCode',
                        xml_model.SD_RegisterDocumentIdDetails_DocKindCode,
                        codeListId=code_list['doc_type']
                    )
                    addE(reg_doc, 'casdo', 'RegistrationNumberId',
                         xml_model.SD_RegisterDocumentIdDetails_RegistrationNumberId)
                    srd.append(reg_doc)

                if xml_model.SD_RepresentativeContractDetails_DocId is not None:
                    contract = E(etree.QName(xml_nsmap['cacdo'], 'RepresentativeContractDetails'))
                    addE(
                        contract,
                        'csdo',
                        'DocKindCode',
                        xml_model.SD_RepresentativeContractDetails_DocKindCode,
                        codeListId=code_list['doc_type']
                    )
                    addE(contract, 'csdo', 'DocId', xml_model.SD_RepresentativeContractDetails_DocId)
                    addE(contract, 'csdo', 'DocCreationDate',
                         xml_model.SD_RepresentativeContractDetails_DocCreationDate)
                    srd.append(contract)

                my_doc.append(srd)
        # END сведения об аттестате и договоре

        # сведения о подписывающем лице
        sign_person = E(etree.QName(xml_nsmap['cacdo'], 'SignatoryPersonV2Details'))

        # если не указана фамилия и номер паспорта - берем данные из водителя
        if (xml_model.SP_LastName is None) and (xml_model.SP_DocId is None):
            # данные из водителя
            person = E(etree.QName(xml_nsmap['cacdo'], 'SigningDetails'))
            fullname = E(etree.QName(xml_nsmap['ccdo'], 'FullNameDetails'))
            addE(fullname, 'csdo', 'FirstName', xml_model.CarrierRepresentative_FirstName)
            addE(fullname, 'csdo', 'MiddleName', xml_model.CarrierRepresentative_MiddleName)
            addE(fullname, 'csdo', 'LastName', xml_model.CarrierRepresentative_LastName)
            person.append(fullname)

            addE(person, 'csdo', 'PositionName', xml_model.CarrierRepresentative_PositionName)
            d = xml_model.EDocDateTime
            addE(person, 'casdo', 'SigningDate', str(d.strftime('%Y-%m-%d')))

            sign_person.append(person)

            identity_doc = E(etree.QName(xml_nsmap['ccdo'], 'IdentityDocV3Details'))
            addE(
                identity_doc,
                'csdo',
                'UnifiedCountryCode',
                xml_model.CarrierRepresentative_UnifiedCountryCode,
                codeListId=code_list['country']
            )
            addE(
                identity_doc,
                'csdo',
                'IdentityDocKindCode',
                xml_model.CarrierRepresentative_IdentityDocKindCode,
                codeListId=code_list['doc_kind']
            )
            addE(identity_doc, 'csdo', 'DocId', xml_model.CarrierRepresentative_DocId)
            addE(identity_doc, 'csdo', 'DocCreationDate', xml_model.CarrierRepresentative_DocCreationDate)
            addE(identity_doc, 'csdo', 'DocValidityDate', xml_model.CarrierRepresentative_DocValidityDate)
            sign_person.append(identity_doc)

        else:
            # данные из полей ТД о подписывающем лице
            person = E(etree.QName(xml_nsmap['cacdo'], 'SigningDetails'))
            fullname = E(etree.QName(xml_nsmap['ccdo'], 'FullNameDetails'))
            addE(fullname, 'csdo', 'FirstName', xml_model.SP_FirstName)
            addE(fullname, 'csdo', 'MiddleName', xml_model.SP_MiddleName)
            addE(fullname, 'csdo', 'LastName', xml_model.SP_LastName)
            person.append(fullname)

            addE(person, 'csdo', 'PositionName', xml_model.SP_PositionName)
            d = xml_model.EDocDateTime
            addE(person, 'casdo', 'SigningDate', str(d.strftime('%Y-%m-%d')))

            sign_person.append(person)

            identity_doc = E(etree.QName(xml_nsmap['ccdo'], 'IdentityDocV3Details'))
            addE(
                identity_doc,
                'csdo',
                'UnifiedCountryCode',
                xml_model.SP_UnifiedCountryCode,
                codeListId=code_list['country']
            )
            addE(
                identity_doc,
                'csdo',
                'IdentityDocKindCode',
                xml_model.SP_IdentityDocKindCode,
                codeListId=code_list['doc_kind']
            )
            addE(identity_doc, 'csdo', 'DocId', xml_model.SP_DocId)
            addE(identity_doc, 'csdo', 'DocCreationDate', xml_model.SP_DocCreationDate)
            addE(identity_doc, 'csdo', 'DocValidityDate', xml_model.SP_DocValidityDate)
            sign_person.append(identity_doc)

            if xml_model.SP_QualificationCertificateId is not None:
                addE(sign_person, 'casdo', 'QualificationCertificateId', xml_model.SP_QualificationCertificateId)

            if xml_model.SP_POA_DocId is not None:
                poa = E(etree.QName(xml_nsmap['cacdo'], 'PowerOfAttorneyDetails'))
                addE(
                    poa,
                    'csdo',
                    'DocKindCode',
                    xml_model.SP_POA_DocKindCode,
                    codeListId=code_list['doc_type']
                )
                addE(poa, 'csdo', 'DocId', xml_model.SP_POA_DocId)
                addE(poa, 'csdo', 'DocCreationDate', xml_model.SP_POA_DocCreationDate)
                addE(poa, 'csdo', 'DocValidityDate', xml_model.SP_POA_DocValidityDate)
                sign_person.append(poa)

        my_doc.append(sign_person)
        # END сведения о подписывающем лице

        # END формирование ТД

    if flag_file:
        tree = etree.ElementTree(my_doc)
        xml_file = BytesIO()
        tree.write(xml_file, pretty_print=True, encoding='utf-8', xml_declaration=True, standalone='yes')
        return xml_file
    else:
        return etree.tostring(my_doc, pretty_print=True, encoding='utf-8', xml_declaration=True, standalone='yes').decode(
        'utf-8')
