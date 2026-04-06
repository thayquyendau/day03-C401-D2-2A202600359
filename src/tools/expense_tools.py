import os
import csv
from datetime import datetime
import json

DB_FILE = os.path.join(os.path.dirname(__file__), '..', '..', 'report', 'transactions.csv')

# ======== DANH MỤC CHUẨN HOÁ ========
# Mọi category LLM bịa ra sẽ được map về 1 trong các danh mục chuẩn này
STANDARD_CATEGORIES = {
    "Ăn uống": ["ăn", "uống", "food", "phở", "cơm", "bún", "mì", "bánh", "trà sữa",
                 "cà phê", "cafe", "coffee", "highland", "shopee", "shopeefood",
                 "grab food", "gofood", "beverage", "đồ ăn", "đồ uống", "kem",
                 "nhậu", "bia", "lẩu", "nước"],
    "Đi lại":  ["xăng", "xe", "grab", "gojek", "taxi", "bus", "đi lại", "di chuyển",
                 "xăng xe", "đổ xăng", "gửi xe", "vé", "tàu", "máy bay"],
    "Mua sắm": ["mua", "sắm", "quần", "áo", "giày", "dép", "túi", "shopping",
                 "lazada", "tiki", "sendo"],
    "Giải trí": ["phim", "nhạc", "chơi", "game", "karaoke", "giải trí", "vé xem",
                  "du lịch", "netflix", "spotify"],
    "Giáo dục": ["sách", "học", "khoá", "course", "udemy", "giáo dục", "trường"],
    "Hoá đơn":  ["điện", "nước", "internet", "wifi", "thuê nhà", "hoá đơn", "phí"],
    "Sức khoẻ": ["thuốc", "bệnh viện", "khám", "sức khoẻ", "gym", "tập"],
}

def _normalize_category(raw_category: str) -> str:
    """Map bất kỳ category nào LLM bịa ra về danh mục chuẩn."""
    raw = raw_category.lower().strip()
    for std_cat, keywords in STANDARD_CATEGORIES.items():
        if raw == std_cat.lower():
            return std_cat
        for kw in keywords:
            if kw in raw:
                return std_cat
    return "Khác"

def _get_today() -> str:
    """Luôn trả về ngày hôm nay dạng YYYY-MM-DD."""
    return datetime.now().strftime('%Y-%m-%d')

def _init_db():
    os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['date', 'amount', 'category', 'note'])

