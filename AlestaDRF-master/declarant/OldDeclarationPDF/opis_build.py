import shutil
from io import BytesIO

from PyPDF2 import PdfReader
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen.canvas import Canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Table, TableStyle, Spacer
import tempfile
import PyPDF2
from collections import OrderedDict

from declarant.OldDeclarationPDF.ColorFrame import *
from declarant.OldDeclarationPDF.my_pdf_unit import *
from declarant.OldDeclarationPDF.db_to_data import *

pagex, pagey = A4
pdfmetrics.registerFont(TTFont('Times-Roman-Cyr', 'declarant/OldDeclarationPDF/timesnrcyrmt.ttf'))
pdfmetrics.registerFont(TTFont('Arial', 'declarant/OldDeclarationPDF/Arial.ttf'))
bottom_watermark = 'ALESTA: +375 33 62 62 122 (BY); +370 61 61 81 11 (LT); +7 958 581 51 49 (RU); +48 858 760 005 (PL); E-MAIL: mail@alesta.group'
reverse_top = 'ДОПОЛНЕНИЕ К ТРАНЗИТНОЙ ДЕКЛАРАЦИИ № __________________________________________________ НА ___ Л.'


x0 = 1.4 * cm
y0 = 1.4 * cm
x1 = pagex - 1.4 * cm
y1 = pagey - 0.6 * cm

def get_name_doc(s):
    if s == '02015':
        return 'CMR'
    elif s == '04021':
        return 'Счет-фактура (инвойс)'
    elif s == '04025':
        return 'Счет-проформа (проформа)'
    elif s == '02016':
        return 'Транспортная накладная'
    elif s == '09024':
        return 'Свидетельство о допущении ТСМП к перевозке товаров под таможенными пломбами и печатями'
    elif s == '04131':
        return 'Отгрузочный (упаковочный) лист'
    elif s == '01207':
        return 'Фитосанитарный сертификат'
    elif s == '02024':
        return 'Книжка МДП'
    elif s == '05012':
        return 'Решение о классификации товаров'
    elif s == '05013':
        return 'Предварительное решение о классификации товаров в соответствии с ТН ВЭД ЕАЭС'
    elif s == '01011':
        return 'Лицензия на экспорт и (или) импорт товаров'
    else:
        return 'Иные документы'


