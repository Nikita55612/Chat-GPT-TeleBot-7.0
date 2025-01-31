from telebot.types import InlineKeyboardMarkup as tbMarkup, InlineKeyboardButton as tbButton
from config import Bot as cfg
from users import User as U
import typing
import gpt


class Ru:
    CLIENT_MARKUP = tbMarkup().add(
            tbButton("📊 Статистика", callback_data=f"statistics"),
            tbButton("⚙️ Настройки", callback_data="settings"), row_width=2).add(
            tbButton("💎", callback_data="payment"), row_width=1
        )
    STATISTICS_MARKUP = tbMarkup().add(
        tbButton("⬇️ Загрузить историю", callback_data="load_history"),
        tbButton("📈 График расхода токенов", callback_data="statistics_"), row_width=1).add(
        tbButton("⬅️ Назад", callback_data="statistics_back_client"),
        tbButton("🔄 Обновить", callback_data="statistics"), row_width=2)
    
    STATISTICS_MARKUP_ = tbMarkup().add(
        tbButton("⬇️ Загрузить историю", callback_data="load_history"),
        tbButton("📊 Дневная гистограмма запросов", callback_data="statistics"), row_width=1).add(
        tbButton("⬅️ Назад", callback_data="statistics_back_client"),
        tbButton("🔄 Обновить", callback_data="statistics_"), row_width=2)
    
    STAT_BACK_CLIENT_MARKUP = tbMarkup().add(tbButton("⬅️ Назад", callback_data="statistics_back_client"))

    CONTEXT_MARKUP = tbMarkup().add(
        tbButton("🧹 Очистить контекст", callback_data="clear_context_"),
        tbButton("🔂 Макс. буфер контекста", callback_data="context_buffer"),
        tbButton("⬅️ Назад", callback_data="settings"), row_width=2)
    
    PAYMENT_MARKUP = tbMarkup().add(
        tbButton("💰 Пополнить баланс", callback_data="top_up_balance"),
        tbButton("🛒 Купить токены", callback_data="buy_tokens"),
        tbButton("⬅️ Назад", callback_data="client"), row_width=1)
    
    BUY_TOKENS_MARKUP = tbMarkup().add(
        tbButton("10.000", callback_data="buy_tokens=10000"),
        tbButton("20.000", callback_data="buy_tokens=20000"),
        tbButton("50.000", callback_data="buy_tokens=50000"),
        tbButton("100.000", callback_data="buy_tokens=100000"), row_width=1).add(
        tbButton("⬅️ Назад", callback_data="payment"),
        tbButton("🔄 Обновить", callback_data="buy_tokens"), row_width=2)
    
    INSUFFICIENT_FUNDS_MARKUP = tbMarkup().add(
        tbButton("💰 Пополнить баланс", callback_data="top_up_balance"),
        tbButton("❌ Закрыть", callback_data="close"), row_width=1)
    
    CLOSE_MARKUP = tbMarkup().add(tbButton("❌ Закрыть", callback_data="close"), row_width=1)

    CHECK_PAYMENT_BUTTON = tbButton("🔄 Проверить оплату", callback_data="payment_verification")

    BACK_TO_PAYMENT_BUTTON = tbButton("⬅️ Назад", callback_data="payment")


class En:
    CLIENT_MARKUP = tbMarkup().add(
            tbButton("📊 Statistics", callback_data=f"statistics"),
            tbButton("⚙️ Settings", callback_data="settings"), row_width=2).add(
            tbButton("💎", callback_data="payment"), row_width=1
        )
    STATISTICS_MARKUP = tbMarkup().add(
        tbButton("⬇️ Load history", callback_data="load_history"),
        tbButton("📈 Token consumption chart", callback_data="statistics_"), row_width=1).add(
        tbButton("⬅️ Back", callback_data="statistics_back_client"),
        tbButton("🔄 Update", callback_data="statistics"), row_width=2)
    
    STATISTICS_MARKUP_ = tbMarkup().add(
        tbButton("⬇️ Load history", callback_data="load_history"),
        tbButton("📊 Daily request histogram", callback_data="statistics"), row_width=1).add(
        tbButton("⬅️ Back", callback_data="statistics_back_client"),
        tbButton("🔄 Update", callback_data="statistics_"), row_width=2)
    
    STAT_BACK_CLIENT_MARKUP = tbMarkup().add(tbButton("⬅️ Back", callback_data="statistics_back_client"))

    CONTEXT_MARKUP = tbMarkup().add(
        tbButton("🧹 Clear context", callback_data="clear_context_"),
        tbButton("🔂 Max context buffer", callback_data="context_buffer"),
        tbButton("⬅️ Back", callback_data="settings"), row_width=2)
    
    PAYMENT_MARKUP = tbMarkup().add(
        tbButton("💰 Top up balance", callback_data="top_up_balance"),
        tbButton("🛒 Buy tokens", callback_data="buy_tokens"),
        tbButton("⬅️ Back", callback_data="client"), row_width=1)
    
    BUY_TOKENS_MARKUP = tbMarkup().add(
        tbButton("10.000", callback_data="buy_tokens=10000"),
        tbButton("20.000", callback_data="buy_tokens=20000"),
        tbButton("50.000", callback_data="buy_tokens=50000"),
        tbButton("100.000", callback_data="buy_tokens=100000"), row_width=1).add(
        tbButton("⬅️ Back", callback_data="payment"),
        tbButton("🔄 Update", callback_data="buy_tokens"), row_width=2)
    
    INSUFFICIENT_FUNDS_MARKUP = tbMarkup().add(
        tbButton("💰 Top up balance", callback_data="top_up_balance"),
        tbButton("❌ Close", callback_data="close"), row_width=1)
    
    CLOSE_MARKUP = tbMarkup().add(tbButton("❌ Close", callback_data="close"), row_width=1)

    CHECK_PAYMENT_BUTTON = tbButton("🔄 Check payment", callback_data="payment_verification")

    BACK_TO_PAYMENT_BUTTON = tbButton("⬅️ Back", callback_data="payment")


