from users import User as U
from gpt import models
import tiktoken
import typing


def get_models_info():
    return "".join(
        [f"<a href='{getattr(models, i)[0].source if isinstance(getattr(models, i), list) else getattr(models, i).source}'>{i}</a>\n" 
         for i in models.list_])


class Answers:
    class En:
        start_answer0 = "Hello! How can I assist you today?"
        clear_context_answer0 = "Context cleared successfully!"
        clear_context_answer1 = "The context has already been cleared!"
        models = f"Models:\n{get_models_info()}"
        stat_not_enough_data = "There is not enough data to generate statistics!"
        load_history_timeout = "Load history timeout:"
        context_info = "Context is needed so that the neural network understands the general " \
                       "essence of the dialogue from previous messages. The saved context spends tokens. " \
                       "Context can be cleared if it is no longer relevant to the dialogue. " \
                       "You can clear the context with the command"
        context_buffer_info = "\n\nThe maximum context buffer is the limit after which no new context " \
                              "will be added. Once the limit is reached, the new context will replace the old one. " \
                              "The context can be completely disabled by setting the context buffer to 0"
        insufficient_funds = "Insufficient funds!"
        buy_tokens = "-"
        pay_except = "The pay parameter is not defined!\nSpecify the payment amount separated by a space after the pay command\nExample: /pay 75.5"
        invoice = "Invoice:"
        send_invoice_timeout = "Send invoice timeout:"
        payment_verification_timeout = "Payment verification timeout:"
        top_up_balance_info = "You can create the top-up amount yourself using the /pay command\n" \
                              "Example: /pay 121.55\n" \
                              "After payment, you must click the button:\n🔄 Check payment\n" \
                              "For payment questions: @GPT_LiveSupport202X_bot"
        payment_failed_verification = "Payment failed verification"
    
    class Ru:
        start_answer0 = "Привет! Как я могу помочь тебе сегодня?"
        clear_context_answer0 = "Контекст успешно очищен!"
        clear_context_answer1 = "Контекст уже очищен!"
        models = f"Модели:\n{get_models_info()}"
        stat_not_enough_data = "Недостаточно данных для формирования статистики!"
        load_history_timeout = "Тайм-аут загрузки истории:"
        context_info = "Контекст нужен для того, чтобы нейронная сеть понимала общую суть " \
                       "диалога из предыдущих сообщений. Сохраненный контекст тратит токены." \
                       "Контекст можно очистить, если он больше не имеет отношение к диалогу. " \
                       "Очистить контекст можно командой"
        context_buffer_info = "\n\nМаксимальный буфер контекста это лимит после которого не будет " \
                              "добавляться новый контекст.По достижении лимита новый контекст будет " \
                              "заменять собой старый. Контекст можно вовсе отключить выставив буфер контекста в 0"
        insufficient_funds = "Недостаточно средств!"
        buy_tokens = "-"
        pay_except = "Параметр pay не определен!\nУкажите сумму оплаты через пробел после команды pay\nПример: /pay 75.5"
        invoice = "Счет на оплату:"
        send_invoice_timeout = "Тайм-аут отправки счета:"
        payment_verification_timeout = "Тайм-аут проверки платежа:"
        top_up_balance_info = "Сумму для пополнения можно указать самостоятельно, используя команду /pay\n" \
                              "Пример: /pay 121.55\n" \
                              "После оплаты необходимо нажать кнопку:\n🔄 Проверить оплату\n" \
                              "По вопросам оплаты: @GPT_LiveSupport202X_bot"
        payment_failed_verification = "Оплата не прошла проверку"

    en = En
    ru = Ru


def get_client_menu_text(u: U | typing.Any) -> str:
    if u.profile.language == "en":
        return f"🔐 <b><i>Personal Area</i></b>\n\n" \
               f"👤 Name: <b>{u.name} (ID: <code>{u.id}</code>)</b>\n\n" \
               f"💎 Token balance: <b>{u.profile.tokens}</b>\n" \
               f"💰 Balance: <b>{u.profile.balance}₽</b>\n" \
               f"⏱ Before token renewal: <b>{u.profile.hours_deff_reset}h</b>\n" \
               f"ℹ️ Status: <b>{u.profile.status}</b>" 
    else:
        return f"🔐 <b><i>Личный кабинет</i></b>\n\n" \
               f"👤 Имя: <b>{u.name} (ID: <code>{u.id}</code>)</b>\n\n" \
               f"💎 Баланс токенов: <b>{u.profile.tokens}</b>\n" \
               f"💰 Внутренний баланс: <b>{u.profile.balance}₽</b>\n" \
               f"⏱ До обновления токенов: <b>{u.profile.hours_deff_reset}ч</b>\n" \
               f"ℹ️ Статус: <b>{u.profile.status}</b>" 
    

