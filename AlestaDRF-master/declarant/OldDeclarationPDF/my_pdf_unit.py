# KeepInFrame параметр mode:
#    truncate - вписывает в ширину, если строки не влазят - обрезает
#    error - генерирует исключение, если не влазит по каким-то параметрам
#    shrink - вписывает содержимое в рамку уменьшая шрифт
#    overflow - вписывает в ширину, если строки не влазят - пишет поверх

import reportlab
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import KeepInFrame, Paragraph
from reportlab.lib.colors import black, white

fontsize_data = 8
fontsize = 8
opis_fontsize = 11
oborot = ' СМ. ОБОРОТ'

style = ParagraphStyle('standart_style',
                       alignment=0,
                       allowOrphans=0,
                       allowWidows=1,
                       # autoLeading='min',
                       backColor=None,
                       borderColor=black,
                       borderPadding=0,
                       borderRadius=None,
                       borderWidth=0,
                       bulletAnchor='start',
                       bulletFontName='Arial',
                       bulletFontSize=fontsize,
                       bulletIndent=0,
                       embeddedHyphenation=0,
                       endDots=None,
                       firstLineIndent=0,
                       fontName="Arial",
                       fontSize=fontsize,
                       justifyBreaks=0,
                       justifyLastLine=0,
                       leading=9,
                       leftIndent=1,
                       linkUnderline=0,
                       rightIndent=1,
                       spaceAfter=0,
                       spaceBefore=0,
                       spaceShrinkage=0.05,
                       splitLongWords=1,
                       strikeGap=1,
                       strikeOffset=0.25,
                       strikeWidth=1,
                       textColor=black,
                       textTransform=None,
                       underlineGap=1,
                       underlineOffset=-0.125,
                       underlineWidth=1,
                       uriWasteReduce=0,
                       wordWrap=False,
                       )

style_data = ParagraphStyle('standart_style',
                            alignment=0,
                            allowOrphans=0,
                            allowWidows=1,
                            backColor=None,
                            borderColor=black,
                            borderPadding=0,
                            borderRadius=None,
                            borderWidth=0,
                            bulletAnchor='start',
                            bulletFontName='Arial',
                            bulletFontSize=fontsize_data,
                            bulletIndent=0,
                            embeddedHyphenation=0,
                            endDots=None,
                            firstLineIndent=0,
                            fontName="Arial",
                            fontSize=fontsize_data,
                            justifyBreaks=0,
                            justifyLastLine=0,
                            leading=fontsize_data + 1,
                            leftIndent=1,
                            linkUnderline=0,
                            rightIndent=1,
                            spaceAfter=0,
                            spaceBefore=0,
                            spaceShrinkage=0.05,
                            splitLongWords=1,
                            strikeGap=1,
                            strikeOffset=0.25,
                            strikeWidth=1,
                            textColor=black,
                            textTransform=None,
                            underlineGap=1,
                            underlineOffset=-0.125,
                            underlineWidth=1,
                            uriWasteReduce=0,
                            wordWrap=False,
                            )

opis_data = ParagraphStyle('standart_style',
                           alignment=0,
                           allowOrphans=0,
                           allowWidows=1,
                           backColor=None,
                           borderColor=black,
                           borderPadding=0,
                           borderRadius=None,
                           borderWidth=0,
                           bulletAnchor='start',
                           bulletFontName='Arial',
                           bulletFontSize=opis_fontsize,
                           bulletIndent=0,
                           embeddedHyphenation=0,
                           endDots=None,
                           firstLineIndent=0,
                           fontName="Arial",
                           fontSize=opis_fontsize,
                           justifyBreaks=0,
                           justifyLastLine=0,
                           leading=opis_fontsize + 1,
                           leftIndent=1,
                           linkUnderline=0,
                           rightIndent=1,
                           spaceAfter=0,
                           spaceBefore=0,
                           spaceShrinkage=0.05,
                           splitLongWords=1,
                           strikeGap=1,
                           strikeOffset=0.25,
                           strikeWidth=1,
                           textColor=black,
                           textTransform=None,
                           underlineGap=1,
                           underlineOffset=-0.125,
                           underlineWidth=1,
                           uriWasteReduce=0,
                           wordWrap='LTR',
                           )

opis_data_center = ParagraphStyle('standart_style',
                                  alignment=TA_CENTER,
                                  allowOrphans=0,
                                  allowWidows=1,
                                  backColor=None,
                                  borderColor=black,
                                  borderPadding=0,
                                  borderRadius=None,
                                  borderWidth=0,
                                  bulletAnchor='start',
                                  bulletFontName='Arial',
                                  bulletFontSize=opis_fontsize,
                                  bulletIndent=0,
                                  embeddedHyphenation=0,
                                  endDots=None,
                                  firstLineIndent=0,
                                  fontName="Arial",
                                  fontSize=opis_fontsize,
                                  justifyBreaks=0,
                                  justifyLastLine=0,
                                  leading=opis_fontsize + 1,
                                  leftIndent=1,
                                  linkUnderline=0,
                                  rightIndent=1,
                                  spaceAfter=0,
                                  spaceBefore=0,
                                  spaceShrinkage=0.05,
                                  splitLongWords=1,
                                  strikeGap=1,
                                  strikeOffset=0.25,
                                  strikeWidth=1,
                                  textColor=black,
                                  textTransform=None,
                                  underlineGap=1,
                                  underlineOffset=-0.125,
                                  underlineWidth=1,
                                  uriWasteReduce=0,
                                  wordWrap='LTR',
                                  )

