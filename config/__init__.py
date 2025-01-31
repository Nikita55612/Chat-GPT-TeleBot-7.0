

class Users:
    dir: str = "users\\data"
    default_user: dict = {
        "tokens": 20000,
        "limit_tokens": 16000,
        "balance": 0,
        "status": "user",
        "model": "deepseek_chat",
        "language": "en",
        "hours_deff_reset": 0,
        "hours_reset_limit": 96,
        "count_limit_tokens_reset": 0,
        "max_context_buffer": 2,
        "context": [],
        "payments": [],
        "load_history_dt": 1708436387.160761,
        "last_history_update_dt": 1708436387.160761,
        "last_payment_verification_dt": 1708436387.160761,
        "last_send_invoice_dt": 1708436387.160761
    }
    history_coluns = [
        "datetime",
        "type",
        "model",
        "request",
        "response",
        "context_buffer",
        "total_tokens",
        "request_method",
        "response_method"
        ]


class Bot:
    token = "5884773644:QQWerma5mmKRksoL7opT_as..."
    YOOMONEY_TOKEN = "4100117625714625.D705916F26D5BF1B597FF3155FB9C481B2744E7170448FB2703E06..."
    my_commands = [
        ("/client", "🔐"),
        ("/models", "🧬"),
        ("/clear_context", "🧹"),
    ]
    commands = ["start", "client", "models", "clear_context", "pay", "cmd"]
    load_history_timeout = 3600
    send_invoice_timeout = 60
    payment_verification_timeout = 45
    users_dir: str = Users.dir
    admins = ["500295076"]
    PAYMENTS_BUTTONS = {"69": 69.99, "139": 139.99, "249": 249.99, "369": 369.99,}
    token_rate_mult = 3.5


class GPT:
    api_keys_path = "gpt\\api_keys.json"
    cache_path = "gpt\\load_cache.json"


class CFG(Users, Bot, GPT):
    pass
