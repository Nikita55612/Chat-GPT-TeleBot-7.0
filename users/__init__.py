from config import Users as cfg
from pydantic import BaseModel
import time
import json
import csv
import os


def save_json(data: dict, filename: str):
    with open(filename, "w", encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


os.mkdir(cfg.dir) if not os.path.exists(cfg.dir) else ...
CACHE = {}


def get_users_list():
    return os.listdir(path=cfg.dir)


class Profile(BaseModel):
    tokens: int
    limit_tokens: int
    balance: float
    status: str
    model: str
    language: str
    registration_dt: float
    last_reset_limit_dt: float
    hours_deff_reset: int
    hours_reset_limit: int
    count_limit_tokens_reset: int
    context: list
    payments: list
    max_context_buffer: int
    last_history_update_dt: float
    load_history_dt: float
    last_payment_verification_dt: float
    last_send_invoice_dt: float


class User:
    def __init__(self, id: int | str) -> None:
        self.id: str = str(id)
        self.profile_path_ = f"{cfg.dir}\\{self.id}\\profile.json"
        self.history_path_ = f"{cfg.dir}\\{self.id}\\history.csv"
        self.profile: Profile = self.__read_profile()
        self.history: list[list] = None


    def get_history(self) -> list[list]:
        with open(self.history_path_, newline="", encoding="utf-8") as f:
            self.history = list(csv.reader(f))[1:]
        return self.history

    def save(self) -> None:
        if self.history:
            with open(self.history_path_, "w", newline="", encoding="utf-8") as f:
                csv.writer(f).writerows([cfg.history_coluns] + self.history)
            self.profile.last_history_update_dt = time.time()
        data = self.profile.dict()
        save_json(data, self.profile_path_)
        CACHE[self.id] = data

    def __init(self) -> dict:
        data, dt_now = cfg.default_user, time.time()
        data["registration_dt"] = dt_now
        data["last_reset_limit_dt"] = dt_now
        data["last_history_update_dt"] = dt_now
        data["load_history_dt"] = 1708436387.160761
        data["last_send_invoice_dt"] = 1708436387.160761
        return data

    def __create(self) -> dict:
        os.makedirs(f"{cfg.dir}//{self.id}", exist_ok=True)
        data = self.__init()
        save_json(data, self.profile_path_)
        with open(self.history_path_, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(cfg.history_coluns)
        return data
        
    def __read_profile(self) -> Profile:
        if data := CACHE.get(self.id):
            return Profile(**data)
        try:
            with open(self.profile_path_, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            data = self.__create()
        CACHE[self.id] = data
        return Profile(**data)
        

def __iter_users():
    for id_ in get_users_list():
        _c = False
        with open(f"{cfg.dir}\\{id_}\\profile.json", "r", encoding="utf-8") as f:
            profile: dict = json.load(f)
        for i in cfg.default_user:
            if not (item := profile.get(i)):
                profile[i] = cfg.default_user[i]
                _c = True
        if _c:
            save_json(profile, f"{cfg.dir}\\{id_}\\profile.json")
__iter_users()