opis_data_table = ParagraphStyle('standart_style',
                                 alignment=0,
                                 allowOrphans=0,
                                 allowWidows=1,
                                 backColor=None,
                                 borderColor=black,
                                 borderPadding=0,
                                 borderRadius=None,
                                 borderWidth=0,
                                 bulletAnchor='start',
                                 bulletFontName='Arial',
                                 bulletFontSize=opis_fontsize - 1,
                                 bulletIndent=0,
                                 embeddedHyphenation=0,
                                 endDots=None,
                                 firstLineIndent=0,
                                 fontName="Arial",
                                 fontSize=opis_fontsize - 1,
                                 justifyBreaks=0,
                                 justifyLastLine=0,
                                 leading=opis_fontsize,
                                 leftIndent=1,
                                 linkUnderline=0,
                                 rightIndent=1,
                                 spaceAfter=0,
                                 spaceBefore=0,
                                 spaceShrinkage=0.05,
                                 splitLongWords=1,
                                 strikeGap=1,
                                 strikeOffset=0.25,
                                 strikeWidth=1,
                                 textColor=black,
                                 textTransform=None,
                                 underlineGap=1,
                                 underlineOffset=-0.125,
                                 underlineWidth=1,
                                 uriWasteReduce=0,
                                 wordWrap='LTR',
                                 )

opis_data_table_center = ParagraphStyle('standart_style',
                                        alignment=TA_CENTER,
                                        allowOrphans=0,
                                        allowWidows=1,
                                        backColor=None,
                                        borderColor=black,
                                        borderPadding=0,
                                        borderRadius=None,
                                        borderWidth=0,
                                        bulletAnchor='start',
                                        bulletFontName='Arial',
                                        bulletFontSize=opis_fontsize - 1,
                                        bulletIndent=0,
                                        embeddedHyphenation=0,
                                        endDots=None,
                                        firstLineIndent=0,
                                        fontName="Arial",
                                        fontSize=opis_fontsize - 1,
                                        justifyBreaks=0,
                                        justifyLastLine=0,
                                        leading=opis_fontsize,
                                        leftIndent=1,
                                        linkUnderline=0,
                                        rightIndent=1,
                                        spaceAfter=0,
                                        spaceBefore=0,
                                        spaceShrinkage=0.05,
                                        splitLongWords=1,
                                        strikeGap=1,
                                        strikeOffset=0.25,
                                        strikeWidth=1,
                                        textColor=black,
                                        textTransform=None,
                                        underlineGap=1,
                                        underlineOffset=-0.125,
                                        underlineWidth=1,
                                        uriWasteReduce=0,
                                        wordWrap='LTR',
                                        )

style_data_center = ParagraphStyle('standart_style',
                                   alignment=TA_CENTER,
                                   allowOrphans=0,
                                   allowWidows=1,
                                   backColor=None,
                                   borderColor=black,
                                   borderPadding=0,
                                   borderRadius=None,
                                   borderWidth=0,
                                   bulletAnchor='start',
                                   bulletFontName='Arial',
                                   bulletFontSize=fontsize_data,
                                   bulletIndent=0,
                                   embeddedHyphenation=0,
                                   endDots=None,
                                   firstLineIndent=0,
                                   fontName="Arial",
                                   fontSize=fontsize_data,
                                   justifyBreaks=0,
                                   justifyLastLine=0,
                                   leading=fontsize_data - 1,
                                   leftIndent=1,
                                   linkUnderline=0,
                                   rightIndent=1,
                                   spaceAfter=0,
                                   spaceBefore=0,
                                   spaceShrinkage=0.05,
                                   splitLongWords=1,
                                   strikeGap=1,
                                   strikeOffset=0.25,
                                   strikeWidth=1,
                                   textColor=black,
                                   textTransform=None,
                                   underlineGap=1,
                                   underlineOffset=-0.125,
                                   underlineWidth=1,
                                   uriWasteReduce=0,
                                   wordWrap=False,
                                   )


