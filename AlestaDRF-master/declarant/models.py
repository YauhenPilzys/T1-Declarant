from django.contrib.auth.models import User
from django.db import models


#######################################################################
# модели, для хранения основных данных в БД и подстановки в XML
#######################################################################

# декларант, перевозчик и перевозчик по ТТ ЕАЭС
#from declarant.refresh_records import refresh_db


class DeclarantCarrier(models.Model):
    SubjectBriefName = models.CharField(max_length=120, blank=False)
    TaxpayerId = models.CharField(max_length=20, blank=True, null=True)
    UnifiedCountryCode = models.CharField(max_length=2, blank=False)
    RegionName = models.CharField(max_length=120, blank=True, null=True)
    CityName = models.CharField(max_length=120, blank=False)
    StreetName = models.CharField(max_length=120, blank=False)
    BuildingNumberId = models.CharField(max_length=50, blank=True, null=True)
    RoomNumberId = models.CharField(max_length=20, blank=True, null=True)


# отправитель, получатель
class ConsignorConsignee(models.Model):
    SubjectBriefName = models.CharField(max_length=120, blank=False)
    TaxpayerId = models.CharField(max_length=20, blank=True, null=True)
    UnifiedCountryCode = models.CharField(max_length=2, blank=False)
    RegionName = models.CharField(max_length=120, blank=True, null=True)
    CityName = models.CharField(max_length=120, blank=False)
    StreetName = models.CharField(max_length=120, blank=False)
    BuildingNumberId = models.CharField(max_length=50, blank=True, null=True)
    RoomNumberId = models.CharField(max_length=20, blank=True, null=True)


# Лицо, предоставившее ПИ
class PIDeclarant(models.Model):
    SubjectBriefName = models.CharField(max_length=120, blank=False)
    TaxpayerId = models.CharField(max_length=20, blank=False, null=True)
    UnifiedCountryCode = models.CharField(max_length=2, blank=False)
    RegionName = models.CharField(max_length=120, blank=True, null=True)
    CityName = models.CharField(max_length=120, blank=False)
    StreetName = models.CharField(max_length=120, blank=False)
    BuildingNumberId = models.CharField(max_length=50, blank=True, null=True)
    RoomNumberId = models.CharField(max_length=20, blank=True, null=True)
    RegistrationNumberId = models.CharField(max_length=50, blank=False)


# водитель (или принципал для ТД)
class CarrierRepresentative(models.Model):
    FirstName = models.CharField(max_length=120, blank=False)
    MiddleName = models.CharField(max_length=120, blank=True, null=True)
    LastName = models.CharField(max_length=120, blank=False)
    PositionName = models.CharField(max_length=120, default='ВОДИТЕЛЬ')
    UnifiedCountryCode = models.CharField(max_length=2, blank=False)
    IdentityDocKindCode = models.CharField(max_length=7, blank=False)
    DocId = models.CharField(max_length=50, blank=False)
    DocCreationDate = models.DateField(blank=False)
    DocValidityDate = models.DateField(blank=True, null=True)
    # ниже поля только для принципала ТД
    QualificationCertificateId = models.CharField(max_length=6, blank=True, null=True)
    POA_DocKindCode = models.CharField(max_length=5, blank=True, null=True)
    POA_DocId = models.CharField(max_length=50, blank=True, null=True)
    POA_DocCreationDate = models.DateField(blank=True, null=True)
    POA_DocValidityDate = models.DateField(blank=True, null=True)

