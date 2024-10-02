from django.db.models import Q
from django.core import serializers

from declarant.models import ConsignmentItem, Sanction
from declarant.serializers import SanctionSerializer


def sanction_check_xml(s):
    """
        Осуществляем проверку на санции всех товаров в XML по кодам.
        @param s: id xml файла в базе
        @return: сами коды и подходящие записи из базы
    """

    all_result = []
    items_list = ConsignmentItem.objects.filter(xml_id=s)
    if items_list:
        for _i in items_list:
            _q = Sanction.objects.filter(
                Q(code__startswith=_i.CommodityCode) |
                Q(code=_i.CommodityCode[:8]) |
                Q(code=_i.CommodityCode[:6]) |
                Q(code=_i.CommodityCode[:4]) |
                Q(code=_i.CommodityCode[:2])
            )
            si = []
            for __q in _q:
                si.append(SanctionSerializer(__q).data)
            all_result.append({_i.CommodityCode: si})
    return {
        'result': all_result
    }