from datetime import datetime

from rest_framework import viewsets
from .models import *
from .serializers import *
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import filters
from rest_framework.viewsets import ViewSet
from .paginations import *
from django.http import HttpResponse, FileResponse
from django.views.generic import View
from django.dispatch import Signal
from django.http import JsonResponse
from django.views.generic import View
from .models import Structure
from django.shortcuts import render
from django.http import HttpResponse
import pandas as pd
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
# import update_tnved as UpdTnvedLib
import t1.payment_calculating as PaymCalcLib
from rest_framework import generics
from django.shortcuts import get_object_or_404
from django.db import transaction
import chardet
from .xml_loader_t1 import new_xml_load, update_t1_xml_load
import json
from .xml_utils import xml_from_db_t1
from rest_framework.decorators import action




#http://127.0.0.1:8000/get_xml_file_t1/38/?file=1 и если ?file=0 то выводим в JSON , если ?file=1 то скачиваем нашу XML
class GetXMlFileT1(APIView):
    """Выгрузка XML по xml_id. С параметром - ?file=1 - вернет XML-файл"""
    permission_classes = (IsAuthenticated,)

    def get(self, request, xml_id):
        flag = True if request.GET.get("file", '0') == '1' else False
        xml_data = xml_from_db_t1(xml_id, flag)

        if flag:
            # Получаем объект t1_xml по xml_id для доступа к номеру декларации
            try:
                xml_object = t1_xml.objects.get(id=xml_id)
            except t1_xml.DoesNotExist:
                return HttpResponse("Запись не найдена", status=404)

            # Используем номер декларации RefNumHEA4 для имени файла
            ref_num_hea4 = xml_object.RefNumHEA4
            filename = f"{ref_num_hea4}.xml"

            # Читаем содержимое файла для отправки
            with open(xml_data, 'r', encoding='utf-8') as xml_file:
                response = HttpResponse(xml_file.read(), content_type='application/xml')
                response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
        else:
            # Вернуть XML как текст, не экранируя символы
            return HttpResponse(xml_data, content_type='application/xml')


class GetLRN(APIView): #Вывод посленего LRN номера
    #http://127.0.0.1:8000/api/get-lrn/
    """ Генерация последнего LRN номера создания XML  """
    permission_classes = (IsAuthenticated,)
    def get(self, request):
        try:
            # Получаем последнюю запись из таблицы t1_xml для текущего пользователя
            latest_xml = t1_xml.objects.filter(user=self.request.user).latest('date_time')
            lrn = latest_xml.LRN if latest_xml else None
            return Response({'LRN': lrn})
        except t1_xml.DoesNotExist:
            return Response({'error': 'Записей не найдено'}, status=404)
        except Exception as e:
            return Response({'error': f'Произошла ошибка: {str(e)}'}, status=500)



# class T1NewXmlDB(APIView):
#     #http://127.0.0.1:8000/t1_new_xml/
#     """ Запись данных декларации в БД """
#     permission_classes = (IsAuthenticated,)
#
#     def post(self, request):
#         try:
#             request_data = json.dumps(request.data)
#             response = new_xml_load(request_data, self.request.user)
#             return Response(response)
#         except Exception as e:
#             messages = [f'При сохранении XML возникла ошибка: {str(e)}']
#             return Response({
#                 'id': 0,
#                 'messages': messages,
#                 'warnings': [],
#             })


