from dataclasses import dataclass
from openai import OpenAI
import typing
import g4f


g4f.debug.version_check = False


@dataclass(unsafe_hash=True)
class Model:
    model_name: str | typing.Any
    api_name: str
    client_type: str
    client: OpenAI
    base_url: str
    api_key: bool
    source: str


deepseek_chat = Model(
    model_name="deepseek-chat",
    api_name="deepseek",
    client_type="openai",
    client=OpenAI,
    base_url="https://api.deepseek.com/v1",
    api_key=True,
    source="https://platform.deepseek.com/docs"
)

deepseek_coder = Model(
    model_name="deepseek-coder",
    api_name="deepseek",
    client_type="openai",
    client=OpenAI,
    base_url="https://api.deepseek.com/v1",
    api_key=True,
    source="https://github.com/deepseek-ai/DeepSeek-Coder"
)

pai_001_light = Model(
    model_name="pai-001-light",
    api_name="pawan",
    client_type="openai",
    client=OpenAI,
    base_url="https://api.pawan.krd/v1",
    api_key=True,
    source="https://github.com/PawanOsman/ChatGPT"
)

pai_001 = Model(
    model_name="pai-001",
    api_name="pawan",
    client_type="openai",
    client=OpenAI,
    base_url="https://api.pawan.krd/v1",
    api_key=True,
    source="https://github.com/PawanOsman/ChatGPT"
)

g4f_auto = [
    Model(
        model_name=i,
        api_name=f"g4f_{i.name}",
        client_type="g4f",
        client=g4f.ChatCompletion,
        base_url=None,
        api_key=False,
        source="https://github.com/xtekky/gpt4free"
    ) for i in [g4f.models.gpt_35_long, g4f.models.gpt_35_turbo_0613, g4f.models.gpt_35_turbo_16k, 
                g4f.models.gpt_35_turbo_16k_0613, g4f.models.gpt_35_turbo, g4f.models.default]
]

llama2_70b = Model(
    model_name=g4f.models.llama2_70b,
    api_name=f"g4f_llama2_70b",
    client_type="g4f",
    client=g4f.ChatCompletion,
    base_url=None,
    api_key=False,
    source="https://github.com/facebookresearch/llama"
)


list_: list[str] = ["deepseek_chat", "deepseek_coder", "pai_001_light", "pai_001", "g4f_auto", "llama2_70b"]
