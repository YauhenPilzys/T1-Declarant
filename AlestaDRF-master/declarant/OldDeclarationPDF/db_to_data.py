from declarant.country import dataCountry
from declarant.models import XMLModel, TransportXML, TransitGuarantee, Transhipment, TransportTranshipment, \
    ContainerTranshipment, ConsignmentItem, ContainerCI, PIPrecedingDocDetails, PIGoodsDocDetails


def date_convert_for_print(d):
    if d:
        s = str(d)
        return s[8:10] + '.' + s[5:7] + '.' + s[:4]
    else:
        return ''

def date_convert_for_sert(d):
    if d:
        s = str(d)
        return s[8:10] + s[5:7] + s[2:4]
    else:
        return ''

def g52_data_convert(s):
    if s:
        return s.strip().replace(' ', '_')
    else:
        return '_'

class Item:
    def test_data(self):
        self.g31_3 = '3 КОНТЕЙНЕР'  # номер контейнера для товара, если есть
        self.g31_2 = '2 33, ZZ'  # кол-во мест  (для насыпа, налива должно быть '2 0/NE')
        self.g31_1 = 'НИЖНЯЯ ФУТЕРОВКА ЗАГРУЗОЧНОГО БУНКЕРА (ДЭКИ);ЗАЩИТА НАПРАВЛЯЮЩИХ (ДЭКИ);МОДУЛИ ГРОХОТА (' \
                     'ДЭКИ);БОКОВАЯ ФУТЕРОВКА (ДЭКИ);БОКОВОЙ ВКЛАДЫШ (ДЭКИ);КАССЕТА ДЛЯ ПЛАСТИНЧАТОГО СИТА;' \
                     'НИЖНЯЯ ФУТЕРОВКА ЗАГРУЗОЧНОГО БУНКЕРА (ДЭКИ);ЗАЩИТА НАПРАВЛЯЮЩИХ (ДЭКИ);МОДУЛИ ГРОХОТА (' \
                     'ДЭКИ);БОКОВАЯ ФУТЕРОВКА (ДЭКИ);БОКОВОЙ ВКЛАДЫШ (ДЭКИ);КАССЕТА ДЛЯ ПЛАСТИНЧАТОГО СИТА;'
        # описание товара
        self.g33_1 = '3917320009'  # код ТН ВЭД
        self.g33_2 = 'С'  # если у декларанта есть информация, что в отношении товара не установлены запреты и ограничения
        self.g33_3 = 'K'  # если разобранный товар перевозится частями
        self.g35 = '22000.000000'  # вес брутто товара
        self.g40 = ['09035 11216401/200923/0163258', '09035 11216401/200923/0163259',
                    '09035 11216401/200923/0163260']  # предшествующий документ(ы)
        self.g41_1 = '123.000000 КГ'  # дополнительная единица измерения
        self.g41_2 = '166'  # код дополнительной единицы измерения
        self.g42_1 = 'USD'  # код валюты
        self.g42_2 = '123450.00'  # стоимость товара
        self.g44 = [  # документы
            '02024 XX7654321 01.01.2023',
            '02015 AZ8923 03.03.2023',
            '04021 INVOICE12983 12.12.2022',
            '04021 INVOICE12984 12.12.2022',
            '02099 123 12.12.2022',
            '04021 INVOICE12985 12.12.2022',
            '04021 INVOICE12986 12.12.2022',
            '04021 INVOICE12987 12.12.2022',
            '04021 INVOICE12988 12.12.2022',
            '09024 16404/3/123123 01.05.2022',
            '02024 XX7654321 01.01.2023',
            '02015 AZ8923 03.03.2023',
            '04021 INVOICE12983 12.12.2022',
            '04021 INVOICE12984 12.12.2022',
            '02099 123 12.12.2022',
            '04021 INVOICE12985 12.12.2022',
            '04021 INVOICE12986 12.12.2022',
            '04021 INVOICE12987 12.12.2022',
            '04021 INVOICE12988 12.12.2022',
            '09024 16404/3/123123 01.05.2022',
            '02024 XX7654321 01.01.2023',
            '02015 AZ8923 03.03.2023',
            '04021 INVOICE12983 12.12.2022',
            '04021 INVOICE12984 12.12.2022',
            '02099 123 12.12.2022',
            '04021 INVOICE12985 12.12.2022',
            '04021 INVOICE12986 12.12.2022',
            '04021 INVOICE12987 12.12.2022',
            '04021 INVOICE12988 12.12.2022',
            '09024 16404/3/123123 01.05.2022',
            '02024 XX7654321 01.01.2023',
            '02015 AZ8923 03.03.2023',
            '04021 INVOICE12983 12.12.2022',
            '04021 INVOICE12984 12.12.2022',
            '02099 123 12.12.2022',
            '04021 INVOICE12985 12.12.2022',
            '04021 INVOICE12986 12.12.2022',
            '04021 INVOICE12987 12.12.2022',
            '04021 INVOICE12988 12.12.2022',
            '09024 16404/3/123123 01.05.2022',
            '02024 XX7654321 01.01.2023',
            '02015 AZ8923 03.03.2023',
            '04021 INVOICE12983 12.12.2022',
            '04021 INVOICE12984 12.12.2022',
            '02099 123 12.12.2022',
            '04021 INVOICE12985 12.12.2022',
            '04021 INVOICE12986 12.12.2022',
            '04021 INVOICE12987 12.12.2022',
            '04021 INVOICE12988 12.12.2022',
            '09024 16404/3/123123 01.05.2022',
            '02024 XX7654321 01.01.2023',
            '02015 AZ8923 03.03.2023',
            '04021 INVOICE12983 12.12.2022',
            '04021 INVOICE12984 12.12.2022',
            '02099 123 12.12.2022',
            '04021 INVOICE12985 12.12.2022',
            '04021 INVOICE12986 12.12.2022',
            '04021 INVOICE12987 12.12.2022',
            '04021 INVOICE12988 12.12.2022',
            '09024 16404/3/123123 01.05.2022',
            '02024 XX7654321 01.01.2023',
            '02015 AZ8923 03.03.2023',
            '04021 INVOICE12983 12.12.2022',
            '04021 INVOICE12984 12.12.2022',
            '02099 123 12.12.2022',
            '04021 INVOICE12985 12.12.2022',
            '04021 INVOICE12986 12.12.2022',
            '04021 INVOICE12987 12.12.2022',
            '04021 INVOICE12988 12.12.2022',
            '09024 16404/3/123123 01.05.2022',
            '02024 XX7654321 01.01.2023',
            '02015 AZ8923 03.03.2023',
            '04021 INVOICE12983 12.12.2022',
            '04021 INVOICE12984 12.12.2022',
            '02099 123 12.12.2022',
        ]

    def load_from_db(self, cons_item):
        _query = ContainerCI.objects.filter(ci=cons_item)
        self.g31_3 = '3 ' + ' '.join(item.ContainerId for item in _query if item.ContainerId)  # номер контейнера для товара, если есть
        self.g31_2 = ' '.join(item for item in [
            '2',
            str(cons_item.CargoQuantity or ''),
            cons_item.PackageKindCode,
        ] if item)   # кол-во мест
        self.g31_1 = ' '.join(item for item in [
            cons_item.GoodsDescriptionText,
            cons_item.GoodsDescriptionText1,
            cons_item.GoodsDescriptionText2,
            cons_item.GoodsDescriptionText3,
        ] if item)
        # описание товара
        self.g33_1 = cons_item.CommodityCode  # код ТН ВЭД
        self.g33_2 = None  # если у декларанта есть информация, что в отношении товара не установлены запреты и ограничения
        self.g33_3 = None  # если разобранный товар перевозится частями
        self.g35 = str(cons_item.UnifiedGrossMassMeasure or '')  # вес брутто товара
        _query = PIPrecedingDocDetails.objects.filter(ci=cons_item)
        self.g40 = []
        for _q in _query:
            self.g40.append(' '.join(item for item in [
                _q.DocKindCode,
                _q.DocId,
            ] if item))  # предшествующий документ(ы)
        self.g41_1 = ' '.join(item for item in [
            str(cons_item.GM_GoodsMeasure or ''),
            cons_item.GM_MeasureUnitAbbreviationCode
        ] if item)  # дополнительная единица измерения
        self.g41_2 = cons_item.GM_measurementUnitCode  # код дополнительной единицы измерения
        self.g42_1 = cons_item.currencyCode  # код валюты
        self.g42_2 = str(cons_item.CAValueAmount or '')  # стоимость товара

        _query = PIGoodsDocDetails.objects.filter(ci=cons_item)
        self.g44 = []
        for _q in _query:
            _list = [
                _q.DocKindCode,
                _q.DocId,
                date_convert_for_print(_q.DocCreationDate)
            ]
            self.g44.append(' '.join(item for item in _list if item))   # документы


