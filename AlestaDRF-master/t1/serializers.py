from rest_framework import serializers
from .models import Recipient, Sender, Carrier, Product, Document, Pre_Document, Structure, t1_xml, Routes


class RoutesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Routes
        fields = '__all__'


class SenderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sender
        fields = '__all__'


class RecipientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipient
        fields = '__all__'

class CarrierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Carrier
        fields = '__all__'


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = '__all__'

class Pre_DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pre_Document
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    documents = DocumentSerializer(many=True, read_only=True)
    pre_documents = Pre_DocumentSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = '__all__'


class StructureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Structure
        fields = '__all__'

class t1_xmlSerializer(serializers.ModelSerializer):
    class Meta:
        model = t1_xml
        fields = '__all__'

#Вывод общей информации, те строки какие мы хотим видеть + добавили чтоб выводилось "Пупкин И."
class T1XML_INFOSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    date_time = serializers.SerializerMethodField()

    class Meta:
        model = t1_xml
        fields = ['id', 'user', 'date_time', 'status', 'LRN', 'MRN']

    def get_user(self, obj):
        user = obj.user
        if user:
            first_name = user.first_name
            if first_name:
                return f"{user.last_name} {first_name[0]}."
            return user.last_name
        return ""

    def get_date_time(self, obj):
        # Форматирование даты и времени без миллисекунд
        if obj.date_time:
            return obj.date_time.strftime('%Y-%m-%d %H:%M:%S')
        return None

