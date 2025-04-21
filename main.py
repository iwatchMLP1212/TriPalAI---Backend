import openai
import os
import json
from dotenv import load_dotenv
from openai import OpenAIError

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

EXAMPLE_RESPONSE = {
    "type": "giới thiệu",
    "topic": "văn hóa",
    "answer": "Nikola Tesla là một nhà phát minh và kỹ sư điện nổi tiếng với các đóng góp trong lĩnh vực điện năng.",
    "suggest": ["phân tích", "so sánh"]
}

SYSTEM_PROMPT = [
    {"role": "system", "content": f"Hãy trả lời câu hỏi theo định dạng JSON này: {json.dumps(EXAMPLE_RESPONSE, ensure_ascii=False)}. Lưu ý: nên đa dạng hoá và tăng sự sáng tạo trong gợi ý."}
]

message_list = SYSTEM_PROMPT.copy()

TOOL = [
    {
        "type": "function",
        "function": {
            "name": "generate_response",
            "description": "Tạo câu trả lời theo định dạng JSON cố định.",
            "parameters": {
                "type": "object",
                "properties": {
                    "type": {"type": "string", "enum": ["giới thiệu", "phân tích", "so sánh"]},
                    "topic": {"type": "string"},
                    "answer": {"type": "string"},
                    "suggest": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                },
                "required": ["type", "topic", "answer", "suggest"]
            }
        }
    }
]

TOOL_CHOICE = {"type": "function", "function": {"name": "generate_response"}}

def validate_response(response):
    """Validates JSON response."""
    required_fields = ["type", "topic", "answer", "suggest"]
    
    if not isinstance(response, dict):
        return {"error": "Response is not a valid JSON object."}
    
    for field in required_fields:
        if field not in response:
            return {"error": f"Missing required field: {field}"}
    
    if not isinstance(response["type"], str):
        return {"error": "Invalid 'type' value."}
    
    if not isinstance(response["topic"], str):
        return {"error": "Invalid 'topic' value."}
    
    if not isinstance(response["answer"], str):
        return {"error": "Invalid 'answer' value."}
    
    if not isinstance(response["suggest"], list) or not all(isinstance(item, str) for item in response["suggest"]):
        return {"error": "Invalid 'suggest' value. It should be a list of strings."}
    
    return response

def get_answer(message):
    global message_list

    AI_MODEL = "gpt-4o-mini"
    MAX_TOKENS = 800

    try:
        if len(message_list) > 5:
            message_list = SYSTEM_PROMPT + message_list[-4:]

        message_list.append({"role": "user", "content": message})

        response = openai.chat.completions.create(
            model=AI_MODEL,
            messages=message_list,
            max_tokens=MAX_TOKENS,
            tools=TOOL,
            tool_choice=TOOL_CHOICE,
        )

        if response.choices[0].message.tool_calls:
            tool_response = response.choices[0].message.tool_calls[0].function.arguments
            ai_reply = json.loads(tool_response)
        else:
            return {"error": "AI không gọi tool."}

        validated_reply = validate_response(ai_reply)

        if "error" in validated_reply:
            return validated_reply

        message_list.append({"role": "assistant", "content": json.dumps(validated_reply, ensure_ascii=False)})

        print("responses:", json.dumps(message_list, ensure_ascii=False, indent=2))

        return validated_reply

    except OpenAIError as e:
        return {"error": f"API Error: {str(e)}"}


# Giao diện CLI đơn giản
def main():
    while True:
        message = input("You: ")
        if message.lower() == "quit":
            break
        answer = get_answer(message)

if __name__ == "__main__":
    main()