# транспортные средства
class Transport(models.Model):
    TransportMeansRegId = models.CharField(max_length=40, blank=False)
    countryCode = models.CharField(max_length=2, blank=False)
    VehicleId = models.CharField(max_length=40, blank=False)
    TransportTypeCode = models.CharField(max_length=3, blank=False)
    VehicleMakeCode = models.CharField(max_length=3, blank=False)
    VehicleMakeName = models.CharField(max_length=25, blank=False)
    VehicleModelName = models.CharField(max_length=250, blank=True, null=True)
    DocId = models.CharField(max_length=50, blank=True, null=True)
    Carrier = models.ForeignKey(DeclarantCarrier, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('TransportMeansRegId', 'Carrier', 'TransportTypeCode')


class TreeTnved(models.Model):
    #ParentID - ссылка на родительский элемент дерева или null для корневых элементов.
    ParentID = models.ForeignKey('self', null=True, on_delete=models.CASCADE)

    # Name - наименование элемента дерева
    Name = models.CharField(max_length=1000, blank=False)

    # Code - форматированный код элемента дерева (может отсутствовать!)
    Code = models.CharField(max_length=13, null=True)

    # DateFrom - дата начала действия элемента, если она установлена. YYYY-MM-DD.
    DateFrom = models.DateTimeField(null=True)

    # DateTo - дата завершения действия элемента, если она установлена. YYYY-MM-DD.
    DateTo = models.DateTimeField(null=True)


# коды ТН ВЭД и тарифы
class Tnved(models.Model):
    TreeID = models.ForeignKey(TreeTnved, on_delete=models.CASCADE)
    Name = models.CharField(max_length=1000, blank=False)    # "чистопородные племенные животные: 🡺 коровы",
    Code = models.CharField(max_length=13, blank=False)     # "0102 21 300 0",

    # текстовое представление таможенного тарифа, действующего на дату запроса.
    # Например "5%", "15%, но не менее 0,15 EUR за 1кг", "8,2% плюс 0,4 EUR за 1 шт" и т.п.
    TariffText = models.CharField(max_length=50, blank=False)

    # адвалорная ставка действующего таможенного тарифа в процентах.
    # Если адвалорная ставка не установлена, поле отсутствует
    TariffAdvalor = models.FloatField(null=True, blank=True)

    # специфическая ставка действующего таможенного тарифа в единицах валюты.
    # Если специфическая ставка не установлена, поле отсутствует
    TariffSpecific = models.FloatField(null=True, blank=True)

    # валюта, в которой указана ставка действующего таможенного тарифа, текстовый трёхбуквенный код.
    # Например, "EUR", "USD" и т.п.
    # Если специфическая ставка не установлена, поле отсутствует.
    TariffSpecificCurrency = models.CharField(max_length=3, null=True, blank=True)

    # Количество единиц измерения, за которое установлена специфическая
    # ставка действующего таможенного тарифа.
    # Если специфическая ставка не установлена, поле отсутствует
    TariffSpecificMeasureAmount = models.DecimalField(null=True, blank=True, max_digits=8, decimal_places=2)

    # Единица измерения, за которую установлена специфическая ставка действующего
    # таможенного тарифа, краткое наименование. Например "кг", "шт" и т.п.
    # Если специфическая ставка не установлена, поле отсутствует
    TariffSpecificMeasureUnit = models.CharField(null=True, max_length=20, blank=True)

    # Признак сложения адвалорной и специфической ставок действующего таможенного тарифа.
    # Если заданы обе ставки и это поле установлено в "1", то тариф сформулирован
    # в виде "X% плюс Y [валюта] за Z [единица измерения]". Если заданы обе ставки и это поле отсутствует,
    # то тариф сформулирован в виде "X%, но не менее Y [валюта] за Z [единица измерения]".
    TariffSpecificAddedToAdvalor = models.CharField(null=True, max_length=1, blank=True)

    # Дополнительная единица измерения, краткое наименование. Например "кг", "шт" и т.п.
    # Если дополнительная единица к коду ТНВЭД не установлена, поле отсутствует
    AdditionalMeasureUnit = models.CharField(null=True, max_length=20, blank=True)

    # Признак наличия (1 = да) действующих антидемпинговых пошлин для кода ТНВЭД.
    # Для более подробной информации можно выполнить запрос R12.
    # Если антидемпинговые пошлины к коду ТНВЭД не добавлены, поле отсутствует.
    Ad = models.CharField(null=True, max_length=1, blank=True)

    # Признак наличия (1 = да) действующих специальных тарифов для кода ТНВЭД.
    # Для более подробной информации можно выполнить запрос R12.
    # Если специальные тарифы к коду ТНВЭД не добавлены, поле отсутствует.
    Sp = models.CharField(null=True, max_length=1, blank=True)

    # Признак наличия (1 = да) действующих в Республике Беларусь акцизов для кода ТНВЭД.
    # Для более подробной информации можно выполнить запрос R12.
    # Если акцизы к коду ТНВЭД не добавлены, поле отсутствует.
    Ex = models.CharField(null=True, max_length=1, blank=True)

    # Признак наличия (1 = да) действующих в Республике Беларусь записей таможенного реестра
    # интеллектуальной собственности для кода ТНВЭД. Для более подробной информации выполнить запрос R12.
    # Если записей таможенного реестра интеллектуальной собственности к коду ТНВЭД не добавлены, поле отсутствует
    Ip = models.CharField(null=True, max_length=1, blank=True)

    # действующая ставка сбора за таможенное оформление
    F = models.DecimalField(null=True, blank=True, max_digits=8, decimal_places=2)

    # Признак наличия (1 = да) действующих в Республике Беларусь кодов дополнительной таможенной информации
    # для кода ТНВЭД. Для более подробной информации можно посетить страницу, адрес которой указан в поле URL
    # или выполнить запрос R12. Если коды дополнительной таможенной информации к коду ТНВЭД не добавлены,
    # это поле отсутствует.
    Ta = models.CharField(null=True, max_length=1, blank=True)

    # Дата начала действия кода ТНВЭД, если она установлена. YYYY-MM-DD.
    DateFrom = models.DateField(null=True)

    # Дата завершения действия кода ТНВЭД, если она установлена. YYYY-MM-DD.
    DateTo = models.DateField(null=True)


# акцизы для кодов ТН ВЭД
class Excise(models.Model):
    # связь с таблицой кодов ТН ВЭД
    TnvedID = models.ForeignKey(Tnved, on_delete=models.CASCADE)

    # Наименование акциза
    Name = models.CharField(max_length=1000, blank=False)

    # Дата начала действия ставки акциза
    DateFrom = models.DateField(null=True)

    # Дата завершения действия ставки акциза
    DateTo = models.DateField(null=True)

    # Специфическая ставка акциза
    Rate = models.FloatField(null=True, blank=True)

    # Текстовый трёхбуквенный код валюты специфической ставки в соответствии с Классификатором валют
    Currency = models.CharField(max_length=3, blank=True)

    # Количество товара, за которое установлена специфическая ставка акциза
    Amount = models.DecimalField(null=True, blank=True, max_digits=8, decimal_places=2)

    # Единица измерения, за которую установлена специфическая ставка акциза, краткое наименование.
    # Например “кг”, “шт” и т.п.
    MeasureUnit = models.CharField(null=True, max_length=20, blank=True)

    # Полное текстовое представление ставки акциза (для отображения). Например “0,15 EUR за 1кг”
    RateText = models.CharField(max_length=100, blank=False)


#######################################################################
# модели, непосредственно относящиеся к формированию XML
#######################################################################

# перецепки
class Transhipment(models.Model):
    CargoOperationKindCode = models.CharField(max_length=1, blank=True, null=True)
    ContainerIndicator = models.CharField(max_length=1, blank=False)
    CACountryCode = models.CharField(max_length=2, blank=False)
    ShortCountryName = models.CharField(max_length=40, blank=False)
    PlaceName = models.CharField(max_length=120, blank=True, null=True)
    CustomsOfficeCode = models.CharField(max_length=43, blank=True, null=True)
    CustomsOfficeName = models.CharField(max_length=50, blank=True, null=True)
    UnifiedTransportModeCode = models.CharField(max_length=2, blank=False)
    RegistrationNationalityCode = models.CharField(max_length=2, blank=False)
    TransportMeansQuantity = models.IntegerField(blank=False)
    # внешний ключ
    xml = models.ForeignKey('XMLModel', on_delete=models.CASCADE)


# транспорт в перецепке
class TransportTranshipment(models.Model):
    TransportMeansRegId = models.CharField(max_length=40, blank=False)
    countryCode = models.CharField(max_length=2, blank=False)
    TransportTypeCode = models.CharField(max_length=3, blank=False)
    # внешний ключ
    transhipment_xml = models.ForeignKey(Transhipment, on_delete=models.CASCADE)


# контейнеры в перецепке
class ContainerTranshipment(models.Model):
    ContainerId = models.CharField(max_length=17, blank=False)
    # внешний ключ
    transhipment_xml = models.ForeignKey(Transhipment, on_delete=models.CASCADE)


# гаранты в XML
class TransitGuarantee(models.Model):
    TransitGuaranteeMeasureCode = models.CharField(max_length=2, blank=False)
    GuaranteeAmount = models.DecimalField(blank=True, null=True, max_digits=11, decimal_places=1)
    currencyCode = models.CharField(max_length=3, blank=True, default='BYN', null=True)
    # секция для номера сертификата
    GC_CustomsOfficeCode = models.CharField(max_length=8, blank=True, null=True)
    GC_DocCreationDate = models.DateField(blank=True, null=True)
    GC_CustomsDocumentId = models.CharField(max_length=10, blank=True, null=True)
    # секция для подтверждающего документа
    RD_UnifiedCountryCode = models.CharField(max_length=2, blank=True, null=True)
    RD_RegistrationNumberId = models.CharField(max_length=50, blank=True, null=True)
    # секция для таможенного сопровождения
    ES_SubjectBriefName = models.CharField(max_length=120, blank=True, null=True)
    ES_TaxpayerId = models.CharField(max_length=20, blank=True, null=True)
    ES_BankId = models.CharField(max_length=9, blank=True, null=True)
    # внешний ключ
    xml = models.ForeignKey('XMLModel', on_delete=models.CASCADE)


# транспорт в XML
class TransportXML(models.Model):
    TransportMeansRegId = models.CharField(max_length=40, blank=False)
    countryCode = models.CharField(max_length=2, blank=False)
    VehicleId = models.CharField(max_length=40, blank=False)
    TransportTypeCode = models.CharField(max_length=3, blank=False)
    VehicleMakeCode = models.CharField(max_length=3, blank=False)
    VehicleMakeName = models.CharField(max_length=25, blank=False, null=True)
    VehicleModelName = models.CharField(max_length=250, blank=True, null=True)
    DocId = models.CharField(max_length=50, blank=True, null=True)
    # внешний ключ
    xml = models.ForeignKey('XMLModel', on_delete=models.CASCADE)


# контейнеры в XML
class ContainerXML(models.Model):
    ContainerId = models.CharField(max_length=17, blank=False)
    # внешний ключ
    xml = models.ForeignKey('XMLModel', on_delete=models.CASCADE)


# товары в XML
class ConsignmentItem(models.Model):
    ConsignmentItemOrdinal = models.PositiveIntegerField(blank=False)
    CommodityCode = models.CharField(max_length=10, blank=True, null=True)
    GoodsDescriptionText = models.CharField(max_length=250, blank=True, null=True)
    GoodsDescriptionText1 = models.CharField(max_length=250, blank=True, null=True)
    GoodsDescriptionText2 = models.CharField(max_length=250, blank=True, null=True)
    GoodsDescriptionText3 = models.CharField(max_length=250, blank=True, null=True)
    UnifiedGrossMassMeasure = models.DecimalField(blank=True, null=True, max_digits=17, decimal_places=6)
    measurementUnitCode = models.CharField(max_length=3, blank=True, default='166')
    # GoodsMeasureDetails
    GM_GoodsMeasure = models.DecimalField(blank=True, null=True, max_digits=17, decimal_places=6)
    GM_measurementUnitCode = models.CharField(max_length=3, blank=True, null=True)
    GM_MeasureUnitAbbreviationCode = models.CharField(max_length=20, blank=True, null=True)
    # AddGoodsMeasureDetails
    AGM_GoodsMeasure = models.DecimalField(blank=True, null=True, max_digits=17, decimal_places=6)
    AGM_measurementUnitCode = models.CharField(max_length=3, blank=True, null=True)
    AGM_MeasureUnitAbbreviationCode = models.CharField(max_length=20, blank=True, null=True)
    # CargoPackagePalletDetails
    PackageAvailabilityCode = models.CharField(max_length=1, default='0')
    CargoQuantity = models.PositiveIntegerField(blank=False)
    CargoPackageInfoKindCode = models.CharField(max_length=1, default='0')
    PackageKindCode = models.CharField(max_length=2, blank=False)
    PackageQuantity = models.PositiveIntegerField(blank=False)
    # стоимость
    CAValueAmount = models.DecimalField(blank=True, null=True, max_digits=17, decimal_places=2)
    currencyCode = models.CharField(max_length=3, blank=True, null=True)
    # внешний ключ
    xml = models.ForeignKey('XMLModel', on_delete=models.CASCADE)

    # поля только в ТДrgnm
    GoodsTraceabilityCode = models.CharField(max_length=1, blank=True, null=True)
    LicenseGoodsKindCode = models.CharField(max_length=1, blank=True, null=True)
    # кол-во отслеживаемого товара
    TM_GoodsMeasure = models.DecimalField(blank=True, null=True, max_digits=17, decimal_places=6)
    TM_measurementUnitCode = models.CharField(max_length=3, blank=True, null=True)
    TM_MeasureUnitAbbreviationCode = models.CharField(max_length=20, blank=True, null=True)
    # таможенная стоимость
    CustomsValueAmount = models.DecimalField(blank=True, null=True, max_digits=17, decimal_places=2)
    CV_currencyCode = models.CharField(max_length=3, blank=True, null=True, default='BYN')

# контейнеры в товаре
class ContainerCI(models.Model):
    ContainerId = models.CharField(max_length=17, blank=False)
    # внешний ключ на товар
    ci = models.ForeignKey(ConsignmentItem, on_delete=models.CASCADE)


# предшедствующие документы
class PIPrecedingDocDetails(models.Model):
    DocKindCode = models.CharField(max_length=5, blank=False)
    DocId = models.CharField(max_length=50, blank=False)
    DocCreationDate = models.DateField(blank=False)
    ConsignmentItemOrdinal = models.PositiveIntegerField(blank=True, null=True)  # только для ТД
    # внешний ключ на товар
    ci = models.ForeignKey(ConsignmentItem, on_delete=models.CASCADE)

# документы в товаре
class PIGoodsDocDetails(models.Model):
    DocKindCode = models.CharField(max_length=5, blank=False)
    DocId = models.CharField(max_length=50, blank=False)
    DocCreationDate = models.DateField(blank=False)
    # внешний ключ на товар
    ci = models.ForeignKey(ConsignmentItem, on_delete=models.CASCADE)


# основная информация в XML
class XMLModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_DEFAULT, default=1)
    XmlType = models.CharField(max_length=4, blank=False, default='PIAT')
    EDocCode = models.CharField(max_length=10, default='R.042')
    EDocId = models.CharField(max_length=36, blank=False)
    EDocDateTime = models.DateTimeField(auto_now_add=True)
    EDocIndicatorCode = models.CharField(max_length=2, blank=False)
    PreliminaryInformationUsageCode1 = models.CharField(max_length=2, blank=False, default='01')
    PreliminaryInformationUsageCode2 = models.CharField(max_length=2, blank=False, default='06')
    PreliminaryInformationUsageCode3 = models.CharField(max_length=2, blank=False, default='14')

    # PIATEntryCheckPointDetails
    ECP_CustomsOfficeCode = models.CharField(max_length=8, blank=True, null=True)
    ECP_BorderCheckpointName = models.CharField(max_length=50, blank=True, null=True)

    # PIDeclarantDetails
    PIDeclarant_SubjectBriefName = models.CharField(max_length=120, blank=False)
    PIDeclarant_TaxpayerId = models.CharField(max_length=20, blank=True, null=True)
    PIDeclarant_UnifiedCountryCode = models.CharField(max_length=2, blank=False)
    PIDeclarant_RegionName = models.CharField(max_length=120, blank=True, null=True)
    PIDeclarant_CityName = models.CharField(max_length=120, blank=False)
    PIDeclarant_StreetName = models.CharField(max_length=120, blank=False)
    PIDeclarant_BuildingNumberId = models.CharField(max_length=50, blank=True, null=True)
    PIDeclarant_RoomNumberId = models.CharField(max_length=20, blank=True, null=True)
    PIDeclarant_RegistrationNumberId = models.CharField(max_length=50, blank=False)

    # PIATBorderTransportDetails и PITransitTransportMeansDetails
    UnifiedTransportModeCode = models.CharField(max_length=2, blank=False)
    TransportMeansQuantity = models.PositiveSmallIntegerField(blank=False)
    ContainerIndicator = models.CharField(max_length=1, default='0')
    Transport_EqualIndicator = models.CharField(max_length=1, default='1')

    # TIRCarnetIdDetails
    TIRCarnetIndicator = models.CharField(max_length=1, blank=False)
    TIRSeriesId = models.CharField(max_length=2, blank=True, null=True)
    TIRId = models.CharField(max_length=8, blank=True, null=True)
    TIRPageOrdinal = models.PositiveSmallIntegerField(blank=True, null=True)
    TIRHolderId = models.CharField(max_length=18, blank=True, null=True)

    DeclarationKindCode = models.CharField(max_length=10, blank=False)
    TransitProcedureCode = models.CharField(max_length=10, blank=False)
    TransitFeatureCode = models.CharField(max_length=10, blank=True, null=True)

    LoadingListsQuantity = models.PositiveIntegerField(blank=True, null=True)
    LoadingListsPageQuantity = models.PositiveIntegerField(blank=True, null=True)
    GoodsQuantity = models.PositiveIntegerField(blank=False)
    CargoQuantity = models.PositiveIntegerField(blank=False)
    SealQuantity = models.PositiveIntegerField(blank=True, null=True)
    SealId = models.CharField(max_length=120, blank=True, null=True)

    # TransitTerminationDetails
    TT_CustomsOfficeCode = models.CharField(max_length=8, blank=False)
    TT_CustomsOfficeName = models.CharField(max_length=50, blank=False)
    TT_CustomsControlZoneId = models.CharField(max_length=50, blank=True, null=True)
    TT_UnifiedCountryCode = models.CharField(max_length=2, blank=False, null=True)

    # PIATTransportDocumentDetails
    TD_DocKindCode = models.CharField(max_length=5, blank=True)
    TD_DocId = models.CharField(max_length=50, blank=True)
    TD_DocCreationDate = models.DateField(blank=True, null=True)

    # DepartureCountryDetails
    DepartureCountry_CACountryCode = models.CharField(max_length=2, blank=False)
    DepartureCountry_ShortCountryName = models.CharField(max_length=40, blank=False)

    # DestinationCountryDetails
    DestinationCountry_CACountryCode = models.CharField(max_length=2, blank=False)
    DestinationCountry_ShortCountryName = models.CharField(max_length=40, blank=False)

    CAInvoiceValueAmount = models.DecimalField(blank=False, default=0, max_digits=17, decimal_places=2)
    IVA_currencyCode = models.CharField(max_length=3, blank=False, default='EUR')
    UnifiedGrossMassMeasure = models.DecimalField(blank=False, default=0, max_digits=17, decimal_places=6)
    measurementUnitCode = models.CharField(max_length=3, blank=False, default='166')

    # ОТПРАВИТЕЛЬ
    # PIATConsignorDetails
    Consignor_SubjectBriefName = models.CharField(max_length=120, blank=False)
    Consignor_TaxpayerId = models.CharField(max_length=20, blank=True, null=True)
    Consignor_UnifiedCountryCode = models.CharField(max_length=2, blank=False)
    Consignor_RegionName = models.CharField(max_length=120, blank=True, null=True)
    Consignor_CityName = models.CharField(max_length=120, blank=False)
    Consignor_StreetName = models.CharField(max_length=120, blank=False)
    Consignor_BuildingNumberId = models.CharField(max_length=50, blank=True, null=True)
    Consignor_RoomNumberId = models.CharField(max_length=20, blank=True, null=True)

    # ПОЛУЧАТЕЛЬ
    # PIATConsigneeDetails
    Consignee_SubjectBriefName = models.CharField(max_length=120, blank=False)
    Consignee_TaxpayerId = models.CharField(max_length=20, blank=True, null=True)
    Consignee_UnifiedCountryCode = models.CharField(max_length=2, blank=False)
    Consignee_RegionName = models.CharField(max_length=120, blank=True, null=True)
    Consignee_CityName = models.CharField(max_length=120, blank=False)
    Consignee_StreetName = models.CharField(max_length=120, blank=False)
    Consignee_BuildingNumberId = models.CharField(max_length=50, blank=True, null=True)
    Consignee_RoomNumberId = models.CharField(max_length=20, blank=True, null=True)

    # ДЕКЛАРАНТ
    # PITransitDeclarantDetails
    TransitDeclarant_EqualIndicator = models.CharField(max_length=1, default='0')
    TransitDeclarant_SubjectBriefName = models.CharField(max_length=120, blank=False)
    TransitDeclarant_TaxpayerId = models.CharField(max_length=20, blank=True, null=True)
    TransitDeclarant_UnifiedCountryCode = models.CharField(max_length=2, blank=False)
    TransitDeclarant_RegionName = models.CharField(max_length=120, blank=True, null=True)
    TransitDeclarant_CityName = models.CharField(max_length=120, blank=False)
    TransitDeclarant_StreetName = models.CharField(max_length=120, blank=False)
    TransitDeclarant_BuildingNumberId = models.CharField(max_length=50, blank=True, null=True)
    TransitDeclarant_RoomNumberId = models.CharField(max_length=20, blank=True, null=True)

    # ПЕРЕВОЗЧИК ПО ТТ ЕАЭС
    # PIUnionCarrierDetails
    UnionCarrier_SubjectBriefName = models.CharField(max_length=120, blank=False)
    UnionCarrier_TaxpayerId = models.CharField(max_length=20, blank=True, null=True)
    UnionCarrier_UnifiedCountryCode = models.CharField(max_length=2, blank=False)
    UnionCarrier_RegionName = models.CharField(max_length=120, blank=True, null=True)
    UnionCarrier_CityName = models.CharField(max_length=120, blank=False)
    UnionCarrier_StreetName = models.CharField(max_length=120, blank=False)
    UnionCarrier_BuildingNumberId = models.CharField(max_length=50, blank=True, null=True)
    UnionCarrier_RoomNumberId = models.CharField(max_length=20, blank=True, null=True)

    # ПЕРЕВОЗЧИК
    # CarrierRepresentativeDetails
    CarrierRepresentative_FirstName = models.CharField(max_length=120, blank=False)
    CarrierRepresentative_MiddleName = models.CharField(max_length=120, blank=True, null=True)
    CarrierRepresentative_LastName = models.CharField(max_length=120, blank=False)
    CarrierRepresentative_PositionName = models.CharField(max_length=120, default='ВОДИТЕЛЬ')
    CarrierRepresentative_UnifiedCountryCode = models.CharField(max_length=2, blank=False)
    CarrierRepresentative_IdentityDocKindCode = models.CharField(max_length=7, blank=True, null=True)
    CarrierRepresentative_DocId = models.CharField(max_length=50, blank=False)
    CarrierRepresentative_DocCreationDate = models.DateField(blank=False)
    CarrierRepresentative_DocValidityDate = models.DateField(blank=True, null=True)
    CarrierRepresentative_RoleCode = models.CharField(max_length=1, default='1')

    # PIATCarrierDetails
    Carrier_SubjectBriefName = models.CharField(max_length=120, blank=False)
    Carrier_TaxpayerId = models.CharField(max_length=20, blank=True, null=True)
    Carrier_UnifiedCountryCode = models.CharField(max_length=2, blank=False)
    Carrier_RegionName = models.CharField(max_length=120, blank=True, null=True)
    Carrier_CityName = models.CharField(max_length=120, blank=False)
    Carrier_StreetName = models.CharField(max_length=120, blank=False)
    Carrier_BuildingNumberId = models.CharField(max_length=50, blank=True, null=True)
    Carrier_RoomNumberId = models.CharField(max_length=20, blank=True, null=True)

    # поля, специфичные для ТД
    SD_RegisterDocumentIdDetails_DocKindCode = models.CharField(max_length=5, null=True)
    SD_RegisterDocumentIdDetails_RegistrationNumberId = models.CharField(max_length=50, null=True)
    SD_RepresentativeContractDetails_DocKindCode = models.CharField(max_length=5, null=True)
    SD_RepresentativeContractDetails_DocId = models.CharField(max_length=50, null=True)
    SD_RepresentativeContractDetails_DocCreationDate = models.DateField(blank=True, null=True)
    SD_RepresentativeContractDetails_UnifiedCountryCode = models.CharField(max_length=2, blank=True, null=True)

    SP_FirstName = models.CharField(max_length=120, blank=True, null=True)
    SP_MiddleName = models.CharField(max_length=120, blank=True, null=True)
    SP_LastName = models.CharField(max_length=120, blank=True, null=True)
    SP_PositionName = models.CharField(max_length=120, blank=True, null=True)
    SP_UnifiedCountryCode = models.CharField(max_length=2, blank=True, null=True)
    SP_IdentityDocKindCode = models.CharField(max_length=7, blank=True, null=True)
    SP_DocId = models.CharField(max_length=50, blank=True, null=True)
    SP_DocCreationDate = models.DateField(blank=True, null=True)
    SP_DocValidityDate = models.DateField(blank=True, null=True)
    SP_QualificationCertificateId = models.CharField(max_length=6, blank=True, null=True)
    SP_POA_DocKindCode = models.CharField(max_length=5, blank=True, null=True)
    SP_POA_DocId = models.CharField(max_length=50, blank=True, null=True)
    SP_POA_DocCreationDate = models.DateField(blank=True, null=True)
    SP_POA_DocValidityDate = models.DateField(blank=True, null=True)

    #Контакты
    CD_CommunicationChannelCode = models.CharField(max_length=2, blank=True, null=True)
    CD_CommunicationChannelName = models.CharField(max_length=50, blank=True, null=True)
    CD_CommunicationChannelId = models.CharField(max_length=100, blank=True, null=True)

    TD_ExchangeRate = models.DecimalField(blank=False, default=0, max_digits=10, decimal_places=4)
    TD_ER_currencyCode = models.CharField(max_length=3, blank=False, default='EUR')
    TD_ER_scaleNumber = models.CharField(max_length=6, blank=False, default='0')
    TD_CustomsValueAmount = models.DecimalField(blank=False, default=0, max_digits=17, decimal_places=2)
    TD_CV_currencyCode = models.CharField(max_length=3, blank=False, default='BYN')

    transport_list = models.CharField(max_length=50, blank=True, null=True)

    def save(self, need_refresh=True, *args, **kwargs):
        super().save(*args, **kwargs)  # Call the "real" save() method.
        if need_refresh:
            refresh_db(self.id)



