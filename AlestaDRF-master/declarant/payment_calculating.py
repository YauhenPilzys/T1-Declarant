import decimal
import json
import logging
from datetime import date
from copy import deepcopy

from .models import Tnved, ConsignmentItem, ExchangeRatesNBRB, Excise, TreeTnved
import declarant.exchange_rates_load as NbrbLib


logger2 = logging.getLogger(__name__)
logger2.setLevel(logging.INFO)

# настройка обработчика и форматировщика для logger2
handler2 = logging.FileHandler(f"{__name__}.log", mode='a')
formatter2 = logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s")

# добавление форматировщика к обработчику
handler2.setFormatter(formatter2)
# добавление обработчика к логгеру
logger2.addHandler(handler2)


def add_space_to_tnved_code(s):
    """ дополняем пробелами код, т.к. в дереве тн вэд хранится он с пробелами
    коды тн вэд должны быть длиной больше 6 символов """
    if len(s) == 6:
        t = s[0:4] + ' ' + s[4:6]
    elif 6 < len(s) < 10:
        t = s[0:4] + ' ' + s[4:6] + ' ' + s[6:len(s)]
    elif len(s) == 10:
        t = s[0:4] + ' ' + s[4:6] + ' ' + s[6:9] + ' ' + s[9]
    return t


def get_value_exchange_rate(currency, date_er):
    """ функция возвращает курс валюты на указанную дату
        если в таблице курса нет, пытаемся его загрузить

        возвращает курс валюты деленый на количество валюты, если курс найден/загружен
        иначе возвращает 0 """
    if currency == 'BYN':
        return 1  # для белоруского рубля курс всегда 1:1
    else:
        try:
            # получаем курс валюты
            exch_rate_obj = ExchangeRatesNBRB.objects.get(Cur_Abbreviation=currency, Date=date_er)
            # если в таблице нет курса для указанной валюты
        except ExchangeRatesNBRB.DoesNotExist:
            # выполняем процедуру загрузки ежедневных курсов на дату расчета платежей
            NbrbLib.load_exchange_rates_from_nbrb(date_er, 0)
            exch_rate_obj = ExchangeRatesNBRB.objects.filter(Cur_Abbreviation=currency, Date=date_er).first()
            # если в таблице все ещё нет курса для указанной валюты
            if not exch_rate_obj:
                # выполняем процедуру загрузки ежемесячно устанавливаемых курсов на дату расчета платежей
                NbrbLib.load_exchange_rates_from_nbrb(date_er, 1)
                exch_rate_obj = ExchangeRatesNBRB.objects.filter(Cur_Abbreviation=currency, Date=date_er).first()
                if not exch_rate_obj:
                    # выполняем загрузку курса валюты с tws.by
                    NbrbLib.load_exchange_rates_from_tws(currency, date_er)
                    exch_rate_obj = ExchangeRatesNBRB.objects.filter(Cur_Abbreviation=currency, Date=date_er).first()
                    if not exch_rate_obj:
                        return 0
        return exch_rate_obj.Cur_OfficialRate / exch_rate_obj.Cur_Scale