def get_payment_menu_text(u: U | typing.Any) -> str:
    if u.profile.language == "en":
        return f"💎 Token balance: <b>{u.profile.tokens}</b>\n" \
               f"💰 Balance: <b>{u.profile.balance}₽</b>\n" \
               f"⏱ Before token renewal: <b>{u.profile.hours_deff_reset}h</b>\n" \
               f"ℹ️ Status: <b>{u.profile.status}</b>""" 
    else:
        return f"💎 Баланс токенов: <b>{u.profile.tokens}</b>\n" \
               f"💰 Внутренний баланс: <b>{u.profile.balance}₽</b>\n" \
               f"⏱ До обновления токенов: <b>{u.profile.hours_deff_reset}ч</b>\n" \
               f"ℹ️ Статус: <b>{u.profile.status}</b>"
    

def token_balance_empty_text(u: U | typing.Any) -> str:
    if u.profile.language == "en":
        return f"You have no tokens left!\nTokens will be updated in {u.profile.hours_deff_reset}h.\n" \
               f"You can buy tokens for your internal balance or subscribe for more tokens."
    else:
        return f"У вас не осталось токенов!\nТокены обновятся через {u.profile.hours_deff_reset}ч.\n" \
               f"Вы можете купить токены за внутренний баланс или оформить " \
               f"подписку на большее количество токенов."

    
def get_settings_menu_text(u: U | typing.Any) -> str:
    if u.profile.language == "en":
        return f"⚙️ <b><i>Settings</i></b>\n\n" \
               f"🧬 Model: <b>{u.profile.model}</b>\n" \
               f"🈂️ Language: <b>{u.profile.language}</b>\n"
    else:
        return f"🔐 <b><i>Настройки</i></b>\n\n" \
               f"🧬 Модель: <b>{u.profile.model}</b>\n" \
               f"🈂️ Язык: <b>{u.profile.language}</b>\n"


def get_context_text_info(u: U | typing.Any) -> str:
    context_info, context_cost, n_buffer = "", 0, 1
    t_buffer = "Buffer" if u.profile.language == "en" else "Буфер"
    if not u.profile.context:
        context_info = f"{t_buffer}: <b>0/{u.profile.max_context_buffer}</b>\n-\n"
    else:
        encoding = tiktoken.get_encoding("cl100k_base")
        for n, c in enumerate(u.profile.context):
            if n % 2 == 0:
                context_info += f"{t_buffer}: <b>{n_buffer}/{u.profile.max_context_buffer}</b>\n"
                n_buffer += 1
            context_info += f"{c['role']}: {c['content'][:40]}...\n"
            context_cost += len(encoding.encode(c["content"]))
    if u.profile.language == "en":
        return f"{Answers.En.context_info}\n\n" \
               f"Saved context:\n\n<b>{context_info}</b>\n" \
               f"Total context cost: <b>~{context_cost}</b> token\n" \
               f"Maximum context buffer: <b>{u.profile.max_context_buffer}</b>" 
    else:
        return f"{Answers.Ru.context_info}\n\n" \
               f"Сохраненный контекст:\n\n<b>{context_info}</b>\n" \
               f"Общая стоимость контекста: <b>~{context_cost}</b> токена\n" \
               f"Максимальный буфер контекста: <b>{u.profile.max_context_buffer}</b>"
    

def get_gpt_request_info(u: U | typing.Any) -> str:
    if u.profile.language == "en":
        return f"🧬 Model: <b>{u.profile.model}</b>\n" \
               f"🗃 Context buffer: <b>{int(len(u.profile.context) / 2)}/{u.profile.max_context_buffer}</b>\n\n" \
               f"⏳  Processing request..." 
    else:
        return f"🧬 Модель: <b>{u.profile.model}</b>\n" \
               f"🗃 Буфер контекста: <b>{int(len(u.profile.context) / 2)}/{u.profile.max_context_buffer}</b>\n\n" \
               f"⏳  Обработка запроса..." 
    

def get_confirm_buy_tokens_text(u: U | typing.Any, price: float, tokens: int) -> str:
    if u.profile.language == "en":
        return f"Price: <b>{price}₽</b>\n" \
               f"Confirm the purchase of <b>{tokens}</b> tokens:"
    else:
        return f"Цена: <b>{price}₽</b>\n" \
               f"Подтвердите покупку <b>{tokens}</b> токенов:"


def confirm_buy_tokens_successfully_text(u: U | typing.Any, tokens: int) -> str:
    if u.profile.language == "en":
        return f"Purchase confirmed!\n<b>{tokens}</b> tokens were credited to the account.\n" \
               f"💎 Token balance: <b>{u.profile.tokens}</b>"
    else:
        return f"Покупка подтверждена!\nНа счет зачислено <b>{tokens}</b> токенов.\n" \
               f"💎 Баланс токенов: <b>{u.profile.tokens}</b>"

    