def make_opis(data, flag=True):
    '''
        Формирование описи
        :param data: данные для заполнения (в db_to_data.py)
        :param flag: указывает, нужен ли текст "Ознакомлен..."
    '''
    temp_base = tempfile.TemporaryFile()
    doc = SimpleDocTemplate(temp_base, pagesize=A4, rightMargin=1.4 * cm, leftMargin=1.4 * cm, topMargin=0.6 * cm,
                            bottomMargin=1.4 * cm)

    canvas = Canvas(temp_base, pagesize=A4)

    elements = []


    elements.append(Paragraph('Опись документов, составляющих транзитную декларацию', style=opis_data_center))
    elements.append(Spacer(width=pagex, height=0.1 * cm))
    elements.append(Paragraph('N ________________________________________________________________________________', style=opis_data_center))
    elements.append(Spacer(width=pagex, height=0.1 * cm))
    elements.append(Paragraph('(заполняется должностным лицом таможенного органа отправления)', style=opis_data_center))
    elements.append(Spacer(width=pagex, height=0.8 * cm))

    # поиск всех документов
    docs44 = []
    for i in data.items:
        docs44.extend(i.g44)

    new_docs44 = list(OrderedDict.fromkeys(docs44))  # убираем дубликаты документов

    el = []
    el.append([
        Paragraph('№ п/п', style=opis_data_table_center),
        Paragraph('Наименование документа', style=opis_data_table_center),
        Paragraph('Номер и дата составления документа', style=opis_data_table_center),
        Paragraph('Количество листов/экземпляров', style=opis_data_table_center),
    ])
    counter = 1
    for _e in new_docs44:
        _tl = _e.split(' ')
        type_d = _tl[0]
        d = ' '.join(_tl[1:-1])
        data_d = _tl[-1]
        el.append([
            Paragraph(str(counter), style=opis_data_table_center),
            Paragraph(get_name_doc(type_d), style=opis_data_table_center),
            Paragraph(f'{d} ({data_d})', style=opis_data_table_center),
            Paragraph('', style=opis_data_table_center),
        ])
        counter += 1

    t_g44 = Table(el, colWidths=(1.2 * cm, 4.5 * cm, x1 - x0 - 7.7 * cm, 3 * cm), rowHeights=None, repeatRows=1)
    t_g44.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('GRID', (0, 0), (-1, -1), 0.25, colors.black),
        ('FONT', (0, 0), (-1, -1), 'Arial', opis_fontsize-1),
    ]))
    elements.append(t_g44)
    elements.append(Spacer(width=pagex, height=0.8 * cm))

    if flag:
        elements.append(Paragraph('С обязанностями, установленными статьями 150, 308 Таможенного кодекса ЕАЭС, ознакомлен.', style=opis_data))

    elements.append(Spacer(width=pagex, height=0.4 * cm))

    el = []
    el.append([
        Paragraph(data.g50_c, style=opis_data_table_center),
        Paragraph(data.g50_v_fio, style=opis_data_table_center),
        Paragraph('', style=opis_data_table_center),
        Paragraph('', style=opis_data_table_center),
    ])
    el.append([
        Paragraph('___________________________________', style=opis_data_table_center),
        Paragraph('________________________', style=opis_data_table_center),
        Paragraph('____________', style=opis_data_table_center),
        Paragraph('____________', style=opis_data_table_center),
    ])
    el.append([
        Paragraph('(наименование перевозчика)', style=opis_data_table_center),
        Paragraph('(инициалы и фамилия представителя перевозчика)', style=opis_data_table_center),
        Paragraph('(подпись)', style=opis_data_table_center),
        Paragraph('(дата)', style=opis_data_table_center),
    ])

    t_g = Table(el, colWidths=(x1 - x0 - 11 * cm, 5 * cm, 3 * cm, 3 * cm), rowHeights=None)
    t_g.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('FONT', (0, 0), (-1, -1), 'Arial', opis_fontsize - 1),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
    ]))
    elements.append(t_g)
    elements.append(Spacer(width=pagex, height=0.8 * cm))

    if flag:
        elements.append(Paragraph('С обязанностями, установленными статьями 153, 309 Таможенного кодекса ЕАЭС, ознакомлен.', style=opis_data))

    elements.append(Spacer(width=pagex, height=0.4 * cm))

    el = []
    el.append([
        Paragraph(data.g50[1], style=opis_data_table_center),
        Paragraph(data.g50_v_fio, style=opis_data_table_center),
        Paragraph('', style=opis_data_table_center),
        Paragraph('', style=opis_data_table_center),
    ])
    el.append([
        Paragraph('___________________________________', style=opis_data_table_center),
        Paragraph('________________________', style=opis_data_table_center),
        Paragraph('____________', style=opis_data_table_center),
        Paragraph('____________', style=opis_data_table_center),
    ])
    el.append([
        Paragraph('(наименование и адрес декларанта)', style=opis_data_table_center),
        Paragraph('(инициалы и фамилия представителя декларанта, подающего транзитную декларацию)', style=opis_data_table_center),
        Paragraph('(подпись)', style=opis_data_table_center),
        Paragraph('(дата представления описи)', style=opis_data_table_center),
    ])

    t_g = Table(el, colWidths=(x1 - x0 - 11 * cm, 5 * cm, 3 * cm, 3 * cm), rowHeights=None)
    t_g.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('FONT', (0, 0), (-1, -1), 'Arial', opis_fontsize - 1),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
    ]))
    elements.append(t_g)
    elements.append(Spacer(width=pagex, height=1.5 * cm))

    el = []

    el.append([
        Paragraph('___________________________________', style=opis_data_table_center),
        Paragraph('________________________', style=opis_data_table_center),
        Paragraph('____________', style=opis_data_table_center),
        Paragraph('____________', style=opis_data_table_center),
    ])
    el.append([
        Paragraph('', style=opis_data_table_center),
        Paragraph('(инициалы и фамилия должностного лица таможенного органа)',
                  style=opis_data_table_center),
        Paragraph('(подпись, ЛНП)', style=opis_data_table_center),
        Paragraph('(дата выпуска товаров)', style=opis_data_table_center),
    ])

    t_g = Table(el, colWidths=(x1 - x0 - 11 * cm, 5 * cm, 3 * cm, 3 * cm), rowHeights=None, repeatRows=1)
    t_g.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('FONT', (0, 0), (-1, -1), 'Arial', opis_fontsize - 1),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
    ]))
    elements.append(t_g)

    def printTop(canvas, doc):
        frame_watermark = Frame(x0, y0 - 0.6 * cm, x1 - x0, 0.6 * cm, leftPadding=1, bottomPadding=1,
                                rightPadding=1, topPadding=1, showBoundary=0)
        text = [bottom_watermark]
        placeToFrameWithShrink(text, frame_watermark, canvas, align='CENTER')
        pass

    doc.build(elements, onFirstPage=printTop, onLaterPages=printTop)

    return temp_base

def full_opis_api(idxml, f):
    '''
    Формирование описи на основе предостваленных данных
    :param idxml: ид xml в базе данных
    '''

    temp_final = BytesIO()

    # загружаем данные
    data = InfoTD()
    data.load_from_db(idxml)

    merger = PyPDF2.PdfMerger()
    # формируем опись
    merger.append(make_opis(data, flag=f))

    merger.write(temp_final)
    return temp_final