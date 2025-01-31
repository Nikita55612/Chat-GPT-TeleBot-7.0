from users import User, get_users_list
from . import content, markups, utils
from datetime import datetime as dt
from config import Bot as cfg
import yoomoney as ym
import telebot
import time
import gpt


bot = telebot.TeleBot(cfg.token)
bot.set_my_commands([telebot.types.BotCommand(*i) for i in cfg.my_commands])
ym_client = ym.Client(cfg.YOOMONEY_TOKEN)
ym_receiver = ym_client.account_info().account
CACHE = {}


def get_ym_receipt_url(sum: float, label: str) -> str:
    return ym.Quickpay(receiver=ym_receiver, quickpay_form="shop", targets="Sponsor this project", 
                       paymentType="SB", sum=sum, label=label).base_url


class TUser(User):
    def __init__(self, id, chat_id, name=None) -> None:
        self.chat_id = chat_id
        self.name = name
        super().__init__(id)

    def update_hours_deff_reset(self) -> None:
        prev_hours_deff_reset = self.profile.hours_deff_reset
        dt_now = time.time()
        deff_time = dt_now - self.profile.last_reset_limit_dt
        hour = max([round((self.profile.hours_reset_limit) - (deff_time / 3600)), 0])
        self.profile.hours_deff_reset = hour
        if hour == 0 and self.profile.tokens < self.profile.limit_tokens:
            self.profile.tokens = self.profile.limit_tokens
            self.profile.last_reset_limit_dt = dt_now
            self.profile.count_limit_tokens_reset += 1
        self.save() if prev_hours_deff_reset != self.profile.hours_deff_reset else ...

    def clear_context_and_save(self) -> None:
        self.profile.context.clear()
        self.save()

    def get_client_menu_text(self) -> str:
        return content.get_client_menu_text(self)

    def get_change_model_markup(self):
        return markups.get_change_model_markup(self)
    
    def get_settings_menu_text(self) -> str:
        return content.get_settings_menu_text(self)
    
    def get_settings_markup(self):
        return markups.get_settings_markup(self)
    
    def get_statistics(self) -> tuple | None:
        return utils.get_statistics(self)
    
    def get_context_buffer_markup(self):
        return markups.get_context_buffer_markup(self)
    
    def get_try_gpt_request_again_markup(self, prompt: str):
        return markups.get_try_gpt_request_again_markup(self, prompt)
    
    def get_context_text_info(self) -> str:
        return content.get_context_text_info(self)
    
    def get_gpt_request_info(self) -> str:
        return content.get_gpt_request_info(self)
    
    def token_balance_empty_text(self) -> str:
        return content.token_balance_empty_text(self)

    def voice_to_text(self) -> str:
        return utils.voice_to_text(self)
    
    def get_payment_menu_text(self) -> str:
        return content.get_payment_menu_text(self)
    
    def token_rate_text(self, n: int = 1000) -> str:
        return utils.token_rate_text(self, n)
    
    def get_confirm_buy_tokens_text(self, price: float, tokens: int) -> str:
        return content.get_confirm_buy_tokens_text(self, price, tokens)
    
    def get_confirm_buy_tokens_markup(self, tokens):
        return markups.get_confirm_buy_tokens_markup(self, tokens)
    
    def confirm_buy_tokens_successfully_text(self, tokens) -> str:
        return content.confirm_buy_tokens_successfully_text(self, tokens)
    
    def get_pay_markup(self, url: str, pay: float):
        return markups.get_pay_markup(self, url, pay)
    
    def get_top_up_balance_markup(self):
        return markups.get_top_up_balance_markup(self)
    
    def apply_gpt_response(self, gpt_response: gpt.Response, request_method: str, response_method: str) -> None:
        if time.time() - self.profile.last_history_update_dt > 600:
            self.update_hours_deff_reset()
        self.profile.tokens -= gpt_response.total_tokens
        if self.profile.max_context_buffer == 0:
            self.profile.context.clear() if self.profile.context else ...
        else:
            self.profile.context = gpt_response.context[-self.profile.max_context_buffer*2:]
        self.get_history()
        self.history.append(
            [
                dt.now(), 
                "gpt", 
                self.profile.model, 
                gpt_response.prompt,
                gpt_response.content, 
                len(self.profile.context) - 1,
                gpt_response.total_tokens,
                request_method, 
                response_method
            ]
        )
        self.save()
        