def start_calc_payment_xml(xml_id, date_calc=date.today()):
    logger2.info('Start calculating payment for xml with id ' + str(xml_id))
    total_duties = 0
    total_excises = 0
    total_vats = 0
    warnings = {}
    w_messages = []
    code_list = []
    description_code_list = []
    payments = {}
    w_messages.append('Все расчеты произведены исходя из курсов на ' + str(date_calc) + '.')
    for ci in ConsignmentItem.objects.filter(xml_id=xml_id):

        customs_charges = []  # для хранения таможенных сборов
        customs_duties = []  # для хранения таможенных пошлин
        info_customs_duties = []  # текстовое описание тарифа
        excises = []  # для хранения акцизов
        info_excises = []  # текстовое описание акциза
        vats = []  # для хранения ндс
        all_values = dict()  # сумма пошлина + акциз + ндс для сортировки

        value_exch_rate = get_value_exchange_rate(ci.currencyCode, date_calc)
        print(value_exch_rate, ci.currencyCode, date_calc)
        tnved_obj = Tnved.objects.filter(Code__startswith=ci.CommodityCode)
        warnings[ci.ConsignmentItemOrdinal] = []
        if tnved_obj.count() > 1:
            warnings[ci.ConsignmentItemOrdinal].append(f'Для кода {ci.CommodityCode} найдено несколько вариантов расчета платежей.')
        counter = 0
        for t in tnved_obj:
            counter += 1
            customs_charges.append(t.F)  # таможенный сбор

            info_customs_duties.append(t.TariffText)   # инфа по тамож. пошлине

            # расчет таможенной пошлины
            if t.TariffAdvalor is not None:
                advalor = ci.CAValueAmount * value_exch_rate * decimal.Decimal(t.TariffAdvalor) / 100
                advalor = advalor.quantize(decimal.Decimal("1.00"), decimal.ROUND_CEILING)
            else:
                advalor = 0
            specific = 0
            if t.TariffSpecific:  # если установлена специфическая ставка пошлины
                spec_tariff_currency_value = get_value_exchange_rate(t.TariffSpecificCurrency, date_calc)
                # можем рассчитывать пошлину с использованием специфической ставки
                # ищем подходящую единицу измерения в двух полях
                if (t.TariffSpecificMeasureUnit.upper() == ci.GM_MeasureUnitAbbreviationCode) and ci.GM_GoodsMeasure:
                    specific = decimal.Decimal(t.TariffSpecific) * t.TariffSpecificMeasureAmount * spec_tariff_currency_value * ci.GM_GoodsMeasure
                elif (t.TariffSpecificMeasureUnit.upper() == ci.AGM_MeasureUnitAbbreviationCode) and ci.AGM_GoodsMeasure:
                    specific = decimal.Decimal(t.TariffSpecific) * t.TariffSpecificMeasureAmount * spec_tariff_currency_value * ci.AGM_GoodsMeasure
                else:
                    warnings[ci.ConsignmentItemOrdinal].append(
                        f'Для кода {ci.CommodityCode} для расчета платежей по позиции {t.Code} должна быть указана дополнительная единица измерения в "{t.TariffSpecificMeasureUnit}".')
                specific = specific.quantize(decimal.Decimal("1.00"), decimal.ROUND_CEILING)
            if t.TariffSpecificAddedToAdvalor:  # если стоит признак суммы, то складываем платежи, иначе берем большие
                all_value = advalor + specific
            else:
                all_value = advalor if advalor > specific else specific

            customs_duties.append(all_value)

            # акцизы
            if t.Ex:
                exc_obj = Excise.objects.filter(TnvedID=t)  # поиск акцизов для позиции в ТН ВЭД
                one_excise = []  # акцизы по одной подходящей позиции из ТН ВЭД
                one_info_excise = []  # инфо по акцизу (наименование)
                for ex in exc_obj:
                    one_info_excise.append(ex.Name)
                    spec_tariff_currency_value = get_value_exchange_rate(ex.Currency, date_calc)
                    if (ex.MeasureUnit.upper() == ci.GM_MeasureUnitAbbreviationCode) and ci.GM_GoodsMeasure:
                        one_excise.append((decimal.Decimal(ex.Rate) * spec_tariff_currency_value * ex.Amount * ci.GM_GoodsMeasure).quantize(decimal.Decimal("1.00"), decimal.ROUND_CEILING))
                    elif (ex.MeasureUnit.upper() == ci.AGM_MeasureUnitAbbreviationCode) and ci.AGM_GoodsMeasure:
                        one_excise.append((decimal.Decimal(ex.Rate) * spec_tariff_currency_value * ex.Amount * ci.AGM_GoodsMeasure).quantize(decimal.Decimal("1.00"), decimal.ROUND_CEILING))
                    else:
                        warnings[ci.ConsignmentItemOrdinal].append(
                            f'Для кода {ci.CommodityCode} для расчета акцизов по позиции {t.Code} ({ex.Name}) должна быть указана дополнительная единица измерения в "{ex.MeasureUnit}".')
                        one_excise.append(0)

                # надо отсортировать акцизы с описанием по убыванию
                new_x, new_y = zip(*sorted(zip(one_excise, one_info_excise), reverse=True))

                # добавляем к результату инфу по акцизам
                excises.append(deepcopy(new_x))
                info_excises.append(deepcopy(new_y))

                all_value += new_x[0]   # добавляем к общей сумме наибольший акциз

            # считаем НДС
            # для транзита величина установлена 20%
            # при использовании алгоритма для расчета в случае импорта - надо использовать доп. информацию по НДС
            vat = ((all_value + ci.CAValueAmount * value_exch_rate) * 20 / 100).quantize(decimal.Decimal("1.00"), decimal.ROUND_CEILING)
            vats.append(vat)
            all_value += vat

            all_values[counter] = all_value

        # уберем одинаковые платежи
        _tmp_list = []
        for i in range(len(customs_charges)):
            # строим кортежи
            _tmp_list.append((customs_charges[i], customs_duties[i], info_customs_duties[i], vats[i], all_values[i+1]))
        _tmp_set = set(_tmp_list)
        customs_charges.clear()
        customs_duties.clear()
        info_customs_duties.clear()
        vats.clear()
        all_values.clear()
        counter = 0
        for _s in _tmp_set:
            counter += 1
            customs_charges.append(_s[0])
            customs_duties.append(_s[1])
            info_customs_duties.append(_s[2])
            vats.append(_s[3])
            all_values[counter] = _s[4]

        # уберем одинаковые акцизы
        _tmp_list.clear()
        for i in range(len(excises)):
            for j in range(len(excises[i])):
                _tmp_list.append((excises[i][j], info_excises[i][j]))
        _tmp_set = set(_tmp_list)
        one_excise = []
        one_info_excise = []
        for _s in _tmp_set:
            one_excise.append(_s[0])
            one_info_excise.append(_s[1])
        if _tmp_set:
            new_x, new_y = zip(*sorted(zip(one_excise, one_info_excise), reverse=True))
            excises = list(deepcopy(new_x))
            info_excises = list(deepcopy(new_y))
        else:
            excises = []
            info_excises = []

        # сортируем наши платежи по убыванию
        sort_all_values_keys = sorted(all_values, key=all_values.get, reverse=True)
        tmp_customs_charges = []  # для хранения таможенных сборов
        tmp_customs_duties = []  # для хранения таможенных пошлин
        tmp_info_customs_duties = []  # текстовое описание тарифа
        tmp_excises = []  # для хранения акцизов
        tmp_info_excises = []  # текстовое описание акциза
        tmp_vats = []  # для хранения ндс
        tmp_all_duties = []  # все платежи
        for elem in sort_all_values_keys:
            if elem <= len(customs_charges):
                tmp_customs_charges.append(customs_charges[elem-1])
            if elem <= len(customs_duties):
                tmp_customs_duties.append(customs_duties[elem-1])
                tmp_info_customs_duties.append(info_customs_duties[elem-1])
            # if elem <= len(excises):
            #     tmp_excises.append(excises[elem-1])
            #     tmp_info_excises.append(info_excises[elem-1])
            if elem <= len(vats):
                tmp_vats.append(vats[elem-1])
            if elem <= len(all_values):
                tmp_all_duties.append(all_values[elem])
        # собираем общую информацию по платежам
        if len(customs_duties):
            total_duties += customs_duties[sort_all_values_keys[0]-1]
        if len(excises):
            total_excises += excises[sort_all_values_keys[0]-1]
        if len(vats):
            total_vats += vats[sort_all_values_keys[0]-1]

        # сохраняем информацию в payments
        payments[ci.ConsignmentItemOrdinal] = {
            'customs_charges': tmp_customs_charges.copy(),
            'customs_duties': tmp_customs_duties.copy(),
            'info_customs_duties': tmp_info_customs_duties.copy(),
            'excises': excises.copy(),
            'info_excises': info_excises.copy(),
            'vats': tmp_vats.copy(),
            'all_duties': tmp_all_duties.copy(),
            'code': ci.CommodityCode,
            'description_code': ' '.join(
                [
                    ci.GoodsDescriptionText,
                    ci.GoodsDescriptionText1,
                    ci.GoodsDescriptionText2,
                    ci.GoodsDescriptionText3,
                ]
            ).strip(),
        }

    return {
        'result': 'ok',
        'total': {
            'total_duties': total_duties,
            'total_excises': total_excises,
            'total_vats': total_vats,
        },
        'warnings': warnings,
        'messages': w_messages,
        'payments': payments,
    }


