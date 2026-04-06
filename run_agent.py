import os
from dotenv import load_dotenv
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.openai_provider import OpenAIProvider
from src.core.gemini_provider import GeminiProvider
from src.agent.agent import ReActAgent
from src.tools.expense_tools import EXPENSE_TOOLS_MAP

def run_agent_interactive():
    load_dotenv()
    provider_name = os.getenv("DEFAULT_PROVIDER", "openai").lower()

    print("=" * 60)
    print("💸 AI EXPENSE MANAGEMENT AGENT")
    print(f"   Provider: {provider_name.upper()}")
    print("=" * 60)
    print("Gõ câu hỏi hoặc khoản chi tiêu bằng tiếng Việt.")
    print("Gõ 'exit' hoặc 'thoát' để kết thúc.")
    print("-" * 60)

    # 1. Khởi tạo LLM
    if provider_name == "openai":
        llm = OpenAIProvider(model_name="gpt-3.5-turbo")
    elif provider_name == "gemini":
        llm = GeminiProvider(model_name="gemini-1.5-flash")
    else:
        print("❌ Vui lòng chọn provider openai hoặc gemini trong file .env")
        return

    # 2. Gắn Tool vào Agent
    agent = ReActAgent(llm=llm, tools=EXPENSE_TOOLS_MAP, max_steps=6)

    # 3. Vòng lặp nhận input từ bàn phím
    while True:
        try:
            user_input = input("\n👤 Bạn: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\n👋 Tạm biệt!")
            break

        if not user_input:
            continue

        if user_input.lower() in ["exit", "thoát", "quit"]:
            print("👋 Tạm biệt! Kiểm tra file report/transactions.csv để xem lịch sử chi tiêu.")
            break

        print("\n" + "=" * 50)
        final_response = agent.run(user_input)
        print("=" * 50)

        print(f"\n🤖 Trả lời: {final_response}")
        print("\n✅ (Dữ liệu đã được cập nhật vào report/transactions.csv nếu có giao dịch mới)")

if __name__ == "__main__":
    run_agent_interactive()
