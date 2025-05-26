import streamlit as st

st.set_page_config(page_title="💼 KPI и Оклад Калькулятор", layout="centered")

# 💰 Графики смен
shifts = {
    "07:00-16:00": (7, 16),
    "08:00-17:00": (8, 17),
    "08:30-17:30": (8.5, 17.5),
    "09:00-18:00": (9, 18),
    "09:30-18:30": (9.5, 18.5),
    "10:00-19:00": (10, 19),
    "11:00-20:00": (11, 20),
    "12:00-21:00": (12, 21),
    "14:00-23:00": (14, 23),
    "15:00-00:00": (15, 24),
    "16:00-01:00": (16, 25),
    "17:00-02:00": (17, 26),
    "21:00-09:00": (21, 33)
}

def format_money(val):
    return f"{int(val):,}".replace(",", " ")

def calculate_kpi(value, thresholds, reverse=False):
    sorted_thresholds = sorted(thresholds, reverse=not reverse)
    for threshold, percent in sorted_thresholds:
        if (not reverse and value >= threshold) or (reverse and value <= threshold):
            return percent
    return thresholds[-1][1] if reverse else 0

# 💻 Заголовок
st.markdown("<h1 style='text-align: center;'>💼 Расчет KPI и оклада</h1>", unsafe_allow_html=True)

# Общие значения по умолчанию
total_bonus = st.number_input("Общая сумма KPI (в сумах)", value=2_126_000, step=100_000)
hourly_rate = st.number_input("Часовая ставка (сум/час)", value=27560, step=1000)

tabs = st.tabs(["📊 KPI", "💰 Оклад", "🧾 Общая сумма"])

# ===== KPI ТАБ =====
with tabs[0]:
    st.subheader("📊 Введите показатели KPI")
    quality = st.slider("Качество (%)", 91, 100, 100)
    svd = st.slider("СВД (сек)", 100, 140, 120)
    svz = st.slider("СВЗ (сек)", 120, 150, 130)
    cs = st.slider("CS", 4.4, 5.0, 4.8, step=0.01)

    # Пороговые значения
    quality_tiers = [(100, 100), (99, 90), (98, 80), (97, 70), (96, 60), (95, 50), (94, 40), (93, 30), (92, 20), (91, 10)]
    svd_tiers = [(120, 100), (125, 80), (130, 60), (135, 30), (140, 0)]
    svz_tiers = [(130, 100), (135, 90), (140, 80), (145, 70), (150, 0)]
    cs_tiers = [(5.0, 100), (4.8, 100), (4.7, 80), (4.6, 60), (4.5, 30), (4.49, 0)]

    weights = {"quality": 0.4, "svd": 0.25, "svz": 0.25, "cs": 0.1}

    quality_percent = calculate_kpi(quality, quality_tiers)
    svd_percent = calculate_kpi(svd, svd_tiers, reverse=True)
    svz_percent = calculate_kpi(svz, svz_tiers, reverse=True)
    cs_percent = calculate_kpi(cs, cs_tiers)

    quality_sum = total_bonus * weights["quality"] * quality_percent / 100
    svd_sum = total_bonus * weights["svd"] * svd_percent / 100
    svz_sum = total_bonus * weights["svz"] * svz_percent / 100
    cs_sum = total_bonus * weights["cs"] * cs_percent / 100
    total_kpi = quality_sum + svd_sum + svz_sum + cs_sum

    st.success("✅ KPI Расчёт завершён:")
    st.markdown(f"""
    | Метрика | % | Сумма |
    |--------|----|-------|
    | Качество | {quality_percent}% | **{format_money(quality_sum)} сум** |
    | СВД     | {svd_percent}% | **{format_money(svd_sum)} сум** |
    | СВЗ     | {svz_percent}% | **{format_money(svz_sum)} сум** |
    | CS      | {cs_percent}% | **{format_money(cs_sum)} сум** |
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.success(f"💸 Общий KPI: **{format_money(total_kpi)} сум**")

# ===== ОКЛАД ТАБ =====
with tabs[1]:
    st.subheader("💰 Укажите смены:")
    total_salary = 0
    night_hours = 0

    for shift_name, (start, end) in shifts.items():
        count = st.number_input(f"{shift_name}", min_value=0, value=0, step=1)
        normal = 0
        night = 0
        shift_duration = end - start
        effective_duration = shift_duration - 1 if shift_duration > 5 else shift_duration

        for h in range(int(start), int(start + effective_duration)):
            hour_mod = h % 24
            if 22 <= hour_mod or hour_mod < 6:
                night += 1
            else:
                normal += 1

        total_salary += count * (normal * hourly_rate + night * hourly_rate * 1.5)
        night_hours += count * night

    taxed_salary = total_salary * 0.88

    st.success("✅ Расчёт завершён:")
    st.markdown(f"""
    - 🕒 Ночных часов: **{int(night_hours)}** ×1.5  
    - 💼 Оклад (до налогов): **{format_money(total_salary)} сум**  
    - 🧾 После 12% налога: **{format_money(taxed_salary)} сум**
    """)

# ===== ИТОГ =====
with tabs[2]:
    final_total = total_kpi + taxed_salary

    st.markdown("<h2 style='text-align: center;'>🧾 Общая сумма к получению</h2>", unsafe_allow_html=True)
    st.success(f"💵 Всего: **{format_money(final_total)} сум** (KPI + Оклад после налога)")

    st.markdown("""
        <style>
        .stApp {
            background-color: #f9f9f9;
        }
        .stNumberInput > div {
            transition: all 0.3s ease;
        }
        .stNumberInput > div:hover {
            background-color: #e0f7fa;
        }
        </style>
    """, unsafe_allow_html=True)