class T1NewXmlDB(APIView):
    #http://127.0.0.1:8000/t1_new_xml/
    # Сделана проверка для записей если одинаковые поля то оставляем, если поле разное то создаем новую запись в БД
    """ Запись данных декларации в БД и формирование XML """
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            # Получаем данные запроса
            request_data = request.data

            # Начинаем транзакцию, чтобы все изменения сохранялись только при успехе всех операций
            with transaction.atomic():
                # Проверка и обработка данных отправителя
                sender_name = request_data.get("NamCO17")
                sender_address = request_data.get("StrAndNumCO122")
                sender_city = request_data.get("CitCO124")
                sender_country = request_data.get("CouCO125")
                sender_index = request_data.get("PosCodCO123")

                sender, sender_created = Sender.objects.update_or_create(
                    name=sender_name,
                    address=sender_address,
                    city=sender_city,
                    defaults={
                        'country': sender_country,
                        'index': sender_index
                    }
                )

                # Проверка и обработка данных получателя
                recipient_name = request_data.get("NamCE17")
                recipient_address = request_data.get("StrAndNumCE122")
                recipient_city = request_data.get("CitCE124")
                recipient_country = request_data.get("CouCE125")
                recipient_index = request_data.get("PosCodCE123")

                recipient, recipient_created = Recipient.objects.update_or_create(
                    name=recipient_name,
                    address=recipient_address,
                    city=recipient_city,
                    defaults={
                        'country': recipient_country,
                        'index': recipient_index
                    }
                )

                # Проверка и обработка данных перевозчика
                carrier_name = request_data.get("NamCARTRA121")
                carrier_address = request_data.get("StrAndNumCARTRA254")
                carrier_city = request_data.get("CitCARTRA789")
                carrier_country = request_data.get("CouCodCARTRA587")
                carrier_index = request_data.get("PosCodCARTRA121")

                carrier, carrier_created = Carrier.objects.update_or_create(
                    name=carrier_name,
                    address=carrier_address,
                    city=carrier_city,
                    defaults={
                        'country': carrier_country,
                        'index': carrier_index
                    }
                )

                # После обновления или создания записей переходим к формированию XML
                # Преобразуем данные запроса в JSON-строку для передачи в функцию new_xml_load
                request_data_json = json.dumps(request_data)

                # Формируем XML с использованием функции new_xml_load
                response = new_xml_load(request_data_json, self.request.user)

            # Возвращаем успешный ответ с результатом формирования XML
            return Response(response)

        except Exception as e:
            # В случае ошибки возвращаем сообщение об ошибке
            messages = [f'При сохранении XML возникла ошибка: {str(e)}']
            return Response({
                'id': 0,
                'messages': messages,
                'warnings': [],
            })


class UpdateXmlDBT1(APIView):
    """ Обновление данных декларации в БД """
    permission_classes = (IsAuthenticated,)

    def post(self, request, xml_id):
        return Response(update_t1_xml_load(request.body, self.request.user, xml_id))


# Вывод водов товаров с родителями
# http://127.0.0.1:8000/api/v1/get_structure_code_description/0101/
class STRUCTUREСodeDescription(APIView):
    """ Описание по коду товара с файла """
    permission_classes = (IsAuthenticated,)

    def get(self, request, code_structure):
        if 2 <= len(code_structure) <= 12:
            return Response(PaymCalcLib.get_structure_code_description(code_structure), status=status.HTTP_200_OK)
        else:
            return Response({'error': 'The code length must be from 6 to 10!'}, status=status.HTTP_400_BAD_REQUEST)


