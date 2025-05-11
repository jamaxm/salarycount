import streamlit as st

# Графики смен
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

# Формат суммы с пробелами
def format_money(val):
    return f"{int(val):,}".replace(",", " ")

# Универсальный расчет KPI
def calculate_kpi(value, thresholds, reverse=False):
    sorted_thresholds = sorted(thresholds, reverse=not reverse)
    for threshold, percent in sorted_thresholds:
        if (not reverse and value >= threshold) or (reverse and value <= threshold):
            return percent
    return thresholds[-1][1] if reverse else 0

st.set_page_config(page_title="KPI и Оклад Калькулятор", layout="centered")
st.title("💼 Расчет KPI и оклада")

# Общая сумма KPI
total_bonus = st.number_input("Общая сумма KPI (в сумах)", value=1_000_000, step=100_000)

# KPI блок
st.header("📊 Расчет KPI")

quality = st.slider("Качество (%)", 91, 100, 100)
svd = st.slider("СВД (сек)", 100, 140, 120)
svz = st.slider("СВЗ (сек)", 120, 150, 130)
cs = st.slider("CS", 4.4, 5.0, 4.8, step=0.01)

# Пороговые значения
quality_tiers = [(100, 100), (99, 90), (98, 80), (97, 70), (96, 60), (95, 50), (94, 40), (93, 30), (92, 20), (91, 10)]
svd_tiers = [(120, 100), (125, 80), (130, 60), (135, 30), (140, 0)]
svz_tiers = [(130, 100), (135, 90), (140, 80), (145, 70), (150, 0)]
cs_tiers = [(5.0, 100), (4.8, 100), (4.7, 80), (4.6, 60), (4.5, 30), (4.49, 0)]

# Вес целей
weights = {
    "quality": 0.4,
    "svd": 0.25,
    "svz": 0.25,
    "cs": 0.1
}

# KPI проценты
quality_percent = calculate_kpi(quality, quality_tiers)
svd_percent = calculate_kpi(svd, svd_tiers, reverse=True)
svz_percent = calculate_kpi(svz, svz_tiers, reverse=True)
cs_percent = calculate_kpi(cs, cs_tiers)

# KPI суммы
quality_sum = total_bonus * weights["quality"] * quality_percent / 100
svd_sum = total_bonus * weights["svd"] * svd_percent / 100
svz_sum = total_bonus * weights["svz"] * svz_percent / 100
cs_sum = total_bonus * weights["cs"] * cs_percent / 100
total_kpi = quality_sum + svd_sum + svz_sum + cs_sum

# Вывод KPI
st.subheader("🔹 Результаты KPI:")
st.write(f"KPI по качеству: **{format_money(quality_sum)} сум**")
st.write(f"KPI по СВД: **{format_money(svd_sum)} сум**")
st.write(f"KPI по СВЗ: **{format_money(svz_sum)} сум**")
st.write(f"KPI по CS: **{format_money(cs_sum)} сум**")
st.success(f"Итоговый KPI: **{format_money(total_kpi)} сум**")

# Оклад
st.header("💰 Расчет оклада по часовой ставке")

hourly_rate = st.number_input("Часовая ставка (сум/час)", value=15000, step=1000)

st.subheader("Выберите количество смен по графику:")
total_salary = 0
night_hours = 0

for shift_name, (start, end) in shifts.items():
    count = st.number_input(f"{shift_name}", min_value=0, value=0, step=1)
    normal = 0
    night = 0
    for h in range(int(start), int(end)):
        hour_mod = h % 24
        if 22 <= hour_mod or hour_mod < 6:
            night += 1
        else:
            normal += 1
    total_salary += count * (normal * hourly_rate + night * hourly_rate * 1.5)
    night_hours += count * night

taxed_salary = total_salary * 0.88

st.subheader("📄 Оклад:")
st.write(f"Общий оклад (до налогов): **{format_money(total_salary)} сум**")
st.write(f"В том числе {int(night_hours)} ночных часов ×1.5")
st.success(f"💸 Чистыми на руки (после 12% налога): **{format_money(taxed_salary)} сум**")

# 💵 Общая сумма: KPI + оклад после налога
final_total = total_kpi + taxed_salary
st.header("🧾 Общая сумма к получению")
st.success(f"💵 Всего: **{format_money(final_total)} сум** (KPI + Оклад после налога)")
