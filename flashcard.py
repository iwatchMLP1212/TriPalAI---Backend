import os
import json
from datetime import datetime
from dotenv import load_dotenv
import openai
import psycopg2
from psycopg2.extras import execute_values

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

DB_CONFIG = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", 5432),
}

def generate_flashcards_from_chat(chat_transcript: str, user_email: str):
    prompt = f"""
    Bạn là một công cụ học tập. Hãy thực hiện ba nhiệm vụ:

    1. Tóm tắt nội dung chính của đoạn hội thoại sau thành một đoạn văn ngắn, súc tích.
    2. Chuyển nội dung đoạn hội thoại đã tóm tắt thành các flashcard dạng câu hỏi - đáp hoặc khái niệm - định nghĩa, theo cấu trúc JSON như sau:

    [
      {{
        "front": "Nội dung phía trước flashcard (ví dụ: câu hỏi, khái niệm)",
        "back": "Nội dung phía sau flashcard (ví dụ: câu trả lời, định nghĩa)"
      }}
    ]

    3. Tạo ra một tiêu đề (title) ngắn gọn và mô tả (description) cho bộ flashcard này. 
       Tiêu đề phải phản ánh nội dung chính của bộ flashcard, và mô tả phải cung cấp thông tin ngắn gọn về mục đích của bộ flashcard.

    Đây là đoạn hội thoại:
    <<<
    {chat_transcript}
    >>>

    Trả về kết quả dưới dạng một đối tượng JSON:
    {{
      "flashcards": [ ... ],
      "title": "Tiêu đề của bộ flashcard",
      "description": "Mô tả về bộ flashcard"
    }}

    Lưu ý: chỉ trả về JSON có phần flashcards, title và description, không cần thêm bất kỳ văn bản nào khác. Nếu không thể tạo flashcard từ đoạn hội thoại, hãy trả về một thông báo rõ ràng trong JSON với key: "error".
    """

    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        content = response.choices[0].message.content
        parsed = json.loads(content)

        if "flashcards" in parsed:
            flashcard_set_id = create_flashcard_set(user_email, parsed["flashcards"], parsed["title"], parsed["description"])
            save_flashcards_to_db(parsed["flashcards"], flashcard_set_id, user_email)
            return {
                "flashcards": parsed["flashcards"],
                "title": parsed["title"],
                "description": parsed["description"]
            }
        return parsed
    except Exception as e:
        return {"error": str(e)}

def create_flashcard_set(user_email: str, flashcards=None, title=None, description=None):
    try:
        flashcards = flashcards or []
        title = title or "Flashcard mới"
        description = description or "Bộ flashcard được tạo ra từ đoạn chat"
        flashcards_count = len(flashcards)
        is_completed = False
        last_studied = datetime.utcnow()

        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO flashcard_sets (
                title, description, user_email,
                is_completed, last_studied, created_at, flashcards_count
            ) 
            VALUES (%s, %s, %s, %s, %s, %s, %s) 
            RETURNING id;
        """, (
            title, description, user_email,
            is_completed, last_studied, last_studied, flashcards_count
        ))

        flashcard_set_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()

        print(f"✅ Flashcard set created for {user_email} with ID {flashcard_set_id}")
        return flashcard_set_id
    except Exception as e:
        print(f"❌ Failed to create flashcard set: {e}")
        return None

def save_flashcards_to_db(flashcards, flashcard_set_id, user_email):
    try:
        if not flashcard_set_id:
            raise ValueError("Flashcard set ID is invalid")

        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        values = [(fc["front"], fc["back"], flashcard_set_id, user_email) for fc in flashcards]

        execute_values(
            cur,
            "INSERT INTO flashcards (front, back, flashcard_set_id, user_email) VALUES %s",
            values
        )

        conn.commit()
        cur.close()
        conn.close()
        print(f"✅ {len(flashcards)} flashcards saved to DB.")
    except Exception as e:
        print(f"❌ Failed to save flashcards: {e}")

if __name__ == "__main__":
    chat_transcript = """
    Người dùng: Hôm nay chúng ta học về định luật Newton.
    Trợ lý: Định luật thứ nhất nói rằng một vật sẽ giữ nguyên trạng thái chuyển động hoặc đứng yên nếu không có lực nào tác dụng lên nó.
    Người dùng: Còn định luật thứ hai?
    Trợ lý: F = ma, tức là lực bằng khối lượng nhân gia tốc.
    Người dùng: Và định luật thứ ba?
    Trợ lý: Mỗi lực tác dụng đều có một lực phản lực bằng và ngược chiều.
    """

    output = generate_flashcards_from_chat(chat_transcript, "duyminht651@gmail.com")
    print(json.dumps(output, indent=2, ensure_ascii=False))
