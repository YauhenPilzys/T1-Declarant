from django.http import HttpResponse, FileResponse

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, mixins, status

from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import filters
from rest_framework.viewsets import ViewSet

import declarant.update_tnved as UpdTnvedLib
import declarant.payment_calculating as PaymCalcLib
import declarant.exchange_rates_load as NbrbLib
from declarant.OldDeclarationPDF.declaration_build import full_TD_api
from declarant.OldDeclarationPDF.opis_build import full_opis_api

from declarant.create_xml import *
from declarant.filename_unit import get_name_opis, get_name_TD, get_name_xml
from declarant.filters import CustomSanctionsFilterBackend
from declarant.json_to_db import new_xml_load, update_xml_load
from declarant.paginations import ConsigmentItemsAPIListPagination, DocsAPIListPagination, AllOtherAPIListPagination, \
    TnvedAPIListPagination
from declarant.sanctions_check import sanction_check_xml
from declarant.serializers import *


from declarant.xml_to_db import start_work_with_xml



class DeclarantTreeTnvedUpdate(APIView):
    """ Запуск процедуры обновления кодов ТН ВЭД и тарифов """
    permission_classes = (IsAuthenticated, IsAdminUser,)

    def post(self, request):
        return Response(UpdTnvedLib.update_tnved())


class ExchangeRatesLoad(APIView):
    """ Загрузка курсов валют с nbrb.by """
    permission_classes = (IsAuthenticated, IsAdminUser,)

    def post(self, request):
        return Response(NbrbLib.load_exchange_rates_from_nbrb())


class DeclarantCarrierAPI(viewsets.ModelViewSet):
    """ Декларант, перевозчик и перевозчик по ТТ ЕАЭС, параметр search - по полю SubjectBriefName и TaxpayerId """
    queryset = DeclarantCarrier.objects.all()
    serializer_class = DeclarantCarrierSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = AllOtherAPIListPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['SubjectBriefName', 'TaxpayerId']


class ConsignorConsigneeAPI(viewsets.ModelViewSet):
    """ Отправитель, получатель, параметр search - по полю SubjectBriefName и TaxpayerId """
    queryset = ConsignorConsignee.objects.all()
    serializer_class = ConsignorConsigneeSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = AllOtherAPIListPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['SubjectBriefName', 'TaxpayerId']

class PIDeclarantAPI(viewsets.ModelViewSet):
    """ Лицо, предоставившее ПИ, параметр search - по полю SubjectBriefName и TaxpayerId """
    queryset = PIDeclarant.objects.all()
    serializer_class = PIDeclarantSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = AllOtherAPIListPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['SubjectBriefName', 'TaxpayerId']


class CarrierRepresentativeAPI(viewsets.ModelViewSet):
    """ Водитель, параметр search - по полю DocId """
    queryset = CarrierRepresentative.objects.all()
    serializer_class = CarrierRepresentativeSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = AllOtherAPIListPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['DocId', ]


class TransportAPI(viewsets.ModelViewSet):
    """ Транспортные средства (список), параметр search - по полю TransportMeansRegId и VehicleId"""
    queryset = Transport.objects.all()
    serializer_class = TransportSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = AllOtherAPIListPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['TransportMeansRegId', 'VehicleId']


class TreeTnvedAPI(viewsets.ReadOnlyModelViewSet):
    """ Дерево кодов, параметр search - по полю Name и Code, фильтрация - по ParentId и id """
    queryset = TreeTnved.objects.all()
    serializer_class = TreeTnvedSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = TnvedAPIListPagination
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['Name', '^Code']
    filterset_fields = ['ParentID', 'id']


class TnvedAPI(viewsets.ReadOnlyModelViewSet):
    """ Коды ТН ВЭД и тарифы, параметр search - по полю Name и Code, фильтрация по TreeID и id """
    queryset = Tnved.objects.all()
    serializer_class = TnvedSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = TnvedAPIListPagination
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['Name', '^Code']
    filterset_fields = ['TreeID', 'id']


class ExciseAPI(viewsets.ReadOnlyModelViewSet):
    """ Акцизы к кодам ТН ВЭД, параметр search - по полям Name(акциза), Name(кода ТНВЭД) и Code(кода ТНВЭД), фильтрация по  TnvedID__id и id"""
    queryset = Excise.objects.all()
    serializer_class = ExciseSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = TnvedAPIListPagination
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['Name', 'TnvedID__Name', 'TnvedID__Code']
    filterset_fields = ['TnvedID__id', 'id']


