from datetime import date
import requests
import logging
from declarant.update_tnved import start_session, stop_session

from .models import ExchangeRatesNBRB

logger2 = logging.getLogger(__name__)
logger2.setLevel(logging.INFO)

# настройка обработчика и форматировщика для logger2
handler2 = logging.FileHandler(f"{__name__}.log", mode='a')
formatter2 = logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s")

# добавление форматировщика к обработчику
handler2.setFormatter(formatter2)
# добавление обработчика к логгеру
logger2.addHandler(handler2)


def load_exchange_rates_from_nbrb(ondate=date.today(), period=0):
    """ period=0 - загрузка ежедневно устанавливаемых курсов
        period=1 - загрузка ежемесячно устанавливаемых курсов """
    str_period = 'ежемесячно' if period else 'ежедневно'
    logger2.info(f'Запрос {str_period} устанавливаемых курсов с nbrb.by на дату {str(ondate)}.')
    params = dict(ondate=ondate, periodicity=period)
    res = requests.get('https://www.nbrb.by/api/exrates/rates', params=params)
    if res:
        logger2.info(f'Получены {str_period} устанавливаемые курсы на дату {str(ondate)}.')
        json = res.json()
        for j in json:
            exch_rate_obj = ExchangeRatesNBRB()
            exch_rate_obj.Cur_ID = j['Cur_ID']
            exch_rate_obj.Date = j['Date']
            exch_rate_obj.Cur_Abbreviation = j['Cur_Abbreviation']
            exch_rate_obj.Cur_Scale = j['Cur_Scale']
            exch_rate_obj.Cur_Name = j['Cur_Name']
            exch_rate_obj.Cur_OfficialRate = j['Cur_OfficialRate']
            try:
                exch_rate_obj.save()
            except:
                logger2.info('Не сохранен курс валюты: ' + str(j['Cur_ID']) + ' на ' + str(j['Date']))
    else:
        logger2.info(
            f'Ошибка. Данные по {str_period} устанавливаемым курсам с nbrb.by  на дату {str(ondate)} не получены.')
    return {'result': 'ok'}


def load_exchange_rates_from_tws(currency, ondate=date.today(), LatestAvailable=1):
    session_key = start_session()
    if session_key:
        logger2.info(f'Загрузка курса валюты {currency} на {ondate} c tws.by!')
        params = dict(SessionKey=session_key, Currency=currency, Date=ondate, LatestAvailable=LatestAvailable)
        res = requests.get('https://www.tws.by/tws/api/r23', params=params)
        if res:
            json = res.json()
            if json['error_code'] == 0:
                exch_rate_obj = ExchangeRatesNBRB()
                exch_rate_obj.Cur_ID = 0  # при подгрузке с tws этого параметра нету
                exch_rate_obj.Date = json['Date']
                exch_rate_obj.Cur_Abbreviation = currency
                exch_rate_obj.Cur_Scale = json['CurrencyAmount']
                exch_rate_obj.Cur_Name = currency
                exch_rate_obj.Cur_OfficialRate = json['Rate']
                try:
                    exch_rate_obj.save()
                except:
                    logger2.info(f'Не сохранен курс валюты: {currency} на {json["Date"]}')
    stop_session()
