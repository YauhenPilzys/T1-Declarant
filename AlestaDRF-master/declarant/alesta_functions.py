from datetime import datetime


def type_from_xml_name(s):
    """ функция возвращает тип xml-файла исходя из его имени
        варианты:
            PIAT - ЭПИ
            TD - декларация
            PI - старый формат ЭПИ (не обрабатываем)
            GS - сертификат обеспечения (не обрабатываем)
    """
    enable_types = {'PIAT', 'TD'}
    tmps = s[s.find('_') + 1:]  # берем только содержимое после подчеркивания
    x1 = tmps.find('.')     # чаще всего тип файла заканчивается точкой
    x2 = tmps.find('(')     # но может заканчиваться и скобкой
    if (x2 < x1) & (x2 > 0):
        type_xml = tmps[:x2]
    else:
        type_xml = tmps[:x1]
    if type_xml in enable_types:
        return type_xml
    else:
        return ''


def get_serifikat_date(d):
    """
        Функция возвращает сокращенную дату из полной
        Пример: 2023-03-20 => 200323
    """
    dt = datetime.strptime(d, '%Y-%m-%d')
    return dt.strftime("%d%m%y")


def dt_to_xml_format(d):
    """
        Функция возвращает строку из даты, для записи в xml
        Пример: 2023-03-13 12:53:00 => 2023-03-13T12:53:00
    """
    t = str(d.strftime('%Y-%m-%d %H:%M:%S'))
    return t.replace(' ', 'T')