# ****************************

class XMLModelAPI(viewsets.ModelViewSet):
    """ Основная инфа по XML """
    queryset = XMLModel.objects.all()
    serializer_class = XMLModelSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = AllOtherAPIListPagination


class TranshipmentAPI(mixins.CreateModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):
    """ Перецепки """
    queryset = Transhipment.objects.all()
    serializer_class = TranshipmentSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = AllOtherAPIListPagination


class TranshipmentByIDAPI(mixins.ListModelMixin,
                          viewsets.GenericViewSet):
    """ Перецепки в хмл по xml_id"""
    serializer_class = TranshipmentSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = AllOtherAPIListPagination

    def get_queryset(self):
        try:
            xml_id = int(self.kwargs['xml_id'])
        except:
            xml_id = -1
        if xml_id == -1:
            queryset = Transhipment.objects.all()
        else:
            queryset = Transhipment.objects.filter(xml_id=xml_id)
        return queryset


class TransportTranshipmentAPI(mixins.CreateModelMixin,
                               mixins.RetrieveModelMixin,
                               mixins.UpdateModelMixin,
                               mixins.DestroyModelMixin,
                               viewsets.GenericViewSet):
    """ Транспорт в перецепке """
    queryset = TransportTranshipment.objects.all()
    serializer_class = TransportTranshipmentSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = AllOtherAPIListPagination


class TransportTranshipmentByTransIDAPI(mixins.ListModelMixin,
                                        viewsets.GenericViewSet):
    """ Транспорт в перецепке по transhipment_xml_id"""
    serializer_class = TransportTranshipmentSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = AllOtherAPIListPagination

    def get_queryset(self):
        try:
            transhipment_xml_id = int(self.kwargs['transhipment_xml_id'])
        except:
            transhipment_xml_id = -1
        if transhipment_xml_id == -1:
            queryset = TransportTranshipment.objects.all()
        else:
            queryset = TransportTranshipment.objects.filter(transhipment_xml_id=transhipment_xml_id)
        return queryset


class ContainerTranshipmentAPI(mixins.CreateModelMixin,
                               mixins.RetrieveModelMixin,
                               mixins.UpdateModelMixin,
                               mixins.DestroyModelMixin,
                               viewsets.GenericViewSet):
    """ Контейнеры в перецепке """
    queryset = ContainerTranshipment.objects.all()
    serializer_class = ContainerTranshipmentSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = AllOtherAPIListPagination


class ContainerTranshipmentByTransIDAPI(mixins.ListModelMixin,
                                        viewsets.GenericViewSet):
    """ Контейнеры в перецепке по transhipment_xml_id """
    serializer_class = ContainerTranshipmentSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = AllOtherAPIListPagination

    def get_queryset(self):
        try:
            transhipment_xml_id = int(self.kwargs['transhipment_xml_id'])
        except:
            transhipment_xml_id = -1
        if transhipment_xml_id == -1:
            queryset = ContainerTranshipment.objects.all()
        else:
            queryset = ContainerTranshipment.objects.filter(transhipment_xml_id=transhipment_xml_id)
        return queryset


class TransitGuaranteeAPI(mixins.CreateModelMixin,
                          mixins.RetrieveModelMixin,
                          mixins.UpdateModelMixin,
                          mixins.DestroyModelMixin,
                          viewsets.GenericViewSet):
    """ Гаранты в XML """
    queryset = TransitGuarantee.objects.all()
    serializer_class = TransitGuaranteeSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = AllOtherAPIListPagination


class TransitGuaranteeByIDAPI(mixins.ListModelMixin,
                              viewsets.GenericViewSet):
    """ Гаранты в XML по xml_id"""
    serializer_class = TransitGuaranteeSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = AllOtherAPIListPagination

    def get_queryset(self):
        try:
            xml_id = int(self.kwargs['xml_id'])
        except:
            xml_id = -1
        if xml_id == -1:
            queryset = TransitGuarantee.objects.all()
        else:
            queryset = TransitGuarantee.objects.filter(xml_id=xml_id)
        return queryset


class TransportXMLAPI(mixins.CreateModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):
    """ Транспорт в XML """
    queryset = TransportXML.objects.all()
    serializer_class = TransportXMLSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = AllOtherAPIListPagination


