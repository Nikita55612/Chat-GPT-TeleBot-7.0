from matplotlib import pyplot as plt
from datetime import datetime as dt
from config import Users as cfg
import speech_recognition as sr
from config import Bot as bcfg
from users import User as U
import soundfile as sf
import matplotlib
import requests
import typing

matplotlib.use("agg")


CACHE = {}


def voice_to_text(u: U | typing.Any) -> str:
    data, samplerate = sf.read(f"{cfg.dir}//{u.id}//voice_request.ogg")
    sf.write(f"{cfg.dir}//{u.id}//voice_request.wav", data, samplerate)
    rec = sr.Recognizer()
    with sr.AudioFile(f"{cfg.dir}//{u.id}//voice_request.wav") as af:
        audio_content = rec.record(af)
    return rec.recognize_google(audio_content, language="en-US" if u.profile.language == "en" else "ru-RU")


def tokens_to_rub(tokens: int) -> float:
    if CACHE.get("usd_to_rub"):
        usd_to_rub = CACHE["usd_to_rub"]
    else:
        try:
            response = requests.get("https://query1.finance.yahoo.com/v8/finance/chart/RUB=X?interval=2m&range=5m")
            if response.status_code == 200:
                data = response.json()
                usd_to_rub = data["chart"]["result"][0]["meta"]["chartPreviousClose"]
                CACHE["usd_to_rub"] = usd_to_rub
            else:
                usd_to_rub = 90
        except Exception as _ex:
            usd_to_rub = 90
    return round(usd_to_rub * 0.002 / 1000 * tokens * bcfg.token_rate_mult, 2)


def token_rate_text(u: U | typing.Any, n: int = 1000) -> str:
    rate = tokens_to_rub(n)
    if u.profile.language == "en":
        return f"💎 Token balance: <b>{u.profile.tokens}</b>\n" \
               f"💰 Balance: <b>{u.profile.balance}</b>\n" \
               f"📉 Token rate for today: {rate}₽ for {n} tokens" 
    else:
        return f"💎 Баланс токенов: <b>{u.profile.tokens}</b>\n" \
               f"💰 Внутренний баланс: <b>{u.profile.balance}</b>\n" \
               f"📉 Курс токена на сегодня: {rate}₽ за {n} токенов" 


def get_statistics(u: U | typing.Any) -> tuple | None:
    history = u.get_history()
    if len(history) < 2:
        return None
    cache_key = f"{u.id}__{history[-1][0]}{u.profile.language}"
    if CACHE.get(cache_key):
        return CACHE[cache_key]
    stat = {
        "total_requests": len(history), 
        "sum_total_tokens": 0, 
        "sum_requests": 0, 
        "sum_responses": 0, 
        "total_tokens_list": [], 
        "dt_list": []
    }
    if u.profile.language == "en":
        plt_title0 = "Daily histogram of requests"
        plt_title01 = "Daily histogram of requests\n100 days"
        plt_title1 = "Token consumption chart"
        plt_title11 = "Token consumption chart\n100 latest requests"
        plt_xlabel0 = "Date"
        plt_ylabel0 = "Number of requests"
        plt_xlabel1 = "Request number"
        plt_ylabel1 = "Number of tokens"
    else:
        plt_title0 = "Дневная гистограмма запросов"
        plt_title01 = "Дневная гистограмма запросов\n100 дней"
        plt_title1 = "График расхода токенов"
        plt_title11 = "График расхода токенов\n100 последних запросов"
        plt_xlabel0 = "Дата"
        plt_ylabel0 = "Количество запросов"
        plt_xlabel1 = "Номер запроса"
        plt_ylabel1 = "Количество токенов"

    for i in history:
        stat["dt_list"].append(dt.strptime(i[0].split(" ")[0], "%Y-%m-%d"))
        stat["total_tokens_list"].append(int(i[6]))
        stat["sum_requests"] += len(i[3])
        stat["sum_responses"] += len(i[4])
    stat["sum_total_tokens"] = sum(stat["total_tokens_list"])
    stat["set_dt"] = list(set(stat["dt_list"]))
    stat["dt_requests"] = [stat["dt_list"].count(i) for i in stat["set_dt"]]

    plt.style.use('dark_background')
    fig, ax = plt.subplots()
    if len(stat["set_dt"]) > 100:
        stat["set_dt"] = stat["set_dt"][len(stat["set_dt"]) - 100:]
        stat["dt_requests"] = stat["dt_requests"][len(stat["set_dt"]) - 100:]
        ax.set_title(plt_title01)
    else:
        ax.set_title(plt_title0)
    ax.bar(stat["set_dt"], stat["dt_requests"], color="#00ffc0")
    plt.gcf().autofmt_xdate()
    plt.xlabel(plt_xlabel0)
    plt.ylabel(plt_ylabel0)
    plt.savefig(f"{cfg.dir}//{u.id}//daily_histogram.png")
    plt.close(fig)

    if stat["total_requests"] > 100:
        stat["total_tokens_list"] = stat["total_tokens_list"][stat["total_requests"] - 100:]
        plt.title(plt_title11)
    else:
        plt.title(plt_title1)
    plt.plot(range(len(stat["total_tokens_list"])), stat["total_tokens_list"], color="#00ffc0")
    plt.xlabel(plt_xlabel1)
    plt.ylabel(plt_ylabel1)  
    plt.savefig(f"{cfg.dir}//{u.id}//token_consumption.png")
    plt.close()

    avg_total_tokens = round(stat["sum_total_tokens"] / stat["total_requests"])
    avg_sum_requests = round(stat["sum_requests"] / stat["total_requests"])
    avg_sum_responses = round(stat["sum_responses"] / stat["total_requests"])
    if u.profile.language == "en":
        text = f"📈 Total requests: <b>{stat['total_requests']}</b>\n\n" \
               f"📍 Total tokens spent: <b>{stat['sum_total_tokens']}</b>\n" \
               f"📍 Average value of tokens per request: <b>{avg_total_tokens}</b>\n\n" \
               f"💬 Average request length: <b>{avg_sum_requests}</b> chars\n" \
               f"💬 Average answer length: <b>{avg_sum_responses}</b> chars\n\n" \
               f"⏱ Date and time of first/last request:\n<b>{history[0][0]}/{history[-1][0]}</b>" 
    else:
        text = f"📈 Всего запросов: <b>{stat['total_requests']}</b>\n\n" \
               f"📍 Всего потрачено токенов: <b>{stat['sum_total_tokens']}</b>\n" \
               f"📍 Среднее значение токенов на один запрос: <b>{avg_total_tokens}</b>\n\n" \
               f"💬 Средняя длина запроса: <b>{avg_sum_requests}</b> chars\n" \
               f"💬 Средняя длина ответа: <b>{avg_sum_responses}</b> chars\n\n" \
               f"⏱ Дата и время первого/последнего запроса:\n<b>{history[0][0]}/{history[-1][0]}</b>"
    for i in CACHE.copy():
        if i.split("__")[0] == u.id:
            del CACHE[i]
    CACHE[cache_key] = (
        text, f"{cfg.dir}//{u.id}//daily_histogram.png", f"{cfg.dir}//{u.id}//token_consumption.png"
    )
    return CACHE[cache_key]


tokens_to_rub(0)

