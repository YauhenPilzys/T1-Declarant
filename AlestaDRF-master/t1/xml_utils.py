import xml.etree.ElementTree as ET
from io import BytesIO
from .models import *
from django.http import Http404
import logging
from xml.dom import minidom

logger = logging.getLogger(__name__)


def xml_from_db_t1(xml_id, flag_file=False):
    # Получаем объект t1_xml по xml_id
    try:
        xml_object = t1_xml.objects.get(id=xml_id)
    except t1_xml.DoesNotExist:
        return "Запись не найдена"

    # Создаем корневой элемент XML
    root = ET.Element("CC015B")

    # Общая информация
    ET.SubElement(root, "SynIdeMES1").text = xml_object.SynIdeMES1
    ET.SubElement(root, "SynVerNumMES2").text = xml_object.SynVerNumMES2
    ET.SubElement(root, "MesSenMES3").text = xml_object.MesSenMES3
    ET.SubElement(root, "MesRecMES6").text = xml_object.MesRecMES6
    ET.SubElement(root, "DatOfPreMES9").text = xml_object.DatOfPreMES9
    ET.SubElement(root, "TimOfPreMES10").text = xml_object.TimOfPreMES10
    ET.SubElement(root, "IntConRefMES11").text = xml_object.IntConRefMES11
    ET.SubElement(root, "MesIdeMES19").text = xml_object.MesIdeMES19
    ET.SubElement(root, "MesTypMES20").text = xml_object.MesTypMES20

    # Информация о декларации
    declaration_info = ET.SubElement(root, "HEAHEA")
    ET.SubElement(declaration_info, "RefNumHEA4").text = xml_object.RefNumHEA4
    ET.SubElement(declaration_info, "TypOfDecHEA24").text = xml_object.TypOfDecHEA24
    ET.SubElement(declaration_info, "CouOfDesCodHEA30").text = xml_object.CouOfDesCodHEA30
    ET.SubElement(declaration_info, "PlaOfLoaCodHEA46").text = xml_object.PlaOfLoaCodHEA46
    ET.SubElement(declaration_info, "CouOfDisCodHEA55").text = xml_object.CouOfDisCodHEA55
    ET.SubElement(declaration_info, "InlTraModHEA75").text = xml_object.InlTraModHEA75
    ET.SubElement(declaration_info, "IdeOfMeaOfTraAtDHEA78").text = xml_object.IdeOfMeaOfTraAtDHEA78
    ET.SubElement(declaration_info, "NatOfMeaOfTraAtDHEA80").text = xml_object.NatOfMeaOfTraAtDHEA80
    ET.SubElement(declaration_info, "IdeOfMeaOfTraCroHEA85").text = xml_object.IdeOfMeaOfTraCroHEA85
    ET.SubElement(declaration_info, "NatOfMeaOfTraCroHEA87").text = xml_object.NatOfMeaOfTraCroHEA87
    # Всегда выводим индикатор контейнера, даже если он пустой
    ET.SubElement(declaration_info, "ConIndHEA96").text = xml_object.ConIndHEA96 if xml_object.ConIndHEA96 else ""

    # Если индикатор контейнера не пустой, выводим номер контейнера
    if xml_object.ConIndHEA96:
        ET.SubElement(declaration_info, "ConNum").text = xml_object.ConNum
    ET.SubElement(declaration_info, "DiaLanIndAtDepHEA254").text = xml_object.DiaLanIndAtDepHEA254
    ET.SubElement(declaration_info, "NCTSAccDocHEA601LNG").text = xml_object.NCTSAccDocHEA601LNG
    ET.SubElement(declaration_info, "TotNumOfIteHEA305").text = xml_object.TotNumOfIteHEA305
    ET.SubElement(declaration_info, "TotNumOfPacHEA306").text = xml_object.TotNumOfPacHEA306
    ET.SubElement(declaration_info, "TotGroMasHEA307").text = xml_object.TotGroMasHEA307
    ET.SubElement(declaration_info, "DecDatHEA383").text = xml_object.DecDatHEA383
    ET.SubElement(declaration_info, "DecPlaHEA394").text = xml_object.DecPlaHEA394
    ET.SubElement(declaration_info, "TraChaMetOfPayHEA1").text = xml_object.TraChaMetOfPayHEA1
    ET.SubElement(declaration_info, "SecHEA358").text = xml_object.SecHEA358
    ET.SubElement(declaration_info, "CodPlUnHEA357").text = xml_object.CodPlUnHEA357

    # Информация о поручителе
    sender_info = ET.SubElement(root, "TRAPRIPC1")
    ET.SubElement(sender_info, "NamPC17").text = xml_object.NamPC17
    ET.SubElement(sender_info, "StrAndNumPC122").text = xml_object.StrAndNumPC122
    ET.SubElement(sender_info, "PosCodPC123").text = xml_object.PosCodPC123
    ET.SubElement(sender_info, "CitPC124").text = xml_object.CitPC124
    ET.SubElement(sender_info, "CouPC125").text = xml_object.CouPC125
    ET.SubElement(sender_info, "NADLNGPC").text = xml_object.NADLNGPC
    ET.SubElement(sender_info, "TINPC159").text = xml_object.TINPC159

    # Информация о отправителе груза
    sender_info = ET.SubElement(root, "TRACONCO1")
    ET.SubElement(sender_info, "NamCO17").text = xml_object.NamCO17
    ET.SubElement(sender_info, "StrAndNumCO122").text = xml_object.StrAndNumCO122
    ET.SubElement(sender_info, "PosCodCO123").text = xml_object.PosCodCO123
    ET.SubElement(sender_info, "CitCO124").text = xml_object.CitCO124
    ET.SubElement(sender_info, "CouCO125").text = xml_object.CouCO125
    # ET.SubElement(sender_info, "NADLNGPC").text = xml_object.NADLNGPC


    # Информация о получателе
    sender_info = ET.SubElement(root, "TRACONCE1")
    ET.SubElement(sender_info, "NamCE17").text = xml_object.NamCE17
    ET.SubElement(sender_info, "StrAndNumCE122").text = xml_object.StrAndNumCE122
    ET.SubElement(sender_info, "PosCodCE123").text = xml_object.PosCodCE123
    ET.SubElement(sender_info, "CitCE124").text = xml_object.CitCE124
    ET.SubElement(sender_info, "CouCE125").text = xml_object.CouCE125
    ET.SubElement(sender_info, "NADLNGCE").text = xml_object.NADLNGCE

    # Таможня отправления
    customs_departure = ET.SubElement(root, "CUSOFFDEPEPT")
    ET.SubElement(customs_departure, "RefNumEPT1").text = xml_object.RefNumEPT1

    # Таможня назначения
    customs_destination = ET.SubElement(root, "CUSOFFDESEST")
    ET.SubElement(customs_destination, "RefNumEST1").text = xml_object.RefNumEST1

    # Информация о представителе
    representative_info = ET.SubElement(root, "REPREP")
    ET.SubElement(representative_info, "NamREP5").text = xml_object.NamREP5
    ET.SubElement(representative_info, "RepCapREP18").text = xml_object.RepCapREP18
    ET.SubElement(representative_info, "RepCapREP18LNG").text = xml_object.RepCapREP18LNG


    # Информация о гарантиях
    guarantee_info = ET.SubElement(root, "GUAGUA")
    ET.SubElement(guarantee_info, "GuaTypGUA1").text = xml_object.GuaTypGUA1
    guarantee_ref = ET.SubElement(guarantee_info, "GUAREFREF")
    ET.SubElement(guarantee_ref, "GuaRefNumGRNREF1").text = xml_object.GuaRefNumGRNREF1
    ET.SubElement(guarantee_ref, "AccCodREF6").text = xml_object.AccCodREF6
    vallimnoneclim = ET.SubElement(guarantee_ref, "VALLIMNONECLIM")
    ET.SubElement(vallimnoneclim, "NotValForOthConPLIM2").text = xml_object.NotValForOthConPLIM2



    # Получаем связанные объекты Product и их информацию
    for product in xml_object.product_set.all():
        product_info = ET.SubElement(root, "GOOITEGDS")
        ET.SubElement(product_info, "IteNumGDS7").text = product.IteNumGDS7
        ET.SubElement(product_info, "ComCodTarCodGDS10").text = product.ComCodTarCodGDS10
        ET.SubElement(product_info, "GooDesGDS23").text = product.GooDesGDS23
        ET.SubElement(product_info, "GroMasGDS46").text = product.GroMasGDS46

        # Добавление документов товара
        for document in product.document_set.all():
            document_info = ET.SubElement(product_info, "PRODOCDC2")
            ET.SubElement(document_info, "DocTypDC21").text = document.DocTypDC21
            ET.SubElement(document_info, "DocRefDC23").text = document.DocRefDC23
            ET.SubElement(document_info, "DocRefDCLNG").text = document.DocRefDCLNG
            ET.SubElement(document_info, "ComOfInfDC25").text = document.ComOfInfDC25
            ET.SubElement(document_info, "ComOfInfDC25LNG").text = document.ComOfInfDC25LNG

            # Добавляем информацию о предварительных документах
            for pre_document in product.pre_document_set.all():
                pre_document_info = ET.SubElement(product_info, "PPREADMREFAR2")
                ET.SubElement(pre_document_info, "PreDocTypAR21").text = pre_document.PreDocTypAR21
                ET.SubElement(pre_document_info, "PreDocRefAR26").text = pre_document.PreDocRefAR26
                ET.SubElement(pre_document_info, "PreDocRefLNG").text = pre_document.PreDocRefLNG
                # ET.SubElement(pre_document_info, "ComOfInfDC25").text = pre_document.ComOfInfDC25
                # ET.SubElement(pre_document_info, "ComOfInfDC25LNG").text = pre_document.ComOfInfDC25LNG

            # Добавляем информацию об упаковке
        packaging_info = ET.SubElement(product_info, "PACGS2")
        ET.SubElement(packaging_info, "MarNumOfPacGS21").text = product.MarNumOfPacGS21
        ET.SubElement(packaging_info, "MarNumOfPacGS21LNG").text = product.MarNumOfPacGS21LNG
        ET.SubElement(packaging_info, "KinOfPacGS23").text = product.KinOfPacGS23
        ET.SubElement(packaging_info, "NumOfPacGS24").text = product.NumOfPacGS24

        # # Информации о втором получателе нету в этой актуальной XML
        # recipient_info = ET.SubElement(root, "TRACONCE2")
        # ET.SubElement(recipient_info, "NamCE17").text = xml_object.NamCE17
        # ET.SubElement(recipient_info, "StrAndNumCE122").text = xml_object.StrAndNumCE122
        # ET.SubElement(recipient_info, "PosCodCE123").text = xml_object.PosCodCE123
        # ET.SubElement(recipient_info, "CitCE124").text = xml_object.CitCE124
        # ET.SubElement(recipient_info, "CouCE125").text = xml_object.CouCE125
        # ET.SubElement(recipient_info, "NADLNGCE").text = xml_object.NADLNGCE

        # Маршруты
        for route in xml_object.routes_set.all():
            route_info = ET.SubElement(root, "ITI")
            ET.SubElement(route_info, "CouOfRouCodITI1").text = route.CouOfRouCodITI1

        # Информация о транспортной компании
        transport_company_info = ET.SubElement(root, "CARTRA100")
        ET.SubElement(transport_company_info, "NamCARTRA121").text = xml_object.NamCARTRA121
        ET.SubElement(transport_company_info, "StrAndNumCARTRA254").text = xml_object.StrAndNumCARTRA254
        ET.SubElement(transport_company_info, "PosCodCARTRA121").text = xml_object.PosCodCARTRA121
        ET.SubElement(transport_company_info, "CitCARTRA789").text = xml_object.CitCARTRA789
        ET.SubElement(transport_company_info, "CouCodCARTRA587").text = xml_object.CouCodCARTRA587
        ET.SubElement(transport_company_info, "NADCARTRA121").text = xml_object.NADCARTRA121

        # Информация о отправителе для этого груза
        second_carrier_info = ET.SubElement(root, "TRACORSEC037")
        ET.SubElement(second_carrier_info, "NamTRACORSEC041").text = xml_object.NamTRACORSEC041
        ET.SubElement(second_carrier_info, "StrNumTRACORSEC043").text = xml_object.StrNumTRACORSEC043
        ET.SubElement(second_carrier_info, "PosCodTRACORSEC042").text = xml_object.PosCodTRACORSEC042
        ET.SubElement(second_carrier_info, "CitTRACORSEC038").text = xml_object.CitTRACORSEC038
        ET.SubElement(second_carrier_info, "CouCodTRACORSEC039").text = xml_object.CouCodTRACORSEC039
        ET.SubElement(second_carrier_info, "TRACORSEC037LNG").text = xml_object.TRACORSEC037LNG

        # Информация о получателе для этого груза
        second_sender_info = ET.SubElement(root, "TRACONSEC029")
        ET.SubElement(second_sender_info, "NameTRACONSEC033").text = xml_object.NameTRACONSEC033
        ET.SubElement(second_sender_info, "StrNumTRACONSEC035").text = xml_object.StrNumTRACONSEC035
        ET.SubElement(second_sender_info, "PosCodTRACONSEC034").text = xml_object.PosCodTRACONSEC034
        ET.SubElement(second_sender_info, "CitTRACONSEC030").text = xml_object.CitTRACONSEC030
        ET.SubElement(second_sender_info, "CouCodTRACONSEC031").text = xml_object.CouCodTRACONSEC031
        ET.SubElement(second_sender_info, "TRACONSEC029LNG").text = xml_object.TRACONSEC029LNG

        # Информация о брокере
        broker_info = ET.SubElement(root, "CUSBROINF")
        ET.SubElement(broker_info, "NamNFO101").text = xml_object.NamNFO101
        ET.SubElement(broker_info, "StrNumNFO103").text = xml_object.StrNumNFO103
        ET.SubElement(broker_info, "PosCodNFO105").text = xml_object.PosCodNFO105
        ET.SubElement(broker_info, "CitNFO104").text = xml_object.CitNFO104
        ET.SubElement(broker_info, "CounNFO102").text = xml_object.CounNFO102
        ET.SubElement(broker_info, "NADLNGNFO").text = xml_object.NADLNGNFO
        ET.SubElement(broker_info, "TinNFO100").text = xml_object.TinNFO100

        # Преобразование дерева в строку XML
        xml_data = ET.tostring(root, encoding="unicode", method='xml')

        if flag_file:
            # Используем xml.dom.minidom для форматирования с отступами
            parsed_xml = minidom.parseString(xml_data)
            pretty_xml = parsed_xml.toprettyxml(indent="  ")

            # Сохранение в файл
            with open("output.xml", "w", encoding="utf-8") as file:
                file.write(pretty_xml)
            return "output.xml"

        return xml_data

