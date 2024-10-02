from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *
from . import views

router = DefaultRouter()
router.register(r'senders', SenderViewSet)
router.register(r'recipients', RecipientViewSet)
router.register(r'carriers', CarrierViewSet)
router.register(r'products', ProductViewSet)
router.register(r'documents', DocumentViewSet)
router.register(r'pre_documents', Pre_DocumentViewSet)
router.register(r'structures', StructureViewSet)
router.register(r't1_xml', t1_xmlViewSet)


urlpatterns = [
    path('', include(router.urls)),

]