@bot.message_handler(commands=cfg.commands)
def commands_processing(m):
    u = TUser(m.from_user.id, m.chat.id, m.from_user.username)
    respondent: content.Answers.En = getattr(content.Answers, u.profile.language)

    if m.text == "/start":
        bot.send_message(u.chat_id, respondent.start_answer0)
    elif m.text == "/client":
        u.update_hours_deff_reset()
        bot.send_message(u.chat_id, u.get_client_menu_text(), "HTML",
                         reply_markup=getattr(markups, u.profile.language).CLIENT_MARKUP)
    elif m.text == "/clear_context":
        if u.profile.context:
            u.clear_context_and_save()
            bot.send_message(u.chat_id, respondent.clear_context_answer0)
        else:
            bot.send_message(u.chat_id, respondent.clear_context_answer1)
    elif m.text == "/models":
        bot.send_message(u.chat_id, respondent.models, "HTML",
                         reply_markup=u.get_change_model_markup(), 
                         disable_web_page_preview=True)
    elif m.text.startswith("/pay"):
        try:
            pay =  float(m.text.replace("/pay", "").strip())
        except ValueError:
            pay = 0
        if pay > 0:
            dt_now = time.time()
            deff_time_ = round(dt_now - u.profile.last_send_invoice_dt, 2)
            if deff_time_ > cfg.send_invoice_timeout:
                bot.send_message(u.chat_id, respondent.invoice, 
                                reply_markup=u.get_pay_markup(get_ym_receipt_url(pay, f"v2_{len(u.profile.payments)}_{u.id}"), pay))
                u.profile.last_send_invoice_dt = dt_now
                u.save()
            else:
                bot.send_message(u.chat_id, f"{respondent.send_invoice_timeout} {cfg.send_invoice_timeout - deff_time_}s")
        else:
            bot.send_message(u.chat_id, respondent.pay_except)
    elif m.text.startswith("/cmd"):
        if u.id not in cfg.admins:
            return
        def send_oll(message_):
            for u_id in get_users_list():
                try:
                    bot.send_message(int(u_id), message_, parse_mode="HTML")
                except telebot.apihelper.ApiTelegramException:
                    pass
            return "send_oll"
        
        try_eval =  m.text.replace("/cmd", "").strip()
        try:
            try_eval = eval(try_eval, {"bot": bot, "send_oll": send_oll,})
            try:
                bot.send_message(u.chat_id, f"Вывод консоли: {try_eval}")
            except telebot.apihelper.ApiTelegramException:
                with open(f"{cfg.users_dir}//{u.id}//send_document.txt", "w", encoding="utf-8") as f:
                    f.write(f"{try_eval}")
                with open(f"{cfg.users_dir}//{u.id}//send_document.txt", "r", encoding="utf-8") as f:
                    bot.send_document(u.chat_id, f)
                
        except Exception as ex:
            bot.send_message(u.chat_id, f"Вывод консоли: {ex}")
        

