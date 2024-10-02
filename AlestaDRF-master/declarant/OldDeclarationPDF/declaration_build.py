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


class AdditionalData:
    def __init__(self):
        self.g31 = []  # номер товара, для которого сведения выносятся на оборотку и наименование товара
        self.g40 = []  # предшедствующие доки
        self.g44 = []  # доки к товару
        self.g50 = []  # перевозчики (не относится к товару, может быть только на первой странице)
        self.g52_1 = []  # гарант (не относится к товару, может быть только на первой странице)
        self.g52_2 = []  # гарант (не относится к товару, может быть только на первой странице)
        self.g52_3 = []  # гарант (не относится к товару, может быть только на первой странице)

    '''
    def __str__(self):
        print(self.g31)
        print(self.g40)
        print(self.g44)
        print(self.g50)
        print(self.g52_1)
        print(self.g52_2)
        print(self.g52_3)
    '''


def first_page_TD(data):
    temp_base = tempfile.TemporaryFile()
    #temp_final = tempfile.TemporaryFile(delete=False)
    temp_final = tempfile.TemporaryFile()
    path_final = temp_final.name
    merger = PyPDF2.PdfMerger()

    canvas = Canvas(temp_base, pagesize=A4)

    # внешний прямоугольник
    canvas.rect(x0, y0, x1 - x0, y1 - y0)
    canvas.saveState()
    canvas.setStrokeColor(white)
    canvas.restoreState()

    # графа ТРАНЗИТНАЯ ДЕКЛАРАЦИЯ
    frame = Frame(x0, y1 - 0.8 * cm, 9.8 * cm, 0.8 * cm, leftPadding=1, bottomPadding=1,
                  rightPadding=1, topPadding=1, showBoundary=1)
    text = ["ТРАНЗИТНАЯ ДЕКЛАРАЦИЯ"]
    placeToFrameWithTruncate(text, frame, canvas)

    canvas.rect(x0, y1 - 9.8 * cm, 0.6 * cm, 9 * cm, stroke=1, fill=0)
    canvas.rect(x0 + 0.6 * cm, y1 - 9.8 * cm, 0.6 * cm, 9 * cm, stroke=1, fill=0)
    canvas.rect(x0, y1 - 1.6 * cm, 1.2 * cm, 0.8 * cm, stroke=1, fill=0)
    #canvas.rect(x0, y1 - 9.8 * cm, 9.8 * cm, 0.8 * cm, stroke=1, fill=0)

    canvas.rect(x0 + 9.8 * cm, y1 - 0.4 * cm, 3.1 * cm, 0.4 * cm, stroke=1, fill=0)

    frame = Frame(x0 + 9.8 * cm, y1 - 0.8 * cm, 3.1 * cm, 0.4 * cm, leftPadding=1, bottomPadding=1,
                  rightPadding=1, topPadding=1, showBoundary=1)
    text = ["1 ДЕКЛАРАЦИЯ"]
    placeToFrameWithTruncate(text, frame, canvas)

    # графа А
    frameA = Frame(x0 + 12.9 * cm, y1 - 2 * cm, x1 - x0 - 12.9 * cm, 2 * cm, leftPadding=1, bottomPadding=1,
                   rightPadding=1, topPadding=1, showBoundary=1)
    text = ["А ОРГАН ОТПРАВЛЕНИЯ"]
    placeToFrameWithTruncate(text, frameA, canvas)

    # графа 1
    frame1_1 = Frame(x0 + 9.8 * cm, y1 - 1.2 * cm, 0.7 * cm, 0.4 * cm, leftPadding=1, bottomPadding=1, rightPadding=1, topPadding=1, showBoundary=1)
    text = [""]
    placeToFrameWithTruncate(text, frame1_1, canvas)
    frame1_2 = Frame(x0 + 10.5 * cm, y1 - 1.2 * cm, 1.2 * cm, 0.4 * cm, leftPadding=1, bottomPadding=1, rightPadding=1,
                     topPadding=1, showBoundary=1)
    text = [""]
    placeToFrameWithTruncate(text, frame1_2, canvas)
    frame1_3 = Frame(x0 + 11.7 * cm, y1 - 1.2 * cm, 1.2 * cm, 0.4 * cm, leftPadding=1, bottomPadding=1, rightPadding=1,
                     topPadding=1, showBoundary=1)
    text = [""]
    placeToFrameWithTruncate(text, frame1_3, canvas)

    # графа 3
    frame = Frame(x0 + 9.8 * cm, y1 - 1.6 * cm, 1.4 * cm, 0.4 * cm, leftPadding=1, bottomPadding=1,
                  rightPadding=1, topPadding=1, showBoundary=1)
    text = ["3 Формы"]
    placeToFrameWithTruncate(text, frame, canvas)

    frame3_1 = Frame(x0 + 9.8 * cm, y1 - 2 * cm, 0.7 * cm, 0.4 * cm, leftPadding=1,
                   bottomPadding=1, rightPadding=1, topPadding=1, showBoundary=1)
    text = [""]
    placeToFrameWithTruncate(text, frame3_1, canvas)

    frame3_2 = Frame(x0 + 10.5 * cm, y1 - 2 * cm, 0.7 * cm, 0.4 * cm, leftPadding=1,
                     bottomPadding=1, rightPadding=1, topPadding=1, showBoundary=1)
    text = [""]
    placeToFrameWithTruncate(text, frame3_2, canvas)

    # графа 4
    frame = Frame(x0 + 11.2 * cm, y1 - 1.6 * cm, 1.7 * cm, 0.4 * cm, leftPadding=1, bottomPadding=1,
                  rightPadding=1, topPadding=1, showBoundary=1)
    text = ["4 Отгр спец"]
    placeToFrameWithTruncate(text, frame, canvas)

    frame4 = Frame(x0 + 11.2 * cm, y1 - 2 * cm, 1.7 * cm, 0.4 * cm, leftPadding=1,
                     bottomPadding=1, rightPadding=1, topPadding=1, showBoundary=1)
    text = [""]
    placeToFrameWithTruncate(text, frame4, canvas)

    # графа 5
    frame = Frame(x0 + 9.8 * cm, y1 - 2.4 * cm, 2 * cm, 0.4 * cm, leftPadding=1, bottomPadding=1,
                   rightPadding=1, topPadding=1, showBoundary=1)
    text = ["5 Всего т-ов"]
    placeToFrameWithTruncate(text, frame, canvas)

    frame5 = Frame(x0 + 9.8 * cm, y1 - 2.8 * cm, 2 * cm, 0.4 * cm, leftPadding=1, bottomPadding=1,
                   rightPadding=1, topPadding=1, showBoundary=1)
    text = [""]
    placeToFrameWithTruncate(text, frame5, canvas)

    # графа 6
    frame = Frame(x0 + 11.8 * cm, y1 - 2.4 * cm, 2 * cm, 0.4 * cm, leftPadding=1, bottomPadding=1,
                   rightPadding=1, topPadding=1, showBoundary=1)
    text = ["6 Всего мест"]
    placeToFrameWithTruncate(text, frame, canvas)

    frame6 = Frame(x0 + 11.8 * cm, y1 - 2.8 * cm, 2 * cm, 0.4 * cm, leftPadding=1, bottomPadding=1,
                   rightPadding=1, topPadding=1, showBoundary=1)
    text = [""]
    placeToFrameWithTruncate(text, frame6, canvas)

    canvas.rect(x0 + 13.8 * cm, y1 - 2.8 * cm, x1 - x0 - 13.8 * cm, 0.8 * cm, stroke=1, fill=0)

    # графа 2
    frame2 = Frame(x0 + 1.2 * cm, y1 - 2.8 * cm, 8.6 * cm, 2 * cm, leftPadding=1, bottomPadding=1,
                   rightPadding=1, topPadding=1, showBoundary=1)
    text = ["2 Отправитель/Экспортер"]
    placeToFrameWithTruncate(text, frame2, canvas)

    # графа 8
    frame8 = Frame(x0 + 1.2 * cm, y1 - 4.8 * cm, 8.6 * cm, 2 * cm, leftPadding=1, bottomPadding=1,
                   rightPadding=1, topPadding=1, showBoundary=1)
    text = ["8 Получатель"]
    placeToFrameWithTruncate(text, frame8, canvas)

    canvas.rect(x0 + 1.2 * cm, y1 - 6.4 * cm, 8.6 * cm, 1.6 * cm, stroke=1, fill=0)
    text = ["N"]
    frame = Frame(x0 + 5.5 * cm, y1 - 1.2 * cm, 1 * cm, 0.4 * cm, leftPadding=1, bottomPadding=1,
                   rightPadding=1, topPadding=1, showBoundary=0)
    placeToFrameWithTruncate(text, frame, canvas)
    frame = Frame(x0 + 5.5 * cm, y1 - 3.2 * cm, 1 * cm, 0.4 * cm, leftPadding=1, bottomPadding=1,
                  rightPadding=1, topPadding=1, showBoundary=0)
    placeToFrameWithTruncate(text, frame, canvas)
    frame = Frame(x0 + 5.5 * cm, y1 - 5.2 * cm, 1 * cm, 0.4 * cm, leftPadding=1, bottomPadding=1,
                  rightPadding=1, topPadding=1, showBoundary=0)
    placeToFrameWithTruncate(text, frame, canvas)

    # графа 15
    frame15 = Frame(x0 + 9.8 * cm, y1 - 5.6 * cm, 4 * cm, 0.8 * cm, leftPadding=1, bottomPadding=1,
                    rightPadding=1, topPadding=1, showBoundary=1)
    text = ["15 Страна отправления"]
    placeToFrameWithTruncate(text, frame15, canvas)
    canvas.rect(x0 + 13.8 * cm, y1 - 5.6 * cm, x1 - x0 - 13.8 * cm, 0.8 * cm, stroke=1, fill=0)

    # графа 17
    frame17 = Frame(x0 + 13.8 * cm, y1 - 6.4 * cm, x1 - x0 - 13.8 * cm, 0.8 * cm, leftPadding=1, bottomPadding=1,
                    rightPadding=1, topPadding=1, showBoundary=1)
    text = ["17 Страна назначения"]
    placeToFrameWithTruncate(text, frame17, canvas)
    canvas.rect(x0 + 9.8 * cm, y1 - 6.4 * cm, 4 * cm, 0.8 * cm, stroke=1, fill=0)

    # графа 18
    frame18 = Frame(x0 + 1.2 * cm, y1 - 7.7 * cm, 7.1 * cm, 1.3 * cm, leftPadding=1, bottomPadding=1,
                    rightPadding=1, topPadding=1, showBoundary=1)
    text = ["18 Идентификация и страна регистрации трансп. средства при отправлении/прибытии"]
    placeToFrameWithTruncate(text, frame18, canvas)
    canvas.line(x0 + 7.7 * cm, y1 - 7.7 * cm, x0 + 7.7 * cm, y1 - 7.3 * cm)  # в графе 18

    # графа 19
    frame19 = Frame(x0 + 8.3 * cm, y1 - 7.7 * cm, 1.5 * cm, 1.3 * cm, leftPadding=1, bottomPadding=1,
                    rightPadding=1, topPadding=1, showBoundary=1)
    text = ["19 Конт."]
    placeToFrameWithTruncate(text, frame19, canvas)

    # графа 21
    frame21 = Frame(x0 + 1.2 * cm, y1 - 9 * cm, 8.6 * cm, 1.3 * cm, leftPadding=1, bottomPadding=1,
                    rightPadding=1, topPadding=1, showBoundary=1)
    text = ["21 Идентификатор и страна регистрации транспортного средства на границе"]
    placeToFrameWithTruncate(text, frame21, canvas)
    canvas.line(x0 + 9.2 * cm, y1 - 9 * cm, x0 + 9.2 * cm, y1 - 8.6 * cm)  # в графе 21

    # графа 22
    frame22 = Frame(x0 + 9.8 * cm, y1 - 9 * cm, 5 * cm, 1.3 * cm, leftPadding=1, bottomPadding=1,
                    rightPadding=1, topPadding=1, showBoundary=1)
    text = ["22 Валюта и общ. ст. по счету"]
    placeToFrameWithTruncate(text, frame22, canvas)
    canvas.line(x0 + 10.8 * cm, y1 - 9 * cm, x0 + 10.8 * cm, y1 - 8.6 * cm)  # в графе 22
    canvas.line(x0 + 10.8 * cm, y1 - 7.7 * cm, x0 + 10.8 * cm, y1 - 7.3 * cm)  # над графой 22
    canvas.line(x1 - 1 * cm, y1 - 7.7 * cm, x1 - 1 * cm, y1 - 7.3 * cm)  # над графой 22
    canvas.rect(x0 + 14.8 * cm, y1 - 9 * cm, 1.5 * cm, 1.3 * cm, stroke=1, fill=0)
    canvas.rect(x0 + 16.3 * cm, y1 - 9 * cm, x1 - x0 - 16.3 * cm, 1.3 * cm, stroke=1, fill=0)
    canvas.line(x0 + 16.9 * cm, y1 - 9 * cm, x0 + 16.9 * cm, y1 - 8.6 * cm)  # справа от графы 22
    canvas.line(x0 + 17.5 * cm, y1 - 9 * cm, x0 + 17.5 * cm, y1 - 8.6 * cm)  # справа от графы 22

    # графа 25
    frame25 = Frame(x0 + 1.2 * cm, y1 - 9.8 * cm, 8.6 * cm, 0.8 * cm, leftPadding=1, bottomPadding=1,
                    rightPadding=1, topPadding=1, showBoundary=1)
    text = ["25 Вид транспорта на границе"]
    placeToFrameWithTruncate(text, frame25, canvas)
    canvas.line(x0 + 2.2 * cm, y1 - 9.8 * cm, x0 + 2.2 * cm, y1 - 9.4 * cm)  # в графе 25
    canvas.line(x0 + 9.2 * cm, y1 - 9.8 * cm, x0 + 9.2 * cm, y1 - 9.4 * cm)  # в графе 25
    canvas.rect(x0 + 9.8 * cm, y1 - 9.8 * cm, x1 - x0 - 9.8 * cm, 0.8 * cm, stroke=1, fill=0)

    # графа 31 (только заголовок)
    frame31_ = Frame(x0, y1 - 13.4 * cm, 1.2 * cm, 3.6 * cm, leftPadding=1, bottomPadding=1,
                     rightPadding=1, topPadding=1, showBoundary=1)
    text = ["31 Грузовые места и описание товаров"]
    placeToFrameWithTruncate(text, frame31_, canvas)

    # графа 44 (только заголовок)
    frame44_ = Frame(x0, y1 - 15.4 * cm, 1.2 * cm, 2 * cm, leftPadding=1, bottomPadding=1,
                     rightPadding=1, topPadding=1, showBoundary=1)
    text = ["44 Доп. инф./ Пред. док./ Серт. и разр."]
    placeToFrameWithTruncate(text, frame44_, canvas)

    # графа 55
    frame55_ = Frame(x0, y1 - 18.4 * cm, 1.2 * cm, 3 * cm, leftPadding=1, bottomPadding=1,
                     rightPadding=1, topPadding=1, showBoundary=1)
    text = ["55 Перегрузки"]
    placeToFrameWithTruncate(text, frame55_, canvas)

    # графа F
    frameF = Frame(x0, y1 - 19.9 * cm, 1.2 * cm, 1.5 * cm, leftPadding=1, bottomPadding=1,
                   rightPadding=1, topPadding=1, showBoundary=1)
    text = ["F Подтверждение комп органов"]
    placeToFrameWithTruncate(text, frameF, canvas)

    # графа 31 (текст в графе)
    frame31 = Frame(x0 + 1.2 * cm, y1 - 13.4 * cm, 9.6 * cm, 3.6 * cm, leftPadding=1, bottomPadding=1,
                    rightPadding=1, topPadding=1, showBoundary=1)
    placeToFrameWithTruncate([""], frame31, canvas)
    frame31__ = Frame(x0 + 1.2 * cm, y1 - 10.6 * cm, 7.5 * cm, 0.8 * cm, leftPadding=1, bottomPadding=1,
                      rightPadding=1, topPadding=1, showBoundary=0)
    text = ["Маркировка и количество - Номера контейнеров - Количество и отличительные особенности товаров"]
    placeToFrameWithTruncate(text, frame31__, canvas)

    # графа 32
    frame32 = Frame(x0 + 8.8 * cm, y1 - 10.6 * cm, 2 * cm, 0.8 * cm, leftPadding=1, bottomPadding=1,
                    rightPadding=1, topPadding=1, showBoundary=1)
    text = ["32 Товар"]
    placeToFrameWithTruncate(text, frame32, canvas)
    canvas.line(x0 + 9.8 * cm, y1 - 10.6 * cm, x0 + 9.8 * cm, y1 - 10.2 * cm)  # в графе 32

    # графа 33
    frame33 = Frame(x0 + 10.8 * cm, y1 - 10.6 * cm, 4 * cm, 0.8 * cm, leftPadding=1, bottomPadding=1,
                    rightPadding=1, topPadding=1, showBoundary=1)
    text = ["33 Код товара"]
    placeToFrameWithTruncate(text, frame33, canvas)
    canvas.rect(x0 + 14.8 * cm, y1 - 10.6 * cm, 1.5 * cm, 0.8 * cm, stroke=1, fill=0)  # правее графы 33
    canvas.rect(x0 + 16.3 * cm, y1 - 10.6 * cm, x1 - x0 - 16.3 * cm, 0.8 * cm, stroke=1, fill=0)  # правее графы 33
    canvas.line(x0 + 13.6 * cm, y1 - 10.6 * cm, x0 + 13.6 * cm, y1 - 10.2 * cm)  # в графе 33
    canvas.line(x0 + 14.2 * cm, y1 - 10.6 * cm, x0 + 14.2 * cm, y1 - 10.2 * cm)  # в графе 33

    # графа 35
    canvas.rect(x0 + 10.8 * cm, y1 - 11.4 * cm, 1 * cm, 0.8 * cm, stroke=1, fill=0)  # под графой 33
    canvas.rect(x0 + 10.8 * cm, y1 - 11.8 * cm, 1 * cm, 0.4 * cm, stroke=1, fill=0)  # под графой 33
    frame35 = Frame(x0 + 11.8 * cm, y1 - 11.4 * cm, 4.5 * cm, 0.8 * cm, leftPadding=1, bottomPadding=1,
                    rightPadding=1, topPadding=1, showBoundary=1)
    text = ["35 Вес брутто (кг)"]
    placeToFrameWithTruncate(text, frame35, canvas)
    canvas.rect(x0 + 11.8 * cm, y1 - 11.8 * cm, 4.5 * cm, 0.4 * cm, stroke=1, fill=0)  # под графой 35

    # графа 40
    frame40 = Frame(x0 + 10.8 * cm, y1 - 12.6 * cm, x1 - x0 - 10.8 * cm, 0.8 * cm, leftPadding=1, bottomPadding=1,
                    rightPadding=1, topPadding=1, showBoundary=1)
    text = ["40 Общая декл./Предшествующий документ"]
    placeToFrameWithTruncate(text, frame40, canvas)

    # графа 41
    frame41 = ColorFrame(x0 + 10.8 * cm, y1 - 13.4 * cm, 4 * cm, 0.8 * cm, leftPadding=1, bottomPadding=1,
                         rightPadding=1, topPadding=1, showBoundary=1, background=white)
    text = ["41 Дополн. ед. изм."]
    placeToFrameWithTruncate(text, frame41, canvas)

    # графа 42
    frame42 = Frame(x0 + 14.8 * cm, y1 - 13.4 * cm, x1 - x0 - 14.8 * cm, 0.8 * cm, leftPadding=1, bottomPadding=1,
                    rightPadding=1, topPadding=1, showBoundary=1)
    text = ["42 Валюта и стоим. тов."]
    placeToFrameWithTruncate(text, frame42, canvas)
    canvas.line(x0 + 15.8 * cm, y1 - 13.4 * cm, x0 + 15.8 * cm, y1 - 13 * cm)  # в графе 33

    # код ДИ
    frameDI = Frame(x0 + 13.8 * cm, y1 - 14.2 * cm, 2 * cm, 0.8 * cm, leftPadding=1, bottomPadding=1,
                    rightPadding=1, topPadding=1, showBoundary=1)
    text = ["Код ДИ"]
    placeToFrameWithTruncate(text, frameDI, canvas)

    # графа 44
    frame44 = Frame(x0 + 1.2 * cm, y1 - 15.4 * cm, 12.6 * cm, 2 * cm, leftPadding=1, bottomPadding=1,
                    rightPadding=1, topPadding=1, showBoundary=1)
    text = [""]
    placeToFrameWithTruncate(text, frame44, canvas)

    # графа 55-1 место
    frame55_place_1 = Frame(x0 + 1.2 * cm, y1 - 16.4 * cm, 8.6 * cm, 1 * cm, leftPadding=1, bottomPadding=1,
                            rightPadding=1, topPadding=1, showBoundary=1)
    text = ["Место и страна"]
    placeToFrameWithTruncate(text, frame55_place_1, canvas)

    # графа 55-2 место
    frame55_place_2 = Frame(x0 + 9.8 * cm, y1 - 16.4 * cm, x1 - x0 - 9.8 * cm, 1 * cm, leftPadding=1,
                            bottomPadding=1, rightPadding=1, topPadding=1, showBoundary=1)
    text = ["Место и страна"]
    placeToFrameWithTruncate(text, frame55_place_2, canvas)

    # графа 55-1 авто
    frame55_ts_1 = Frame(x0 + 1.2 * cm, y1 - 17.2 * cm, 8.6 * cm, 0.8 * cm, leftPadding=1, bottomPadding=1,
                         rightPadding=1, topPadding=1, showBoundary=1)
    text = ["Идент. и страна регистрации транспортного средства"]
    placeToFrameWithTruncate(text, frame55_ts_1, canvas)
    canvas.line(x0 + 9.2 * cm, y1 - 17.2 * cm, x0 + 9.2 * cm, y1 - 16.8 * cm)  # в графе 55-1 авто

    # графа 55-2 авто
    frame55_ts_2 = Frame(x0 + 9.8 * cm, y1 - 17.2 * cm, x1 - x0 - 9.8 * cm, 0.8 * cm, leftPadding=1, bottomPadding=1,
                         rightPadding=1, topPadding=1, showBoundary=1)
    text = ["Идент. и страна регистрации транспортного средства"]
    placeToFrameWithTruncate(text, frame55_ts_2, canvas)
    canvas.line(x1 - 0.6 * cm, y1 - 17.2 * cm, x1 - 0.6 * cm, y1 - 16.8 * cm)  # в графе 55-2 авто

    # графа 55-1 контейнер
    frame55_cont_1_ = Frame(x0 + 1.2 * cm, y1 - 18 * cm, 1.2 * cm, 0.8 * cm, leftPadding=1, bottomPadding=1,
                            rightPadding=1, topPadding=1, showBoundary=1)
    text = ["Контейнер"]
    placeToFrameWithTruncate(text, frame55_cont_1_, canvas)
    frame55_cont_1 = Frame(x0 + 3 * cm, y1 - 18 * cm, 6.8 * cm, 0.8 * cm, leftPadding=1, bottomPadding=1,
                           rightPadding=1, topPadding=1, showBoundary=1)  # справа от графы 55-1 контейнер
    text = ["(1) Номер нового контейнера"]
    placeToFrameWithTruncate(text, frame55_cont_1, canvas)

    # графа 55-2 контейнер
    frame55_cont_2_ = Frame(x0 + 9.8 * cm, y1 - 18 * cm, 1.2 * cm, 0.8 * cm, leftPadding=1, bottomPadding=1,
                            rightPadding=1, topPadding=1, showBoundary=1)
    text = ["Контейнер"]
    placeToFrameWithTruncate(text, frame55_cont_2_, canvas)
    frame55_cont_2 = Frame(x0 + 11.6 * cm, y1 - 18 * cm, x1 - x0 - 11.6 * cm, 0.8 * cm, leftPadding=1,
                           bottomPadding=1,
                           rightPadding=1, topPadding=1, showBoundary=1)  # справа от графы 55-2 контейнер
    text = ["(1) Номер нового контейнера"]
    placeToFrameWithTruncate(text, frame55_cont_2, canvas)

    text = ["(1) Указать 1 если ДА или 0 если НЕТ"]
    frame = Frame(x0 + 1.2 * cm, y1 - 18.4 * cm, 8.6 * cm, 0.4 * cm, leftPadding=1, bottomPadding=1,
                            rightPadding=1, topPadding=1, showBoundary=1)
    placeToFrameWithTruncate(text, frame, canvas)
    frame = Frame(x0 + 9.8 * cm, y1 - 18.4 * cm, x1 - x0 - 9.8 * cm, 0.4 * cm, leftPadding=1, bottomPadding=1,
                  rightPadding=1, topPadding=1, showBoundary=1)
    placeToFrameWithTruncate(text, frame, canvas)

    # графа F-1
    frame = Frame(x0 + 1.2 * cm, y1 - 19.9 * cm, 8.6 * cm, 1.5 * cm, leftPadding=1, bottomPadding=1,
                            rightPadding=1, topPadding=1, showBoundary=1)
    text = ["Новые пломбы: Номер:"]
    placeToFrameWithTruncate(text, frame, canvas)
    fr = Frame(x0 + 6.8 * cm, y1 - 18.8 * cm, 3 * cm, 0.4 * cm, leftPadding=1, bottomPadding=1,
                  rightPadding=1, topPadding=1, showBoundary=0)
    text = ["Тип:"]
    placeToFrameWithTruncate(text, fr, canvas)
    fr = Frame(x0 + 1.2 * cm, y1 - 19.9 * cm, 2 * cm, 0.4 * cm, leftPadding=1, bottomPadding=1,
               rightPadding=1, topPadding=1, showBoundary=0)
    text = ["Подпись"]
    placeToFrameWithTruncate(text, fr, canvas)
    fr = Frame(x0 + 6.8 * cm, y1 - 19.9 * cm, 3 * cm, 0.4 * cm, leftPadding=1, bottomPadding=1,
               rightPadding=1, topPadding=1, showBoundary=0)
    text = ["Печать"]
    placeToFrameWithTruncate(text, fr, canvas)

    # графа F-2
    frame = Frame(x0 + 9.8 * cm, y1 - 19.9 * cm, x1 - x0 - 9.8 * cm, 1.5 * cm, leftPadding=1, bottomPadding=1,
                  rightPadding=1, topPadding=1, showBoundary=1)
    text = ["Новые пломбы: Номер:"]
    placeToFrameWithTruncate(text, frame, canvas)
    fr = Frame(x1 - 3 * cm, y1 - 18.8 * cm, 3 * cm, 0.4 * cm, leftPadding=1, bottomPadding=1,
               rightPadding=1, topPadding=1, showBoundary=0)
    text = ["Тип:"]
    placeToFrameWithTruncate(text, fr, canvas)
    fr = Frame(x0 + 9.8 * cm, y1 - 19.9 * cm, 2 * cm, 0.4 * cm, leftPadding=1, bottomPadding=1,
               rightPadding=1, topPadding=1, showBoundary=0)
    text = ["Подпись"]
    placeToFrameWithTruncate(text, fr, canvas)
    fr = Frame(x1 - 3 * cm, y1 - 19.9 * cm, 3 * cm, 0.4 * cm, leftPadding=1, bottomPadding=1,
               rightPadding=1, topPadding=1, showBoundary=0)
    text = ["Печать"]
    placeToFrameWithTruncate(text, fr, canvas)

    # графа 50
    canvas.rect(x0, y1 - 23.4 * cm, 1.2 * cm, 3.5 * cm, stroke=1, fill=0)
    frame50 = Frame(x0 + 1.2 * cm, y1 - 23.4 * cm, 10.5 * cm, 3.5 * cm, leftPadding=1, bottomPadding=1,
                    rightPadding=1, topPadding=1, showBoundary=1)
    text = ["50 Принципал"]
    placeToFrameWithTruncate(text, frame50, canvas)
    fr = Frame(x0 + 5 * cm, y1 - 20.3 * cm, 1 * cm, 0.4 * cm, leftPadding=1, bottomPadding=1,
               rightPadding=1, topPadding=1, showBoundary=0)
    text = ["N"]
    placeToFrameWithTruncate(text, fr, canvas)
    fr = Frame(x0 + 9.2 * cm, y1 - 20.3 * cm, 3 * cm, 0.4 * cm, leftPadding=1, bottomPadding=1,
               rightPadding=1, topPadding=1, showBoundary=0)
    text = ["Подпись:"]
    placeToFrameWithTruncate(text, fr, canvas)

    # графа C
    frameC = Frame(x0 + 11.7 * cm, y1 - 23.4 * cm, x1 - x0 - 11.7 * cm, 3.5 * cm, leftPadding=1, bottomPadding=1,
                   rightPadding=1, topPadding=1, showBoundary=1)
    text = ["C ОРГАН ОТПРАВЛЕНИЯ"]
    placeToFrameWithTruncate(text, frameC, canvas)

    # графа 52
    frame52_1 = Frame(x0, y1 - 24.7 * cm, 11.7 * cm, 1.3 * cm, leftPadding=1, bottomPadding=1,
                    rightPadding=1, topPadding=1, showBoundary=1)
    text = ["52 Гарантия"]
    placeToFrameWithTruncate(text, frame52_1, canvas)

    frame52_2 = Frame(x0 + 11 * cm, y1 - 24.7 * cm, 0.7 * cm, 1.3 * cm, leftPadding=1, bottomPadding=1,
                      rightPadding=1, topPadding=1, showBoundary=0)
    text = ["Код"]
    placeToFrameWithTruncate(text, frame52_2, canvas)
    canvas.line(x0 + 11 * cm, y1 - 24.7 * cm, x0 + 11 * cm, y1 - 24.3 * cm)

    # графа 53
    frame53 = Frame(x0 + 11.7 * cm, y1 - 24.7 * cm, x1 - x0 - 11.7 * cm, 1.3 * cm, leftPadding=1, bottomPadding=1,
                    rightPadding=1, topPadding=1, showBoundary=1)
    text = ["53 Орган назначения (и страна)"]
    placeToFrameWithTruncate(text, frame53, canvas)

    # графа D
    frameD = Frame(x0, y0, 7 * cm, y1 - y0 - 24.7 * cm, leftPadding=1, bottomPadding=1,
                   rightPadding=1, topPadding=1, showBoundary=1)
    text = ["D. ОТМЕТКИ  ОРГАНА ОТПРАВЛЕНИЯ Печать:"]
    placeToFrameWithTruncate(text, frameD, canvas)
    fr = Frame(x0, y0 + 2.3 * cm, 3 * cm, 0.4 * cm, leftPadding=1, bottomPadding=1, rightPadding=1, topPadding=1, showBoundary=0)
    text = ["Результат"]
    placeToFrameWithTruncate(text, fr, canvas)
    fr = Frame(x0, y0 + 1.9 * cm, 2 * cm, 0.4 * cm, leftPadding=1, bottomPadding=1, rightPadding=1, topPadding=1,
               showBoundary=0)
    text = ["Нал. пл.:"]
    placeToFrameWithTruncate(text, fr, canvas)
    fr = Frame(x0 + 2 * cm, y0 + 1.9 * cm, 2 * cm, 0.4 * cm, leftPadding=1, bottomPadding=1, rightPadding=1, topPadding=1,
               showBoundary=0)
    text = ["Номер:"]
    placeToFrameWithTruncate(text, fr, canvas)
    fr = Frame(x0, y0 + 1.5 * cm, 2 * cm, 0.4 * cm, leftPadding=1, bottomPadding=1, rightPadding=1, topPadding=1,
               showBoundary=0)
    text = ["Тип:"]
    placeToFrameWithTruncate(text, fr, canvas)
    fr = Frame(x0, y0 + 1.1 * cm, 4 * cm, 0.4 * cm, leftPadding=1, bottomPadding=1, rightPadding=1, topPadding=1,
               showBoundary=0)
    text = ["Срок транзита (Дата):"]
    placeToFrameWithTruncate(text, fr, canvas)
    fr = Frame(x0, y0 + 0.2 * cm, 3 * cm, 0.4 * cm, leftPadding=1, bottomPadding=1, rightPadding=1, topPadding=1, showBoundary=0)
    text = ["Подпись"]
    placeToFrameWithTruncate(text, fr, canvas)

    # графа I
    frameI = Frame(x0 + 7 * cm, y0, 6 * cm, y1 - y0 - 24.7 * cm, leftPadding=1, bottomPadding=1,
                   rightPadding=1, topPadding=1, showBoundary=1)
    text = ["I. КОНТРОЛЬ ОРГАНА НАЗНАЧЕНИЯ"]
    placeToFrameWithTruncate(text, frameI, canvas)
    fr = Frame(x0 + 7 * cm, y0 + 2.3 * cm, 4 * cm, 0.4 * cm, leftPadding=1, bottomPadding=1, rightPadding=1, topPadding=1,
               showBoundary=0)
    text = ["Дата прибытия:"]
    placeToFrameWithTruncate(text, fr, canvas)
    fr = Frame(x0 + 7 * cm, y0 + 1.9 * cm, 4 * cm, 0.4 * cm, leftPadding=1, bottomPadding=1, rightPadding=1, topPadding=1,
               showBoundary=0)
    text = ["Проверка пломб:"]
    placeToFrameWithTruncate(text, fr, canvas)
    fr = Frame(x0 + 7 * cm, y0 + 1.1 * cm, 4 * cm, 0.4 * cm, leftPadding=1, bottomPadding=1, rightPadding=1, topPadding=1,
               showBoundary=0)
    text = ["Комментарии:"]
    placeToFrameWithTruncate(text, fr, canvas)

    # графа справа внизу
    frame = Frame(x0 + 13 * cm, y0, x1 - x0 - 13 * cm, y1 - y0 - 24.7 * cm, leftPadding=1, bottomPadding=1,
                   rightPadding=1, topPadding=1, showBoundary=1)
    text = ["Экз. возвращен"]
    placeToFrameWithTruncate(text, frame, canvas)
    fr = Frame(x0 + 13 * cm, y0 + 2.3 * cm, 4 * cm, 0.4 * cm, leftPadding=1, bottomPadding=1, rightPadding=1,
               topPadding=1,
               showBoundary=0)
    text = ["Дата:"]
    placeToFrameWithTruncate(text, fr, canvas)
    fr = Frame(x0 + 13 * cm, y0 + 1.9 * cm, 4 * cm, 0.4 * cm, leftPadding=1, bottomPadding=1, rightPadding=1,
               topPadding=1, showBoundary=0)
    text = ["После рег. под"]
    placeToFrameWithTruncate(text, fr, canvas)
    fr = Frame(x0 + 13 * cm, y0 + 1.5 * cm, 2 * cm, 0.4 * cm, leftPadding=1, bottomPadding=1, rightPadding=1, topPadding=1,
               showBoundary=0)
    text = ["N"]
    placeToFrameWithTruncate(text, fr, canvas)
    fr = Frame(x0 + 13 * cm, y0 + 0.2 * cm, 3 * cm, 0.4 * cm, leftPadding=1, bottomPadding=1, rightPadding=1, topPadding=1,
               showBoundary=0)
    text = ["Подпись"]
    placeToFrameWithTruncate(text, fr, canvas)
    fr = Frame(x0 + 16 * cm, y0 + 0.2 * cm, 2 * cm, 0.4 * cm, leftPadding=1, bottomPadding=1, rightPadding=1,
               topPadding=1, showBoundary=0)
    text = ["Печать"]
    placeToFrameWithTruncate(text, fr, canvas)

    frame_watermark = Frame(x0, y0 - 0.6 * cm, x1 - x0, 0.6 * cm, leftPadding=1, bottomPadding=1,
                            rightPadding=1, topPadding=1, showBoundary=0)
    text = [bottom_watermark]
    placeToFrameWithShrink(text, frame_watermark, canvas)

    #убираем внешнюю рамку
    canvas.saveState()
    canvas.setStrokeColor(white)
    canvas.setLineWidth(2)
    canvas.rect(x0, y0, x1 - x0, y1 - y0)
    canvas.restoreState()


    # заполняем данными
    ad = AdditionalData()
    # графа 1
    if data.g1_1 is not None:
        f = Frame(frame1_1.x1, frame1_1.y1, frame1_1.width, 0.4 * cm, leftPadding=1, bottomPadding=1,
                  rightPadding=1, topPadding=1, showBoundary=0)
        text = [data.g1_1]
        placeToFrameWithShrink(text, f, canvas, only_data=1, align='CENTER')

    if data.g1_2 is not None:
        f = Frame(frame1_2.x1, frame1_2.y1, frame1_2.width, 0.4 * cm, leftPadding=1, bottomPadding=1,
                  rightPadding=1, topPadding=1, showBoundary=0)
        text = [data.g1_2]
        placeToFrameWithShrink(text, f, canvas, only_data=1, align='CENTER')

    if data.g1_3 is not None:
        f = Frame(frame1_3.x1, frame1_3.y1, frame1_3.width, 0.4 * cm, leftPadding=1, bottomPadding=1,
                  rightPadding=1, topPadding=1, showBoundary=0)
        text = [data.g1_3]
        placeToFrameWithShrink(text, f, canvas, only_data=1, align='CENTER')


    f = Frame(frame2.x1, frame2.y1, frame2.width, frame2.height - 0.3 * cm, leftPadding=1, bottomPadding=1,
              rightPadding=1, topPadding=1, showBoundary=0)
    text = []
    for _t in data.g2:
        if _t is not None:
            text.append(_t)
    placeToFrameWithShrink(text, f, canvas, only_data=1)


    f = Frame(frame3_1.x1, frame3_1.y1, frame3_1.width, 0.4 * cm, leftPadding=1, bottomPadding=1,
                  rightPadding=1, topPadding=1, showBoundary=0)
    text = ['1']
    placeToFrameWithShrink(text, f, canvas, only_data=1, align='CENTER')

    f = Frame(frame3_2.x1, frame3_2.y1, frame3_2.width, 0.4 * cm, leftPadding=1, bottomPadding=1,
                  rightPadding=1, topPadding=1, showBoundary=0)
    if (len(data.items) - 1) % 3 > 0:
        _t = (len(data.items) - 1) // 3 + 1
    else:
        _t = (len(data.items) - 1) // 3
    text = [str(_t + 1)]
    placeToFrameWithShrink(text, f, canvas, only_data=1, align='CENTER')

    if data.g4 is not None:
        f = Frame(frame4.x1, frame4.y1, frame4.width, 0.4 * cm, leftPadding=1, bottomPadding=1,
                  rightPadding=1, topPadding=1, showBoundary=0)
        text = [data.g4]
        placeToFrameWithShrink(text, f, canvas, only_data=1, align='CENTER')

    if data.g5 is not None:
        f = Frame(frame5.x1, frame5.y1, frame5.width, 0.4 * cm, leftPadding=1, bottomPadding=1,
                  rightPadding=1, topPadding=1, showBoundary=0)
        text = [data.g5]
        placeToFrameWithShrink(text, f, canvas, only_data=1, align='CENTER')

    if data.g6 is not None:
        f = Frame(frame6.x1, frame6.y1, frame6.width, 0.4 * cm, leftPadding=1, bottomPadding=1,
                  rightPadding=1, topPadding=1, showBoundary=0)
        text = [data.g6]
        placeToFrameWithShrink(text, f, canvas, only_data=1, align='CENTER')

    f = Frame(frame8.x1, frame8.y1, frame8.width, frame8.height - 0.3 * cm, leftPadding=1, bottomPadding=1,
              rightPadding=1, topPadding=1, showBoundary=0)
    text = []
    for _t in data.g8:
        if _t is not None:
            text.append(_t)
    placeToFrameWithShrink(text, f, canvas, only_data=1)

    if data.g15 is not None:
        f = Frame(frame15.x1, frame15.y1, frame15.width, frame15.height - 0.4 * cm, leftPadding=1, bottomPadding=1,
                  rightPadding=1, topPadding=1, showBoundary=0)
        text = [data.g15]
        placeToFrameWithShrink(text, f, canvas, only_data=1, align='CENTER')

    if data.g17 is not None:
        f = Frame(frame17.x1, frame17.y1, frame17.width, frame17.height - 0.4 * cm, leftPadding=1, bottomPadding=1,
                  rightPadding=1, topPadding=1, showBoundary=0)
        text = [data.g17]
        placeToFrameWithShrink(text, f, canvas, only_data=1, align='CENTER')

    if data.g18_1 is not None:
        f = Frame(frame18.x1, frame18.y1, frame18.width - 0.6 * cm, frame18.height - 0.8 * cm, leftPadding=1,
                  bottomPadding=1, rightPadding=1, topPadding=1, showBoundary=0)
        text = [data.g18_1]
        placeToFrameWithShrink(text, f, canvas, only_data=1, align='CENTER')

    if data.g18_2 is not None:
        f = Frame(frame18.x1 + frame18.width - 0.6 * cm, frame18.y1, 0.6 * cm, frame18.height - 0.8 * cm, leftPadding=1,
                  bottomPadding=1, rightPadding=1, topPadding=1, showBoundary=0)
        text = [data.g18_2]
        placeToFrameWithShrink(text, f, canvas, only_data=1, align='CENTER')

    if data.g19 is not None:
        f = Frame(frame19.x1, frame19.y1, frame19.width, frame19.height - 0.8 * cm, leftPadding=1, bottomPadding=1,
                  rightPadding=1, topPadding=1, showBoundary=0)
        text = [data.g19]
        placeToFrameWithShrink(text, f, canvas, only_data=1, align='CENTER')

    if data.g21_1 is not None:
        f = Frame(frame21.x1, frame21.y1, frame21.width - 0.6 * cm, frame21.height - 0.8 * cm, leftPadding=1,
                  bottomPadding=1, rightPadding=1, topPadding=1, showBoundary=0)
        text = [data.g21_1]
        placeToFrameWithShrink(text, f, canvas, only_data=1, align='CENTER')

    if data.g21_2 is not None:
        f = Frame(frame21.x1 + frame21.width - 0.6 * cm, frame21.y1, 0.6 * cm, frame21.height - 0.8 * cm, leftPadding=1,
                  bottomPadding=1, rightPadding=1, topPadding=1, showBoundary=0)
        text = [data.g21_2]
        placeToFrameWithShrink(text, f, canvas, only_data=1, align='CENTER')

    if data.g22_1 is not None:
        f = Frame(frame22.x1, frame22.y1, 1 * cm, frame22.height - 0.8 * cm, leftPadding=1, bottomPadding=1,
                  rightPadding=1, topPadding=1, showBoundary=0)
        text = [data.g22_1]
        placeToFrameWithShrink(text, f, canvas, only_data=1, align='CENTER')

    if data.g22_2 is not None:
        f = Frame(frame22.x1 + 1 * cm, frame22.y1, frame22.width - 1 * cm, frame22.height - 0.8 * cm, leftPadding=1,
                  bottomPadding=1, rightPadding=1, topPadding=1, showBoundary=0)
        text = [data.g22_2]
        placeToFrameWithShrink(text, f, canvas, only_data=1, align='CENTER')

    if data.g25 is not None:
        f = Frame(frame25.x1, frame25.y1, 1 * cm, frame25.height - 0.4 * cm, leftPadding=1,
                  bottomPadding=1, rightPadding=1, topPadding=1, showBoundary=0)
        text = [data.g25]
        placeToFrameWithShrink(text, f, canvas, only_data=1, align='CENTER')

    _d = data.items[0]
    if _d.g31_3 is not None:
        f = Frame(frame31.x1, frame31.y1, frame31.width, 0.5 * cm, leftPadding=1, bottomPadding=3,
                  rightPadding=1, topPadding=1, showBoundary=0)
        text = [_d.g31_3]
        placeToFrameWithShrink(text, f, canvas, only_data=1)

    if _d.g31_2 is not None:
        f = Frame(frame31.x1, frame31.y1 + 0.4 * cm, frame31.width, 0.4 * cm, leftPadding=1, bottomPadding=1,
                  rightPadding=1, topPadding=1, showBoundary=0)
        text = [_d.g31_2]
        placeToFrameWithShrink(text, f, canvas, only_data=1)

    if _d.g31_1 is not None:
        f = Frame(frame31.x1, frame31.y1 + 0.8 * cm, frame31.width, frame31.height - 1.6 * cm, leftPadding=1,
                  bottomPadding=1, rightPadding=1, topPadding=1, showBoundary=0)
        text = [_d.g31_1]
        r = placeToFrameWithReturn(text, f, canvas, only_data=1)  # если не влазит - перенос на след. страницу

        ####################
        # тут добавить сохранение данных для переноса на след. страницу
        ad.g31.extend(r)  # номер товара и невлезшее описание
        ######################


    f = Frame(frame32.x1, frame32.y1, 1 * cm, frame32.height - 0.4 * cm, leftPadding=1, bottomPadding=1,
                  rightPadding=1, topPadding=1, showBoundary=0)
    text = ['1']
    placeToFrameWithShrink(text, f, canvas, only_data=1, align='CENTER')

    if _d.g33_1 is not None:
        f = Frame(frame33.x1, frame33.y1, 2.8 * cm, frame33.height - 0.4 * cm, leftPadding=1, bottomPadding=1,
                  rightPadding=1, topPadding=1, showBoundary=0)
        text = [_d.g33_1]
        placeToFrameWithShrink(text, f, canvas, only_data=1, align='CENTER')

    if _d.g33_2 is not None:
        f = Frame(frame33.x1 + 2.8 * cm, frame33.y1, 0.6 * cm, frame33.height - 0.4 * cm, leftPadding=1,
                  bottomPadding=1,
                  rightPadding=1, topPadding=1, showBoundary=0)
        text = [_d.g33_2]
        placeToFrameWithShrink(text, f, canvas, only_data=1, align='CENTER')

    if _d.g33_3 is not None:
        f = Frame(frame33.x1 + 3.4 * cm, frame33.y1, 0.6 * cm, frame33.height - 0.4 * cm, leftPadding=1,
                  bottomPadding=1,
                  rightPadding=1, topPadding=1, showBoundary=0)
        text = [_d.g33_3]
        placeToFrameWithShrink(text, f, canvas, only_data=1, align='CENTER')

    if _d.g35 is not None:
        f = Frame(frame35.x1, frame35.y1, frame35.width, frame35.height - 0.4 * cm, leftPadding=1, bottomPadding=3,
                  rightPadding=1, topPadding=1, showBoundary=0)
        text = [_d.g35]
        placeToFrameWithShrink(text, f, canvas, only_data=1, align='CENTER')

    f = Frame(frame40.x1, frame40.y1 - 0.1 * cm, frame40.width, frame40.height - 0.3 * cm, leftPadding=1, bottomPadding=3,
              rightPadding=1, topPadding=1, showBoundary=0)
    text = []
    for _t in _d.g40:
        if _t is not None:
            text.append(_t)
    r = placeToFrameWithReturn(text, f, canvas, only_data=1)  # если не влазит - перенос на след. страницу

    ####################
    # тут добавить сохранение данных для переноса на след. страницу
    ad.g40.extend(r)  # номер товара и невлезшие предш. доки
    ######################

    if _d.g41_1 is not None:
        f = Frame(frame41.x1, frame41.y1, frame41.width, frame41.height - 0.4 * cm, leftPadding=1,
                  bottomPadding=1, rightPadding=1, topPadding=1, showBoundary=0)
        text = [_d.g41_1]
        placeToFrameWithShrink(text, f, canvas, only_data=1, align='CENTER')

    if _d.g41_2 is not None:
        f = Frame(frameDI.x1, frameDI.y1, frameDI.width, frameDI.height - 0.4 * cm, leftPadding=0,
                  bottomPadding=1,rightPadding=0, topPadding=1, showBoundary=0)
        text = [_d.g41_2]
        placeToFrameWithShrink(text, f, canvas, only_data=1, align='CENTER')

    if _d.g42_1 is not None:
        f = Frame(frame42.x1, frame42.y1, 1 * cm, frame42.height - 0.4 * cm, leftPadding=1, bottomPadding=1,
                  rightPadding=1, topPadding=1, showBoundary=0)
        text = [_d.g42_1]
        placeToFrameWithShrink(text, f, canvas, only_data=1, align='CENTER')

    if _d.g42_2 is not None:
        f = Frame(frame42.x1 + 1 * cm, frame42.y1, frame42.width - 1 * cm, frame42.height - 0.4 * cm, leftPadding=1,
                  bottomPadding=1,
                  rightPadding=1, topPadding=1, showBoundary=0)
        text = [_d.g42_2]
        placeToFrameWithShrink(text, f, canvas, only_data=1, align='CENTER')

    if _d.g44 is not None:
        f = Frame(frame44.x1, frame44.y1 - 0.1, frame44.width, frame44.height, leftPadding=1, bottomPadding=1,
                  rightPadding=1, topPadding=1, showBoundary=0)
        text = []
        for _t in _d.g44:
            if _t is not None:
                text.append(_t)
        if len(text) > 7:
            r = placeToFrameWithReturn(text[:7], f, canvas, only_data=1)
            r.extend(text[7:])
        else:
            r = placeToFrameWithReturn(text, f, canvas, only_data=1)  # если не влазит - перенос на след. страницу

        ####################
        # тут добавить сохранение данных для переноса на след. страницу
        ad.g44.extend(r)  # номер товара и невлезшие доки
        ####################

    if data.g51 is not None:
        f = Frame(frame50.x1, frame50.y1, frame50.width, 0.5 * cm, leftPadding=1, bottomPadding=3,
                  rightPadding=1, topPadding=1, showBoundary=0)
        text = [data.g51]
        placeToFrameWithShrink(text, f, canvas, only_data=1)

    if data.g50_v2 is not None:
        f = Frame(frame50.x1, frame50.y1 + 0.4 * cm, frame50.width, 0.4 * cm, leftPadding=1, bottomPadding=1,
                  rightPadding=1, topPadding=1, showBoundary=0)
        text = [data.g50_v2]
        placeToFrameWithShrink(text, f, canvas, only_data=1)

    if data.g50_v1 is not None:
        f = Frame(frame50.x1, frame50.y1 + 0.7 * cm, frame50.width, 0.4 * cm, leftPadding=1, bottomPadding=1,
                  rightPadding=1, topPadding=1, showBoundary=0)
        text = [data.g50_v1]
        placeToFrameWithShrink(text, f, canvas, only_data=1)

    if data.g50 is not None:
        f = Frame(frame50.x1, frame50.y1 + 1 * cm, frame50.width, frame50.height - 1.4 * cm, leftPadding=1, bottomPadding=1,
                  rightPadding=1, topPadding=1, showBoundary=0)
        text = []
        for _t in data.g50:
            if _t is not None:
                text.append(_t)
        r = placeToFrameWithReturn(text, f, canvas, only_data=1)  # если не влазит - перенос на след. страницу

        ####################
        # тут добавить сохранение данных для переноса на след. страницу
        ad.g50.extend(r)  # невлезшие перевозчики
        ####################

    if len(data.g52_1) > 2:  # если больше двух записей в графе 52, все переношу на обратную сторону
        f = Frame(frame52_1.x1 + 1 * cm, frame52_1.y1, frame52_1.width, frame52_1.height - 0.3 * cm, leftPadding=1, bottomPadding=3,
                  rightPadding=1, topPadding=1, showBoundary=0)
        text = [oborot]
        placeToFrameWithShrink(text, f, canvas, only_data=1, align='LEFT')

        ####################
        # тут добавить сохранение данных для переноса на след. страницу
        ad.g52_1.extend(data.g52_1)  # невлезшие сертификаты/гаранты
        ad.g52_2.extend(data.g52_2)
        ####################

    else:
        if data.g52_1 is not None:
            f = Frame(frame52_1.x1, frame52_1.y1, frame52_1.width, frame52_1.height - 0.3 * cm, leftPadding=1, bottomPadding=1,
                      rightPadding=1, topPadding=1, showBoundary=0)
            text = []
            for _t in data.g52_1:
                if _t is not None:
                    text.append(_t)
            r = placeToFrameWithReturn(text, f, canvas, only_data=1)  # если не влазит - перенос на след. страницу

        if data.g52_2 is not None:
            f = Frame(frame52_2.x1, frame52_2.y1, frame52_2.width, frame52_2.height - 0.3 * cm, leftPadding=1,
                      bottomPadding=1, rightPadding=1, topPadding=1, showBoundary=0)
            text = []
            for _t in data.g52_2:
                if _t is not None:
                    text.append(_t)
            r = placeToFrameWithReturn(text, f, canvas, only_data=1)  # если не влазит - перенос на след. страницу

    if data.g53 is not None:
        f = Frame(frame53.x1, frame53.y1, frame53.width, frame53.height - 0.4 * cm, leftPadding=1, bottomPadding=1,
                  rightPadding=1, topPadding=1, showBoundary=0)
        text = [data.g53]
        placeToFrameWithShrink(text, f, canvas, only_data=1, align='LEFT')

    if data.g55_1_place is not None:
        f = Frame(frame55_place_1.x1, frame55_place_1.y1, frame55_place_1.width, frame55_place_1.height - 0.4 * cm,
                  leftPadding=1, bottomPadding=1, rightPadding=1, topPadding=1, showBoundary=0)
        text = [data.g55_1_place]
        placeToFrameWithShrink(text, f, canvas, only_data=1, align='CENTER')

    if data.g55_2_place is not None:
        f = Frame(frame55_place_2.x1, frame55_place_2.y1, frame55_place_2.width, frame55_place_2.height - 0.4 * cm,
                  leftPadding=1, bottomPadding=1, rightPadding=1, topPadding=1, showBoundary=0)
        text = [data.g55_2_place]
        placeToFrameWithShrink(text, f, canvas, only_data=1, align='CENTER')

    if data.g55_1_ts_1 is not None:
        f = Frame(frame55_ts_1.x1, frame55_ts_1.y1, frame55_ts_1.width - 0.6 * cm, frame55_ts_1.height - 0.4 * cm,
                  leftPadding=1, bottomPadding=1, rightPadding=1, topPadding=1, showBoundary=0)
        text = [data.g55_1_ts_1]
        placeToFrameWithShrink(text, f, canvas, only_data=1, align='CENTER')

    if data.g55_1_ts_2 is not None:
        f = Frame(frame55_ts_1.x1 + frame55_ts_1.width - 0.6 * cm, frame55_ts_1.y1, 0.6 * cm,
                  frame55_ts_1.height - 0.4 * cm, leftPadding=1, bottomPadding=1,
                  rightPadding=1, topPadding=1, showBoundary=0)
        text = [data.g55_1_ts_2]
        placeToFrameWithShrink(text, f, canvas, only_data=1, align='CENTER')

    if data.g55_2_ts_1 is not None:
        f = Frame(frame55_ts_2.x1, frame55_ts_2.y1, frame55_ts_2.width - 0.6 * cm, frame55_ts_2.height - 0.4 * cm,
                  leftPadding=1, bottomPadding=1, rightPadding=1, topPadding=1, showBoundary=0)
        text = [data.g55_2_ts_1]
        placeToFrameWithShrink(text, f, canvas, only_data=1, align='CENTER')

    if data.g55_2_ts_2 is not None:
        f = Frame(frame55_ts_2.x1 + frame55_ts_2.width - 0.6 * cm, frame55_ts_2.y1, 0.6 * cm,
                  frame55_ts_2.height - 0.4 * cm, leftPadding=1, bottomPadding=1,
                  rightPadding=1, topPadding=1, showBoundary=0)
        text = [data.g55_2_ts_2]
        placeToFrameWithShrink(text, f, canvas, only_data=1, align='CENTER')

    if data.g55_1_cont_1 is not None:
        f = Frame(frame55_cont_1.x1 - 0.6 * cm, frame55_cont_1.y1, 0.6 * cm, frame55_cont_1.height - 0.4 * cm,
                  leftPadding=1, bottomPadding=1, rightPadding=1, topPadding=1, showBoundary=0)
        text = [data.g55_1_cont_1]
        placeToFrameWithShrink(text, f, canvas, only_data=1, align='CENTER')

    if data.g55_1_cont_2 is not None:
        f = Frame(frame55_cont_1.x1 + 0.5 * cm, frame55_cont_1.y1, frame55_cont_1.width - 0.5 * cm,
                  frame55_cont_1.height - 0.4 * cm,
                  leftPadding=1, bottomPadding=1, rightPadding=1, topPadding=1, showBoundary=0)
        text = [data.g55_1_cont_2]
        placeToFrameWithShrink(text, f, canvas, only_data=1, align='CENTER')

    if data.g55_2_cont_1 is not None:
        f = Frame(frame55_cont_2.x1 - 0.6 * cm, frame55_cont_2.y1, 0.6 * cm, frame55_cont_2.height - 0.4 * cm,
                  leftPadding=1, bottomPadding=1, rightPadding=1, topPadding=1, showBoundary=0)
        text = [data.g55_2_cont_1]
        placeToFrameWithShrink(text, f, canvas, only_data=1, align='CENTER')

    if data.g55_2_cont_2 is not None:
        f = Frame(frame55_cont_2.x1 + 0.5 * cm, frame55_cont_2.y1, frame55_cont_2.width - 0.5 * cm,
                  frame55_cont_2.height - 0.4 * cm,
                  leftPadding=1, bottomPadding=1, rightPadding=1, topPadding=1, showBoundary=0)
        text = [data.g55_2_cont_2]
        placeToFrameWithShrink(text, f, canvas, only_data=1, align='CENTER')

    if data.gA is not None:
        f = Frame(frameA.x1, frameA.y1, frameA.width, frameA.height - 0.4 * cm,
                  leftPadding=1, bottomPadding=1, rightPadding=1, topPadding=1, showBoundary=0)
        text = [data.gA]
        placeToFrameWithShrink(text, f, canvas, only_data=1, align='LEFT')

    if data.gC is not None:
        f = Frame(frameC.x1, frameC.y1, frameC.width, frameC.height - 0.4 * cm,
                  leftPadding=1, bottomPadding=1, rightPadding=1, topPadding=1, showBoundary=0)
        text = [data.gC]
        placeToFrameWithShrink(text, f, canvas, only_data=1, align='LEFT')

    if data.gD is not None:
        f = Frame(frameD.x1, frameD.y1 + 0.4 * cm, frameD.width, 0.8 * cm,
                  leftPadding=1, bottomPadding=1, rightPadding=1, topPadding=1, showBoundary=0)
        text = [data.gD]
        placeToFrameWithShrink(text, f, canvas, only_data=1, align='LEFT')

    canvas.save()
    merger.append(temp_base)  # добавляем основную страницу в сборщик PDF

    # Формируем обратную сторону основного листа
    if (len(ad.g31) + len(ad.g40) + len(ad.g31) + len(ad.g44) + len(ad.g50) + len(ad.g52_1) +
        len(ad.g52_2)) > 0:
        temp_base = tempfile.TemporaryFile()
        doc = SimpleDocTemplate(temp_base, pagesize=A4, rightMargin=1.4 * cm, leftMargin=1.4 * cm, topMargin=0.6 * cm,
                                bottomMargin=1.4 * cm)
        elements = []

        if len(ad.g31) > 0:  # если есть дополнительное описание товара
            el = []
            elements.append(Paragraph('31. Наименование товара (дополнительно)', style=style_data))
            elements.append(Spacer(width=pagex, height=0.1 * cm))
            el.append(['№', 'Наименование товара'])
            for _e in ad.g31:
                el.append([Paragraph('1', style=style_data), Paragraph(_e, style=style_data)])

            t_g31 = Table(el, colWidths=(1 * cm, x1 - x0 - 1 * cm), rowHeights=None, repeatRows=1)
            t_g31.setStyle(TableStyle([
                ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('LINEBELOW', (0, 0), (-1, 0), 0.25, colors.black),
                ('LINEBELOW', (0, 'splitlast'), (-1, 'splitlast'), 0.25, colors.black),
                ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
                ('BOX', (0, 0), (0, -1), 0.25, colors.black),
                ('FONT', (0, 0), (-1, -1), 'Arial', fontsize_data),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
            ]))
            elements.append(t_g31)
            elements.append(Spacer(width=pagex, height=0.2 * cm))

        if len(ad.g40) > 0:  # если не вместились предшествующие доки
            el = []
            elements.append(Paragraph('40. Предшествующие документы', style=style_data))
            elements.append(Spacer(width=pagex, height=0.1 * cm))
            el.append(['№', '№ Предшествующего документа'])
            for _e in ad.g40:
                el.append([Paragraph('1', style=style_data), Paragraph(_e, style=style_data)])

            t_g40 = Table(el, colWidths=(1 * cm, x1 - x0 - 1 * cm), rowHeights=None, repeatRows=1)
            t_g40.setStyle(TableStyle([
                ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                # ('GRID', (0, 0), (0, -1), 0.25, colors.black),
                ('LINEBELOW', (0, 0), (-1, 0), 0.25, colors.black),
                ('LINEBELOW', (0, 'splitlast'), (-1, 'splitlast'), 0.25, colors.black),
                ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
                ('BOX', (0, 0), (0, -1), 0.25, colors.black),
                ('FONT', (0, 0), (-1, -1), 'Arial', fontsize_data),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
            ]))
            elements.append(t_g40)
            elements.append(Spacer(width=pagex, height=0.2 * cm))

        if len(ad.g44) > 0:  # если не вместились доки
            el = []
            elements.append(Paragraph('44. Дополнительная информация / Представляемый документ', style=style_data))
            elements.append(Spacer(width=pagex, height=0.1 * cm))
            el.append(['№', '№ Документа', 'Дата'])
            for _e in ad.g44:
                _tl = _e.split(' ')
                dok = ' '.join(_tl[:-1])
                data_dok = _tl[-1]
                el.append([
                    Paragraph('1', style=style_data),
                    Paragraph(dok, style=style_data),
                    Paragraph(data_dok, style=style_data),
                ])

            t_g44 = Table(el, colWidths=(1 * cm, x1 - x0 - 4 * cm, 3 * cm), rowHeights=None, repeatRows=1)
            t_g44.setStyle(TableStyle([
                ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('LINEBELOW', (0, 0), (-1, 0), 0.25, colors.black),
                ('LINEBELOW', (0, 'splitlast'), (-1, 'splitlast'), 0.25, colors.black),
                ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
                ('BOX', (0, 0), (0, -1), 0.25, colors.black),
                ('BOX', (-1, 0), (-1, -1), 0.25, colors.black),
                ('FONT', (0, 0), (-1, -1), 'Arial', fontsize_data),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
            ]))
            elements.append(t_g44)
            elements.append(Spacer(width=pagex, height=0.2 * cm))

        if len(ad.g50) > 0:  # если не вместился перевозчик (перевозчики)
            el = []
            elements.append(Paragraph('50. Принципал', style=style_data))
            elements.append(Spacer(width=pagex, height=0.1 * cm))
            el.append(['Принципал'])
            for _e in ad.g50:
                el.append([Paragraph(_e, style=style_data)])

            t_g50 = Table(el, colWidths=(x1 - x0), rowHeights=None, repeatRows=1)
            t_g50.setStyle(TableStyle([
                ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('LINEBELOW', (0, 0), (-1, 0), 0.25, colors.black),
                ('LINEBELOW', (0, 'splitlast'), (-1, 'splitlast'), 0.25, colors.black),
                ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
                ('FONT', (0, 0), (-1, -1), 'Arial', fontsize_data),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
            ]))
            elements.append(t_g50)
            elements.append(Spacer(width=pagex, height=0.2 * cm))

        if len(ad.g52_1) + len(ad.g52_2) > 0:  # если не вместились гарантии
            elements.append(Paragraph('52. Гарантии (продолжение)', style=style_data))
            elements.append(Spacer(width=pagex, height=0.1 * cm))
            count_row = max(len(ad.g52_1), len(ad.g52_2))
            el = [['Код', 'Сумма', 'Номер документа', 'Дата док.', 'УНП/МФО', 'Лицо, осущ.там.сопровожд.']]
            for i in range(count_row):
                el.append(6 * [''])
            for i in range(0, len(ad.g52_1)):
                if ad.g52_1[i] is not None:
                    _tl = ad.g52_1[i].split(' ')
                    if _tl[0] == '_':
                        _tl[0] = ' '
                    el[i+1][1] = Paragraph(_tl[0], style=style_data)
                    if len(_tl) > 1:
                        if _tl[1] == '_':
                            _tl[1] = ' '
                        el[i + 1][2] = Paragraph(_tl[1], style=style_data)
                    if len(_tl) > 2:
                        if _tl[2] == '_':
                            _tl[2] = ' '
                        el[i + 1][3] = Paragraph(_tl[2], style=style_data)
                    if len(_tl) > 3:
                        if _tl[3] == '_':
                            _tl[3] = ' '
                        el[i + 1][4] = Paragraph(_tl[3], style=style_data)
                    if len(_tl) > 4:
                        if _tl[4] == '_':
                            _tl[4] = ' '
                        el[i + 1][5] = Paragraph(_tl[4], style=style_data)
            for i in range(0, len(ad.g52_2)):
                if ad.g52_2[i] is not None:
                    el[i+1][0] = Paragraph(ad.g52_2[i], style=style_data)

            t_g52 = Table(el, colWidths=(1 * cm, 2 * cm, x1 - x0 - 11 * cm, 2 * cm, 2 * cm, 4 * cm), rowHeights=None, repeatRows=1)
            t_g52.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('LINEBELOW', (0, 0), (-1, 0), 0.25, colors.black),
                ('LINEBELOW', (0, 'splitlast'), (-1, 'splitlast'), 0.25, colors.black),
                ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
                ('BOX', (0, 0), (0, -1), 0.25, colors.black),
                ('BOX', (1, 0), (1, -1), 0.25, colors.black),
                ('BOX', (2, 0), (2, -1), 0.25, colors.black),
                ('BOX', (3, 0), (3, -1), 0.25, colors.black),
                ('BOX', (-1, 0), (-1, -1), 0.25, colors.black),
                ('FONT', (0, 0), (-1, -1), 'Arial', fontsize_data),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
            ]))
            elements.append(t_g52)
            elements.append(Spacer(width=pagex, height=0.2 * cm))

        def printTop(canvas, doc):
            pass

        doc.build(elements, onFirstPage=printTop, onLaterPages=printTop)
        merger.append(temp_base)  # добавляем дополнительную страницу в сборщик PDF

        # если количество дополнительных страниц четное - то добавляем еще пустую
        reader = PdfReader(temp_base)
        number_of_pages = len(reader.pages)
        if number_of_pages % 2 == 0:
            temp_base = tempfile.TemporaryFile()
            doc = SimpleDocTemplate(temp_base, pagesize=A4)
            elements = [Paragraph('')]
            doc.build(elements)
            merger.append(temp_base)  # добавляем пустую страницу в сборщик PDF
    else:
        # просто добавляем пустую страницу
        temp_base = tempfile.TemporaryFile()
        doc = SimpleDocTemplate(temp_base, pagesize=A4)
        elements = [Paragraph('')]
        doc.build(elements)
        merger.append(temp_base)  # добавляем пустую страницу в сборщик PDF

    merger.write(temp_final)
    return temp_final
    #temp_final.close()
    #shutil.copy(path_final, filename)
    #os.remove(path_final)