# def xml_from_db_t1(xml_id, flag_file=False):
#     # Получаем объект t1_xml по xml_id
#     try:
#         xml_object = t1_xml.objects.get(id=xml_id)
#     except t1_xml.DoesNotExist:
#         return "Запись не найдена"
#
#     # Создаем корневой элемент XML
#     root = ET.Element("root")
#
#     # Общая информация о заполняющих в T1 XML выводить не надо
#     # general_info = ET.SubElement(root, "GeneralInformation")
#     # ET.SubElement(general_info, "User").text = str(xml_object.user.id)
#     # ET.SubElement(general_info, "Status").text = str(xml_object.status)
#     # ET.SubElement(general_info, "DateTime").text = xml_object.date_time.isoformat()
#     # ET.SubElement(general_info, "LRN").text = xml_object.LRN
#     # ET.SubElement(general_info, "MRN").text = xml_object.MRN
#
#     # Общая информация
#     general_info_data = ET.SubElement(root, "GeneralInfoData")
#     ET.SubElement(general_info_data, "SynIdeMES1").text = xml_object.SynIdeMES1
#     ET.SubElement(general_info_data, "SynVerNumMES2").text = xml_object.SynVerNumMES2
#     ET.SubElement(general_info_data, "MesSenMES3").text = xml_object.MesSenMES3
#     ET.SubElement(general_info_data, "MesRecMES6").text = xml_object.MesRecMES6
#     ET.SubElement(general_info_data, "DatOfPreMES9").text = xml_object.DatOfPreMES9
#     ET.SubElement(general_info_data, "TimOfPreMES10").text = xml_object.TimOfPreMES10
#     ET.SubElement(general_info_data, "IntConRefMES11").text = xml_object.IntConRefMES11
#     ET.SubElement(general_info_data, "MesIdeMES19").text = xml_object.MesIdeMES19
#     ET.SubElement(general_info_data, "MesTypMES20").text = xml_object.MesTypMES20
#
#     # Информация о декларации
#     declaration_info = ET.SubElement(root, "HEAHEA_инф_о_декларации")
#     ET.SubElement(declaration_info, "RefNumHEA4").text = xml_object.RefNumHEA4
#     ET.SubElement(declaration_info, "TypOfDecHEA24").text = xml_object.TypOfDecHEA24
#     ET.SubElement(declaration_info, "CouOfDesCodHEA30").text = xml_object.CouOfDesCodHEA30
#     ET.SubElement(declaration_info, "PlaOfLoaCodHEA46").text = xml_object.PlaOfLoaCodHEA46
#     ET.SubElement(declaration_info, "CouOfDisCodHEA55").text = xml_object.CouOfDisCodHEA55
#     ET.SubElement(declaration_info, "InlTraModHEA75").text = xml_object.InlTraModHEA75
#     ET.SubElement(declaration_info, "IdeOfMeaOfTraAtDHEA78").text = xml_object.IdeOfMeaOfTraAtDHEA78
#     ET.SubElement(declaration_info, "NatOfMeaOfTraAtDHEA80").text = xml_object.NatOfMeaOfTraAtDHEA80
#     ET.SubElement(declaration_info, "IdeOfMeaOfTraCroHEA85").text = xml_object.IdeOfMeaOfTraCroHEA85
#     ET.SubElement(declaration_info, "NatOfMeaOfTraCroHEA87").text = xml_object.NatOfMeaOfTraCroHEA87
#     ET.SubElement(declaration_info, "ConIndHEA96").text = xml_object.ConIndHEA96
#     ET.SubElement(declaration_info, "ConNum").text = xml_object.ConNum
#     ET.SubElement(declaration_info, "DiaLanIndAtDepHEA254").text = xml_object.DiaLanIndAtDepHEA254
#     ET.SubElement(declaration_info, "NCTSAccDocHEA601LNG").text = xml_object.NCTSAccDocHEA601LNG
#     ET.SubElement(declaration_info, "TotNumOfIteHEA305").text = xml_object.TotNumOfIteHEA305
#     ET.SubElement(declaration_info, "TotNumOfPacHEA306").text = xml_object.TotNumOfPacHEA306
#     ET.SubElement(declaration_info, "TotGroMasHEA307").text = xml_object.TotGroMasHEA307
#     ET.SubElement(declaration_info, "DecDatHEA383").text = xml_object.DecDatHEA383
#     ET.SubElement(declaration_info, "DecPlaHEA394").text = xml_object.DecPlaHEA394
#     ET.SubElement(declaration_info, "TraChaMetOfPayHEA1").text = xml_object.TraChaMetOfPayHEA1
#     ET.SubElement(declaration_info, "SecHEA358").text = xml_object.SecHEA358
#     ET.SubElement(declaration_info, "CodPlUnHEA357").text = xml_object.CodPlUnHEA357
#
#     # Кто выдает гарантию
#     # guarantee_info = ET.SubElement(root, "TRAPRIPC1_кто_выдает_гарантию_АЛЕСТА_ДОЛЖНА_БЫТЬ_ТУТ")
#     # ET.SubElement(guarantee_info, "NamPC17").text = xml_object.NamPC17
#     # ET.SubElement(guarantee_info, "StrAndNumPC122").text = xml_object.StrAndNumPC122
#     # ET.SubElement(guarantee_info, "PosCodPC123").text = xml_object.PosCodPC123
#     # ET.SubElement(guarantee_info, "CitPC124").text = xml_object.CitPC124
#     # ET.SubElement(guarantee_info, "CouPC125").text = xml_object.CouPC125
#     # ET.SubElement(guarantee_info, "NADLNGPC").text = xml_object.NADLNGPC
#     # ET.SubElement(guarantee_info, "TINPC159").text = xml_object.TINPC159
#     #
#     # # Отправитель
#     # sender_info = ET.SubElement(root, "TRACONCE1_ОТПРАВИТЕЛЬ")
#     # ET.SubElement(sender_info, "NamCO17").text = xml_object.NamCO17  #Не совпадает с Т1 (NamCE17)
#     # ET.SubElement(sender_info, "StrAndNumCO122").text = xml_object.StrAndNumCO122
#     # ET.SubElement(sender_info, "PosCodCO123").text = xml_object.PosCodCO123
#     # ET.SubElement(sender_info, "CitCO124").text = xml_object.CitCO124
#     # ET.SubElement(sender_info, "CouCO125").text = xml_object.CouCO125
#     # # НЕ хватает как в Т1 поля <NADLNGCE>LT</NADLNGCE> - язык получателя
#     #
#     # # Таможня отправления
#     # customs_departure = ET.SubElement(root, "CUSOFFDEPEPT_ТАМОЖЕННЫЙ_ОРГАН_ОТПРАВЛЕНИЯ")
#     # ET.SubElement(customs_departure, "RefNumEPT1").text = xml_object.RefNumEPT1
#     #
#     # # Таможня назначения
#     # customs_destination = ET.SubElement(root, "CUSOFFDESEST_ТАМОЖЕННЫЙ_ОРГАН_НАЗНАЧЕНИЯ")
#     # ET.SubElement(customs_destination, "RefNumEST1").text = xml_object.RefNumEST1
#     #
#     # #КОНТЕЙНЕР ДОБАВИТЬ
#     #
#     # # Информация о представителе
#     # representative_info = ET.SubElement(root, "REPREP_ПРЕДСТАВИТЕЛЬ")
#     # ET.SubElement(representative_info, "NamREP5").text = xml_object.NamREP5
#     # ET.SubElement(representative_info, "RepCapREP18").text = xml_object.RepCapREP18
#     # ET.SubElement(representative_info, "RepCapREP18LNG").text = xml_object.RepCapREP18LNG
#
#     # Информация о гарантии
#     guarantee_info = ET.SubElement(root, "TRAPRIPC1_кто_выдает_гарантию_АЛЕСТА_ДОЛЖНА_БЫТЬ_ТУТ")
#     ET.SubElement(guarantee_info, "NamPC17").text = xml_object.NamPC17
#     ET.SubElement(guarantee_info, "StrAndNumPC122").text = xml_object.StrAndNumPC122
#     ET.SubElement(guarantee_info, "PosCodPC123").text = xml_object.PosCodPC123
#     ET.SubElement(guarantee_info, "CitPC124").text = xml_object.CitPC124
#     ET.SubElement(guarantee_info, "CouPC125").text = xml_object.CouPC125
#     ET.SubElement(guarantee_info, "NADLNGPC").text = xml_object.NADLNGPC
#     ET.SubElement(guarantee_info, "TINPC159").text = xml_object.TINPC159
#
#     # Отправитель
#     sender_info = ET.SubElement(root, "TRACONCE1_ОТПРАВИТЕЛЬ")
#     ET.SubElement(sender_info, "NamCO17").text = xml_object.NamCO17
#     ET.SubElement(sender_info, "StrAndNumCO122").text = xml_object.StrAndNumCO122
#     ET.SubElement(sender_info, "PosCodCO123").text = xml_object.PosCodCO123
#     ET.SubElement(sender_info, "CitCO124").text = xml_object.CitCO124
#     ET.SubElement(sender_info, "CouCO125").text = xml_object.CouCO125
#     # Добавляем недостающий элемент языка получателя
#     ET.SubElement(sender_info, "NADLNGCE").text = xml_object.NADLNGCE
#
#     # Таможня отправления
#     customs_departure = ET.SubElement(root, "CUSOFFDEPEPT_ТАМОЖЕННЫЙ_ОРГАН_ОТПРАВЛЕНИЯ")
#     ET.SubElement(customs_departure, "RefNumEPT1").text = xml_object.RefNumEPT1
#
#     # Таможня назначения
#     customs_destination = ET.SubElement(root, "CUSOFFDESEST_ТАМОЖЕННЫЙ_ОРГАН_НАЗНАЧЕНИЯ")
#     ET.SubElement(customs_destination, "RefNumEST1").text = xml_object.RefNumEST1
#
#     # Информация о представителе
#     representative_info = ET.SubElement(root, "REPREP_ПРЕДСТАВИТЕЛЬ")
#     ET.SubElement(representative_info, "NamREP5").text = xml_object.NamREP5
#     ET.SubElement(representative_info, "RepCapREP18").text = xml_object.RepCapREP18
#     ET.SubElement(representative_info, "RepCapREP18LNG").text = xml_object.RepCapREP18LNG
#
#     # Информация о гарантии
#     guarantee_info = ET.SubElement(root, "GUAGUA_ГАРАНТИЯ")
#     ET.SubElement(guarantee_info, "GuaTypGUA1").text = xml_object.GuaTypGUA1
#     guarantee_ref = ET.SubElement(guarantee_info, "GUAREFREF")
#     ET.SubElement(guarantee_ref, "GuaRefNumGRNREF1").text = xml_object.GuaRefNumGRNREF1
#     ET.SubElement(guarantee_ref, "AccCodREF6").text = xml_object.AccCodREF6
#     vallimnoneclim = ET.SubElement(guarantee_ref, "VALLIMNONECLIM")
#     ET.SubElement(vallimnoneclim, "NotValForOthConPLIM2").text = xml_object.NotValForOthConPLIM2
#
#     # Получаем связанные объекты Product и их информацию
#     for product in xml_object.product_set.all():
#         product_info = ET.SubElement(root, "GOOITEGDS")
#         ET.SubElement(product_info, "IteNumGDS7").text = product.IteNumGDS7
#         ET.SubElement(product_info, "ComCodTarCodGDS10").text = product.ComCodTarCodGDS10
#         ET.SubElement(product_info, "GooDesGDS23").text = product.GooDesGDS23
#         ET.SubElement(product_info, "GroMasGDS46").text = product.GroMasGDS46
#
#         # Добавление документов товара выше
#         for document in product.document_set.all():
#             document_info = ET.SubElement(product_info, "PRODOCDC2")
#             ET.SubElement(document_info, "DocTypDC21").text = document.DocTypDC21
#             ET.SubElement(document_info, "DocRefDC23").text = document.DocRefDC23
#             ET.SubElement(document_info, "DocRefDCLNG").text = document.DocRefDCLNG
#             ET.SubElement(document_info, "ComOfInfDC25").text = document.ComOfInfDC25
#             ET.SubElement(document_info, "ComOfInfDC25LNG").text = document.ComOfInfDC25LNG
#
#         # Добавляем информацию о предварительных документах
#         for pre_document in product.pre_document_set.all():
#             pre_document_info = ET.SubElement(product_info, "PPREADMREFAR2")
#             ET.SubElement(pre_document_info, "PreDocTypAR21").text = pre_document.PreDocTypAR21
#             ET.SubElement(pre_document_info, "PreDocRefAR26").text = pre_document.PreDocRefAR26
#             ET.SubElement(pre_document_info, "PreDocRefLNG").text = pre_document.PreDocRefLNG
#             ET.SubElement(pre_document_info, "ComOfInfDC25").text = pre_document.ComOfInfDC25
#             ET.SubElement(pre_document_info, "ComOfInfDC25LNG").text = pre_document.ComOfInfDC25LNG
#
#         # Добавляем информацию об упаковке
#         packaging_info = ET.SubElement(product_info, "PACGS2")
#         ET.SubElement(packaging_info, "MarNumOfPacGS21").text = product.MarNumOfPacGS21
#         ET.SubElement(packaging_info, "MarNumOfPacGS21LNG").text = product.MarNumOfPacGS21LNG
#         ET.SubElement(packaging_info, "KinOfPacGS23").text = product.KinOfPacGS23
#         ET.SubElement(packaging_info, "NumOfPacGS24").text = product.NumOfPacGS24
#
#     # Добавление информации о получателе
#     recipient_info = ET.SubElement(root, "TRACONCE2")
#     ET.SubElement(recipient_info, "NamCE17").text = xml_object.NamCE17
#     ET.SubElement(recipient_info, "StrAndNumCE122").text = xml_object.StrAndNumCE122
#     ET.SubElement(recipient_info, "PosCodCE123").text = xml_object.PosCodCE123
#     ET.SubElement(recipient_info, "CitCE124").text = xml_object.CitCE124
#     ET.SubElement(recipient_info, "CouCE125").text = xml_object.CouCE125
#     ET.SubElement(recipient_info, "NADLNGCE").text = xml_object.NADLNGCE
#
#     # Маршруты
#     for route in xml_object.routes_set.all():
#         route_info = ET.SubElement(root, "ITI")
#         ET.SubElement(route_info, "CouOfRouCodITI1").text = route.CouOfRouCodITI1
#
#     # Генерация XML
#     xml_data = ET.tostring(root, encoding="unicode")
#
#     if flag_file:
#         # Сохранение в файл
#         with open("output.xml", "w", encoding="utf-8") as file:
#             file.write(xml_data)
#         return xml_data
#
#     return xml_data

