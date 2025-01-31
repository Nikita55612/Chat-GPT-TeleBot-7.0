from dataclasses import dataclass
from users import Profile as UP
from contextlib import suppress
from config import GPT as cfg
from users import save_json
from . import models
import tiktoken
import random
import typing
import json
import os


def safe_open(filename, mode='r', encoding='utf-8'):
    with suppress(FileNotFoundError):
        return open(filename, mode, encoding=encoding)

def get_models():
    return [getattr(models, i) for i in models.list_ if getattr(models, i, None)]

def get_api_keys():
    with safe_open(cfg.api_keys_path) as f:
        api_keys = json.load(f) if f else {}
    if not api_keys:
        api_keys = {model.api_name: [] for model in get_models() if model.api_key}
        save_json(api_keys, cfg.api_keys_path)
    return api_keys

def get_cache():
    with safe_open(cfg.cache_path) as f:
        cache = json.load(f) if f else {}
    for model in get_models():
        if isinstance(model, list):
            for m_ in model:
                cache.setdefault(m_.api_name, {"requests": 0, "successful": 0})
        else:
            cache.setdefault(model.api_name, {"requests": 0, "successful": 0})
    save_json(cache, cfg.cache_path)
    return cache


CACHE = get_cache()
api_keys = get_api_keys()
encoding = tiktoken.get_encoding("cl100k_base")


def save_cache():
    with open(cfg.cache_path, "w", encoding="utf-8") as f:
        json.dump(CACHE, f, indent=4, ensure_ascii=False)


@dataclass(unsafe_hash=True)
class Response:
    content: str
    prompt: str
    total_tokens: int
    context: list[dict]
    error: str


def request(prompt: str, user_profile: UP, model_: typing.Any = None) -> Response:
    response_ = Response("", prompt, 0, [], None)
    if model_:
        model = model_
    else:
        model: models.Model | list[models.Model] = getattr(models, user_profile.model, None)
        if isinstance(model, list):
            for i in model:
                response = request(prompt, user_profile, i)
                if not response.error:
                    return response
            return response

    CACHE[model.api_name]["requests"] += 1
    messages = user_profile.context
    messages.append({"role": "user", "content": prompt})
    try:
        if model.client_type == "openai":
            client: models.OpenAI = model.client(api_key=random.choice(api_keys[model.api_name]), 
                                                 base_url=model.base_url)
            response = client.chat.completions.create(
                model=model.model_name,
                messages=messages
            )
            response_.content = response.choices[0].message.content
            response_.total_tokens = response.usage.total_tokens
            messages.append({"role": "assistant", "content": response_.content})
            response_.context = messages
        elif model.client_type == "g4f":
            client: models.g4f.ChatCompletion = model.client
            response = client.create(
                model=model.model_name,
                messages=messages,
                stream=False
            )
            response_.content = response
            messages.append({"role": "assistant", "content": response})
            for i in messages:
                response_.total_tokens += len(encoding.encode(i["content"]))
            response_.context = messages
        CACHE[model.api_name]["successful"] += 1
    except Exception as ex:
        try:
            response_.error = ex.__dict__["message"]
        except KeyError:
            response_.error = str(ex)[:220]
    save_cache() if random.random() < 0.05 else ...
    return response_






