import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# 設定頁面資訊
st.set_page_config(page_title="投資成本最佳化工具", layout="wide")

st.title("📊 投資成本最佳化與零成本分析工具")
st.markdown("---")

# --- 側邊欄：輸入參數 ---
st.sidebar.header("📥 輸入持倉數據")
C = st.sidebar.number_input("原始平均成本 (C)", value=141.131, step=0.01, format="%.3f")
total_qty = st.sidebar.number_input("總持股股數 (Q)", value=30, step=1)
P = st.sidebar.number_input("預計賣出價格 (P)", value=145.0, step=0.1)

# --- 代數意義說明區 ---
with st.expander("📝 查看公式代數意義與邏輯"):
    st.latex(r"C: \text{原始均價 (Cost) —— 你的投入成本線}")
    st.latex(r"P: \text{賣出價格 (Price) —— 預期的套現位置}")
    st.latex(r"x: \text{賣出比例 (Ratio) —— } \frac{\text{賣出股數}}{\text{總股數}}")
    st.latex(r"k: \text{下降係數 (K-Factor) —— } \frac{x}{1-x} \text{ (賣出與剩餘的比例)}")
    st.markdown("---")
    st.write("### 核心公式")
    st.info("1. **新成本公式：** $f(x) = C - (P - C) \times k$  \n"
            "   *意義：剩餘每一股的成本，會扣除掉『價差乘以槓桿係數』的獲利。*")
    st.info("2. **零成本比例：** $x = \\frac{C}{P}$  \n"
            "   *意義：當賣出金額等於總本金時，剩餘持股成本歸零。*")

# --- 即時診斷區 ---
st.header("🔍 即時交易診斷")
diff = P - C
r = diff / C

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("當前獲利幅度 (r)", f"{r:.2%}")
with col2:
    zero_cost_x = C / P
    st.metric("零成本需賣出比例 (x)", f"{zero_cost_x:.2%}")
with col3:
    zero_cost_qty = total_qty * zero_cost_x
    st.metric("需賣出股數 (以回本)", f"{int(np.ceil(zero_cost_qty))} 股")

# --- 互動式模擬 ---
st.subheader("🛠️ 賣出策略模擬")
sell_qty = st.slider("選擇賣出股數", 1, total_qty - 1, int(total_qty/3))
x_current = sell_qty / total_qty
k_current = x_current / (1 - x_current)
new_cost = C - (diff * k_current)

st.success(f"若以 ${P} 賣出 {sell_qty} 股，剩餘 {total_qty - sell_qty} 股的新成本將降至： **${new_cost:.3f}**")

# --- 視覺化圖表 ---
st.subheader("📈 成本下降矩陣曲線")

# 生成多條不同 P 的曲線
p_range = [P, P+10, P+20, P+40, P+60]
ratios = np.linspace(0.05, 0.9, 100)

fig = go.Figure()

for p_val in p_range:
    costs = (C - p_val * ratios) / (1 - ratios)
    fig.add_trace(go.Scatter(x=ratios*100, y=costs, name=f"賣出價 ${p_val}"))

# 標註當前位置
fig.add_trace(go.Scatter(
    x=[x_current * 100], y=[new_cost],
    mode='markers+text',
    marker=dict(size=12, color='red'),
    text=[f"當前決策: {new_cost:.2f}"],
    textposition="top center",
    name="目前選定策略"
))

fig.update_layout(
    xaxis_title="賣出比例 (%)",
    yaxis_title="剩餘單位成本 (USD)",
    yaxis_range=[-20, C + 20],
    hovermode="x unified"
)
fig.add_hline(y=0, line_dash="dash", line_color="green", annotation_text="零成本線")
fig.add_hline(y=C, line_dash="dot", line_color="gray", annotation_text="原始均價")

st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.caption("本工具由 Python Streamlit 驅動，專為量化投資最佳化設計。")
