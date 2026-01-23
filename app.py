import streamlit as st
import numpy as np
import scipy.io
import os
import time
import random
import pandas as pd
import altair as alt

# --- 1. 数据处理部分 ---
def sort_by_time(filename):
    try:
        parts = filename.replace('.mat', '').split('-')
        return tuple(map(int, parts))
    except:
        return 0

def scgload(path):
    try:
        scg_data = scipy.io.loadmat(path)
        if 'spline_data_x' in scg_data:
            x = scg_data['spline_data_x'].flatten()
        elif 'accresult' in scg_data:
            x = scg_data['accresult'][0].flatten()
        else:
            return np.array([])
        return x
    except:
        return np.array([])

@st.cache_data
def load_all_data(data_folder):
    if os.path.exists(data_folder):
        scg_dir = sorted([f for f in os.listdir(data_folder) if f.endswith('.mat')], key=sort_by_time)
        all_x_list = []
        for scg_file in scg_dir[:20]: 
            x = scgload(os.path.join(data_folder, scg_file))
            if len(x) > 0:
                all_x_list.extend(x)
        if len(all_x_list) > 0:
            return np.array(all_x_list)
    return np.sin(np.linspace(0, 100, 10000)) + np.random.normal(0, 0.2, 10000)

# --- 2. 界面样式配置 ---
st.set_page_config(page_title="SCG Monitor", layout="centered")

