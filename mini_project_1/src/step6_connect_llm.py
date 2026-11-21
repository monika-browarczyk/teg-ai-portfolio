"""KROK 6: Podłącz swój LLM

CEL
    Sprawdź połączenie z dużym modelem językowym (ang. large language model, LLM): zbuduj model czatu dla wybranego
    dostawcy, wyślij mu jedną wiadomość (ang. prompt) i zobacz odpowiedź oraz liczbę zużytych tokenów.

    Dostawcę ustawiasz w config.yaml (llm.provider i llm.model):
        openai       bezpośrednio API OpenAI (zalecane)          klucz: OPENAI_API_KEY
        openrouter   jedno API do modeli wielu dostawców        klucz: OPENROUTER_API_KEY
        ollama       model uruchomiony na twoim komputerze      bez klucza i bez opłat
    Kod musi obsługiwać wszystkie trzy; zalecamy openai / gpt-5.4-mini.
    Jak skonfigurować każdego z nich: „Podłącz swój LLM” w mini_project_1/README.md.

WYNIK
    build_llm(config) zwraca model czatu z LangChain:

        llm = build_llm(config)
        llm.invoke("Przywitaj się po angielsku.").content    -> 'Hello!'

    measure_call(llm, prompt) wysyła jeden prompt i zwraca odpowiedź i informacje o zużyciu tokenów:

        measure_call(llm, "Wymień trzy stolice państw UE.")
        -> {"answer": "Berlin, Paryż i Madryt.", "input_tokens": 16, "output_tokens": 9}

WYMAGANIA (sprawdzają je testy)
    build_llm(config):
    - Dostawca, model i temperatura pochodzą z config.get("llm.provider"),
      config.get("llm.model") i config.get("llm.temperature").
    - "openai": model czatu OpenAI z kluczem odczytanym ze zmiennej środowiskowej
      o nazwie podanej w config.get("llm.api_key_env")["openai"].
    - "openrouter": ta sama klasa modelu czatu OpenAI (OpenRouter udostępnia interfejs zgodny
      z API OpenAI), skierowana na config.get("llm.base_urls")["openrouter"], z kluczem
      ze zmiennej o nazwie podanej w config.get("llm.api_key_env")["openrouter"].
    - "ollama": model czatu Ollama pod adresem config.get("llm.base_urls")["ollama"],
      bez klucza.
    - Brak klucza zgłasza MissingConfigError (z helpers.config), a komunikat podaje
      nazwę zmiennej do ustawienia. Każdy inny dostawca zgłasza ConfigError, a komunikat
      wymienia trzech dozwolonych.
    measure_call(llm, prompt):
    - Wysyła `prompt` jako jedną wiadomość i zwraca słownik z "answer" (tekst
      odpowiedzi) oraz "input_tokens" / "output_tokens" policzonymi przez dostawcę.
    - Jeśli odpowiedź nie zawiera liczby tokenów, zgłoś ValueError. Nigdy jej nie zgaduj.

ZALECANE NARZĘDZIA
    init_chat_model z LangChain (jedna funkcja dla wszystkich trzech dostawców)
    i usage_metadata odpowiedzi. Przykłady: „Przybornik” w mini_project_1/README.md.

NA KONIEC SPRAWDŹ KOD POLECENIEM
    uv run pytest mini_project_1/tests/test_step6_connect_llm.py -v
    uv run python mini_project_1/src/first_llm_call.py     (jedno prawdziwe wywołanie: znacznie poniżej centa, w Ollamie za darmo)
"""

import os

from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel

from helpers.config import Config, ConfigError, MissingConfigError


def build_llm(config: Config) -> BaseChatModel:
    provider = config.get("llm.provider")
    supported_providers = ("openai", "openrouter", "ollama")
    if provider not in supported_providers:
        raise ConfigError(f"Dozwoleni dostawcy LLM: {', '.join(supported_providers)}")

    model_name = config.get("llm.model")
    temperature = config.get("llm.temperature")
    if provider == "ollama":
        return init_chat_model(
            model_name,
            model_provider="ollama",
            temperature=temperature,
            base_url=config.get("llm.base_urls")["ollama"],
        )

    key_variable = config.get("llm.api_key_env")[provider]
    api_key = os.environ.get(key_variable)
    if not api_key:
        raise MissingConfigError(
            f"Zmienna {key_variable} nie jest ustawiona. Dodaj ją do .env."
        )

    base_url = (
        config.get("llm.base_urls")["openrouter"] if provider == "openrouter" else None
    )
    return init_chat_model(
        model_name,
        model_provider="openai",
        temperature=temperature,
        api_key=api_key,
        base_url=base_url,
    )


def measure_call(llm: BaseChatModel, prompt: str) -> dict:
    response = llm.invoke(prompt)
    usage = response.usage_metadata
    if usage is None or any(
        usage.get(key) is None for key in ("input_tokens", "output_tokens")
    ):
        raise ValueError(
            "Odpowiedź modelu nie zawiera liczby tokenów wejściowych i wyjściowych"
        )

    return {
        "answer": response.text,
        "input_tokens": usage["input_tokens"],
        "output_tokens": usage["output_tokens"],
    }
