# 📦 TriPalAI Backend

Đây là backend của hệ thống TriPalAI – trợ lý học tập AI dành cho học sinh Việt Nam. Backend được xây dựng bằng Python (FastAPI), cung cấp API phục vụ cho frontend và xử lý truy vấn AI, xác thực người dùng, lưu trữ dữ liệu, phân tích hành vi học sinh và tích hợp AI model từ OpenAI.

---

## ⚙️ Công nghệ sử dụng

- **FastAPI** – framework nhẹ, mạnh mẽ cho REST API
- **Uvicorn** – ASGI server để chạy ứng dụng
- **Python** – backend logic & xử lý AI
- **OpenAI SDK** – kết nối và xử lý tương tác AI

---

## 🚀 Hướng dẫn chạy local

### 1. Clone repo

```bash
git clone https://github.com/iwatchMLP1212/TriPalAI---Backend.git
cd TriPalAI---Backend
```

### 2. Tạo và kích hoạt môi trường ảo

```bash
python -m venv venv
source venv/bin/activate       # nếu dùng: macOS/Linux
venv\Scripts\activate          # nếu dùng: Windows
```

### 3. Cài đặt các dependencies

```bash
pip install -r requirements.txt
```

### 4. Tạo file .env

```env
OPENAI_API_KEY=your_openai_key
```

### 5. Khởi tạo database

Đảm bảo PostgreSQL đang chạy và bạn đã tạo sẵn database tripalai
Chạy lệnh migrate (tùy theo hệ ORM – ví dụ Alembic hoặc Drizzle, cấu hình cụ thể tuỳ repo bạn setup).
