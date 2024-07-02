from openai import OpenAI
from dotenv import load_dotenv
import os
load_dotenv()
OPENAI_KEY = os.getenv("OPENAI_KEY")
client = OpenAI(api_key=OPENAI_KEY)

def function_call(param):
    functions = [
        {
            "name": "get_country",
            "description": "국가명에 대한 정보를 구합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "country": {
                        "type": "string",
                        "description": "국가명"
                    },
                    "currency": {
                        "type": "string",
                        "description": "화폐단위"
                    },
                    "capital": {
                        "type": "string",
                        "description": "수도"
                    },
                },
                "required": ["country", "currency", "capital"]
            }
        }
    ]
    q = f"{param}에 대한 정보를 구해주세요."
    completions = client.chat.completions.create(
        model="gpt-3.5-turbo-0613",
        messages=[
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": q}
        ],
        functions=functions,
        function_call="auto"
    )
    return completions.choices[0].message.function_call.arguments


def get_chat_complete(prompt):
    completions = client.chat.completions.create(
        model="gpt-3.5-turbo-0613",
        messages=[
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": prompt}
        ]
    )
    return completions.choices[0].message.content

if __name__ == "__main__":
    prompt = '''대한민국 가요중에서 슬픈 발라드 노래를 3곡만 추천해줘.
    노래는 제목과 가수명으로 구성되어 있는데 다음과 같은 형식을 지켜야해
    [
        {
            "song": "노래제목",
            "artist": "가수명"
        }
    ]
    '''
    # v = get_chat_complete(prompt)
    # print(v)
    v = function_call("대한민국")
    print(v)