def placeToFrameWithTruncate(pg_text, fr, canv, only_data=0, align='LEFT'):
    '''
    Добавляет в рамку текст, если не влазит - просто обрезает
    :param pg_text: список строк, которые надо вписать
    :param fr: переменнаяя типа Frame, в которую надо добавить текст
    :param canv: Canvas, на котором размещаем рамку
    :param only_data: если параметр равен 1 - то вписывать как данные, без заголовка, иначе pg_text[0] - как заголовок
    :param align: определяет горизонтальное выравнивание LEFT(по умолчанию) и CENTER
    '''
    p_text = []
    for i in range(0, len(pg_text)):
        if (i == 0) and (only_data == 0):
            p_text.append(Paragraph(pg_text[i], style=style))
        else:
            if align == 'CENTER':
                p_text.append(Paragraph(pg_text[i], style=style_data_center))
            else:
                p_text.append(Paragraph(pg_text[i], style=style_data))

    text = KeepInFrame(
        maxWidth=0,
        maxHeight=0,
        content=p_text,
        mode='truncate',
        hAlign=align,
        vAlign='CENTER',
        fakeWidth='0',
    )

    fr.addFromList([text], canv)


def placeToFrameWithShrink(pg_text, fr, canv, only_data=0, align='LEFT'):
    '''
    Добавляет в рамку текст, если не влазит - уменьшает шрифт
    :param pg_text: список строк, которые надо вписать
    :param fr: переменнаяя типа Frame, в которую надо добавить текст
    :param canv: Canvas, на котором размещаем рамку
    :param only_data: если параметр равен 1 - то вписывать как данные, без заголовка, иначе pg_text[0] - как заголовок
    :param align: определяет горизонтальное выравнивание LEFT(по умолчанию) и CENTER
    '''
    p_text = []
    for i in range(0, len(pg_text)):
        if (i == 0) and (only_data == 0):
            p_text.append(Paragraph(pg_text[i], style=style))
        else:
            if align == 'CENTER':
                p_text.append(Paragraph(pg_text[i], style=style_data_center))
            else:
                p_text.append(Paragraph(pg_text[i], style=style_data))

    text = KeepInFrame(
        maxWidth=0,
        maxHeight=0,
        content=p_text,
        mode='shrink',
        hAlign=align,
        vAlign='CENTER',
        fakeWidth='0',
    )

    fr.addFromList([text], canv)


def placeToFrameWithReturn(pg_text, fr, canv, only_data=0, align='LEFT'):
    '''
    Добавляет в рамку текст, если не влазит - возвращает список не поместившихся строк
    :param pg_text: список строк, которые надо вписать
    :param fr: переменнаяя типа Frame, в которую надо добавить текст
    :param canv: Canvas, на котором размещаем рамку
    :param only_data: если параметр равен 1 - то вписывать как данные, без заголовка, иначе pg_text[0] - как заголовок
    :return: возвращает список строк, не поместившихся в рамку
    :param align: определяет горизонтальное выравнивание LEFT(по умолчанию) и CENTER
    '''
    res = []
    add_str = oborot
    tmps = ''  # строка для сбора того, что не влезло
    cut_line_number = 1
    cut_symbol_number = 0
    attempts_count = 0
    printed = False
    while not printed:
        p_text = []
        if attempts_count > 0:  # необходимо обрезать
            for i in range(0, len(pg_text) - cut_line_number):
                if (i == 0) and (only_data == 0):
                    p_text.append(Paragraph(pg_text[i], style=style))
                else:
                    if align == 'CENTER':
                        p_text.append(Paragraph(pg_text[i], style=style_data_center))
                    else:
                        p_text.append(Paragraph(pg_text[i], style=style_data))
            if cut_symbol_number > len(pg_text[-cut_line_number]):
                res.insert(0, tmps)
                tmps = ''
                cut_line_number += 1
                cut_symbol_number = 0
                continue
            if cut_symbol_number == 0:
                s = pg_text[-cut_line_number] + add_str
            else:
                s = pg_text[-cut_line_number][:-cut_symbol_number] + add_str
                tmps = pg_text[-cut_line_number][-cut_symbol_number] + tmps
            cut_symbol_number += 1
            if only_data == 0:
                p_text.append(Paragraph(s, style=style))
            else:
                if align == 'CENTER':
                    p_text.append(Paragraph(s, style=style_data_center))
                else:
                    p_text.append(Paragraph(s, style=style_data))
        else:
            for i in range(0, len(pg_text)):
                if (i == 0) and (only_data == 0):
                    p_text.append(Paragraph(pg_text[i], style=style))
                else:
                    if align == 'CENTER':
                        p_text.append(Paragraph(pg_text[i], style=style_data_center))
                    else:
                        p_text.append(Paragraph(pg_text[i], style=style_data))
        try:
            text = KeepInFrame(
                maxWidth=fr.width,
                maxHeight=fr.height,
                content=p_text,
                mode='error',
                hAlign=align,
                vAlign='CENTER',
                fakeWidth='0',
            )
            fr.addFromList([text], canv)
        except reportlab.platypus.doctemplate.LayoutError:
            attempts_count += 1
        else:
            printed = True
            if tmps != '':
                res.insert(0, tmps)
    return res
