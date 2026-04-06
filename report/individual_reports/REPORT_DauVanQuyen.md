# Individual Report: Lab 3 - Chatbot vs ReAct Agent

- **Student Name**: Đậu Văn Quyền
- **Role**: Prompt & Architecture Engineer
- **Date**: 2026-04-06

---

## I. Technical Contribution (15 Points)

Vai trò chính của em là tối ưu hoá Prompt Engineering. Em thiết kế kiến trúc "luật lệ" (Guardrails) nằm trong System Prompt để hướng dẫn Agent hoạt động tuân thủ kỷ luật đúng vòng lặp. 

- **Modules Implemented**: `src/agent/agent.py` (hàm `get_system_prompt`)
- **Code Highlights**:
```python
        today = datetime.now().strftime('%Y-%m-%d')
        return f"""
        NGÀY HÔM NAY LÀ: {today}
        Khi người dùng nói "hôm nay", "chiều nay", "sáng nay",... luôn dùng ngày: {today}
        QUY TẮC QUAN TRỌNG:
        1. MỖI LƯỢT chỉ gọi DUY NHẤT MỘT Action.
```
- **Documentation**: Kỹ thuật em sử dụng bao gồm Prompt Injection (chèn datetime thực tế mỗi khi Agent chạy), Negative Prompting (TUYỆT ĐỐI KHÔNG...), và Few-shot reasoning (cung cấp ví dụ mẫu về Action gọi Tool).

---

## II. Debugging Case Study (10 Points)

- **Problem Description**: Tình trạng "Hallucination" (ảo giác) nghiêm trọng về khái niệm thời gian: Khi user gõ "đổ xăng hôm nay", CSV lưu dữ liệu với cái date: `2023-11-10`.
- **Diagnosis**: Mô hình ngôn ngữ bị lạc trôi trong thời gian nội bộ lúc nó được huấn luyện. Vì người dùng không cung cấp Date cụ thể, LLM lấy bừa một mốc thời gian để đáp ứng đủ tham số hàm `add_expense(_,_,_,date)`.
- **Solution**: Em tiêm trực tiếp biến số string hiển thị Date Time thực tại vào System Prompt, thiết lập quy luật "Khi nhắc đến hôm nay thì LUÔN dùng biến này".

---

## III. Personal Insights: Chatbot vs ReAct (10 Points)

1. **Reasoning**: Sức mạnh của Prompt quyết định 90% khả năng hoạt động. Nếu ví dụ mẫu của em chỉ cần dư một dấu ngoặc, nó sẽ học theo cái sai lầm ấy cho toàn bộ hành trình sau này.
2. **Reliability**: Em nhận ra sự nguy hiểm nếu cấp Tool tuỳ thích. Một Chatbot ngơ ngáo sẽ mang tính giải trí, nhưng Agent ngơ ngáo có gọi Tool có thể... tiêu diệt luôn cơ sở dữ liệu bảng xoá (Drop DB). Guardrails prompt là chưa đủ.
3. **Observation**: Một Observation khôn khéo từ thiết kế Tool trả về "Lưu thành công: Số tiền X" khiến cho Thought Block vòng tới của LLM ngay lập tức nhận ra mình đã thành công thay vì mù mờ đoán.

---

## IV. Future Improvements (5 Points)

- **Scalability**: Prompt hiện tại đang phình to do phải chứa nội dung toàn bộ các Tool. Ở quy mô to, em sẽ ứng dụng kỹ thuật RAG để Agent lấy ra Doc của chỉ các Tool thực sự khả dụng theo Context hiện tại.
- **Safety**: Xây dựng Agent Supervisor: Sau khi Agent lên kế hoạch gọi hàm, cần có một Agent Cấp cao thứ 2 (hoặc Regex truyền thống) duyệt thẩm định tham số lệnh xem có nằm trong vùng nguy hiểm trước khi cho chạy.
- **Performance**: Giảm độ dài nhắc nhở định dạng JSON trong Prompt bằng các mô hình Fine-Tuned để phản hồi natively.
