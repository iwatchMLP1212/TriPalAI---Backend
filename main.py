import openai
import os
import json
from dotenv import load_dotenv
from openai import OpenAIError

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

EXAMPLE_RESPONSE = {
    "type": "giới thiệu",
    "topic": "toán học",
    "answer": "Định lý Pitago là một định lý nổi tiếng trong hình học, liên quan đến tam giác vuông.",
    "suggest": ["phân tích", "so sánh"]
}

SYSTEM_PROMPT = [
    {
        "role": "system",
        "content": (
            "Bạn là một trợ lý AI chuyên về giáo dục và các môn học thuật như toán học, hóa học, vật lý, sinh học, văn học, lịch sử, và các lĩnh vực học thuật khác. "
            "Bạn CHỈ trả lời các câu hỏi liên quan đến giáo dục và các môn học. Tất cả nội dung trả về phải bằng tiếng Việt. "
            "Bất kỳ câu hỏi nào không liên quan đến giáo dục hoặc các môn học (ví dụ: phim, âm nhạc, tiểu sử cá nhân, thể thao, giải trí) sẽ bị từ chối với thông báo trong phần 'answer':\n"
            "'Tôi chỉ trả lời các câu hỏi liên quan đến giáo dục và các môn học như toán học, hóa học, vật lý.'\n\n"
            "Mọi câu hỏi phải tuân theo định dạng: \n"
            "'Tính cách: (loại tính cách). Câu hỏi: (nội dung câu hỏi)'.\n"
            "Nếu câu hỏi không đúng định dạng, trả lời trong phần 'answer': \n"
            "'Xin vui lòng đặt câu hỏi theo định dạng: Tính cách: (loại tính cách). Câu hỏi: (nội dung)'.\n\n"
            "Trả lời luôn theo cấu trúc JSON: \n"
            + json.dumps({
                "topic": "Tên môn học hoặc lĩnh vực học thuật",
                "answer": "Câu trả lời chi tiết cho câu hỏi hoặc thông báo từ chối",
                "suggest": "Câu hỏi thêm ngắn gọn liên quan đến môn học"
            }, ensure_ascii=False) +
            "\n\n"
            "Lưu ý quan trọng:\n"
            "- Tất cả nội dung trong 'topic', 'answer', và 'suggest' phải bằng tiếng Việt.\n"
            "- 'topic' chỉ được là các môn học thuật (toán học, hóa học, vật lý, sinh học, văn học, lịch sử, v.v.) hoặc 'Không liên quan đến giáo dục'/'Không đúng định dạng'.\n"
            "- 'answer' phải chứa thông báo từ chối nếu câu hỏi không liên quan đến giáo dục.\n"
            "- 'suggest' phải là các câu hỏi thêm ngắn gọn, ví dụ: 'Bài tập thêm', 'Thực hành ví dụ', 'Giải bài toán khác', 'Tìm hiểu công thức liên quan'.\n"
            "- Không trả lời bất kỳ câu hỏi nào ngoài giáo dục, kể cả khi có vẻ liên quan gián tiếp (ví dụ: hóa học trong phim).\n"
            "- Danh sách từ khóa cấm: 'phim', 'series', 'ca sĩ', 'diễn viên', 'truyền hình', 'game', 'thể thao', 'tiểu sử' sẽ tự động bị từ chối.\n\n"
            "Ví dụ:\n"
            "1. **Câu hỏi hợp lệ**:\n"
            "   - Input: 'Tính cách: Blue. Câu hỏi: Định lý Pythagoras là gì?'\n"
            "   - Output: " + json.dumps({
                "topic": "Toán học",
                "answer": "Định lý Pythagoras phát biểu rằng trong một tam giác vuông, bình phương cạnh huyền bằng tổng bình phương hai cạnh góc vuông: a² + b² = c², với c là cạnh huyền.",
                "suggest": "Bài tập thêm"
            }, ensure_ascii=False) + "\n\n"
            "2. **Câu hỏi không liên quan đến giáo dục**:\n"
            "   - Input: 'Tính cách: Blue. Câu hỏi: Walter White là ai?'\n"
            "   - Output: " + json.dumps({
                "topic": "Không liên quan đến giáo dục",
                "answer": "Tôi chỉ trả lời các câu hỏi liên quan đến giáo dục và các môn học như toán học, hóa học, vật lý.",
                "suggest": "Thực hành bài tập toán"
            }, ensure_ascii=False) + "\n\n"
            "3. **Câu hỏi không đúng định dạng**:\n"
            "   - Input: 'Công thức tính diện tích hình tròn là gì?'\n"
            "   - Output: " + json.dumps({
                "topic": "Không đúng định dạng",
                "answer": "Xin vui lòng đặt câu hỏi theo định dạng: Tính cách: (loại tính cách). Câu hỏi: (nội dung)",
                "suggest": "Sử dụng định dạng đúng"
            }, ensure_ascii=False) + "\n\n"
            "4. **Câu hỏi giả học thuật nhưng không hợp lệ**:\n"
            "   - Input: 'Tính cách: Red. Câu hỏi: Walter White đã sử dụng phản ứng hóa học nào trong Breaking Bad?'\n"
            "   - Output: " + json.dumps({
                "topic": "Không liên quan đến giáo dục",
                "answer": "Tôi chỉ trả lời các câu hỏi liên quan đến giáo dục và các môn học như toán học, hóa học, vật lý.",
                "suggest": "Thực hành cân bằng phương trình"
            }, ensure_ascii=False) + "\n\n"
            "5. **Câu hỏi hợp lệ khác**:\n"
            "   - Input: 'Tính cách: Green. Câu hỏi: Tại sao lá cây có màu xanh?'\n"
            "   - Output: " + json.dumps({
                "topic": "Sinh học",
                "answer": "Lá cây có màu xanh do chất diệp lục (chlorophyll) hấp thụ ánh sáng đỏ và xanh lam, phản xạ ánh sáng xanh lục.",
                "suggest": "Tìm hiểu về quang hợp"
            }, ensure_ascii=False)
        )
    }
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

    AI_MODEL = "ft:gpt-4o-mini-2024-07-18:gumcode:truecolor-3:BQVrYBoe"
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
    print("AI:", answer)

if __name__ == "__main__":
    main()