#######################################################################
# модели, для хранения дополнительной информации
#######################################################################

# курсы валют по НБРБ
class ExchangeRatesNBRB(models.Model):
    Cur_ID = models.PositiveIntegerField(blank=False)
    Date = models.DateTimeField(null=False)
    Cur_Abbreviation = models.CharField(max_length=3, blank=False)
    Cur_Scale = models.IntegerField(blank=False)
    Cur_Name = models.CharField(max_length=255, blank=False)
    Cur_OfficialRate = models.DecimalField(blank=False, max_digits=10, decimal_places=4)

    class Meta:
        unique_together = ('Cur_ID', 'Date',)


# для разных видов документов будут храниться разные параметры словаря nsmap
# (для формирования XML)
class NsMap(models.Model):
    xml_type = models.CharField(max_length=4, null=False, blank=False)  # тип xml ("ЭПИ", "ТД")
    name_field = models.CharField(max_length=15, null=False, blank=False)    # название поля (csdo, cacdo, atpi ...)
    text_field = models.CharField(max_length=70, null=False, blank=False)   # содержимое (пример "urn:EEC:M:SimpleDataObjects:v0.4.11")
    date_end = models.DateField(null=False)     # когда перестает действовать, при необходимости добавить новый элемент, в старом меняем дату