@bot.callback_query_handler(func=lambda call: True)
def callback(c):
    u = TUser(c.from_user.id, c.message.chat.id, c.from_user.username)
    respondent: content.Answers.En = getattr(content.Answers, u.profile.language)

    if c.data == "client":
        bot.edit_message_text(u.get_client_menu_text(), u.chat_id, c.message.message_id,
                              reply_markup=getattr(markups, u.profile.language).CLIENT_MARKUP, parse_mode="HTML")
    elif c.data == "language":
        u.profile.language = "ru" if u.profile.language == "en" else "en"
        u.save()
        bot.edit_message_text(u.get_settings_menu_text(), u.chat_id, c.message.message_id,
                              reply_markup=u.get_settings_markup(), 
                              parse_mode="HTML")
    elif c.data == "settings":
        bot.edit_message_text(u.get_settings_menu_text(), u.chat_id, c.message.message_id,
                              reply_markup=u.get_settings_markup(), 
                              parse_mode="HTML")
    elif c.data == "change_model":
        bot.edit_message_text(respondent.models, u.chat_id, c.message.message_id,
                              reply_markup=u.get_change_model_markup(), 
                              parse_mode="HTML", disable_web_page_preview=True)
    elif c.data == "close":
        bot.delete_message(u.chat_id, c.message.message_id)
    elif c.data == "statistics":
        stat = u.get_statistics()
        bot.delete_message(u.chat_id, c.message.message_id)
        if stat:
            with open(stat[1], "rb") as f:
                bot.send_photo(u.chat_id, f, stat[0], 
                               reply_markup=getattr(markups, u.profile.language).STATISTICS_MARKUP, parse_mode="HTML")
        else:
            bot.send_message(u.chat_id, respondent.stat_not_enough_data, 
                             reply_markup=getattr(markups, u.profile.language).STAT_BACK_CLIENT_MARKUP)
    elif c.data == "statistics_":
        stat = u.get_statistics()
        bot.delete_message(u.chat_id, c.message.message_id)
        with open(stat[2], "rb") as f:
            bot.send_photo(u.chat_id, f, stat[0], 
                           reply_markup=getattr(markups, u.profile.language).STATISTICS_MARKUP_, parse_mode="HTML")
    elif c.data == "statistics_back_client":
        bot.delete_message(u.chat_id, c.message.message_id)
        bot.send_message(u.chat_id, u.get_client_menu_text(), "HTML",
                         reply_markup=getattr(markups, u.profile.language).CLIENT_MARKUP)
    elif c.data == "load_history":
        deff_time_ = round(time.time() - u.profile.load_history_dt, 1)
        if deff_time_ > cfg.load_history_timeout:
            with open(f"{cfg.users_dir}//{u.id}//history.csv", "rb") as f:
                bot.send_document(u.chat_id, f)
            u.profile.load_history_dt = time.time()
            u.save()
        else:
            bot.send_message(u.chat_id, f"{respondent.load_history_timeout} {cfg.load_history_timeout - deff_time_}s!")
    elif c.data == "context":
        bot.edit_message_text(u.get_context_text_info(), u.chat_id, c.message.message_id,
                              reply_markup=getattr(markups, u.profile.language).CONTEXT_MARKUP, 
                              parse_mode="HTML")
    elif c.data == "context_buffer":
        bot.edit_message_text(u.get_context_text_info() + respondent.context_buffer_info, 
                              u.chat_id, c.message.message_id,
                              reply_markup=u.get_context_buffer_markup(), 
                              parse_mode="HTML")
    elif c.data == "payment":
        bot.edit_message_text(u.get_payment_menu_text(), 
                              u.chat_id, c.message.message_id,
                              reply_markup=getattr(markups, u.profile.language).PAYMENT_MARKUP, 
                              parse_mode="HTML")
    elif c.data == "buy_tokens":
        bot.edit_message_text(u.token_rate_text(), 
                              u.chat_id, c.message.message_id,
                              reply_markup=getattr(markups, u.profile.language).BUY_TOKENS_MARKUP, 
                              parse_mode="HTML")
    elif c.data == "top_up_balance":
        bot.edit_message_text(f"{u.get_payment_menu_text()}\n\n{respondent.top_up_balance_info}", 
                              u.chat_id, c.message.message_id,
                              reply_markup=u.get_top_up_balance_markup(), 
                              parse_mode="HTML")
    elif c.data == "clear_context":
        if u.profile.context:
            u.clear_context_and_save()
            bot.send_message(u.chat_id, respondent.clear_context_answer0)
        else:
            bot.send_message(u.chat_id, respondent.clear_context_answer1)
    elif c.data == "payment_verification":
        dt_now = time.time()
        deff_time_ = round(dt_now - u.profile.last_reset_limit_dt, 2)
        if deff_time_ >= cfg.payment_verification_timeout:
            operations = {i.label: i.amount for i in ym_client.operation_history().operations if i.label}
            operation_key = f"v2_{len(u.profile.payments)}_{u.id}"
            if operation_key in operations:
                amount = float(operations[operation_key])
                u.profile.balance += amount
                u.profile.payments.append(f"{operation_key}=={amount}")
            else:
                u.profile.last_reset_limit_dt = dt_now
                bot.send_message(u.chat_id, respondent.payment_failed_verification,
                                 reply_markup=getattr(markups, u.profile.language).CLOSE_MARKUP)
            u.save()
        else:
            bot.send_message(u.chat_id, f"{respondent.payment_verification_timeout} {cfg.payment_verification_timeout - deff_time_}s")
    elif c.data.startswith("clear_context_"):
        if u.profile.context:
            u.clear_context_and_save()
            bot.edit_message_text(u.get_context_text_info(), u.chat_id, c.message.message_id,
                                    reply_markup=getattr(markups, u.profile.language).CONTEXT_MARKUP, 
                                    parse_mode="HTML")
    elif c.data.startswith("try_gpt_request_again="):
        prompt = c.data.replace("try_gpt_request_again=", "")
        bot.delete_message(u.chat_id, c.message.message_id)
        info_message_id = bot.send_message(u.chat_id, u.get_gpt_request_info(), parse_mode="HTML").message_id
        response: gpt.Response = gpt.request(prompt, u.profile)
        if response.error:
            bot.edit_message_text(response.error, u.chat_id, info_message_id,
                                  reply_markup=u.get_try_gpt_request_again_markup(prompt))
            return
        u.apply_gpt_response(response, "text", "text")
        bot.edit_message_text(response.content, u.chat_id, info_message_id)
    elif c.data.startswith("create_invoice="):
        pay = float(c.data.replace("create_invoice=", ""))
        dt_now = time.time()
        deff_time_ = round(dt_now - u.profile.last_send_invoice_dt, 2)
        if deff_time_ > cfg.send_invoice_timeout:
            bot.send_message(u.chat_id, respondent.invoice, 
                            reply_markup=u.get_pay_markup(get_ym_receipt_url(pay, f"v2_{len(u.profile.payments)}_{u.id}"), pay))
            u.profile.last_send_invoice_dt = dt_now
            u.save()
        else:
            bot.send_message(u.chat_id, f"{respondent.send_invoice_timeout} {cfg.send_invoice_timeout - deff_time_}s")
    elif c.data.startswith("model="):
        model = c.data.replace("model=", "")
        if model != u.profile.model:
            u.profile.model = model
            u.save()
            bot.edit_message_text(respondent.models, u.chat_id, c.message.message_id,
                                  reply_markup=u.get_change_model_markup(), 
                                  parse_mode="HTML",
                                  disable_web_page_preview=True)
    elif c.data.startswith("context_buffer="):
        context_buffer = int(c.data.replace("context_buffer=", ""))
        if context_buffer != u.profile.max_context_buffer:
            u.profile.max_context_buffer = context_buffer
            u.save()
            bot.edit_message_text(u.get_context_text_info() + respondent.context_buffer_info,
                                  u.chat_id, c.message.message_id,
                                  reply_markup=u.get_context_buffer_markup(), 
                                  parse_mode="HTML")
    elif c.data.startswith("buy_tokens="):
        tokens = int(c.data.replace("buy_tokens=", ""))
        price = utils.tokens_to_rub(tokens)
        if u.profile.balance >= price:
            bot.send_message(u.chat_id, u.get_confirm_buy_tokens_text(price, tokens), 
                             reply_markup=u.get_confirm_buy_tokens_markup(tokens), 
                             parse_mode="HTML")
        else:
            bot.send_message(u.chat_id, respondent.insufficient_funds, 
                             reply_markup=getattr(markups, u.profile.language).INSUFFICIENT_FUNDS_MARKUP)
    elif c.data.startswith("confirm_buy_tokens="):
        tokens = int(c.data.replace("confirm_buy_tokens=", ""))
        price = utils.tokens_to_rub(tokens)
        u.profile.balance = round(u.profile.balance - price, 2)
        u.profile.tokens += tokens
        u.save()
        bot.edit_message_text(u.confirm_buy_tokens_successfully_text(tokens),
                              u.chat_id, c.message.message_id,
                              reply_markup=getattr(markups, u.profile.language).CLOSE_MARKUP, 
                              parse_mode="HTML")
            


