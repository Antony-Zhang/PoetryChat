import os
import queue

from src.presets import OPENAI_API_BASE, CHAT_COMPLETION_URL, BALANCE_API_URL, USAGE_API_URL, API_HOST, IMAGES_COMPLETION_URL


class State:
    interrupted = False
    multi_api_key = False
    chat_completion_url = CHAT_COMPLETION_URL
    balance_api_url = BALANCE_API_URL
    usage_api_url = USAGE_API_URL
    openai_api_base = OPENAI_API_BASE
    images_completion_url = IMAGES_COMPLETION_URL

    def interrupt(self):
        self.interrupted = True

    def recover(self):
        self.interrupted = False

    def set_api_host(self, api_host: str):
        api_host = api_host.rstrip("/")
        if not api_host.startswith("http"):
            api_host = f"https://{api_host}"
        if api_host.endswith("/v1"):
            api_host = api_host[:-3]
        self.chat_completion_url = f"{api_host}/v1/chat/completions"
        self.images_completion_url = f"{api_host}/v1/images/generations"
        self.openai_api_base = f"{api_host}/v1"
        self.balance_api_url = f"{api_host}/dashboard/billing/credit_grants"
        self.usage_api_url = f"{api_host}/dashboard/billing/usage"

    def reset_api_host(self):
        self.chat_completion_url = CHAT_COMPLETION_URL
        self.images_completion_url = IMAGES_COMPLETION_URL
        self.balance_api_url = BALANCE_API_URL
        self.usage_api_url = USAGE_API_URL
        return API_HOST

    def reset_all(self):
        self.interrupted = False
        self.chat_completion_url = CHAT_COMPLETION_URL

    def set_api_key_queue(self, api_key_list):
        self.multi_api_key = True
        self.api_key_queue = queue.Queue()
        for api_key in api_key_list:
            self.api_key_queue.put(api_key)

    def switching_api_key(self, func):
        if not hasattr(self, "api_key_queue"):
            return func

        def wrapped(*args, **kwargs):
            api_key = self.api_key_queue.get()
            args[0].api_key = api_key
            ret = func(*args, **kwargs)
            self.api_key_queue.put(api_key)
            return ret

        return wrapped


state = State()