class InfoTD:
    def test_data(self):
        self.g1_1 = 'ТТ'  # всегда [ТТ]
        self.g1_2 = 'МПO'  # чаще пустое, варианты - [ФЛ, СП, МП, ВН, ГП]
        self.g1_3 = 'ИМ'  # тип транзита - [ИМ, ТР, ТС]
        self.g2 = ['OTPRAVITEL OOO', 'ЛИТВА KAUNAS JOVARU G. 3']  # отправитель
        self.g4 = '1/10'  # отгр. спецификация (страый формат)
        self.g5 = '5'  # всего товаров
        self.g6 = '1234'  # всего мест
        self.g7 = None  # справочный номер [ПТД]
        self.g8 = ['ПОЛУЧАТЕЛЬ ООО',
                   'БЕЛАРУСЬ, МИНСК, УЛ. ВЕРЫ ХОРУЖЕЙ, ДОМ 137, ПОДЪЕЗД 2, КВ. 123, УНП 11212332']  # получатель
        self.g9 = [  # таможенный представитель
            'ТА-1600/0000501',  # номер в реестре
            '11002/ПЭ0055 от 01.09.2023',  # номер договора ДЕКЛАРАНТА с тамож. представителем
            '0999/ПРИКАЗ 01 от 10.04.2017',  # документ подтверждающий полномочия руководителя или номер аттестата
            None,  # доверенность
        ]
        self.g14 = [  # декларант
            'ДЕКЛАРАНТ ООО',
            'БЕЛАРУСЬ ГРОДНО УЛ. ЛИМОЖА, 27/4 УНП 98877667',
            None,  # номер таможенного перевозчика или УЭО
        ]
        self.g15 = 'ЛИТВА'  # страна отправления
        self.g17 = 'РОССИЯ'  # страна назначения
        self.g18_1 = '1: AAA111/PR111139'  # транспорт
        self.g18_2 = 'LT'  # страна регистрации транспорта
        self.g19 = '0'  # контейнер [0, 1]
        self.g20 = None  # пломбы
        self.g21_1 = '2: AA46463/A1111A3'  # транспорт
        self.g21_2 = 'BY'  # страна регистрации транспорта
        self.g22_1 = 'EUR'  # код валюты
        self.g22_2 = '1234567.99'  # сумма по счету
        self.g25 = '31'  # тип транспорта

        self.items = []
        for i in range(1, 6):
            item = Item()
            item.test_data()
            self.items.append(item)

        self.g50 = [  # принципал и перевозчик
            'PRINCIPAL OOO',
            'MINSK, PRITYCKOGO UL. 12-34',
            'PEREVOZ OOO',
            'РОССИЯ МОСКВА УЛ. СОВЕТСКАЯ 111',
        ]
        self.g50_v1 = 'ВОДИТЕЛЬ: ' + 'IVANOV IVAN KH1234567 04.09.2022'
        self.g50_v2 = 'Представленный: ' + 'IVANOV IVAN KH1234567 04.09.2022'
        self.g51 = 'Место и дата: ' + '01.10.2023'  # дата составления декларации
        self.g52_1 = [
            '10000.00 11216000/180923/31353 18.09.2023',
            '5000.00 11216000/180923/31354 18.09.2023',
            '10000.00 11216000/180923/31353 18.09.2023',
            '5000.00 11216000/180923/31354 18.09.2023',
            '10000.00 11216000/180923/31353 18.09.2023',
            '5000.00 11216000/180923/31354 18.09.2023',
            '10000.00 11216000/180923/31353 18.09.2023',
            '5000.00 11216000/180923/31354 18.09.2023',
        ]
        self.g52_2 = [
            '03',
            '03',
            '03',
            '03',
            '03',
            '03',
            '03',
            '03',
        ]

        self.g53 = '112 07208 БИГОСОВО-1 / 07208/ВЗ7475723'

        self.g55_1_place = 'ЛИДА БЕЛАРУСЬ / 112 / 16421'
        self.g55_1_ts_1 = '1: B2222B2/CC33333'
        self.g55_1_ts_2 = 'BY'
        self.g55_1_cont_1 = '1'
        self.g55_1_cont_2 = 'NEW_CONTAINER'

        self.g55_2_place = 'МОСКВА РОССИЯ / 643 / 10130130'
        self.g55_2_ts_1 = '1: P443PP777'
        self.g55_2_ts_2 = 'RU'
        self.g55_2_cont_1 = '0'
        self.g55_2_cont_2 = None

        self.gA = 'BY/130923/000574314'
        self.gC = '112 07208 БИГОСОВО-1'
        self.gD = '112 07208 БИГОСОВО-1 / 07208/ВЗ7475723'

    def load_from_db(self, idxml):
        x = XMLModel.objects.get(pk=idxml)

        self.g1_1 = x.DeclarationKindCode  # всегда [ТТ]
        self.g1_2 = x.TransitFeatureCode  # чаще пустое, варианты - [ФЛ, СП, МП, ВН, ГП]
        self.g1_3 = x.TransitProcedureCode  # тип транзита - [ИМ, ТР, ТС]
        _list = [
                    x.Consignor_TaxpayerId,
                    dataCountry[x.Consignor_UnifiedCountryCode],
                    x.Consignor_RegionName,
                    x.Consignor_CityName,
                    x.Consignor_StreetName,
                    x.Consignor_BuildingNumberId,
                    x.Consignor_RoomNumberId,
                ]
        self.g2 = [x.Consignor_SubjectBriefName,
                   ', '.join(item for item in _list if item)]  # отправитель
        self.g4 = None  # отгр. спецификация (страый формат)
        self.g5 = str(x.GoodsQuantity or '')  # всего товаров
        self.g6 = str(x.CargoQuantity or '')  # всего мест
        self.g7 = None  # справочный номер [ПТД]
        _list = [
                    x.Consignee_TaxpayerId,
                    dataCountry[x.Consignee_UnifiedCountryCode],
                    x.Consignee_RegionName,
                    x.Consignee_CityName,
                    x.Consignee_StreetName,
                    x.Consignee_BuildingNumberId,
                    x.Consignee_RoomNumberId,
                ]
        self.g8 = [x.Consignee_SubjectBriefName,
                   ', '.join(item for item in _list if item)]  # получатель
        self.g9 = [  # таможенный представитель
            None,  # номер в реестре
            None,  # номер договора ДЕКЛАРАНТА с тамож. представителем
            None,  # документ подтверждающий полномочия руководителя или номер аттестата
            None,  # доверенность
        ]
        self.g14 = [  # декларант
            None,  # наименование
            None,    # адрес
            None,  # номер таможенного перевозчика или УЭО
        ]
        self.g15 = x.DepartureCountry_ShortCountryName  # страна отправления
        self.g17 = x.DestinationCountry_ShortCountryName  # страна назначения

        _query = TransportXML.objects.filter(xml=x)
        _n = TransportXML.objects.filter(xml=x).count()
        _s = '/'.join([_q.TransportMeansRegId for _q in _query])
        self.g18_1 = str(_n or '') + ': ' + _s  # транспорт

        self.g18_2 = _query[0].countryCode  # страна регистрации транспорта
        self.g19 = x.ContainerIndicator  # контейнер [0, 1]
        self.g20 = None  # пломбы
        self.g21_1 = None  # транспорт
        self.g21_2 = None  # страна регистрации транспорта
        self.g22_1 = x.IVA_currencyCode  # код валюты
        self.g22_2 = str(x.CAInvoiceValueAmount or '')  # сумма по счету
        self.g25 = x.UnifiedTransportModeCode  # тип транспорта

        self.items = []
        _items = ConsignmentItem.objects.filter(xml=x)
        for _i in _items:
            item = Item()
            item.load_from_db(_i)
            self.items.append(item)

        _list = [
            x.TransitDeclarant_SubjectBriefName,
            x.TransitDeclarant_TaxpayerId,
            dataCountry[x.TransitDeclarant_UnifiedCountryCode],
            x.TransitDeclarant_RegionName,
            x.TransitDeclarant_CityName,
            x.TransitDeclarant_StreetName,
            x.TransitDeclarant_BuildingNumberId,
            x.TransitDeclarant_RoomNumberId,
        ]
        self.g50_d = x.TransitDeclarant_SubjectBriefName
        if x.UnionCarrier_SubjectBriefName:
            _list1 = [
                x.UnionCarrier_SubjectBriefName,
                x.UnionCarrier_TaxpayerId,
                dataCountry[x.UnionCarrier_UnifiedCountryCode],
                x.UnionCarrier_RegionName,
                x.UnionCarrier_CityName,
                x.UnionCarrier_StreetName,
                x.UnionCarrier_BuildingNumberId,
                x.UnionCarrier_RoomNumberId,
            ]
            self.g50_c = x.UnionCarrier_SubjectBriefName
        else:
            _list1 = [
                x.Carrier_SubjectBriefName,
                x.Carrier_TaxpayerId,
                dataCountry[x.Carrier_UnifiedCountryCode],
                x.Carrier_RegionName,
                x.Carrier_CityName,
                x.Carrier_StreetName,
                x.Carrier_BuildingNumberId,
                x.Carrier_RoomNumberId,
            ]
            self.g50_c = x.Carrier_SubjectBriefName
        self.g50 = [  # принципал (декларант) и перевозчик
            ', '.join(item for item in _list if item),
            ', '.join(item for item in _list1 if item),
        ]

        _list = [
            x.CarrierRepresentative_LastName,
            x.CarrierRepresentative_FirstName,
            x.CarrierRepresentative_DocId,
            date_convert_for_print(x.CarrierRepresentative_DocCreationDate),
        ]
        self.g50_v_fio = ' '.join(item for item in [
            x.CarrierRepresentative_LastName,
            x.CarrierRepresentative_FirstName,
        ] if item)

        self.g50_v1 = 'ВОДИТЕЛЬ: ' + ' '.join(item for item in _list if item)
        self.g50_v2 = 'Представленный: ' + ''
        self.g51 = 'Место и дата: ' + date_convert_for_print(x.EDocDateTime)  # дата составления декларации

        self.g52_1 = []
        self.g52_2 = []
        _query = TransitGuarantee.objects.filter(xml_id=x)
        for _q in _query:
            _list = [
                g52_data_convert(str(_q.GuaranteeAmount or '')),
                g52_data_convert('/'.join(_i for _i in [
                    _q.GC_CustomsOfficeCode,
                    date_convert_for_sert(_q.GC_DocCreationDate),
                    _q.GC_CustomsDocumentId,
                ] if _i)),
                g52_data_convert(date_convert_for_print(_q.GC_DocCreationDate)),
                g52_data_convert('/'.join(_i for _i in [
                    _q.ES_TaxpayerId,
                    _q.ES_BankId,
                ] if _i)),
                g52_data_convert(_q.ES_SubjectBriefName),
            ]
            self.g52_2.append(g52_data_convert(_q.TransitGuaranteeMeasureCode))
            self.g52_1.append(' '.join(item for item in _list if item))

        _list = [
            x.TT_CustomsOfficeCode,
            x.TT_CustomsOfficeName,
            x.TT_CustomsControlZoneId
        ]

        self.g53 = ' '.join(item for item in _list if item)
        self.gD = ' '.join(item for item in _list if item)

        _query = Transhipment.objects.filter(xml_id=x)

        if len(_query) > 0:
            _q = _query[0]

            _list = [
                _q.CustomsOfficeName,
                _q.PlaceName,
                _q.ShortCountryName
            ]

            self.g55_1_place = ' '.join(item for item in _list if item)

            _t = TransportTranshipment.objects.filter(transhipment_xml=_q)
            if len(_t) > 0:
                self.g55_1_ts_1 = str(len(_t) or '') + ': ' + '/'.join(item.TransportMeansRegId for item in _t if item.TransportMeansRegId)
                self.g55_1_ts_2 = _t[0].countryCode
            else:
                self.g55_1_ts_1 = None
                self.g55_1_ts_2 = None

            self.g55_1_cont_1 = _q.ContainerIndicator
            _c = ContainerTranshipment.objects.filter(transhipment_xml=_q)
            if len(_c) > 0:
                self.g55_1_cont_2 = ' '.join(item.ContainerId for item in _c if item.ContainerId)
            else:
                self.g55_1_cont_2 = None
        else:
            self.g55_1_place = None
            self.g55_1_ts_1 = None
            self.g55_1_ts_2 = None
            self.g55_1_cont_1 = None
            self.g55_1_cont_2 = None

        if len(_query) > 1:
            _q = _query[1]

            _list = [
                _q.CustomsOfficeName,
                _q.PlaceName,
                _q.ShortCountryName
            ]

            self.g55_2_place = ' '.join(item for item in _list if item)

            _t = TransportTranshipment.objects.filter(transhipment_xml=_q)
            if len(_t) > 0:
                self.g55_2_ts_1 = str(len(_t) or '') + ': ' + '/'.join(
                    item.TransportMeansRegId for item in _t if item.TransportMeansRegId)
                self.g55_2_ts_2 = _t[0].countryCode
            else:
                self.g55_2_ts_1 = None
                self.g55_2_ts_2 = None

            self.g55_2_cont_1 = _q.ContainerIndicator
            _c = ContainerTranshipment.objects.filter(transhipment_xml=_q)
            if len(_c) > 0:
                self.g55_2_cont_2 = ' '.join(item.ContainerId for item in _c if item.ContainerId)
            else:
                self.g55_2_cont_2 = None
        else:
            self.g55_2_place = None
            self.g55_2_ts_1 = None
            self.g55_2_ts_2 = None
            self.g55_2_cont_1 = None
            self.g55_2_cont_2 = None

        self.gA = None  # нету этого поля в БД (номер ЭПИ)

        _list = [
            x.ECP_CustomsOfficeCode,
            x.ECP_BorderCheckpointName,
        ]
        self.gC = ' '.join(item for item in _list if item)