ru = Ru
en = En


def get_change_model_markup(u: U | typing.Any) -> tbMarkup:
    markup = tbMarkup(row_width=1)
    for m in gpt.models.list_:
        markup.add(tbButton(f"✅ {m}" if u.profile.model == m else m, callback_data=f"model={m}"))
    markup.add(tbButton("⬅️ Back" if u.profile.language == "en" else "⬅️ Назад", callback_data="settings"))
    return markup


def get_context_buffer_markup(u: U | typing.Any) -> tbMarkup:
    markup = []
    context_buffer0 = "0 (Off)" if u.profile.language == "en" else "0 (Откл.)"
    markup.append(tbButton(f"✅ {context_buffer0}" if u.profile.max_context_buffer == 0 else context_buffer0, 
                           callback_data=f"context_buffer=0"))
    for i in range(1, 6):
        markup.append(tbButton(f"✅ {i}" if u.profile.max_context_buffer == i else f"{i}", callback_data=f"context_buffer={i}"))
    markup = tbMarkup().add(*markup, row_width=2)
    markup.add(tbButton("⬅️ Back" if u.profile.language == "en" else "⬅️ Назад", callback_data="context"))
    return markup


def get_settings_markup(u: U | typing.Any) -> tbMarkup:
    if u.profile.language == "en":
        return tbMarkup(row_width=1).add(
            tbButton("🧬 Change model", callback_data=f"change_model"),
            tbButton("📝 Context", callback_data="context"),
            tbButton("🇬🇧 en", callback_data=f"language"),
            tbButton("⬅️ Back", callback_data="client")
        )
    else:
        return tbMarkup(row_width=1).add(
            tbButton("🧬 Изменить модель", callback_data=f"change_model"),
            tbButton("📝 Контекст", callback_data="context"),
            tbButton("🇷🇺 ru", callback_data=f"language"),
            tbButton("⬅️ Назад", callback_data="client")
        )
    
def get_top_up_balance_markup(u: U | typing.Any) -> tbMarkup:
    payments_buttons = [tbButton(i, callback_data=f"create_invoice={cfg.PAYMENTS_BUTTONS[i]}") for i in cfg.PAYMENTS_BUTTONS]
    if u.profile.language == "en":
        return tbMarkup(row_width=1).add(
            *payments_buttons, row_width=2).add(En.BACK_TO_PAYMENT_BUTTON, row_width=1)
    else:
        return tbMarkup(row_width=1).add(
            *payments_buttons, row_width=2).add(Ru.BACK_TO_PAYMENT_BUTTON, row_width=1)
    
def get_pay_markup(u: U | typing.Any, url: str, pay: float) -> tbMarkup:
    if u.profile.language == "en":
        return tbMarkup(row_width=1).add(
            tbButton(f"Pay {pay}", url),
            tbButton("🔄 Check payment", callback_data="payment_verification")
        )
    else:
        return tbMarkup(row_width=1).add(
            tbButton(f"Оплатить {pay}", url),
            tbButton("🔄 Проверить оплату", callback_data="payment_verification")
        )
    
def get_try_gpt_request_again_markup(u: U | typing.Any, prompt: str) -> tbMarkup:
    if u.profile.language == "en":
        return tbMarkup().add(tbButton("🔄 Repeat request", callback_data=f"try_gpt_request_again={prompt}"))
    else:
        return tbMarkup().add(tbButton("🔄 Повторить запрос", callback_data=f"try_gpt_request_again={prompt}"))
    
def get_confirm_buy_tokens_markup(u: U | typing.Any, tokens) -> tbMarkup:
    if u.profile.language == "en":
        return tbMarkup().add(
            tbButton("✅ Confirm", callback_data=f"confirm_buy_tokens={tokens}"), 
            tbButton("⛔️ Reject", callback_data="close"), row_width=2)
    else:
        return tbMarkup().add(
            tbButton("✅ Подтвердить", callback_data=f"confirm_buy_tokens={tokens}"), 
            tbButton("⛔️ Отклонить", callback_data="close"), row_width=2)
    