#Загрузка данных и файла в таблицу в БД
@csrf_exempt
def import_data(request):
    if request.method == 'POST':
        file = request.FILES.get('file')
        if file:
            try:
                df = pd.read_excel(file)

                # Замена пустых значений на 'null'
                df.fillna('null', inplace=True)

                # Ensure 'PARENT' column is treated as integers if possible
                df['PARENT'] = df['PARENT'].apply(lambda x: int(x) if x != 'null' else x)

                for index, row in df.iterrows():
                    Structure.objects.get_or_create(
                        CNKEY=row['CNKEY'],
                        LEVEL=row['LEVEL'],
                        CN_CODE=row['CN_CODE'],
                        NAME_EN=row['NAME_EN'],
                        PARENT=row['PARENT'],
                        SU=row['SU'],
                        SU_Name=row['SU_Name']
                    )

                return JsonResponse({'message': 'Data imported successfully'})
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=400)
        else:
            return JsonResponse({'error': 'No file provided'}, status=400)
    elif request.method == 'GET':
        try:
            file_path = 't1/CN2024_Structure1.xlsx'
            df = pd.read_excel(file_path)

            # Замена пустых значений на 'null'
            df.fillna('null', inplace=True)

            # Ensure 'PARENT' column is treated as integers if possible
            df['PARENT'] = df['PARENT'].apply(lambda x: int(x) if x != 'null' else x)

            for index, row in df.iterrows():
                Structure.objects.get_or_create(
                    CNKEY=row['CNKEY'],
                    LEVEL=row['LEVEL'],
                    CN_CODE=row['CN_CODE'],
                    NAME_EN=row['NAME_EN'],
                    PARENT=row['PARENT'],
                    SU=row['SU'],
                    SU_Name=row['SU_Name']
                )

            return JsonResponse({'message': 'Data imported successfully from GET request'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)

class SenderViewSet(viewsets.ModelViewSet):
    queryset = Sender.objects.all()
    serializer_class = SenderSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = APIListPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']


class RecipientViewSet(viewsets.ModelViewSet):
    queryset = Recipient.objects.all()
    serializer_class = RecipientSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = APIListPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']


class CarrierViewSet(viewsets.ModelViewSet):
    queryset = Carrier.objects.all()
    serializer_class = CarrierSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = APIListPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']



class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = APIListPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['IteNumGDS7', 'ComCodTarCodGDS10']


class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = APIListPagination
    filter_backends = [filters.SearchFilter]
    search_fields = []


class Pre_DocumentViewSet(viewsets.ModelViewSet):
    queryset = Pre_Document.objects.all()
    serializer_class = Pre_DocumentSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = APIListPagination
    filter_backends = [filters.SearchFilter]
    search_fields = []


class StructureViewSet(viewsets.ModelViewSet):
    queryset = Structure.objects.all()
    serializer_class = StructureSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = APIListPagination
    filter_backends = [filters.SearchFilter]
    search_fields = []


class RoutesViewSet(viewsets.ModelViewSet):
    queryset = Routes.objects.all()
    serializer_class = RoutesSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = APIListPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['CouOfRouCodITI1']


class t1_xmlViewSet(viewsets.ModelViewSet):
    queryset = t1_xml.objects.all()
    serializer_class = t1_xmlSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = APIListPagination
    filter_backends = [filters.SearchFilter]
    search_fields = []



class T1TableInfo(viewsets.ReadOnlyModelViewSet):
    """ Информация для основной таблицы с записями XML"""
    queryset = t1_xml.objects.all().order_by('-id')
    serializer_class = T1XML_INFOSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = APIListPagination


    # Сортировка по status / LRN / MRN / date_time - сразу выводися статус заданный а дальше все остальные по возрастанию
    # http://127.0.0.1:8000/api/v1/t1_table_xml/filter_data/?status=0
    @action(detail=False, methods=['get'])
    def filter_data(self, request):
        # Получаем параметры из запроса
        status_param = request.GET.get('status', None)
        lrn_param = request.GET.get('LRN', None)
        mrn_param = request.GET.get('MRN', None)
        date_time_param = request.GET.get('date_time', None)

        # Базовый набор данных
        queryset = self.get_queryset()

        # Фильтрация и сортировка по статусу
        if status_param is not None:
            try:
                # Преобразование строки в целое число для фильтрации
                status_int = int(status_param)

                # Фильтрация записей с нужным статусом
                primary_queryset = queryset.filter(status=status_int)

                # Фильтрация всех остальных записей с другими статусами
                remaining_queryset = queryset.exclude(status=status_int).order_by('status')

                # Объединение двух наборов данных: сначала записи с нужным статусом, затем остальные
                queryset = list(primary_queryset) + list(remaining_queryset)

            except ValueError:
                return Response({"error": "Invalid status value. Must be an integer."}, status=400)

        # Дополнительная фильтрация по LRN
        if lrn_param is not None:
            if lrn_param.lower() == 'true':
                # Сортировка по убыванию даты, если LRN=true (самые новые)
                queryset = sorted(queryset, key=lambda x: x.date_time, reverse=True)
            elif lrn_param.lower() == 'false':
                # Сортировка по возрастанию даты, если LRN=false (самые старые)
                queryset = sorted(queryset, key=lambda x: x.date_time)

        # Дополнительная фильтрация по MRN
        if mrn_param is not None:
            if mrn_param.lower() == 'true':
                # Сортировка по убыванию даты, если MRN=true (самые новые)
                queryset = sorted(queryset, key=lambda x: x.date_time, reverse=True)
            elif mrn_param.lower() == 'false':
                # Сортировка по возрастанию даты, если MRN=false (самые старые)
                queryset = sorted(queryset, key=lambda x: x.date_time)

        # Сортировка по date_time
        if date_time_param is not None:
            if date_time_param.lower() == 'true':
                # Сортировка по возрастанию даты (самая ранняя запись)
                queryset = sorted(queryset, key=lambda x: x.date_time)
            elif date_time_param.lower() == 'false':
                # Сортировка по убыванию даты (самая поздняя запись)
                queryset = sorted(queryset, key=lambda x: x.date_time, reverse=True)

        # Пагинация
        paginator = self.pagination_class()
        paginated_queryset = paginator.paginate_queryset(queryset, request, view=self)

        # Сериализация данных
        serializer = self.get_serializer(paginated_queryset, many=True)
        return paginator.get_paginated_response(serializer.data)








class T1FullInfoXML(APIView):
    '''Выгрузка полной информации по T1_XML в json '''
    permission_classes = (IsAuthenticated,)

    def get(self, request, xml_id):
        try:
            x = t1_xml.objects.get(pk=xml_id)
        except t1_xml.DoesNotExist:
            return JsonResponse({'error': 'XML not found'}, status=404)

        full_info = t1_xmlSerializer(x).data

        # товары
        products = Product.objects.filter(t1_xml=x)
        product_list = []
        for product in products:
            _product = ProductSerializer(product).data

            # документы в товаре
            docs = Document.objects.filter(Product=product)
            docs_list = []
            for doc in docs:
                docs_list.append(DocumentSerializer(doc).data)
            _dict = {'Document': docs_list}

            # предшествующие документы
            pre_docs = Pre_Document.objects.filter(Product=product)
            pre_docs_list = []
            for pre_doc in pre_docs:
                pre_docs_list.append(Pre_DocumentSerializer(pre_doc).data)
            _dict.update({'Pre_Document': pre_docs_list})

            _product.update(_dict)
            product_list.append(_product)

        _fd = {'Product': product_list}

        # маршруты следования
        routes = Routes.objects.filter(t1_xml=x)
        routes_list = []
        for route in routes:
            routes_list.append(RoutesSerializer(route).data)
            _dict.update({'Routes': routes_list})
        _fd.update({'Routes': routes_list})

        full_info.update(_fd)
        return JsonResponse(full_info, safe=False)


class T1XMLViewSet(viewsets.ModelViewSet):
    queryset = t1_xml.objects.all()
    serializer_class = T1XML_INFOSerializer

    @action(detail=False, methods=['get'])
    def filter_data(self, request):
        # Получение параметров из GET-запроса
        status_param = request.GET.get('status', None)
        id_param = request.GET.get('id', None)
        lrn_param = request.GET.get('LRN', None)
        mrn_param = request.GET.get('MRN', None)
        order_asc = request.GET.get('order_asc', 'true').lower() == 'true'  # 'true' по умолчанию

        # Фильтрация по параметрам
        queryset = self.get_queryset()

        if status_param is not None:
            queryset = queryset.filter(status=status_param)

        if id_param is not None:
            queryset = queryset.filter(id=id_param)

        if lrn_param is not None:
            queryset = queryset.filter(LRN=lrn_param)

        if mrn_param is not None:
            queryset = queryset.filter(MRN=mrn_param)

        # Сортировка по полю date_time
        if order_asc:
            queryset = queryset.order_by('date_time')  # Сортировка по возрастанию (самые ранние)
        else:
            queryset = queryset.order_by('-date_time')  # Сортировка по убыванию (самые поздние)

        # Сериализация данных
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