def second_page_TD(data):
   # temp_final = tempfile.TemporaryFile(delete=False)
    temp_final = tempfile.TemporaryFile()
    path_final = temp_final.name
    merger = PyPDF2.PdfMerger()

    def place_item(yn, item, item_number):
        '''
        Рисует блоки товаров графы 31 - 44
        :param yn: параметр задает координату по Y, с которой будут рисоваться блоки товара
        '''
        # графа 31 (только заголовок)
        frame31_ = Frame(x0, y1 - 13.4 * cm + yn, 1.2 * cm, 3.6 * cm, leftPadding=1, bottomPadding=1,
                         rightPadding=1, topPadding=1, showBoundary=1)
        text = ["31 Грузовые места и описание товаров"]
        placeToFrameWithTruncate(text, frame31_, canvas)

        # графа 44 (только заголовок)
        frame44_ = Frame(x0, y1 - 15.4 * cm + yn, 1.2 * cm, 2 * cm, leftPadding=1, bottomPadding=1,
                         rightPadding=1, topPadding=1, showBoundary=1)
        text = ["44 Доп. инф./ Пред. док./ Серт. и разр."]
        placeToFrameWithTruncate(text, frame44_, canvas)

        # графа 31 (текст в графе)
        frame31 = Frame(x0 + 1.2 * cm, y1 - 13.4 * cm + yn, 9.6 * cm, 3.6 * cm, leftPadding=1, bottomPadding=1,
                        rightPadding=1, topPadding=1, showBoundary=1)
        placeToFrameWithTruncate([""], frame31, canvas)
        frame31__ = Frame(x0 + 1.2 * cm, y1 - 10.6 * cm + yn, 7.5 * cm, 0.8 * cm, leftPadding=1, bottomPadding=1,
                          rightPadding=1, topPadding=1, showBoundary=0)
        text = ["Маркировка и количество - Номера контейнеров - Количество и отличительные особенности товаров"]
        placeToFrameWithTruncate(text, frame31__, canvas)

        # графа 32
        frame32 = Frame(x0 + 8.8 * cm, y1 - 10.6 * cm + yn, 2 * cm, 0.8 * cm, leftPadding=1, bottomPadding=1,
                        rightPadding=1, topPadding=1, showBoundary=1)
        text = ["32 Товар"]
        placeToFrameWithTruncate(text, frame32, canvas)
        canvas.line(x0 + 9.8 * cm, y1 - 10.6 * cm + yn, x0 + 9.8 * cm, y1 - 10.2 * cm + yn)  # в графе 32

        # графа 33
        frame33 = Frame(x0 + 10.8 * cm, y1 - 10.6 * cm + yn, 4 * cm, 0.8 * cm, leftPadding=1, bottomPadding=1,
                        rightPadding=1, topPadding=1, showBoundary=1)
        text = ["33 Код товара"]
        placeToFrameWithTruncate(text, frame33, canvas)
        canvas.rect(x0 + 14.8 * cm, y1 - 10.6 * cm + yn, 1.5 * cm, 0.8 * cm, stroke=1, fill=0)  # правее графы 33
        canvas.rect(x0 + 16.3 * cm, y1 - 10.6 * cm + yn, x1 - x0 - 16.3 * cm, 0.8 * cm, stroke=1, fill=0)  # правее графы 33
        canvas.line(x0 + 13.6 * cm, y1 - 10.6 * cm + yn, x0 + 13.6 * cm, y1 - 10.2 * cm + yn)  # в графе 33
        canvas.line(x0 + 14.2 * cm, y1 - 10.6 * cm + yn, x0 + 14.2 * cm, y1 - 10.2 * cm + yn)  # в графе 33

        # графа 35
        canvas.rect(x0 + 10.8 * cm, y1 - 11.4 * cm + yn, 1 * cm, 0.8 * cm, stroke=1, fill=0)  # под графой 33
        canvas.rect(x0 + 10.8 * cm, y1 - 11.8 * cm + yn, 1 * cm, 0.4 * cm, stroke=1, fill=0)  # под графой 33
        frame35 = Frame(x0 + 11.8 * cm, y1 - 11.4 * cm + yn, 4.5 * cm, 0.8 * cm, leftPadding=1, bottomPadding=1,
                        rightPadding=1, topPadding=1, showBoundary=1)
        text = ["35 Вес брутто (кг)"]
        placeToFrameWithTruncate(text, frame35, canvas)
        canvas.rect(x0 + 11.8 * cm, y1 - 11.8 * cm + yn, 4.5 * cm, 0.4 * cm, stroke=1, fill=0)  # под графой 35

        # графа 40
        frame40 = Frame(x0 + 10.8 * cm, y1 - 12.6 * cm + yn, x1 - x0 - 10.8 * cm, 0.8 * cm, leftPadding=1, bottomPadding=1,
                        rightPadding=1, topPadding=1, showBoundary=1)
        text = ["40 Общая декл./Предшествующий документ"]
        placeToFrameWithTruncate(text, frame40, canvas)

        # графа 41
        frame41 = ColorFrame(x0 + 10.8 * cm, y1 - 13.4 * cm + yn, 4 * cm, 0.8 * cm, leftPadding=1, bottomPadding=1,
                             rightPadding=1, topPadding=1, showBoundary=1, background=white)
        text = ["41 Дополн. ед. изм."]
        placeToFrameWithTruncate(text, frame41, canvas)

        # графа 42
        frame42 = Frame(x0 + 14.8 * cm, y1 - 13.4 * cm + yn, x1 - x0 - 14.8 * cm, 0.8 * cm, leftPadding=1, bottomPadding=1,
                        rightPadding=1, topPadding=1, showBoundary=1)
        text = ["42 Валюта и стоим. тов."]
        placeToFrameWithTruncate(text, frame42, canvas)
        canvas.line(x0 + 15.8 * cm, y1 - 13.4 * cm + yn, x0 + 15.8 * cm, y1 - 13 * cm + yn)  # в графе 33

        # код ДИ
        frameDI = Frame(x0 + 13.8 * cm, y1 - 14.2 * cm + yn, 2 * cm, 0.8 * cm, leftPadding=1, bottomPadding=1,
                        rightPadding=1, topPadding=1, showBoundary=1)
        text = ["Код ДИ"]
        placeToFrameWithTruncate(text, frameDI, canvas)

        # графа 44
        frame44 = Frame(x0 + 1.2 * cm, y1 - 15.4 * cm + yn, 12.6 * cm, 2 * cm, leftPadding=1, bottomPadding=1,
                        rightPadding=1, topPadding=1, showBoundary=1)
        text = [""]
        placeToFrameWithTruncate(text, frame44, canvas)

        ad = AdditionalData()

        _d = item
        if _d is not None:
            if _d.g31_3 is not None:
                f = Frame(frame31.x1, frame31.y1, frame31.width, 0.5 * cm, leftPadding=1, bottomPadding=3,
                          rightPadding=1, topPadding=1, showBoundary=0)
                text = [_d.g31_3]
                placeToFrameWithShrink(text, f, canvas, only_data=1)

            if _d.g31_2 is not None:
                f = Frame(frame31.x1, frame31.y1 + 0.4 * cm, frame31.width, 0.4 * cm, leftPadding=1, bottomPadding=1,
                          rightPadding=1, topPadding=1, showBoundary=0)
                text = [_d.g31_2]
                placeToFrameWithShrink(text, f, canvas, only_data=1)

            if _d.g31_1 is not None:
                f = Frame(frame31.x1, frame31.y1 + 0.8 * cm, frame31.width, frame31.height - 1.6 * cm, leftPadding=1,
                          bottomPadding=1, rightPadding=1, topPadding=1, showBoundary=0)
                text = [_d.g31_1]
                r = placeToFrameWithReturn(text, f, canvas, only_data=1)  # если не влазит - перенос на след. страницу

                ####################
                # тут добавить сохранение данных для переноса на след. страницу
                ad.g31.extend(r)  # номер товара и невлезшее описание
                ######################


            f = Frame(frame32.x1, frame32.y1, 1 * cm, frame32.height - 0.4 * cm, leftPadding=1, bottomPadding=1,
                          rightPadding=1, topPadding=1, showBoundary=0)
            text = [str(item_number)]
            placeToFrameWithShrink(text, f, canvas, only_data=1, align='CENTER')

            if _d.g33_1 is not None:
                f = Frame(frame33.x1, frame33.y1, 2.8 * cm, frame33.height - 0.4 * cm, leftPadding=1, bottomPadding=1,
                          rightPadding=1, topPadding=1, showBoundary=0)
                text = [_d.g33_1]
                placeToFrameWithShrink(text, f, canvas, only_data=1, align='CENTER')

            if _d.g33_2 is not None:
                f = Frame(frame33.x1 + 2.8 * cm, frame33.y1, 0.6 * cm, frame33.height - 0.4 * cm, leftPadding=1,
                          bottomPadding=1,
                          rightPadding=1, topPadding=1, showBoundary=0)
                text = [_d.g33_2]
                placeToFrameWithShrink(text, f, canvas, only_data=1, align='CENTER')

            if _d.g33_3 is not None:
                f = Frame(frame33.x1 + 3.4 * cm, frame33.y1, 0.6 * cm, frame33.height - 0.4 * cm, leftPadding=1,
                          bottomPadding=1,
                          rightPadding=1, topPadding=1, showBoundary=0)
                text = [_d.g33_3]
                placeToFrameWithShrink(text, f, canvas, only_data=1, align='CENTER')

            if _d.g35 is not None:
                f = Frame(frame35.x1, frame35.y1, frame35.width, frame35.height - 0.4 * cm, leftPadding=1, bottomPadding=3,
                          rightPadding=1, topPadding=1, showBoundary=0)
                text = [_d.g35]
                placeToFrameWithShrink(text, f, canvas, only_data=1, align='CENTER')

            f = Frame(frame40.x1, frame40.y1 - 0.1 * cm, frame40.width, frame40.height - 0.3 * cm, leftPadding=1,
                      bottomPadding=3,
                      rightPadding=1, topPadding=1, showBoundary=0)
            text = []
            for _t in _d.g40:
                if _t is not None:
                    text.append(_t)
            r = placeToFrameWithReturn(text, f, canvas, only_data=1)  # если не влазит - перенос на след. страницу

            ####################
            # тут добавить сохранение данных для переноса на след. страницу
            ad.g40.extend(r)  # номер товара и невлезшие предш. доки
            ######################

            if _d.g41_1 is not None:
                f = Frame(frame41.x1, frame41.y1, frame41.width, frame41.height - 0.4 * cm, leftPadding=1,
                          bottomPadding=1, rightPadding=1, topPadding=1, showBoundary=0)
                text = [_d.g41_1]
                placeToFrameWithShrink(text, f, canvas, only_data=1, align='CENTER')

            if _d.g41_2 is not None:
                f = Frame(frameDI.x1, frameDI.y1, frameDI.width, frameDI.height - 0.4 * cm, leftPadding=0,
                          bottomPadding=1, rightPadding=0, topPadding=1, showBoundary=0)
                text = [_d.g41_2]
                placeToFrameWithShrink(text, f, canvas, only_data=1, align='CENTER')

            if _d.g42_1 is not None:
                f = Frame(frame42.x1, frame42.y1, 1 * cm, frame42.height - 0.4 * cm, leftPadding=1, bottomPadding=1,
                          rightPadding=1, topPadding=1, showBoundary=0)
                text = [_d.g42_1]
                placeToFrameWithShrink(text, f, canvas, only_data=1, align='CENTER')

            if _d.g42_2 is not None:
                f = Frame(frame42.x1 + 1 * cm, frame42.y1, frame42.width - 1 * cm, frame42.height - 0.4 * cm, leftPadding=1,
                          bottomPadding=1,
                          rightPadding=1, topPadding=1, showBoundary=0)
                text = [_d.g42_2]
                placeToFrameWithShrink(text, f, canvas, only_data=1, align='CENTER')

            if _d.g44 is not None:
                f = Frame(frame44.x1, frame44.y1 - 0.1, frame44.width, frame44.height, leftPadding=1, bottomPadding=1,
                          rightPadding=1, topPadding=1, showBoundary=0)
                text = []
                for _t in _d.g44:
                    if _t is not None:
                        text.append(_t)
                if len(text) > 7:
                    r = placeToFrameWithReturn(text[:7], f, canvas, only_data=1)
                    r.extend(text[7:])
                else:
                    r = placeToFrameWithReturn(text, f, canvas, only_data=1)  # если не влазит - перенос на след. страницу

                ####################
                # тут добавить сохранение данных для переноса на след. страницу
                ad.g44.extend(r)  # номер товара и невлезшие доки
                ####################

        return ad

    if (len(data.items) - 1) % 3 > 0:
        count_additional_page = (len(data.items) - 1) // 3 + 1
    else:
        count_additional_page = (len(data.items) - 1) // 3


    for i in range(1, count_additional_page+1):
        temp_base = tempfile.TemporaryFile()
        canvas = Canvas(temp_base, pagesize=A4)

        # внешний прямоугольник
        canvas.rect(x0, y0, x1 - x0, y1 - y0)
        canvas.saveState()
        canvas.setStrokeColor(white)
        canvas.restoreState()

        # графа ТРАНЗИТНАЯ ДЕКЛАРАЦИЯ
        frame = Frame(x0, y1 - 0.8 * cm, 9.8 * cm, 0.8 * cm, leftPadding=1, bottomPadding=1,
                      rightPadding=1, topPadding=1, showBoundary=1)
        text = ["ДОБАВОЧНЫЙ ЛИСТ ТРАНЗИТНОЙ ДЕКЛАРАЦИИ"]
        placeToFrameWithTruncate(text, frame, canvas)

        frame = Frame(x0 + 9.8 * cm, y1 - 0.8 * cm, 3.1 * cm, 0.4 * cm, leftPadding=1, bottomPadding=1,
                      rightPadding=1, topPadding=1, showBoundary=1)
        text = ["1 ДЕКЛАРАЦИЯ"]
        placeToFrameWithTruncate(text, frame, canvas)

        # графа А
        frameA = Frame(x0 + 12.9 * cm, y1 - 2.8 * cm, x1 - x0 - 12.9 * cm, 2.8 * cm, leftPadding=1, bottomPadding=1,
                       rightPadding=1, topPadding=1, showBoundary=1)
        text = ["А ОРГАН ОТПРАВЛЕНИЯ"]
        placeToFrameWithTruncate(text, frameA, canvas)

        # графа 1
        frame1_1 = Frame(x0 + 9.8 * cm, y1 - 1.6 * cm, 1 * cm, 0.8 * cm, leftPadding=1, bottomPadding=1, rightPadding=1,
                         topPadding=1, showBoundary=1)
        text = [""]
        placeToFrameWithTruncate(text, frame1_1, canvas)
        frame1_2 = Frame(x0 + 10.8 * cm, y1 - 1.6 * cm, 1 * cm, 0.8 * cm, leftPadding=1, bottomPadding=1,
                         rightPadding=1,
                         topPadding=1, showBoundary=1)
        text = [""]
        placeToFrameWithTruncate(text, frame1_2, canvas)
        frame1_3 = Frame(x0 + 11.8 * cm, y1 - 1.6 * cm, 1.1 * cm, 0.8 * cm, leftPadding=1, bottomPadding=1,
                         rightPadding=1,
                         topPadding=1, showBoundary=1)
        text = [""]
        placeToFrameWithTruncate(text, frame1_3, canvas)

        # графа 3
        frame = Frame(x0 + 9.8 * cm, y1 - 2 * cm, 3.1 * cm, 0.4 * cm, leftPadding=1, bottomPadding=1,
                      rightPadding=1, topPadding=1, showBoundary=1)
        text = ["3 Формы"]
        placeToFrameWithTruncate(text, frame, canvas)

        frame3_1 = Frame(x0 + 9.8 * cm, y1 - 2.8 * cm, 1 * cm, 0.8 * cm, leftPadding=1,
                         bottomPadding=1, rightPadding=1, topPadding=1, showBoundary=1)
        text = [""]
        placeToFrameWithTruncate(text, frame3_1, canvas)

        frame3_2 = Frame(x0 + 10.8 * cm, y1 - 2.8 * cm, 1 * cm, 0.8 * cm, leftPadding=1,
                         bottomPadding=1, rightPadding=1, topPadding=1, showBoundary=1)
        text = [""]
        placeToFrameWithTruncate(text, frame3_2, canvas)

        frame3_3 = Frame(x0 + 11.8 * cm, y1 - 2.8 * cm, 1.1 * cm, 0.8 * cm, leftPadding=1,
                         bottomPadding=1, rightPadding=1, topPadding=1, showBoundary=1)
        text = [""]
        placeToFrameWithTruncate(text, frame3_3, canvas)

        # графа 2 и 8
        canvas.rect(x0, y1 - 2.8 * cm, 1.2 * cm, 2 * cm, stroke=1, fill=0)
        canvas.rect(x0 + 1.2 * cm, y1 - 2.8 * cm, 8.6 * cm, 2 * cm, stroke=1, fill=0)
        frame2 = Frame(x0 + 1.2 * cm, y1 - 2.8 * cm, 4.3 * cm, 2 * cm, leftPadding=1,
                       bottomPadding=1, rightPadding=1, topPadding=1, showBoundary=0)
        text = ["2 Отправитель/Экспортер"]
        placeToFrameWithTruncate(text, frame2, canvas)
        frame8 = Frame(x0 + 5.5 * cm, y1 - 2.8 * cm, 4.3 * cm, 2 * cm, leftPadding=1,
                       bottomPadding=1, rightPadding=1, topPadding=1, showBoundary=0)
        text = ["8 Получатель"]
        placeToFrameWithTruncate(text, frame8, canvas)

        # заполнение данными листа
        if data.g2[0] is not None:
            f = Frame(frame2.x1, frame2.y1, frame2.width, frame2.height - 0.4 * cm,
                      leftPadding=1, bottomPadding=1, rightPadding=1, topPadding=1, showBoundary=0)
            text = [data.g2[0]]
            placeToFrameWithShrink(text, f, canvas, only_data=1, align='LEFT')

        if data.g8[0] is not None:
            f = Frame(frame8.x1, frame2.y1, frame2.width, frame2.height - 0.4 * cm,
                      leftPadding=1, bottomPadding=1, rightPadding=1, topPadding=1, showBoundary=0)
            text = [data.g8[0]]
            placeToFrameWithShrink(text, f, canvas, only_data=1, align='LEFT')

        if data.g1_1 is not None:
            f = Frame(frame1_1.x1, frame1_1.y1, frame1_1.width, frame1_1.height - 0.2 * cm,
                      leftPadding=1, bottomPadding=1, rightPadding=1, topPadding=1, showBoundary=0)
            text = [data.g1_1]
            placeToFrameWithShrink(text, f, canvas, only_data=1, align='CENTER')

        if data.g1_2 is not None:
            f = Frame(frame1_2.x1, frame1_2.y1, frame1_2.width, frame1_2.height - 0.2 * cm,
                      leftPadding=1, bottomPadding=1, rightPadding=1, topPadding=1, showBoundary=0)
            text = [data.g1_2]
            placeToFrameWithShrink(text, f, canvas, only_data=1, align='CENTER')

        if data.g1_3 is not None:
            f = Frame(frame1_3.x1, frame1_3.y1, frame1_3.width, frame1_3.height - 0.2 * cm,
                      leftPadding=1, bottomPadding=1, rightPadding=1, topPadding=1, showBoundary=0)
            text = [data.g1_3]
            placeToFrameWithShrink(text, f, canvas, only_data=1, align='CENTER')

        f = Frame(frame3_1.x1, frame3_1.y1, frame3_1.width, frame3_1.height - 0.2 * cm,
                      leftPadding=1, bottomPadding=1, rightPadding=1, topPadding=1, showBoundary=0)
        text = [str(i + 1)]
        placeToFrameWithShrink(text, f, canvas, only_data=1, align='CENTER')

        f = Frame(frame3_2.x1, frame3_2.y1, frame3_2.width, frame3_2.height - 0.2 * cm,
                      leftPadding=1, bottomPadding=1, rightPadding=1, topPadding=1, showBoundary=0)
        text = [str(count_additional_page + 1)]
        placeToFrameWithShrink(text, f, canvas, only_data=1, align='CENTER')

        y_coord = 7
        ad_list = []
        k = i * 3 - 2   # 1-ый товар на странице (есть всегда)
        if k < len(data.items):
            _d = data.items[k]
        _ad = place_item(y_coord * cm, _d, k + 1)
        ad_list.append(_ad)
        y_coord -= 5.6

        k = i * 3 - 1  # 2-ой товар на странице (может не быть)
        if k < len(data.items):
            _d = data.items[k]
        else:
            _d = None
        _ad = place_item(y_coord * cm, _d, k + 1)
        ad_list.append(_ad)
        y_coord -= 5.6

        k = i * 3       # 3-ий товар на странице (может не быть)
        if k < len(data.items):
            _d = data.items[k]
        else:
            _d = None
        _ad = place_item(y_coord * cm, _d, k + 1)
        ad_list.append(_ad)

        canvas.rect(x0, y0, 1.2 * cm, y1 - y0 - 19.6 * cm)
        canvas.rect(x0 + 1.2 * cm, y0, 0.6 * cm, y1 - y0 - 19.6 * cm)
        canvas.rect(x0 + 1.8 * cm, y0, 2.6 * cm, y1 - y0 - 19.6 * cm)
        canvas.rect(x0 + 4.4 * cm, y0, 2.6 * cm, y1 - y0 - 19.6 * cm)
        canvas.rect(x0 + 7 * cm, y0, 2.6 * cm, y1 - y0 - 19.6 * cm)
        canvas.rect(x0 + 9.6 * cm, y0, 0.6 * cm, y1 - y0 - 19.6 * cm)
        canvas.rect(x0 + 10.2 * cm, y0, 0.6 * cm, y1 - y0 - 19.6 * cm)
        canvas.rect(x0 + 10.8 * cm, y0, 2.6 * cm, y1 - y0 - 19.6 * cm)
        canvas.rect(x0 + 13.4 * cm, y1 - 23.5 * cm, 2.6 * cm, 3.9 * cm)
        canvas.rect(x0 + 16 * cm, y1 - 23.5 * cm, 1.8 * cm, 3.9 * cm)
        canvas.rect(x0 + 13.4 * cm, y0, 0.6 * cm, y1 - y0 - 23.5 * cm)

        canvas.rect(x0, y1 - 19.9 * cm, x1 - x0, 0.3 * cm)
        canvas.rect(x0, y1 - 23.5 * cm, x1 - x0, 0.3 * cm)
        canvas.rect(x0, y1 - 23.8 * cm, 14 * cm, 0.3 * cm)
        canvas.rect(x0, y0, 14 * cm, 0.3 * cm)

        canvas.rect(x0 + 14 * cm, y1 - 25.5 * cm, 1.5 * cm, 2 * cm)
        canvas.rect(x0 + 15.5 * cm, y1 - 25.5 * cm, x1 - x0 - 15.5 * cm, 2 * cm)

        frame_watermark = Frame(x0, y0 - 0.6 * cm, x1 - x0, 0.6 * cm, leftPadding=1, bottomPadding=1,
                                rightPadding=1, topPadding=1, showBoundary=0)
        text = [bottom_watermark]
        placeToFrameWithShrink(text, frame_watermark, canvas)

        # убираем внешнюю рамку
        canvas.saveState()
        canvas.setStrokeColor(white)
        canvas.setLineWidth(2)
        canvas.rect(x0, y0, x1 - x0, y1 - y0)
        canvas.restoreState()

        canvas.save()
        merger.append(temp_base)  # добавляем страницу в сборщик PDF

        # Формируем обратную сторону доп. листа
        def check_add_data(ad):
            if (len(ad.g31) + len(ad.g40) + len(ad.g31) + len(ad.g44) + len(ad.g50) + len(ad.g52_1) +
                len(ad.g52_2)) > 0:
                return True
            else:
                return False

        if check_add_data(ad_list[0]) or check_add_data(ad_list[1]) or check_add_data(ad_list[2]):
            temp_base = tempfile.TemporaryFile()
            doc = SimpleDocTemplate(temp_base, pagesize=A4, rightMargin=1.4 * cm, leftMargin=1.4 * cm,
                                    topMargin=0.6 * cm,
                                    bottomMargin=1.4 * cm)
            elements = []

            if (len(ad_list[0].g31) > 0) or (len(ad_list[1].g31) > 0) or (len(ad_list[2].g31) > 0):  # если есть дополнительное описание товара
                el = []
                elements.append(Paragraph('31. Наименование товара (дополнительно)', style=style_data))
                elements.append(Spacer(width=pagex, height=0.1 * cm))
                el.append(['№', 'Наименование товара'])
                if (len(ad_list[0].g31) > 0):
                    for _e in ad_list[0].g31:
                        el.append([Paragraph(str(i * 3 - 1), style=style_data), Paragraph(_e, style=style_data)])
                if (len(ad_list[1].g31) > 0):
                    for _e in ad_list[1].g31:
                        el.append([Paragraph(str(i * 3), style=style_data), Paragraph(_e, style=style_data)])
                if (len(ad_list[2].g31) > 0):
                    for _e in ad_list[2].g31:
                        el.append([Paragraph(str(i * 3 + 1), style=style_data), Paragraph(_e, style=style_data)])

                t_g31 = Table(el, colWidths=(1 * cm, x1 - x0 - 1 * cm), rowHeights=None, repeatRows=1)
                t_g31.setStyle(TableStyle([
                    ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                    ('LINEBELOW', (0, 0), (-1, 0), 0.25, colors.black),
                    ('LINEBELOW', (0, 'splitlast'), (-1, 'splitlast'), 0.25, colors.black),
                    ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
                    ('BOX', (0, 0), (0, -1), 0.25, colors.black),
                    ('FONT', (0, 0), (-1, -1), 'Arial', fontsize_data),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                    ('TOPPADDING', (0, 0), (-1, -1), 0),
                ]))
                elements.append(t_g31)
                elements.append(Spacer(width=pagex, height=0.2 * cm))

            if (len(ad_list[0].g40) > 0) or (len(ad_list[1].g40) > 0) or (len(ad_list[2].g40) > 0):  # если не вместились предшествующие доки
                el = []
                elements.append(Paragraph('40. Предшествующие документы', style=style_data))
                elements.append(Spacer(width=pagex, height=0.1 * cm))
                el.append(['№', '№ Предшествующего документа'])
                if (len(ad_list[0].g40) > 0):
                    for _e in ad_list[0].g40:
                        el.append([Paragraph(str(i * 3 - 1), style=style_data), Paragraph(_e, style=style_data)])
                if (len(ad_list[1].g40) > 0):
                    for _e in ad_list[1].g40:
                        el.append([Paragraph(str(i * 3), style=style_data), Paragraph(_e, style=style_data)])
                if (len(ad_list[2].g40) > 0):
                    for _e in ad_list[2].g40:
                        el.append([Paragraph(str(i * 3 + 1), style=style_data), Paragraph(_e, style=style_data)])

                t_g40 = Table(el, colWidths=(1 * cm, x1 - x0 - 1 * cm), rowHeights=None, repeatRows=1)
                t_g40.setStyle(TableStyle([
                    ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                    # ('GRID', (0, 0), (0, -1), 0.25, colors.black),
                    ('LINEBELOW', (0, 0), (-1, 0), 0.25, colors.black),
                    ('LINEBELOW', (0, 'splitlast'), (-1, 'splitlast'), 0.25, colors.black),
                    ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
                    ('BOX', (0, 0), (0, -1), 0.25, colors.black),
                    ('FONT', (0, 0), (-1, -1), 'Arial', fontsize_data),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                    ('TOPPADDING', (0, 0), (-1, -1), 0),
                ]))
                elements.append(t_g40)
                elements.append(Spacer(width=pagex, height=0.2 * cm))

            if (len(ad_list[0].g44) > 0) or (len(ad_list[1].g44) > 0) or (len(ad_list[2].g44) > 0):  # если не вместились доки
                el = []
                elements.append(Paragraph('44. Дополнительная информация / Представляемый документ', style=style_data))
                elements.append(Spacer(width=pagex, height=0.1 * cm))
                el.append(['№', '№ Документа', 'Дата'])
                if (len(ad_list[0].g44) > 0):
                    for _e in ad_list[0].g44:
                        _tl = _e.split(' ')
                        dok = ' '.join(_tl[:-1])
                        data_dok = _tl[-1]
                        el.append([
                            Paragraph(str(i * 3 - 1), style=style_data),
                            Paragraph(dok, style=style_data),
                            Paragraph(data_dok, style=style_data),
                        ])
                if (len(ad_list[1].g44) > 0):
                    for _e in ad_list[1].g44:
                        _tl = _e.split(' ')
                        dok = ' '.join(_tl[:-1])
                        data_dok = _tl[-1]
                        el.append([
                            Paragraph(str(i * 3), style=style_data),
                            Paragraph(dok, style=style_data),
                            Paragraph(data_dok, style=style_data),
                        ])
                if (len(ad_list[2].g44) > 0):
                    for _e in ad_list[2].g44:
                        _tl = _e.split(' ')
                        dok = ' '.join(_tl[:-1])
                        data_dok = _tl[-1]
                        el.append([
                            Paragraph(str(i * 3 + 1), style=style_data),
                            Paragraph(dok, style=style_data),
                            Paragraph(data_dok, style=style_data),
                        ])

                t_g44 = Table(el, colWidths=(1 * cm, x1 - x0 - 4 * cm, 3 * cm), rowHeights=None, repeatRows=1)
                t_g44.setStyle(TableStyle([
                    ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                    ('LINEBELOW', (0, 0), (-1, 0), 0.25, colors.black),
                    ('LINEBELOW', (0, 'splitlast'), (-1, 'splitlast'), 0.25, colors.black),
                    ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
                    ('BOX', (0, 0), (0, -1), 0.25, colors.black),
                    ('BOX', (-1, 0), (-1, -1), 0.25, colors.black),
                    ('FONT', (0, 0), (-1, -1), 'Arial', fontsize_data),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                    ('TOPPADDING', (0, 0), (-1, -1), 0),
                ]))
                elements.append(t_g44)
                elements.append(Spacer(width=pagex, height=0.2 * cm))

            def printTop(canvas, doc):
                pass

            doc.build(elements, onFirstPage=printTop, onLaterPages=printTop)
            merger.append(temp_base)  # добавляем дополнительную страницу в сборщика PDF

            # если количество дополнительных страниц четное - то добавляем еще пустую
            reader = PdfReader(temp_base)
            number_of_pages = len(reader.pages)
            if number_of_pages % 2 == 0:
                temp_base = tempfile.TemporaryFile()
                doc = SimpleDocTemplate(temp_base, pagesize=A4)
                elements = [Paragraph('')]
                doc.build(elements)
                merger.append(temp_base)  # добавляем пустую страницу в сборщика PDF
        else:
            # просто добавляем пустую страницу
            temp_base = tempfile.TemporaryFile()
            doc = SimpleDocTemplate(temp_base, pagesize=A4)
            elements = [Paragraph('')]
            doc.build(elements)
            merger.append(temp_base)  # добавляем пустую страницу в сборщика PDF


    merger.write(temp_final)
    return temp_final
    #temp_final.close()
    #shutil.copy(path_final, filename)


