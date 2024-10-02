from declarant.models import XMLModel

def replace_symbol(s):
    return s.replace('\\', '_').replace('/', '_').replace('|', '_').replace(' ', '_').replace(':', '_').replace('.', '_').replace('?', '_')

def get_name_xml(xml_id):
    '''
        Возвращает имя для xml-файла по данным из базы для записи с xml_id
    '''
    x = XMLModel.objects.get(pk=xml_id)
    return x.EDocId + '_' + x.XmlType + '.xml'

def get_name_TD(xml_id):
    '''
        Возвращает имя для печатной формы декларации по данным из базы для записи с xml_id
    '''
    x = XMLModel.objects.get(pk=xml_id)
    cmr = x.TD_DocId or ''
    return replace_symbol('decl_' + x.transport_list + '_' + cmr + '_' + str(x.pk)) + '.pdf'


def get_name_opis(xml_id):
    '''
        Возвращает имя для описи декларации по данным из базы для записи с xml_id
    '''
    x = XMLModel.objects.get(pk=xml_id)
    cmr = x.TD_DocId or ''
    return replace_symbol('opis_' + x.transport_list + '_' + cmr + '_' + str(x.pk)) + '.pdf'