import streamlit as st
import numpy as np
import scipy.io
import os
import time
import random
import pandas as pd
import altair as alt

# --- 1. 数据处理部分 (保持不变) ---
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

# --- 2. 界面样式配置 (【核心修改：暗黑医疗配色】) ---
st.set_page_config(page_title="SCG Monitor", layout="centered")

st.markdown("""
<style>
    /* 1. 强制全局深色背景 */
    .stApp {
        background-color: #0E1117; /* 深灰/黑背景 */
        color: #FAFAFA;
    }
    
    /* 2. 标题文字颜色 */
    .header-text {
        font-size: 20px; 
        font-weight: 600;
        color: #E0E0E0; /* 浅灰白 */
        margin-bottom: 0px; 
        padding-top: 10px;
        display: flex;
        align-items: center; 
        justify-content: center; 
        text-shadow: 0 0 5px rgba(255,255,255,0.1);
    }

    /* 3. 卡片容器 */
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
        box-shadow: 0 4px 6px rgba(0,0,0,0.3); /* 更深的阴影 */
        height: 140px; 
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        width: 45%; 
        max-width: 150px;
        min-width: 120px;
    }

    /* 4. SBP 卡片 (暗红底 + 亮红字) */
    .card-sbp {
        background-color: #2b0c0c; /* 极深的红色背景 */
        border: 1px solid #8a2be2; /* 甚至可以用紫色或深红边框 */
        border: 1px solid #ff4b4b; /* 亮红边框 */
    }
    
    /* 5. DBP 卡片 (暗绿底 + 荧光绿字) */
    .card-dbp {
        background-color: #0c2b10; /* 极深的绿色背景 */
        border: 1px solid #00ff00; /* 荧光绿边框 */
    }

    .card-title { font-size: 18px; font-weight: bold; margin-bottom: 0px; }
    .card-value { font-size: 42px; font-weight: bold; line-height: 1.1; margin: 2px 0; text-shadow: 0 0 8px currentColor; }
    .card-unit { font-size: 12px; opacity: 0.8; line-height: 1.2; }
    
    /* 6. 按钮样式 (深灰色) */
    div.stButton > button {
        width: 100%;
        border-radius: 8px;
        height: 45px;
        font-weight: bold;
        border: 1px solid #444;
    }
    div[data-testid="column"]:nth-of-type(1) button {
        background-color: #262730; /* 深灰按钮 */
        color: #FFF;
    }
    div[data-testid="column"]:nth-of-type(1) button:hover {
        border-color: #FFF;
        color: #FFF;
    }
    div[data-testid="column"]:nth-of-type(2) button {
        background-color: #1f3a5f; /* 深蓝按钮 */
        color: #4da6ff;
        border: 1px solid #1f3a5f;
    }
    div[data-testid="column"]:nth-of-type(2) button:hover {
        background-color: #2a4b7a;
        color: #FFF;
    }
    
    /* 7. 进度条文字修正 */
    .status-text {
        color: #aaaaaa;
        text-align: left;
        font-size: 14px;
        margin-bottom: 5px;
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
    # 修改了这里的内联样式，使用 CSS 类控制，颜色改为荧光色
    html_code = f"""
    <div class="cards-container">
        <div class="bp-card card-sbp">
            <div class="card-title" style="color: #ff8888;">SBP</div>
            <div class="card-value" style="color: #ff4b4b;">{sbp}</div>
            <div class="card-unit" style="color: #ff8888;">mmHg<br>❤️ Raised</div>
        </div>
        <div class="bp-card card-dbp">
            <div class="card-title" style="color: #88ff88;">DBP</div>
            <div class="card-value" style="color: #00ff00;">{dbp}</div>
            <div class="card-unit" style="color: #88ff88;">mmHg<br>💚 Normal</div>
        </div>
    </div>
    """
    cards_placeholder.markdown(html_code, unsafe_allow_html=True)

# 初始数值
render_cards(120, 70)

st.markdown("<br>", unsafe_allow_html=True)
info_text_placeholder = st.empty()
progress_bar = st.empty()

# 初始文字显示 (改为浅色字体)
info_text_placeholder.markdown(
    f"<div class='status-text'>Waiting for <b>No.{st.session_state.measure_count}</b> measurements.</div>", 
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

# --- 5. 双重循环逻辑 ---
if st.session_state.running:
    # --- SCG 波形设置 ---
    window_size = 1000 
    step = 30           # 保持大步长
    sleep_time = 0.01   # 保持低延迟
    
    # --- 血压更新设置 ---
    cycle_duration = 2.5 
    cycle_start_time = time.time() 
    
    # 【图表配置：纯黑背景 + 荧光绿线】
    base = alt.Chart(pd.DataFrame({'index':[], 'SCG':[]})).mark_line(
        color="#00FF00",  # 典型的医用监护仪荧光绿
        strokeWidth=2     
    ).encode(
        x=alt.X('index', axis=None), 
        y=alt.Y('SCG', axis=alt.Axis(
            grid=True,          
            gridColor='#333333',# 很暗的灰色网格
            tickCount=5,        
            labels=False,       
            domain=False,       
            title=None          
        ), scale=alt.Scale(domain=[-0.05, 0.05]))
    ).properties(
        height=180,
        background='#000000' # 图表区域纯黑
    ).configure_view(
        strokeWidth=0        
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
                f"<div class='status-text'>Waiting for <b>No.{st.session_state.measure_count}</b> measurements.</div>", 
                unsafe_allow_html=True
            )
            
            cycle_start_time = current_time 
            progress_ratio = 0.0 
        
        progress_bar.progress(min(progress_ratio, 1.0))
        time.sleep(sleep_time)