def full_TD(filename, data):
    '''
    Формирование декларации на основе предостваленных данных
    :param filename: имя файла PDF на выходе
    :param data: словарь с данными для декларации (образец в db_to_data.py)
    '''

    temp_final = tempfile.TemporaryFile(delete=False)
    path_final = temp_final.name

    merger = PyPDF2.PdfMerger()
    # формируем основную и обратную страницу
    merger.append(first_page_TD(data))
    # формируем дополнительные страницы и их обратные стороны
    merger.append(second_page_TD(data))

    merger.write(temp_final)
    temp_final.close()
    shutil.copy(path_final, filename)


def full_TD_api(idxml):
    '''
    Формирование декларации на основе предостваленных данных
    :param idxml: ид xml в базе данных
    '''

    #temp_final = tempfile.TemporaryFile(delete=False)
    temp_final = BytesIO()

    # загружаем данные
    data = InfoTD()
    data.load_from_db(idxml)

    merger = PyPDF2.PdfMerger()
    # формируем основную и обратную страницу
    merger.append(first_page_TD(data))
    # формируем дополнительные страницы и их обратные стороны
    merger.append(second_page_TD(data))

    merger.write(temp_final)
    return temp_final

#dekl_test = InfoTD()
#dekl_test.test_data()
#full_TD_api(329203)