# справочник ПТО
class Pto(models.Model):
    CODE = models.CharField(max_length=8, null=False, blank=False)
    NAME = models.CharField(max_length=50, null=False, blank=False)
    COUNTRYCODEDIG = models.CharField(max_length=3, null=False, blank=False)
    COUNTRYCODELIT = models.CharField(max_length=2, null=False, blank=False)


class Sanction(models.Model):
    type = models.CharField(max_length=15, null=False, blank=False)
    code = models.CharField(max_length=10, null=False, blank=False)
    name_r = models.CharField(max_length=1000, null=False, blank=False)
    country = models.CharField(max_length=3, null=True, blank=True)
    sanction_type = models.CharField(max_length=30, null=True, blank=True)
    sanction_descr = models.CharField(max_length=700, null=True, blank=True)
    note = models.CharField(max_length=320, null=True, blank=True)


class DeclarantOrgInfo(models.Model):
    SubjectBriefName = models.CharField(max_length=200, null=False, blank=False)
    TaxpayerId = models.CharField(max_length=12, null=False, blank=False)
    UnifiedCountryCode = models.CharField(max_length=3, null=False, blank=False)
    RegionName = models.CharField(max_length=120, null=True, blank=True)
    CityName = models.CharField(max_length=120, null=False, blank=False)
    StreetName = models.CharField(max_length=120, null=False, blank=False)
    BuildingNumberId = models.CharField(max_length=50, null=True, blank=True)
    RoomNumberId = models.CharField(max_length=20, null=True, blank=True)
    RegistrationNumberId = models.CharField(max_length=50, null=False, blank=False)
    Email = models.CharField(max_length=50, null=True, blank=True)
    Phone = models.CharField(max_length=50, null=False, blank=False, help_text='!!! обязательно в формате +375 33 6262122')

    def __str__(self):
        return self.TaxpayerId + ' ' + self.SubjectBriefName

