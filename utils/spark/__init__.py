import json
import time
from enum import Enum
import requests
import base64
import hmac
import hashlib
from datetime import datetime
from loguru import logger
from pydantic import BaseModel
from urllib.parse import urlparse
from sparkai.llm.llm import ChatSparkLLM, ChunkPrintHandler
from sparkai.core.messages import ChatMessage
from utils import ChatInput


class XunFeiModelEnum(Enum):
    Spark35_Max = "Spark3.5 Max"
    Spark_Pro = "Spark Pro"
    Spark_Lite = "Spark Lite"


class ModelConfig(BaseModel):
    url: str
    domain: str


model_api_url_mapping = {
    "Spark3.5 Max": ModelConfig(url="wss://spark-api.xf-yun.com/v3.5/chat", domain="generalv3.5"),
    "Spark Pro": ModelConfig(url="wss://spark-api.xf-yun.com/v3.1/chat", domain="generalv3"),
    "Spark Lite": ModelConfig(url="wss://spark-api.xf-yun.com/v1.1/chat", domain="general"),
}


class SparkAPI:
    def __init__(self, api_key, api_secret, app_id):
        self.api_key = api_key
        self.app_id = app_id
        self.api_secret = api_secret

    def set_api(self, api_url):
        self.api_url = api_url
        self.host = urlparse(api_url).netloc
        self.path = urlparse(api_url).path

    def generate_signature(self, request_line, date):
        signature_origin = f"host: {self.host}\ndate: {date}\n{request_line}"
        signature_sha = hmac.new(self.api_secret.encode(
        ), signature_origin.encode(), hashlib.sha256).digest()
        signature = base64.b64encode(signature_sha).decode()
        authorization_origin = f"api_key=\"{self.api_key}\", algorithm=\"hmac-sha256\", headers=\"host date request-line\", signature=\"{signature}\""
        return base64.b64encode(authorization_origin.encode()).decode()

    def create_url(self, method='GET'):
        date = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
        request_line = f"{method} {self.path} HTTP/1.1"
        authorization = self.generate_signature(request_line, date)
        return self.api_url + f"?host={self.host}&date={date}&authorization={authorization}"

    def stream_(self, response):
        for message in response:
            yield message
        return 

    def chat(self, chat_input: ChatInput):
        model_config: ModelConfig = model_api_url_mapping[chat_input.model]
        self.set_api(api_url=model_config.url)

        spark = ChatSparkLLM(
            spark_api_url=self.api_url,
            spark_app_id=self.app_id,
            spark_api_key=self.api_key,
            spark_api_secret=self.api_secret,
            spark_llm_domain=model_config.domain,
            streaming=True,
        )
        messages = [ChatMessage(**data.dict()) for data in chat_input.messages]
        if chat_input.stream:
            response = spark.stream(messages)
            return self.stream_(response)
        else:
            response = spark.generate([messages])
            return response