def check_tnved_code(s):
    """
        Осуществляем поиск по кодам ТНВЭД.
        @param s: json с кодами ТНВЭД
        @return: сами коды, их наличие в базе, доп. единицы измерения, доп. единицы для акцизов
    """

    y = json.loads(s)
    code_list = y["checkCodes"]
    code_exist = []
    code_measure = []
    code_exice = []
    all_result = []
    for i in range(len(code_list)):
        _c = code_list[i]
        try:
            c = Tnved.objects.get(Code=_c)  # запрос к таблице ТН ВЭД на точное совпадение
            c_list = [c]
            _e = True
        except:
            _e = False
        if not _e:
            c_list = Tnved.objects.filter(Code__startswith=_c)  # запрос к таблице на частичное совпадение кода (начало)
            if len(c_list) > 0:
                _e = True
            else:
                _e = False
        code_exist.append(_e)
        if _e:
            # код(ы) найден(ы) - ищем доп. едининцы и акцизы
            add_measure = []
            tarif_measure = []
            exice = []
            for _tnved in c_list:
                if _tnved.TariffSpecificMeasureUnit:
                    tarif_measure.append(_tnved.TariffSpecificMeasureUnit)
                if _tnved.AdditionalMeasureUnit:
                    add_measure.append(_tnved.AdditionalMeasureUnit)
                if _tnved.Ex:
                    ex_list = Excise.objects.filter(TnvedID=_tnved.pk)
                    for _ex in ex_list:
                        if _ex.Rate > 0 and _ex.MeasureUnit:
                            exice.append(_ex.MeasureUnit)
            add_measure_set = set(add_measure)
            tarif_measure_set = set(tarif_measure)
            exice_set = set(exice)
            _r = {}
            if len(add_measure_set) > 0:
                _r['AdditionalMeasureUnit'] = add_measure_set
            else:
                _r['AdditionalMeasureUnit'] = False

            if len(tarif_measure_set - add_measure_set) > 0:
                _r['TariffSpecificMeasureUnit'] = tarif_measure_set - add_measure_set
            else:
                _r['TariffSpecificMeasureUnit'] = False

            if len(exice_set - tarif_measure_set - add_measure_set) > 0:
                _r['ExiceMeasureUnit'] = exice_set - tarif_measure_set - add_measure_set
            else:
                _r['ExiceMeasureUnit'] = False

            code_measure.append(_r)
        else:
            code_measure.append(False)

        all_result.append({
            'code': _c,
            'exist': code_exist[i],
            'add_measure': code_measure[i],
        })
    return {
        'result': all_result
    }


def get_tnved_code_description(s):
    """
        Возвращает полное описание кода ТНВЭД по таблице и по дереву.
        @param s: код ТНВЭД
        @return: список с узлами, в котором введенный ТНВЭД - последний
    """
    all_result = []
    # c_list = Tnved.objects.filter(Code__startswith=s)
    c_list = Tnved.objects.filter(Code=s)
    if len(c_list) == 0:
        c_list = TreeTnved.objects.filter(Code=s)
        if len(c_list) == 0:
            c_list = TreeTnved.objects.filter(Code__startswith=s)
        if len(c_list) == 0:
            return {
                'result': []
            }
        all_result.append({
            'code': c_list[0].Code,
            'name': c_list[0].Name,
        })
        tree = c_list[0].ParentID
    else:
        all_result.append({
            'code': c_list[0].Code,
            'name': c_list[0].Name,
        })
        tree = c_list[0].TreeID

    while tree:
        all_result.append({
            'code': tree.Code,
            'name': tree.Name,
        })
        tree = tree.ParentID

    return {
        'result': all_result[::-1]
    }