class UserOrg(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    org = models.ForeignKey(DeclarantOrgInfo, on_delete=models.DO_NOTHING)

    def __str__(self):
        return self.org.SubjectBriefName


class DraftJSON(models.Model):
    class Meta:
        ordering = ['-id']

    user = models.ForeignKey(User, on_delete=models.SET_DEFAULT, default=1)
    note = models.CharField(max_length=50, null=True, blank=True)
    dt_add = models.DateTimeField(auto_now_add=True, blank=True)
    json_data = models.TextField(null=False)

    def __str__(self):
        return self.note

def refresh_db(xml_id):
    """
    обновляем записи в справочниках
    @param xml_id: id записи с информацией для сохранения
    """

    xml = XMLModel.objects.get(pk=xml_id)

    # лицо, предоставившее ПИ
    if xml.PIDeclarant_TaxpayerId:
        try:
            rec = PIDeclarant.objects.get(TaxpayerId=xml.PIDeclarant_TaxpayerId)
        except:
            rec = None
    else:
        try:
            rec = PIDeclarant.objects.get(
                SubjectBriefName=xml.PIDeclarant_SubjectBriefName,
                UnifiedCountryCode=xml.PIDeclarant_UnifiedCountryCode
            )
        except:
            rec = None

    if not rec:
        rec = PIDeclarant()

    rec.SubjectBriefName = xml.PIDeclarant_SubjectBriefName
    rec.TaxpayerId = xml.PIDeclarant_TaxpayerId
    rec.UnifiedCountryCode = xml.PIDeclarant_UnifiedCountryCode
    rec.RegionName = xml.PIDeclarant_RegionName
    rec.CityName = xml.PIDeclarant_CityName
    rec.StreetName = xml.PIDeclarant_StreetName
    rec.BuildingNumberId = xml.PIDeclarant_BuildingNumberId
    rec.RoomNumberId = xml.PIDeclarant_RoomNumberId
    rec.RegistrationNumberId = xml.PIDeclarant_RegistrationNumberId
    rec.save()

    # декларант
    if xml.TransitDeclarant_TaxpayerId:
        try:
            rec = DeclarantCarrier.objects.get(TaxpayerId=xml.TransitDeclarant_TaxpayerId)
        except:
            rec = None
    else:
        try:
            rec = DeclarantCarrier.objects.get(
                SubjectBriefName=xml.TransitDeclarant_SubjectBriefName,
                UnifiedCountryCode=xml.TransitDeclarant_UnifiedCountryCode
            )
        except:
            rec = None

    if not rec:
        rec = DeclarantCarrier()

    rec.SubjectBriefName = xml.TransitDeclarant_SubjectBriefName
    rec.TaxpayerId = xml.TransitDeclarant_TaxpayerId
    rec.UnifiedCountryCode = xml.TransitDeclarant_UnifiedCountryCode
    rec.RegionName = xml.TransitDeclarant_RegionName
    rec.CityName = xml.TransitDeclarant_CityName
    rec.StreetName = xml.TransitDeclarant_StreetName
    rec.BuildingNumberId = xml.TransitDeclarant_BuildingNumberId
    rec.RoomNumberId = xml.TransitDeclarant_RoomNumberId
    rec.save()

    # перевозчик по ТТ ЕАЭС
    if xml.UnionCarrier_TaxpayerId:
        try:
            rec = DeclarantCarrier.objects.get(TaxpayerId=xml.UnionCarrier_TaxpayerId)
        except:
            rec = None
    else:
        try:
            rec = DeclarantCarrier.objects.get(
                SubjectBriefName=xml.UnionCarrier_SubjectBriefName,
                UnifiedCountryCode=xml.UnionCarrier_UnifiedCountryCode
            )
        except:
            rec = None

    if not rec:
        rec = DeclarantCarrier()

    rec.SubjectBriefName = xml.UnionCarrier_SubjectBriefName
    rec.TaxpayerId = xml.UnionCarrier_TaxpayerId
    rec.UnifiedCountryCode = xml.UnionCarrier_UnifiedCountryCode
    rec.RegionName = xml.UnionCarrier_RegionName
    rec.CityName = xml.UnionCarrier_CityName
    rec.StreetName = xml.UnionCarrier_StreetName
    rec.BuildingNumberId = xml.UnionCarrier_BuildingNumberId
    rec.RoomNumberId = xml.UnionCarrier_RoomNumberId
    rec.save()

    # перевозчик
    if xml.Carrier_TaxpayerId:
        try:
            p_rec = DeclarantCarrier.objects.get(TaxpayerId=xml.Carrier_TaxpayerId)
        except:
            p_rec = None
    else:
        try:
            p_rec = DeclarantCarrier.objects.get(
                SubjectBriefName=xml.Carrier_SubjectBriefName,
                UnifiedCountryCode=xml.Carrier_UnifiedCountryCode
            )
        except:
            p_rec = None

    if not p_rec:
        p_rec = DeclarantCarrier()

    p_rec.SubjectBriefName = xml.Carrier_SubjectBriefName
    p_rec.TaxpayerId = xml.Carrier_TaxpayerId
    p_rec.UnifiedCountryCode = xml.Carrier_UnifiedCountryCode
    p_rec.RegionName = xml.Carrier_RegionName
    p_rec.CityName = xml.Carrier_CityName
    p_rec.StreetName = xml.Carrier_StreetName
    p_rec.BuildingNumberId = xml.Carrier_BuildingNumberId
    p_rec.RoomNumberId = xml.Carrier_RoomNumberId
    p_rec.save()

    # отправитель
    if xml.Consignor_TaxpayerId:
        try:
            rec = ConsignorConsignee.objects.get(TaxpayerId=xml.Consignor_TaxpayerId)
        except:
            rec = None
    else:
        try:
            rec = ConsignorConsignee.objects.get(
                SubjectBriefName=xml.Consignor_SubjectBriefName,
                UnifiedCountryCode=xml.Consignor_UnifiedCountryCode
            )
        except:
            rec = None

    if not rec:
        rec = ConsignorConsignee()

    rec.SubjectBriefName = xml.Consignor_SubjectBriefName
    rec.TaxpayerId = xml.Consignor_TaxpayerId
    rec.UnifiedCountryCode = xml.Consignor_UnifiedCountryCode
    rec.RegionName = xml.Consignor_RegionName
    rec.CityName = xml.Consignor_CityName
    rec.StreetName = xml.Consignor_StreetName
    rec.BuildingNumberId = xml.Consignor_BuildingNumberId
    rec.RoomNumberId = xml.Consignor_RoomNumberId
    rec.save()

    # получатель
    if xml.Consignee_TaxpayerId:
        try:
            rec = ConsignorConsignee.objects.get(TaxpayerId=xml.Consignee_TaxpayerId)
        except:
            rec = None
    else:
        try:
            rec = ConsignorConsignee.objects.get(
                SubjectBriefName=xml.Consignee_SubjectBriefName,
                UnifiedCountryCode=xml.Consignee_UnifiedCountryCode
            )
        except:
            rec = None

    if not rec:
        rec = ConsignorConsignee()

    rec.SubjectBriefName = xml.Consignee_SubjectBriefName
    rec.TaxpayerId = xml.Consignee_TaxpayerId
    rec.UnifiedCountryCode = xml.Consignee_UnifiedCountryCode
    rec.RegionName = xml.Consignee_RegionName
    rec.CityName = xml.Consignee_CityName
    rec.StreetName = xml.Consignee_StreetName
    rec.BuildingNumberId = xml.Consignee_BuildingNumberId
    rec.RoomNumberId = xml.Consignee_RoomNumberId
    rec.save()

    # водитель
    if xml.CarrierRepresentative_DocId:
        try:
            rec = CarrierRepresentative.objects.get(DocId=xml.CarrierRepresentative_DocId)
        except:
            rec = None

        if not rec:
            rec = CarrierRepresentative()

        rec.FirstName = xml.CarrierRepresentative_FirstName
        rec.MiddleName = xml.CarrierRepresentative_MiddleName
        rec.LastName = xml.CarrierRepresentative_LastName
        rec.PositionName = xml.CarrierRepresentative_PositionName
        rec.UnifiedCountryCode = xml.CarrierRepresentative_UnifiedCountryCode
        rec.IdentityDocKindCode = xml.CarrierRepresentative_IdentityDocKindCode
        rec.DocId = xml.CarrierRepresentative_DocId
        rec.DocCreationDate = xml.CarrierRepresentative_DocCreationDate
        rec.DocValidityDate = xml.CarrierRepresentative_DocValidityDate
        rec.save()

    # лицо, заполняющее декларацию
    if xml.SP_DocId:
        try:
            rec = CarrierRepresentative.objects.get(DocId=xml.SP_DocId)
        except:
            rec = None

        if not rec:
            rec = CarrierRepresentative()

        rec.FirstName = xml.SP_FirstName
        rec.MiddleName = xml.SP_MiddleName
        rec.LastName = xml.SP_LastName
        rec.PositionName = xml.SP_PositionName
        rec.UnifiedCountryCode = xml.SP_UnifiedCountryCode
        rec.IdentityDocKindCode = xml.SP_IdentityDocKindCode
        rec.DocId = xml.SP_DocId
        rec.DocCreationDate = xml.SP_DocCreationDate
        rec.DocValidityDate = xml.SP_DocValidityDate
        rec.QualificationCertificateId = xml.SP_QualificationCertificateId
        rec.POA_DocKindCode = xml.SP_POA_DocKindCode
        rec.POA_DocId = xml.SP_POA_DocId
        rec.POA_DocCreationDate = xml.SP_POA_DocCreationDate
        rec.POA_DocValidityDate = xml.SP_POA_DocValidityDate
        rec.save()

    # транспорт
    ts_list = TransportXML.objects.filter(xml=xml)
    for ts in ts_list:
        try:
            rec = Transport.objects.get(
                TransportMeansRegId=ts.TransportMeansRegId,
                TransportTypeCode=ts.TransportTypeCode
            )
        except:
            rec = None

        if not rec:
            rec = Transport()

        rec.TransportMeansRegId = ts.TransportMeansRegId
        rec.countryCode = ts.countryCode
        rec.VehicleId = ts.VehicleId
        rec.TransportTypeCode = ts.TransportTypeCode
        rec.VehicleMakeCode = ts.VehicleMakeCode
        rec.VehicleMakeName = ts.VehicleMakeName
        rec.VehicleModelName = ts.VehicleModelName
        rec.DocId = ts.DocId
        rec.Carrier = p_rec
        rec.save()