class TransportXMLByIDAPI(mixins.ListModelMixin,
                          viewsets.GenericViewSet):
    """ Транспорт в XML по xml_id"""
    serializer_class = TransportXMLSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = AllOtherAPIListPagination

    def get_queryset(self):
        try:
            xml_id = int(self.kwargs['xml_id'])
        except:
            xml_id = -1
        if xml_id == -1:
            queryset = TransportXML.objects.all()
        else:
            queryset = TransportXML.objects.filter(xml_id=xml_id)
        return queryset


class ContainerXMLAPI(mixins.CreateModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):
    """ Контейнеры в XML """
    queryset = ContainerXML.objects.all()
    serializer_class = ContainerXMLSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = AllOtherAPIListPagination


class ContainerXMLByIDAPI(mixins.ListModelMixin,
                          viewsets.GenericViewSet):
    """ Контейнеры в XML по xml_id """
    serializer_class = ContainerXMLSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = AllOtherAPIListPagination

    def get_queryset(self):
        try:
            xml_id = int(self.kwargs['xml_id'])
        except:
            xml_id = -1
        if xml_id == -1:
            queryset = ContainerXML.objects.all()
        else:
            queryset = ContainerXML.objects.filter(xml_id=xml_id)
        return queryset


class ConsignmentItemAPI(mixins.CreateModelMixin,
                         mixins.RetrieveModelMixin,
                         mixins.UpdateModelMixin,
                         mixins.DestroyModelMixin,
                         viewsets.GenericViewSet):
    """ товары в XML """
    queryset = ConsignmentItem.objects.all()
    serializer_class = ConsignmentItemSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = ConsigmentItemsAPIListPagination


class ConsignmentItemByIDAPI(mixins.ListModelMixin,
                             viewsets.GenericViewSet):
    """ Товары для хмл по xml_id """
    serializer_class = ConsignmentItemSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = ConsigmentItemsAPIListPagination

    def get_queryset(self):
        try:
            xml_id = int(self.kwargs['xml_id'])
        except:
            xml_id = -1
        if xml_id == -1:
            queryset = ConsignmentItem.objects.all()
        else:
            queryset = ConsignmentItem.objects.filter(xml_id=xml_id)
        return queryset


class ContainerCIAPI(mixins.CreateModelMixin,
                     mixins.RetrieveModelMixin,
                     mixins.UpdateModelMixin,
                     mixins.DestroyModelMixin,
                     viewsets.GenericViewSet):
    """ Контейнеры в товаре """
    queryset = ContainerCI.objects.all()
    serializer_class = ContainerCISerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = AllOtherAPIListPagination


class ContainerCIByIDAPI(mixins.ListModelMixin,
                         viewsets.GenericViewSet):
    """ Контейнеры в товаре по ci_id """
    serializer_class = ContainerCISerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = AllOtherAPIListPagination

    def get_queryset(self):
        try:
            ci_id = int(self.kwargs['ci_id'])
        except:
            ci_id = -1
        if ci_id == -1:
            queryset = ContainerCI.objects.all()
        else:
            queryset = ContainerCI.objects.filter(ci_id=ci_id)
        return queryset


class PIPrecedingDocDetailsAPI(mixins.CreateModelMixin,
                               mixins.RetrieveModelMixin,
                               mixins.UpdateModelMixin,
                               mixins.DestroyModelMixin,
                               viewsets.GenericViewSet):
    """ Предшедствующие документы """
    queryset = PIPrecedingDocDetails.objects.all()
    serializer_class = PIPrecedingDocDetailsSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = DocsAPIListPagination


class PIPrecedingDocDetailsByIDAPI(mixins.ListModelMixin,
                                   viewsets.GenericViewSet):
    """ Предшедствующие документы для товара по ci_id"""
    queryset = PIPrecedingDocDetails.objects.all()
    serializer_class = PIPrecedingDocDetailsSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = DocsAPIListPagination

    def get_queryset(self):
        try:
            ci_id = int(self.kwargs['ci_id'])
        except:
            ci_id = -1
        if ci_id == -1:
            queryset = PIPrecedingDocDetails.objects.all()
        else:
            queryset = PIPrecedingDocDetails.objects.filter(ci_id=ci_id)
        return queryset


class PIGoodsDocDetailsAPI(mixins.CreateModelMixin,
                           mixins.RetrieveModelMixin,
                           mixins.UpdateModelMixin,
                           mixins.DestroyModelMixin,
                           viewsets.GenericViewSet):
    """ Документы в товаре """
    queryset = PIGoodsDocDetails.objects.all()
    serializer_class = PIGoodsDocDetailsSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = DocsAPIListPagination


