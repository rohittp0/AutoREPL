import toml


class Config:
    config = None

    def __new__(cls, *args, **kwargs):
        if cls.config is None:
            cls.config = toml.load("config.toml")
        return super().__new__(cls)

    @property
    def openai_api_key(self):
        return self.config["system"]["openai_api_key"]

    @property
    def volume_path(self):
        return self.config["system"]["volume_path"]

    @property
    def ollama_model(self):
        return self.config["system"]["ollama_model"]

    @property
    def openai_model(self):
        return self.config["system"]["openai_model"]