def _read_db():
    _init_db()
    transactions = []
    with open(DB_FILE, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            transactions.append(row)
    return transactions

def add_expense(amount: float, category: str, note: str, date: str = "") -> str:
    """Lưu một khoản chi mới gồm số tiền, danh mục, ghi chú và thời gian."""
    _init_db()
    # Luôn chuẩn hoá category
    std_category = _normalize_category(category)
    # Luôn dùng ngày hôm nay nếu LLM truyền sai hoặc để trống
    if not date or not date.startswith("2026"):
        date = _get_today()
    with open(DB_FILE, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([date, amount, std_category, note])
    return f"Đã lưu thành công: {amount} VND | Danh mục: {std_category} | Ghi chú: {note} | Ngày: {date}"

def get_monthly_expense() -> str:
    """Lấy tổng chi tiêu trong tháng hiện tại."""
    transactions = _read_db()
    current_month = datetime.now().strftime('%Y-%m')
    total = 0.0
    for t in transactions:
        t_date = t.get('date', '')
        if t_date.startswith(current_month):
            try:
                total += float(t.get('amount', 0))
            except ValueError:
                pass
    return f"Tổng chi trong tháng hiện tại là: {total} VND"

def get_today_expenses() -> str:
    """Lấy danh sách các khoản chi tiêu trong ngày hôm nay."""
    transactions = _read_db()
    today = _get_today()
    today_list = []
    total = 0.0
    for t in transactions:
        if t.get('date', '') == today:
            amt = float(t.get('amount', 0))
            total += amt
            today_list.append(f"  - {t.get('note', 'N/A')}: {amt:,.0f} VND ({t.get('category', 'Khác')})")
    if not today_list:
        return f"Hôm nay ({today}) chưa có khoản chi tiêu nào được ghi nhận."
    result = f"Chi tiêu hôm nay ({today}):\n" + "\n".join(today_list)
    result += f"\nTổng hôm nay: {total:,.0f} VND"
    return result

def get_budget() -> str:
    """Lấy ngân sách tháng của người dùng (Giả lập mặc định 10.000.000 VND)."""
    budget = 10000000.0
    return f"Ngân sách tháng định mức là {budget} VND."

def calculate_percentage(expense: float, budget: float) -> str:
    """Tính phần trăm ngân sách đã sử dụng."""
    if budget == 0:
        return "Lỗi chia cho 0. Ngân sách đang là 0."
    pct = (expense / float(budget)) * 100
    return f"Bạn đã sử dụng {pct:.2f}% ngân sách."

def categorize_expense(description: str) -> str:
    """Tự động phân loại khoản chi theo ghi chú."""
    return _normalize_category(description)

def get_spending_by_category() -> str:
    """Thống kê chi tiêu theo từng danh mục trong tháng."""
    transactions = _read_db()
    stats = {}
    current_month = datetime.now().strftime('%Y-%m')

    for t in transactions:
        if t.get('date', '').startswith(current_month):
            # Chuẩn hoá lại danh mục khi đọc (phòng dữ liệu cũ bị bẩn)
            cat = _normalize_category(t.get('category', 'Khác'))
            amt = float(t.get('amount', 0))
            stats[cat] = stats.get(cat, 0) + amt

    return f"Thống kê theo danh mục: {json.dumps(stats, ensure_ascii=False)}"

# ======== TOOL REGISTRY ========
EXPENSE_TOOLS_MAP = [
    {
        "name": "add_expense",
        "description": "Lưu một khoản chi mới. Nhận: amount (float), category (text - 1 trong: Ăn uống, Đi lại, Mua sắm, Giải trí, Giáo dục, Hoá đơn, Sức khoẻ, Khác), note (text mô tả ngắn), date (text 'YYYY-MM-DD', nếu không biết hãy truyền chuỗi rỗng '')."
    },
    {
        "name": "get_monthly_expense",
        "description": "Lấy tổng chi tiêu trong tháng hiện hành. Không cần tham số."
    },
    {
        "name": "get_today_expenses",
        "description": "Lấy danh sách tất cả khoản chi tiêu trong ngày hôm nay. Dùng khi người dùng hỏi 'hôm nay/chiều nay tôi có chi gì không'. Không cần tham số."
    },
    {
        "name": "get_budget",
        "description": "Lấy ngân sách tháng mặc định. Không cần tham số."
    },
    {
        "name": "calculate_percentage",
        "description": "Tính phần trăm sử dụng. Nhận 2 tham số: expense (float) tổng tiền đã tiêu, budget (float) là ngân sách."
    },
    {
        "name": "categorize_expense",
        "description": "Gợi ý tự động danh mục chuẩn dựa trên mô tả. Nhận 1 tham số description (text)."
    },
    {
        "name": "get_spending_by_category",
        "description": "Trả về thống kê số tiền ở từng danh mục trong tháng. Không cần tham số."
    }
]

def map_tool_call(tool_name: str, args_str: str) -> str:
    """Hàm wrapper để chạy các lệnh Tool linh động từ string"""
    import ast
    try:
        if not args_str.strip():
            args = []
        elif args_str.strip().startswith('(') or args_str.strip().startswith('['):
            args = ast.literal_eval(args_str)
        else:
            if args_str.strip().startswith('{'):
                kwargs = ast.literal_eval(args_str)
                if tool_name == "add_expense":
                    return add_expense(**kwargs)
                elif tool_name == "calculate_percentage":
                    return calculate_percentage(**kwargs)
                elif tool_name == "categorize_expense":
                    return categorize_expense(**kwargs)
            else:
                args = [a.strip().strip("'").strip('"') for a in args_str.split(',')]

        if not isinstance(args, (list, tuple)):
            args = [args]

        if tool_name == "add_expense":
            amount = float(args[0])
            category = str(args[1]) if len(args) > 1 else "Khác"
            note = str(args[2]) if len(args) > 2 else ""
            date = str(args[3]) if len(args) > 3 else ""
            return add_expense(amount, category, note, date)

        elif tool_name == "get_monthly_expense":
            return get_monthly_expense()

        elif tool_name == "get_today_expenses":
            return get_today_expenses()

        elif tool_name == "get_budget":
            return get_budget()

        elif tool_name == "calculate_percentage":
            return calculate_percentage(float(args[0]), float(args[1]))

        elif tool_name == "categorize_expense":
            return categorize_expense(args[0])

        elif tool_name == "get_spending_by_category":
            return get_spending_by_category()

        else:
            return f"❌ Lỗi: Tool '{tool_name}' không tồn tại!"
    except Exception as e:
        return f"❌ Lỗi thực thi Tool {tool_name} với tham số '{args_str}': {e}"
