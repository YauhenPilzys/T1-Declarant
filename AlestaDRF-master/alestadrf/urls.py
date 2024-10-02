"""alestadrf URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django_filters import views
from rest_framework import routers

from rest_framework.schemas import get_schema_view
from django.views.generic import TemplateView
from rest_framework_swagger.views import get_swagger_view

from declarant.views import *
from t1.views import *


from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)


router = routers.DefaultRouter()
router.register(r'declarant_carrier', DeclarantCarrierAPI, basename='declarant_carrier')
router.register(r'consignor_consignee', ConsignorConsigneeAPI, basename='consignor_consignee')
router.register(r'pideclarant', PIDeclarantAPI, basename='pideclarant')
router.register(r'carrier_representative', CarrierRepresentativeAPI, basename='carrier_representative')
router.register(r'transport', TransportAPI, basename='transport')
router.register(r'tree_tnved', TreeTnvedAPI, basename='tree_tnved')
router.register(r'tnved', TnvedAPI, basename='tnved')
router.register(r'excise', ExciseAPI, basename='excise')
router.register(r'upload_xml', XMLFileUploadView, basename="upload_xml")
router.register(r'table_xml', DeclarantTableInfo, basename='table_xml')
router.register(r'draft', DraftJSONAPI, basename='draft')

#T1
router.register(r'recipients', RecipientViewSet, basename='recipients')
router.register(r'senders', SenderViewSet, basename='senders')
router.register(r'carriers', CarrierViewSet, basename='carriers')
router.register(r'products', ProductViewSet, basename='products')
router.register(r'documents', DocumentViewSet, basename='documents')
router.register(r'pre_documents', Pre_DocumentViewSet, basename='pre_documents')
router.register(r'structures', StructureViewSet, basename='structures')
router.register(r't1_xml', t1_xmlViewSet, basename='t1_xml')
router.register(r't1_table_xml', T1TableInfo, basename='t1_table_xml')
router.register(r'routes', RoutesViewSet, basename='routes')




# маршруты по XML
xml_router = routers.DefaultRouter()
xml_router.register(r'xml_info', XMLModelAPI, basename='xml_info')
xml_router.register(r'transhipment', TranshipmentAPI, basename='transhipment')
xml_router.register(r'transport_transhipment', TransportTranshipmentAPI, basename='transport_transhipment')
xml_router.register(r'container_transhipment', ContainerTranshipmentAPI, basename='container_transhipment')
xml_router.register(r'transit_guarantee', TransitGuaranteeAPI, basename='transit_guarantee')
xml_router.register(r'transport_xml', TransportXMLAPI, basename='transport_xml')
xml_router.register(r'container_xml', ContainerXMLAPI, basename='container_xml')
xml_router.register(r'consignment_item', ConsignmentItemAPI, basename='consignment_item')
xml_router.register(r'container_ci', ContainerCIAPI, basename='container_ci')
xml_router.register(r'preceding_doc', PIPrecedingDocDetailsAPI, basename='preceding_doc')
xml_router.register(r'goods_doc', PIGoodsDocDetailsAPI, basename='goods_doc')
xml_router.register(r'sanction', SanctionAPI, basename='sanction')

# точки для получения информации по xml_id
xml_router.register(r'(?P<xml_id>\d+)/consignment_item', ConsignmentItemByIDAPI, basename='consignment_item_by_xmlid')
xml_router.register(r'(?P<xml_id>\d+)/container_xml', ContainerXMLByIDAPI, basename='container_xml_by_xmlid')
xml_router.register(r'(?P<xml_id>\d+)/transport_xml', TransportXMLByIDAPI, basename='transport_xml_by_xmlid')
xml_router.register(r'(?P<xml_id>\d+)/transhipment', TranshipmentByIDAPI, basename='transhipment_by_xmlid')
xml_router.register(r'(?P<xml_id>\d+)/transit_guarantee', TransitGuaranteeByIDAPI, basename='transit_guarantee_by_xmlid')

# точки для получения информации по перецепке по transhipment_xml_id
xml_router.register(r'(?P<transhipment_xml_id>\d+)/transport_transhipment', TransportTranshipmentByTransIDAPI, basename='transport_transhipment_by_transhipment_xml_id')
xml_router.register(r'(?P<transhipment_xml_id>\d+)/container_transhipment', ContainerTranshipmentByTransIDAPI, basename='container_transhipment_by_transhipment_xml_id')

# точки для получения информации по товару по ci_id
xml_router.register(r'(?P<ci_id>\d+)/container_ci', ContainerCIByIDAPI, basename='container_ci_by_ci_id')
xml_router.register(r'(?P<ci_id>\d+)/preceding_doc', PIPrecedingDocDetailsByIDAPI, basename='preceding_doc_by_ci_id')
xml_router.register(r'(?P<ci_id>\d+)/goods_doc', PIGoodsDocDetailsByIDAPI, basename='goods_doc_by_ci_id')


schema_view = get_swagger_view(title='AlestaDRF API')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/treeupdate', DeclarantTreeTnvedUpdate.as_view()),
    path('api/v1/exchangerates', ExchangeRatesLoad.as_view()),
    path('api/v1/payment_calculations/<int:xml_id>/', PaymentCalculations.as_view()),
    path('api/v1/get_xml/<int:xml_id>/', GetXMlFile.as_view()),
    path('api/v1/get_pdf/<int:xml_id>/', GetPDFTD.as_view()),
    path('api/v1/get_opis/<int:xml_id>/', getPDFOpis.as_view()),
    path('api/v1/new_xml', NewXmlDB.as_view()),
    path('api/v1/check_tnved_code/', CheckTNVEDCode.as_view()),
    path('api/v1/get_tnved_code_description/<str:code_tnved>/', TNVEDСodeDescription.as_view()),
    path('api/v1/sanction_check/<str:id_xml>/', SanctionXMLCheck.as_view()),
    path('api/v1/update_xml/<int:xml_id>/', UpdateXmlDB.as_view()),
    path('api/v1/full_info/<int:xml_id>/', GetFullInfoXML.as_view()),
    path('api/v1/', include(router.urls)),
    path('api/v1/xml/', include(xml_router.urls)),
    path('api/v1/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path(r'api/docs/', schema_view),
    path('api/v1/import/', import_data, name='import_data'),
    path('api/v1/get_structure_code_description/<str:code_structure>/', STRUCTUREСodeDescription.as_view()),
    path('api/v1/t1_full_info_xml_get/<int:xml_id>/', T1FullInfoXML.as_view(), name='get_full_info_xml'),
    path('api/v1/t1_new_xml/', T1NewXmlDB.as_view(), name='t1_new_xml'),
    path('api/v1/get-lrn/', GetLRN.as_view(), name='get_lrn'),
    path('api/v1/get_xml_file_t1/<int:xml_id>/', GetXMlFileT1.as_view(), name='get_xml_file_t1'),
    path('api/v1/t1_update_xml/<int:xml_id>/', UpdateXmlDBT1.as_view()),




]