# Когда вставили мы товар - упаковку - перевозчик , мы вставляем второй товар и последующие чтоб выглядели вот так
# <GOOITEGDS> (ИНФОРМАЦИЯ О ТОВАРЕ В ГРУЗЕ)
#     <IteNumGDS7>2</IteNumGDS7> - НОМЕР ТОВАРА В ГРУЗЕ
#     <ComCodTarCodGDS10>020319</ComCodTarCodGDS10> КОД ТОВАРА
#     <GooDesGDS23>KIAUL.SONKAULIAI</GooDesGDS23> ОПИСАНИЕ ТОВАРА
#     <GroMasGDS46>33.32</GroMasGDS46> МАССА ТОВАРА
#     <PREADMREFAR2> (ДОКУМЕНТАЦИЯ ТОВАРА)
#       <PreDocTypAR21>730</PreDocTypAR21> ТИП ДОКУМЕНТА
#       <PreDocRefAR26>B/N</PreDocRefAR26> НОМЕР ДОКУМЕНТА
#       <PreDocRefLNG>LT</PreDocRefLNG> ЯЗЫК ДОКУМЕНТА
#     </PREADMREFAR2>
#     <TRACONCO2> (ИНФОРМАЦИЯ О ПЕРЕВОЗЧИКЕ)
#       <NamCO27>MIRATORG KURSK OOO</NamCO27> - НАЗВАНИЕ
#       <StrAndNumCO222>CHERNICENO 2-1</StrAndNumCO222> АДРЕС И НОМЕР ЗДАНИЯ
#       <PosCodCO223>-</PosCodCO223> ИНДЕКС
#       <CitCO224>OKTYABARSKIY R.</CitCO224> ГОРОД
#       <CouCO225>RU</CouCO225> КОД СТРАНЫ
#       <NADLNGGTCO>LT</NADLNGGTCO> ЯЗЫК
#     </TRACONCO2>
#     <PACGS2> (ИНФОРМАЦИЯ О ПАКЕТИРОВАНИИ ТОВАРА)
#       <MarNumOfPacGS21>B/N</MarNumOfPacGS21> - МАРКИРОВКА УПАКОВКИ
#       <MarNumOfPacGS21LNG>LT</MarNumOfPacGS21LNG> - ЯЗЫК МАРКИРОВКИ
#       <KinOfPacGS23>PK</KinOfPacGS23> - ТИП УПАКОВКИ
#       <NumOfPacGS24>0</NumOfPacGS24> - КОЛИЧЕСТВО УПАКОВОК
#     </PACGS2>
#     <TRACORSECGOO021>
#       <NamTRACORSECGOO025>MIRATORG KURSK OOO</NamTRACORSECGOO025>
#       <StrNumTRACORSECGOO027>CHERNICENO 2-1</StrNumTRACORSECGOO027>
#       <PosCodTRACORSECGOO026>-</PosCodTRACORSECGOO026>
#       <CitTRACORSECGOO022>OKTYABARSKIY R.</CitTRACORSECGOO022>
#       <CouCodTRACORSECGOO023>RU</CouCodTRACORSECGOO023>
#       <TRACORSECGOO021LNG>LT</TRACORSECGOO021LNG>
#     </TRACORSECGOO021>

