import datetime

from rest_framework import serializers
from rest_framework.serializers import Serializer, FileField
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from alestadrf.settings import SIMPLE_JWT
from .alesta_functions import get_serifikat_date
from .models import *


class DeclarantCarrierSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeclarantCarrier
        fields = "__all__"


class ConsignorConsigneeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConsignorConsignee
        fields = "__all__"


class PIDeclarantSerializer(serializers.ModelSerializer):
    class Meta:
        model = PIDeclarant
        fields = "__all__"


class CarrierRepresentativeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarrierRepresentative
        fields = "__all__"


class TransportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transport
        fields = "__all__"


class TreeTnvedSerializer(serializers.ModelSerializer):
    class Meta:
        model = TreeTnved
        fields = "__all__"


class TnvedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tnved
        fields = "__all__"


class ExciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Excise
        fields = "__all__"


class TranshipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transhipment
        fields = "__all__"


class TransportTranshipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransportTranshipment
        fields = "__all__"


class ContainerTranshipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContainerTranshipment
        fields = "__all__"


class TransitGuaranteeSerializer(serializers.ModelSerializer):
    full_gc = serializers.SerializerMethodField('get_full_sert_value')

    class Meta:
        model = TransitGuarantee
        fields = "__all__"

    def get_full_sert_value(self, obj):
        if obj.GC_CustomsDocumentId:
            return obj.GC_CustomsOfficeCode + '/' + get_serifikat_date(str(obj.GC_DocCreationDate)) + '/' + obj.GC_CustomsDocumentId
        else:
            return ''


class TransportXMLSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransportXML
        fields = "__all__"


class ContainerXMLSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContainerXML
        fields = "__all__"


class ConsignmentItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConsignmentItem
        fields = "__all__"


class ContainerCISerializer(serializers.ModelSerializer):
    class Meta:
        model = ContainerCI
        fields = "__all__"


class PIPrecedingDocDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PIPrecedingDocDetails
        fields = "__all__"


class PIGoodsDocDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PIGoodsDocDetails
        fields = "__all__"


class XMLModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = XMLModel
        fields = "__all__"


class UploadSerializer(Serializer):
    file_uploaded = FileField()
    class Meta:
        fields = ['file_uploaded']


class TableXMLSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    XmlType = serializers.CharField(max_length=3)
    EDocDateTime = serializers.DateTimeField()
    user = serializers.CharField(max_length=120)
    transport_list = serializers.CharField(max_length=50)
    TD_DocId = serializers.CharField(max_length=50)
    Consignor_SubjectBriefName = serializers.CharField(max_length=120)
    Consignee_SubjectBriefName = serializers.CharField(max_length=120)
    Carrier_SubjectBriefName = serializers.CharField(max_length=120)
    CarrierRepresentative_LastName = serializers.CharField(max_length=120)


class SanctionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sanction
        fields = "__all__"

class DraftJSONSerializer(serializers.ModelSerializer):
    #user = serializers.PrimaryKeyRelatedField(read_only=True, default=serializers.CurrentUserDefault())
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = DraftJSON
        fields = "__all__"