st.markdown("""
<style>
    html, body, [class*="css"] {
        font-family: 'Helvetica Neue', Arial, sans-serif;
    }
    .header-text {
        font-size: 18px; 
        font-weight: 600;
        color: #333;
        margin-bottom: 0px; 
        padding-top: 10px;
        display: flex;
        align-items: center; 
        justify-content: center; 
    }
    .cards-container {
        display: flex;
        flex-direction: row;
        justify-content: center; 
        gap: 15px; 
        width: 100%;
        margin-top: 10px;
    }
    .bp-card {
        border-radius: 12px;
        padding: 10px;
        text-align: center;
        box-shadow: 0 2px 5px rgba(0,0,0,0.08);
        height: 140px; 
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        width: 45%; 
        max-width: 150px;
        min-width: 120px;
    }
    .card-sbp {
        background-color: #FFE4E1; 
        border: 1px solid #FFCDD2;
    }
    .card-dbp {
        background-color: #C8E6C9; 
        border: 1px solid #A5D6A7;
    }
    .card-title { font-size: 18px; font-weight: bold; margin-bottom: 0px; }
    .card-value { font-size: 40px; font-weight: bold; line-height: 1.1; margin: 2px 0; }
    .card-unit { font-size: 12px; opacity: 0.8; line-height: 1.2; }
    
    div.stButton > button {
        width: 100%;
        border-radius: 8px;
        height: 45px;
        font-weight: bold;
    }
    div[data-testid="column"]:nth-of-type(1) button {
        background-color: #E0E0E0;
        color: #555;
        border: none;
    }
    div[data-testid="column"]:nth-of-type(2) button {
        background-color: #4169E1;
        color: white;
        border: none;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. 状态管理 ---
if 'running' not in st.session_state:
    st.session_state.running = False
if 'measure_count' not in st.session_state:
    st.session_state.measure_count = 0 

data_path = "demo" 
all_x = load_all_data(data_path)

# --- 4. 布局构建 ---
st.markdown('<div class="header-text">💚 Cardiac Signal Monitoring (SCG) :</div>', unsafe_allow_html=True)
chart_placeholder = st.empty()

st.markdown("<br>", unsafe_allow_html=True)
cards_placeholder = st.empty() 

def render_cards(sbp, dbp):
    html_code = f"""
    <div class="cards-container">
        <div class="bp-card card-sbp">
            <div class="card-title" style="color: #8B0000;">SBP</div>
            <div class="card-value" style="color: #8B0000;">{sbp}</div>
            <div class="card-unit" style="color: #8B0000;">mmHg<br>❤️ Raised</div>
        </div>
        <div class="bp-card card-dbp">
            <div class="card-title" style="color: #006400;">DBP</div>
            <div class="card-value" style="color: #006400;">{dbp}</div>
            <div class="card-unit" style="color: #006400;">mmHg<br>💚 Normal</div>
        </div>
    </div>
    """
    cards_placeholder.markdown(html_code, unsafe_allow_html=True)

render_cards(120, 70)

st.markdown("<br>", unsafe_allow_html=True)
info_text_placeholder = st.empty()
progress_bar = st.empty()

info_text_placeholder.markdown(
    f"<div style='text-align: left; font-size: 16px; margin-bottom: 5px;'>Waiting for <b>No.{st.session_state.measure_count}</b> measurements.</div>", 
    unsafe_allow_html=True
)
progress_bar.progress(0)

st.markdown("<br>", unsafe_allow_html=True)
b_col1, b_col2 = st.columns(2)

with b_col1:
    start_clicked = st.button("START", use_container_width=True)
with b_col2:
    stop_clicked = st.button("STOP", use_container_width=True)

if start_clicked:
    st.session_state.running = True
if stop_clicked:
    st.session_state.running = False

# --- 5. 双重循环逻辑 (医学风格版) ---
if st.session_state.running:
    # --- SCG 波形设置 ---
    window_size = 1000 
    step = 30           # 保持大步长以平衡性能
    sleep_time = 0.01   # 保持低延迟
    
    # --- 血压更新设置 ---
    cycle_duration = 2.5 
    cycle_start_time = time.time() 
    
    # 【核心修改：医学监护仪风格配置】
    # 1. mark_line: color="#00FF00" (荧光绿)
    # 2. properties: background="#000000" (纯黑背景)
    # 3. axis: gridColor="#333333" (暗色网格)
    base = alt.Chart(pd.DataFrame({'index':[], 'SCG':[]})).mark_line(
        color="#00FF00",  # 典型的医用监护仪绿色
        strokeWidth=2     # 稍微加粗一点点，更清晰
    ).encode(
        x=alt.X('index', axis=None), 
        y=alt.Y('SCG', axis=alt.Axis(
            grid=True,          # 开启网格
            gridColor='#224422',# 暗绿色的网格线，更有仪器感
            tickCount=5,        # 减少刻度线数量
            labels=False,       # 隐藏Y轴数字，更简洁
            domain=False        # 隐藏轴线
        ), scale=alt.Scale(domain=[-0.05, 0.05]))
    ).properties(
        height=180,
        background='#000000' # 整个图表区域设为黑色
    ).configure_view(
        strokeWidth=0        # 去掉图表外框
    )

    for i in range(0, len(all_x) - window_size, step):
        if not st.session_state.running:
            break
            
        # A: 渲染波形 (原始信号)
        batch_data = all_x[i : i + window_size]
        chart_data = pd.DataFrame({
            "SCG": batch_data, 
            "index": np.arange(len(batch_data)) 
        })
        c = base.properties(data=chart_data)
        chart_placeholder.altair_chart(c, use_container_width=True)
        
        # B: 业务逻辑
        current_time = time.time()
        elapsed_time = current_time - cycle_start_time 
        
        progress_ratio = elapsed_time / cycle_duration
        
        if elapsed_time >= cycle_duration:
            st.session_state.measure_count += 1
            current_sbp = random.randint(119, 121)
            current_dbp = random.randint(68, 71)
            
            render_cards(current_sbp, current_dbp)
            info_text_placeholder.markdown(
                f"<div style='text-align: left; font-size: 16px; margin-bottom: 5px;'>Waiting for <b>No.{st.session_state.measure_count}</b> measurements.</div>", 
                unsafe_allow_html=True
            )
            
            cycle_start_time = current_time 
            progress_ratio = 0.0 
        
        progress_bar.progress(min(progress_ratio, 1.0))
        time.sleep(sleep_time)