# После всех введенных товарах мы вставляем маршруты следования
# <ITI> (ИНФОРМАЦИЯ О МАРШРУТЕ ГРУЗА)
#     <CouOfRouCodITI1>RU</CouOfRouCodITI1> - КОД СТРАНЫ МАРШРУТА
#   </ITI>
#   <ITI>
#     <CouOfRouCodITI1>BY</CouOfRouCodITI1> - КОД СТРАНЫ МАРШРУТА
#   </ITI>
#   <ITI>
#     <CouOfRouCodITI1>LT</CouOfRouCodITI1> - КОД СТРАНЫ МАРШРУТА
#   </ITI>
#   <ITI>
#     <CouOfRouCodITI1>RU</CouOfRouCodITI1> - КОД СТРАНЫ МАРШРУТА
#   </ITI>
# Дальше информация о перевозчике кто везет все
# <CARTRA100> (ИНФОРМАЦИЯ О ТРАНСПОРТНОЙ КОМПАНИИ) перевозчик!!!
#     <NamCARTRA121>MIRATORG LOGISTIK OOO</NamCARTRA121> - НАЗВАНИЕ
#     <StrAndNumCARTRA254>SAVHOZNAYA 12, NEVSKOE P</StrAndNumCARTRA254> АДРЕС ТК
#     <PosCodCARTRA121>-</PosCodCARTRA121> ИНДЕКС
#     <CitCARTRA789>KALININGRAD OBL.</CitCARTRA789> - ГОРОД
#     <CouCodCARTRA587>RU</CouCodCARTRA587> - КОД СТРАНЫ
#     <NADCARTRA121>LT</NADCARTRA121> ГДЕ ЗАРЕГИСТИРОВАНА ТК
#   </CARTRA100>
#   <TRACONSEC029> (ВТОРИЧНАЯ ПЕРЕВОЗОЧНАЯ ТК) отправитель или получатель!!!
#     <NameTRACONSEC033>TK MIRATORG OOO</NameTRACONSEC033> - НАЗВАНИЕ
#     <StrNumTRACONSEC035>CENTRALNAYA 2B</StrNumTRACONSEC035> - УЛИЦА И НОМЕР ЗДАНИЯ
#     <PosCodTRACONSEC034>-</PosCodTRACONSEC034> ИНДЕКС
#     <CitTRACONSEC030>KALININGRAD OBLZAOZERJE</CitTRACONSEC030> ГОРОД
#     <CouCodTRACONSEC031>RU</CouCodTRACONSEC031> КОД СТРАНЫ
#     <TRACONSEC029LNG>LT</TRACONSEC029LNG> ЯЗЫК
#   </TRACONSEC029>
#   <CUSBROINF>  - информация о декларанте кто подает Т1
#     <NamNFO101>ALESTA LT MB</NamNFO101> НАЗВАНИЕ
#     <StrNumNFO103>METALO 2</StrNumNFO103> УЛИЦА
#     <PosCodNFO105>-</PosCodNFO105> ИНДЕКС
#     <CitNFO104>VILNIUS</CitNFO104> ГОРОД
#     <CounNFO102>LT</CounNFO102> КОД СТРАНЫ
#     <NADLNGNFO>LT</NADLNGNFO> ЯЗЫК ДЛЯ НАЗВАНИЯ
#     <TinNFO100>LT304400258</TinNFO100>  ИНДЕКТИФИКАЦИОННЫЙ НОМЕР ПЛАТЕЛЬЗИКА
#   </CUSBROINF>
# </CC015B>