@bot.message_handler(content_types=["text", "voice"])
def text_processing(m):
    u = TUser(m.from_user.id, m.chat.id)

    if u.profile.tokens <= 0:
        bot.send_message(u.chat_id, u.token_balance_empty_text(), parse_mode="HTML")
        return
    info_message_id = bot.send_message(u.chat_id, u.get_gpt_request_info(), parse_mode="HTML").message_id
    prompt = m.text
    if m.content_type == "voice":
        with open(f"{cfg.users_dir}//{u.id}//voice_request.ogg", 'wb') as f:
            f.write(bot.download_file(bot.get_file(m.voice.file_id).file_path))
        prompt = u.voice_to_text()
    response: gpt.Response = gpt.request(prompt, u.profile)
    if response.error:
        bot.edit_message_text(response.error, u.chat_id, info_message_id,
                              reply_markup=u.get_try_gpt_request_again_markup(response.prompt))
        return
    u.apply_gpt_response(response, m.content_type, "text")
    bot.edit_message_text(response.content[:4096], u.chat_id, info_message_id)
    if (len_content := len(response.content)) > 4096:
        for n_ in range(1, round(len_content / 4096) + 1):
            bot.send_message(u.chat_id, response.content[4096 * n_:4096 * (n_ + 1)])


@bot.message_handler(content_types=["document"])
def voice_processing(m):
    u = TUser(m.from_user.id, m.chat.id)