class PIGoodsDocDetailsByIDAPI(mixins.ListModelMixin,
                               viewsets.GenericViewSet):
    """ Документы для товара по ci_id """
    serializer_class = PIGoodsDocDetailsSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = DocsAPIListPagination

    def get_queryset(self):
        try:
            ci_id = int(self.kwargs['ci_id'])
        except:
            ci_id = -1
        if ci_id == -1:
            queryset = PIGoodsDocDetails.objects.all()
        else:
            queryset = PIGoodsDocDetails.objects.filter(ci_id=ci_id)
        return queryset


class PaymentCalculations(APIView):
    """ Расчет платежей для кодов из хмл с ид xml_id """
    permission_classes = (IsAuthenticated,)

    def post(self, request, xml_id):
        return Response(PaymCalcLib.start_calc_payment_xml(xml_id))


class XMLFileUploadView(ViewSet):
    """ Загрузка из файла с ЭПИ или ТД. Возвращает id созданного файла и/или messages с описанием ошибок"""
    serializer_class = UploadSerializer
    permission_classes = (IsAuthenticated,)

    def list(self, request):
        return Response("GET запрос не поддерживается!")

    def create(self, request):
        file_uploaded = request.FILES.get('file_uploaded')
        xml_load_info = start_work_with_xml(str(file_uploaded), file_uploaded, self.request.user)
        if xml_load_info['id']:
            return Response(xml_load_info)
        else:
            return Response(xml_load_info['messages'])


class DeclarantTableInfo(viewsets.ReadOnlyModelViewSet):
    """ Информация для основной таблицы с записями XML"""
    queryset = XMLModel.objects.all().only(
        'XmlType',
        'EDocDateTime',
        'user__username',
        'transport_list',
        'TD_DocId',
        'Consignor_SubjectBriefName',
        'Consignee_SubjectBriefName',
        'Carrier_SubjectBriefName',
        'CarrierRepresentative_LastName',
    ).order_by('-id')
    serializer_class = TableXMLSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = AllOtherAPIListPagination


class GetXMlFile(APIView):
    """ Выгруxml_fromзка xml по xml_id. С параметром - ?file=1 - вернет xml-файл"""
    permission_classes = (IsAuthenticated,)

    def get(self, request, xml_id):
        flag = True if request.GET.get("file", '0') == '1' else False
        if flag:
            fp = xml_from_db(xml_id, flag)
            fp.seek(0)
            return FileResponse(fp, as_attachment=True, filename=get_name_xml(xml_id))
        else:
            return Response(xml_from_db(xml_id, flag))


class GetPDFTD(APIView):
    """ Выгрузка декларации по xml_id """
    permission_classes = (IsAuthenticated,)

    def get(self, request, xml_id):
        fp = full_TD_api(xml_id)
        fp.seek(0)
        return FileResponse(fp, as_attachment=True, filename=get_name_TD(xml_id))


class getPDFOpis(APIView):
    '''Выгрузка описи по xml_id, с параметром ?flag=0 - будет печатать без "Ознакомлен..."'''
    permission_classes = (IsAuthenticated,)

    def get(self, request, xml_id):
        flag = request.GET.get("flag", '1')
        fp = full_opis_api(xml_id, False if flag == '0' else True)
        fp.seek(0)
        return FileResponse(fp, as_attachment=True, filename=get_name_opis(xml_id))


class NewXmlDB(APIView):
    """ Запись данных декларации в БД """
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            response = new_xml_load(request.body, self.request.user)
            return Response(response)
        except Exception as e:
            messages = []
            messages.append('При сохранении XML возникла ошибка: ' + str(e))
            return Response({
                'id': 0,
                'messages': messages,
                'warnings': [],
            })


class UpdateXmlDB(APIView):
    """ Обновление данных декларации в БД """
    permission_classes = (IsAuthenticated,)

    def post(self, request, xml_id):
        return Response(update_xml_load(request.body, self.request.user, xml_id))


