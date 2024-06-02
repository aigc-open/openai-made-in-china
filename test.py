from utils.spark import SparkAPI
from utils import ChatInput

if __name__ == '__main__':
    api = SparkAPI(api_key="98a775df5f2809c07adae80aed1e1e66",
                   api_secret="Y2E1YmIxZWY3YTlkM2JhOGRhMGYxOTE0",
                   app_id="0afaac40--")
    input_ = ChatInput(model="Spark Lite",
                       messages=[{"role": "user", "content": "你好,你是谁呢"}],
                       stream=False)
    res = api.chat(chat_input=input_)
    if input_.stream:
        for i in res:
            print(i)
    else:
        print(res)
