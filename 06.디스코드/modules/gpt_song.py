from openai import OpenAI
from dotenv import load_dotenv
import os
load_dotenv()
OPENAI_KEY = os.getenv("OPENAI_KEY")
client = OpenAI(api_key=OPENAI_KEY)

def get_song_complete(param):
    schema = {
        "type": "object",
        "properties": {
            "songs": {
                "type": "array",
                "description": "데이터 리스트",
                "items": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "노래 제목",
                        },
                        "artist": {
                            "type": "string",
                            "description": "가수명",
                        },
                    }
                }
            }
        }
    }
    description = f"한국 가요 중 {param} 노래 10골의 노래제목과 가수명을 구합니다."
    functions = [
        {
            "name": "get_songs",
            "description": description,
            "parameters": schema
        }
    ]
    completions = client.chat.completions.create(
        model="gpt-3.5-turbo-0613",
        messages=[
            {"role": "system", "content": "You are a helpful assistant"},
        ],
        functions=functions,
        function_call={"name": "get_songs"}
    )
    return completions.choices[0].message.function_call.arguments

if __name__ == "__main__":
    v = get_song_complete("발라드")
    print(v)