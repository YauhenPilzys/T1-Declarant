from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User




class Sender(models.Model):  # Отправитель
    EUEOPIID = models.CharField("проверка номера", max_length=255, blank=True, null=True)
    name = models.CharField("Название", max_length=255)
    address = models.CharField("Адрес", max_length=255)
    index = models.CharField("Индекс", max_length=255)
    city = models.CharField("Город", max_length=255)
    country = models.CharField("Код страны", max_length=255)
    comment = models.CharField("Комментарий", max_length=255)


class Recipient(models.Model):  # Получатель
    EUEOPIID = models.CharField("проверка номера", max_length=255, blank=True, null=True )
    name = models.CharField("Название", max_length=255)
    address = models.CharField("Адрес", max_length=255)
    index = models.CharField("Индекс", max_length=255)
    city = models.CharField("Город", max_length=255)
    country = models.CharField("Код страны", max_length=255)
    comment = models.CharField("Комментарий", max_length=255)


class Carrier(models.Model):  # Перевозчик
    EUEOPIID = models.CharField("проверка номера", max_length=255, blank=True, null=True)
    name = models.CharField("Название", max_length=255)
    address = models.CharField("Адрес", max_length=255)
    index = models.CharField("Индекс", max_length=255)
    city = models.CharField("Город", max_length=255)
    country = models.CharField("Код страны", max_length=255)
    comment = models.CharField("Комментарий", max_length=255)


class Product(models.Model):  # Товар
    t1_xml = models.ForeignKey('t1_xml', on_delete=models.CASCADE, verbose_name="XML")
    IteNumGDS7 = models.CharField("Номер товара", max_length=255)
    ComCodTarCodGDS10 = models.CharField("Код товара", max_length=255)
    GooDesGDS23 = models.CharField("Описание товара", max_length=255)
    GroMasGDS46 = models.CharField("Вес товара", max_length=255)
    MarNumOfPacGS21 = models.CharField("Номер упаковки", max_length=255)
    MarNumOfPacGS21LNG = models.CharField("Язык номера упаковки", max_length=255)
    KinOfPacGS23 = models.CharField("Тип упаковки", max_length=255)
    NumOfPacGS24 = models.CharField("Количество упаковок", max_length=255)


class Document(models.Model):  # Документ
    Product = models.ForeignKey('Product', on_delete=models.CASCADE, verbose_name="Товар")
    DocTypDC21 = models.CharField("Тип документа", max_length=255)
    DocRefDC23 = models.CharField("Номер документа", max_length=255)
    DocRefDCLNG = models.CharField("Язык документа", max_length=255)
    ComOfInfDC25 = models.CharField("Дополнительная информация", max_length=255)
    ComOfInfDC25LNG = models.CharField("Язык дополнительной информации", max_length=255)


class Pre_Document(models.Model):  # Предшествующий документ
    Product = models.ForeignKey('Product', on_delete=models.CASCADE, verbose_name="Товар")
    PreDocTypAR21 = models.CharField("Тип предварительного документа", max_length=255)
    PreDocRefAR26 = models.CharField("Номер предварительного документа", max_length=255)
    PreDocRefLNG = models.CharField("Язык предварительного документа", max_length=255)
    # ComOfInfDC25 = models.CharField("Дополнительная информация", max_length=255)
    # ComOfInfDC25LNG = models.CharField("Язык дополнительной информации", max_length=255)


class Routes(models.Model):  # Маршруты следования
    CouOfRouCodITI1 = models.CharField("Код страны маршрута", max_length=255)
    t1_xml = models.ForeignKey('t1_xml', on_delete=models.CASCADE, verbose_name="XML")


class Structure(models.Model):  #З агрузка в БД кодов товара из файлов
    CNKEY = models.CharField(max_length=255)
    LEVEL = models.CharField(max_length=255)
    CN_CODE = models.CharField(max_length=255)
    NAME_EN = models.TextField()
    PARENT = models.CharField(max_length=255)
    SU = models.CharField(max_length=255)
    SU_Name = models.CharField(max_length=255)