class GetFullInfoXML(APIView):
    '''Выгрузка полной информации по XML в json '''
    permission_classes = (IsAuthenticated,)

    def get(self, request, xml_id):
        x = XMLModel.objects.get(pk=xml_id)
        full_info = XMLModelSerializer(x).data

        # товары
        items = ConsignmentItem.objects.filter(xml=x)
        items_list = []
        for item in items:
            _item = ConsignmentItemSerializer(item).data
            # документы в товаре
            docs = PIGoodsDocDetails.objects.filter(ci=item)
            docs_list = []
            for d in docs:
                docs_list.append(PIGoodsDocDetailsSerializer(d).data)
            _dict = {'PIGoodsDocDetails': docs_list}

            # предшедствующие доки
            p_docs = PIPrecedingDocDetails.objects.filter(ci=item)
            p_docs_list = []
            for d in p_docs:
                p_docs_list.append(PIPrecedingDocDetailsSerializer(d).data)
            _dict.update({'PIPrecedingDocDetails': p_docs_list})

            # контейнеры в товаре
            ci_cont = ContainerCI.objects.filter(ci=item)
            ci_cont_list = []
            for c in ci_cont:
                ci_cont_list.append(ContainerCISerializer(c).data)
            _dict.update({'ContainerCI': ci_cont_list})

            _item.update(_dict)
            items_list.append(_item)
        _fd = {'ConsignmentItem': items_list}

        # перецепки
        transhipments = Transhipment.objects.filter(xml=x)
        tr_list = []
        for tr in transhipments:
            _tr = TranshipmentSerializer(tr).data
            # транспорт в перецепке
            transport_tr = TransportTranshipment.objects.filter(transhipment_xml=tr)
            transport_tr_list = []
            for t in transport_tr:
                transport_tr_list.append(TransportTranshipmentSerializer(t).data)
            _dict = {'TransportTranshipment': transport_tr_list}

            # контейнеры в перецепке
            cont_tr = ContainerTranshipment.objects.filter(transhipment_xml=tr)
            cont_tr_list = []
            for c in cont_tr:
                cont_tr_list.append(ContainerTranshipmentSerializer(c).data)
            _dict.update({'ContainerTranshipment': cont_tr_list})

            _tr.update(_dict)
            tr_list.append(_tr)

        _fd.update({'Transhipment': tr_list})

        # транспорт
        transport = TransportXML.objects.filter(xml=x)
        ts_list = []
        for ts in transport:
            _ts = TransportXMLSerializer(ts).data
            ts_list.append(_ts)
        _fd.update({'Transport': ts_list})

        # контейнеры в XML
        cont_xml = ContainerXML.objects.filter(xml=x)
        cont_xml_list = []
        for c in cont_xml:
            _c = ContainerXMLSerializer(c).data
            cont_xml_list.append(_c)
        _fd.update({'ContainerXML': cont_xml_list})

        # гарантии
        garant = TransitGuarantee.objects.filter(xml=x)
        garant_list = []
        for g in garant:
            _g = TransitGuaranteeSerializer(g).data
            garant_list.append(_g)
        _fd.update({'TransitGuarantee': garant_list})

        full_info.update(_fd)
        return HttpResponse(JSONRenderer().render(full_info), content_type="application/json")


class CheckTNVEDCode(APIView):
    """ Проверка списка кодов по ТН ВЭД """
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        return Response(PaymCalcLib.check_tnved_code(request.body), status=status.HTTP_200_OK)

class TNVEDСodeDescription(APIView):
    """ Описание по коду ТН ВЭД """
    permission_classes = (IsAuthenticated,)

    def get(self, request, code_tnved):
        if 2 <= len(code_tnved) <= 12:
            return Response(PaymCalcLib.get_tnved_code_description(code_tnved), status=status.HTTP_200_OK)
        else:
            return Response({'error': 'The code length must be from 6 to 10!'}, status=status.HTTP_400_BAD_REQUEST)


class SanctionAPI(viewsets.ReadOnlyModelViewSet):
    """ Санкционный список (весь и РФ и РБ и контрсанкции, параметр search - по коду, фильтрация - по типу и коду """
    queryset = Sanction.objects.all()
    serializer_class = SanctionSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = AllOtherAPIListPagination
    filter_backends = [CustomSanctionsFilterBackend, DjangoFilterBackend]
    search_fields = ['^code']
    filterset_fields = ['type', 'code']


class SanctionXMLCheck(APIView):
    """ Проверка кодов из xml на санкции """
    permission_classes = (IsAuthenticated,)

    def get(self, request, id_xml):
        return Response(sanction_check_xml(id_xml), status=status.HTTP_200_OK)


class DraftJSONAPI(viewsets.ModelViewSet):
    """ Черновики с сохраненной информацией """
    queryset = DraftJSON.objects.all()
    serializer_class = DraftJSONSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = AllOtherAPIListPagination
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['note', ]
    filterset_fields = ['user', ]