class t1_xml(models.Model):
    #Общая информация о заполняющих
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    #Статусы - 0  - в работе, 1 - отправляется, 2 - прошло успешно , 3 - ошибка
    # Статус присваивается системой, мы его не трогаем
    status = models.IntegerField("Статус", choices=((0, "0"), (1, "1"), (2, "2"), (3, "3")), default=0)
    date_time = models.DateTimeField("Дата и время")
    LRN = models.CharField("Номер декларации в XML", max_length=255)  # Номер который вводится при заполнении
    # MRN присваивается системой, мы не трогаем
    MRN = models.CharField("Номер при успешной регистрации", max_length=255)

    #Общая информация <CC015B>
    SynIdeMES1 = models.CharField("Идентификатор синтаксического сообщения", max_length=255)
    SynVerNumMES2 = models.CharField("Номер версии синтаксического сообщения", max_length=255)
    MesSenMES3 = models.CharField("Отправитель сообщения", max_length=255)
    MesRecMES6 = models.CharField("Получатель сообщения", max_length=255)
    DatOfPreMES9 = models.CharField("Дата представления сообщения", max_length=255)
    TimOfPreMES10 = models.CharField("Время представления сообщения", max_length=255)
    # Внутренний номер сообщения должен формироваться LTДАТАВРЕМЯ (LT2404050920)н
    IntConRefMES11 = models.CharField("Внутренний номер сообщения", max_length=255)
    # Идентификатор сообщения сделать равным LRN
    MesIdeMES19 = models.CharField("Идентификационный номер сообщения", max_length=255)
    MesTypMES20 = models.CharField("Тип сообщения", max_length=255)

    def save(self, *args, **kwargs):
        # Присваиваем MesIdeMES19 значение LRN
        self.MesIdeMES19 = self.LRN

        # Формируем значение для IntConRefMES11
        if not self.IntConRefMES11:
            if self.date_time:
                # Используем наивный datetime
                formatted_time = self.date_time.strftime("LT%y%m%d%H%M")
                self.IntConRefMES11 = formatted_time

        super().save(*args, **kwargs)

    #Информация о декларации <HEAHEA>
    RefNumHEA4 = models.CharField("номер документа декларации", max_length=255)
    TypOfDecHEA24 = models.CharField("тип декларации", max_length=255)
    CouOfDesCodHEA30 = models.CharField("код страны доставки", max_length=255)
    PlaOfLoaCodHEA46 = models.CharField("код страны загрузки", max_length=255)
    CouOfDisCodHEA55 = models.CharField("код страны отправления", max_length=255)
    InlTraModHEA75 = models.CharField("внутренний транспорт", max_length=255)
    IdeOfMeaOfTraAtDHEA78 = models.CharField("номер тс прибывшего авто", max_length=255)
    NatOfMeaOfTraAtDHEA80 = models.CharField("страна регистрации тс", max_length=255)
    IdeOfMeaOfTraCroHEA85 = models.CharField("номер тс забравшего груз", max_length=255)
    NatOfMeaOfTraCroHEA87 = models.CharField("страна регистрации тс", max_length=255)
    ConIndHEA96 = models.CharField("индикатор контейнера", max_length=255)  # Есть контейнер или нет
    ConNum = models.CharField("номер контейнера", max_length=255)  # Если есть - бывает редко
    DiaLanIndAtDepHEA254 = models.CharField("язык при отправлении", max_length=255)
    NCTSAccDocHEA601LNG = models.CharField("язык оформления документа", max_length=255)
    TotNumOfIteHEA305 = models.CharField("количество единиц товара", max_length=255)
    TotNumOfPacHEA306 = models.CharField("количество упаковок - мест", max_length=255)
    TotGroMasHEA307 = models.CharField("вес брутто по декларации", max_length=255)
    DecDatHEA383 = models.CharField("дата", max_length=255)
    DecPlaHEA394 = models.CharField("место", max_length=255)
    TraChaMetOfPayHEA1 = models.CharField("метод оплаты", max_length=255)
    SecHEA358 = models.CharField("неизвестный параметр", max_length=255)
    CodPlUnHEA357 = models.CharField("код места доставки", max_length=255)
    #</HEAHEA>

    #Информация о ПОРУЧИТЕЛЕ <TRAPRIPC1>
    NamPC17 = models.CharField("название поручителя", max_length=255)
    StrAndNumPC122 = models.CharField("адрес", max_length=255)
    PosCodPC123 = models.CharField("индекс", max_length=255)
    CitPC124 = models.CharField("город", max_length=255)
    CouPC125 = models.CharField("код страны", max_length=255)
    NADLNGPC = models.CharField("язык", max_length=255)
    TINPC159 = models.CharField("номер плательщика", max_length=255)
    #</TRAPRIPC1>

    #ОТПРАВИТЕЛЬ ASSTRA <TRACONCO1>
    NamCO17 = models.CharField("название отправителя", max_length=255)
    StrAndNumCO122 = models.CharField("адрес", max_length=255)
    PosCodCO123 = models.CharField("индекс", max_length=255)
    CitCO124 = models.CharField("город", max_length=255)
    CouCO125 = models.CharField("код страны", max_length=255)
    #</TRACONCO1>


    # ПОЛУЧАТЕЛЬ ASSTRA  <TRACONCE1>
    NamCE17 = models.CharField("название получателя", max_length=255)
    StrAndNumCE122 = models.CharField("адрес", max_length=255)
    PosCodCE123 = models.CharField("индекс", max_length=255)
    CitCE124 = models.CharField("город", max_length=255)
    CouCE125 = models.CharField("код страны", max_length=255)
    NADLNGCE = models.CharField("язык", max_length=255)
    #< / TRACONCE1 >


    #Таможня отправления <CUSOFFDEPEPT>
    RefNumEPT1 = models.CharField("номер таможни отправления", max_length=255)
    # </CUSOFFDEPEPT>

    #Таможня назначения <CUSOFFDESEST>
    RefNumEST1 = models.CharField("номер таможни назначения", max_length=255)
    # </CUSOFFDESEST>

    # #<CTLCL1> (КОНТЕЙНЕР) в XML там указан контейнер. если 1 - то вводим номер его
    # AmeTypFlaCL628 = models.CharField("Индикатор контейнера", max_length=255) #ЕСТЬ КОНТЕЙНЕР ИЛИ НЕТ ( В ДАННОМ СЛУЧАЕ НЕТ)
    # NUMCONT = models.CharField("Номер контейнера если есть", max_length= 255)
    # # </CTLCL1>

    #Информация о представителе  <REPREP>
    NamREP5 = models.CharField("Имя представителя", max_length=255)
    RepCapREP18 = models.CharField("Должность представителя", max_length=255)
    RepCapREP18LNG = models.CharField("Язык указания должности представителя", max_length=255)
    # </REPREP>

    # #Информация о гарантии (одна гарантия)  <GUAGUA>
    GuaTypGUA1 = models.CharField("Тип гарантии", max_length=255)
       #<GUAREFREF>
    GuaRefNumGRNREF1 = models.CharField("Номер гарантии", max_length=255)
    AccCodREF6 = models.CharField("код гарантийного сертификата", max_length=255)
    # <VALLIMNONECLIM> Ограничение на количество
    NotValForOthConPLIM2 = models.CharField("Код страны откуда гарантия", max_length=255)  #этого нету в ТИРЕ
      #</GUAREFREF>
    #</GUAGUA>


    # #Информация об упаковке - cвязано с товаром значит тут не нужно. Все эти поля находятся в таблице PRODUCT
    # MarNumOfPacGS21 = models.CharField("Номер упаковки", max_length=255)
    # MarNumOfPacGS21LNG = models.CharField("Язык номера упаковки", max_length=255)
    # KinOfPacGS23 = models.CharField("Тип упаковки", max_length=255)
    # NumOfPacGS24 = models.CharField("Количество упаковок", max_length=255)

    #Информация о транспортной компании ASSTRA <CARTRA100>
    NamCARTRA121 = models.CharField("Название транспортной компании", max_length=255)
    StrAndNumCARTRA254 = models.CharField("Адрес", max_length=255)
    PosCodCARTRA121 = models.CharField("Почтовый индекса", max_length=255)
    CitCARTRA789 = models.CharField("Город", max_length=255)
    CouCodCARTRA587 = models.CharField("Код страны", max_length=255)
    NADCARTRA121 = models.CharField("Язык", max_length=255)
    #</CARTRA100>


    # # Перевозчик TIR  <TRACORSECGOO021>
    # NamTRACORSECGOO025 = models.CharField("Название перевозчика", max_length=255)
    # StrNumTRACORSECGOO027 = models.CharField("Адрес перевозчика", max_length=255)
    # PosCodTRACORSECGOO026 = models.CharField("Почтовый индекс перевозчика", max_length=255)
    # CitTRACORSECGOO022 = models.CharField("Город перевозчика", max_length=255)
    # CouCodTRACORSECGOO023 = models.CharField("Код страны перевозчика", max_length=255)
    # TRACORSECGOO021LNG = models.CharField("Язык перевозчика", max_length=255)
    # # </TRACORSECGOO021>

    # Информация о отправителе для этого груза!!! ASSTRA  <TRACORSEC037>
    NamTRACORSEC041 = models.CharField("Название отправителя", max_length=255)
    StrNumTRACORSEC043 = models.CharField("Адрес", max_length=255)
    PosCodTRACORSEC042 = models.CharField("Почтовый индекс", max_length=255)
    CitTRACORSEC038 = models.CharField("Город", max_length=255)
    CouCodTRACORSEC039 = models.CharField("Код страны", max_length=255)
    TRACORSEC037LNG = models.CharField("Язык", max_length=255)
    # </TRACORSEC037>

    # Информация о получателя для этого груза!!! <TRACONSEC029>
    NameTRACONSEC033 = models.CharField("Название получателя", max_length=255)
    StrNumTRACONSEC035 = models.CharField("Адрес получателя", max_length=255)
    PosCodTRACONSEC034 = models.CharField("Почтовый индекс получателя", max_length=255)
    CitTRACONSEC030 = models.CharField("Город получателя", max_length=255)
    CouCodTRACONSEC031 = models.CharField("Код страны получателя", max_length=255)
    TRACONSEC029LNG = models.CharField("Язык получателя", max_length=255)
    # </TRACONSEC029>


    #Брокер ( кто выдает Т1, т е MB ALESTA LT) <CUSBROINF>
    NamNFO101 = models.CharField("Название брокера", max_length=255)
    StrNumNFO103 = models.CharField("Адрес брокера", max_length=255)
    PosCodNFO105 = models.CharField("Почтовый индекс брокера", max_length=255)
    CitNFO104 = models.CharField("Город брокера", max_length=255)
    CounNFO102 = models.CharField("Код страны брокера", max_length=255)
    NADLNGNFO = models.CharField("Язык брокера", max_length=255)
    TinNFO100 = models.CharField("номер налогоплательщика брокера", max_length=255)
    #</CUSBROINF>
#</CC015B>
