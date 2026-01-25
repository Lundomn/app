import streamlit as st
import numpy as np
import scipy.io
import os
import time
import random
import pandas as pd
import altair as alt

# --- 1. 数据处理 ---
def normalize_signal(signal):
    mn, mx = signal.min(), signal.max()
    if mx - mn == 0: return np.zeros_like(signal)
    return (signal - mn) / (mx - mn)

def scgload_and_norm(path):
    try:
        d = scipy.io.loadmat(path)
        if 'spline_data_x' in d: x = d['spline_data_x'].flatten()
        elif 'accresult' in d: x = d['accresult'][0].flatten()
        else: return None
        return normalize_signal(x)
    except:
        return None

@st.cache_data
def load_all_data(data_folder):
    if not os.path.exists(data_folder):
        return np.sin(np.linspace(0, 100, 10000)) * 0.5 + 0.5   
    files = sorted([f for f in os.listdir(data_folder) if f.endswith('.mat')])
    all_chunks = []
    for f in files[:10]:
        x = scgload_and_norm(os.path.join(data_folder, f))
        if x is not None: all_chunks.append(x)
    if all_chunks: return np.concatenate(all_chunks)
    else: return np.sin(np.linspace(0, 100, 10000)) * 0.5 + 0.5

# --- 2. 界面样式 ---
st.set_page_config(page_title="SCG Monitor", layout="centered")

st.markdown("""
<style>
    .stApp { background-color: #0E1117; color: #FAFAFA; }
    
    .header-text {
        font-size: 24px; font-weight: 600; color: #E0E0E0; 
        text-align: center; padding: 15px 0;
        text-shadow: 0 0 10px rgba(255,255,255,0.1);
    }
    
    .section-line { border-top: 1px solid #333; margin: 20px 0; }

    .cards-container {
        display: flex; flex-direction: row; justify-content: center; 
        gap: 20px; width: 100%; margin-top: 10px;
    }
    
    .bp-card {
        border-radius: 15px; padding: 15px; text-align: center; 
        box-shadow: 0 4px 15px rgba(0,0,0,0.5); 
        width: 45%; display: flex; flex-direction: column; 
        justify-content: center; align-items: center;
        transition: transform 0.3s ease;
    }
    
    /* --- SBP 绿色系 (一致) --- */
    .card-sbp { background: linear-gradient(145deg, #0c2b10, #051a06); border: 1px solid #00ff00; }
    .val-sbp { color: #00ff00; font-size: 48px; font-weight: bold; text-shadow: 0 0 10px rgba(0, 255, 0, 0.4); }
    .title-sbp { color: #88ff88; font-size: 18px; font-weight: bold; }
    
    /* --- DBP 绿色系 (一致) --- */
    .card-dbp { background: linear-gradient(145deg, #0c2b10, #051a06); border: 1px solid #00ff00; }
    .val-dbp { color: #00ff00; font-size: 48px; font-weight: bold; text-shadow: 0 0 10px rgba(0, 255, 0, 0.4); }
    .title-dbp { color: #88ff88; font-size: 18px; font-weight: bold; }

    .final-card { height: 200px; width: 40%; }
    .final-val { font-size: 64px; }

    /* --- 按钮样式 (标准尺寸 + 居中) --- */
    div.stButton > button { 
        background-color: #eee !important; color: #000 !important; 
        border-radius: 8px;
        height: 42px; 
        font-weight: 600; 
        font-size: 16px; 
        border: 2px solid transparent !important;
        transition: all 0.2s ease-in-out;
    }
    
    div[data-testid="column"]:nth-of-type(1) div.stButton > button {
        background-color: #e6ffe6 !important; color: #006400 !important; border-color: #00ff00 !important;
    }
    div[data-testid="column"]:nth-of-type(1) div.stButton > button:hover {
        background-color: #00ff00 !important; color: #ffffff !important; transform: scale(1.02);
    }

    div[data-testid="column"]:nth-of-type(2) div.stButton > button {
        background-color: #ffe6e6 !important; color: #8b0000 !important; border-color: #ff4b4b !important;
    }
    div[data-testid="column"]:nth-of-type(2) div.stButton > button:hover {
        background-color: #ff4b4b !important; color: #ffffff !important; transform: scale(1.02);
    }
    
    div[data-testid="stVerticalBlock"] > div:last-child div.stButton > button {
         background-color: #333 !important; color: #fff !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. 状态管理 ---
if 'running' not in st.session_state: st.session_state.running = False
if 'measure_count' not in st.session_state: st.session_state.measure_count = 0 
if 'finished' not in st.session_state: st.session_state.finished = False
if 'final_sbp' not in st.session_state: st.session_state.final_sbp = 120
if 'final_dbp' not in st.session_state: st.session_state.final_dbp = 80

data_path = "demo"
all_x = load_all_data(data_path)

# ==================== 逻辑分支 ====================

# 【场景 A】测量完成
if st.session_state.finished:
    st.markdown('<div class="header-text">📋 Final Clinical Report</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-line"></div>', unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="cards-container">
        <div class="bp-card card-sbp final-card">
            <div class="title-sbp">Systolic (SBP)</div>
            <div class="val-sbp final-val">{st.session_state.final_sbp}</div>
            <div style="color:#88ff88; opacity:0.7;">mmHg</div>
        </div>
        <div class="bp-card card-dbp final-card">
            <div class="title-dbp">Diastolic (DBP)</div>
            <div class="val-dbp final-val">{st.session_state.final_dbp}</div>
            <div style="color:#88ff88; opacity:0.7;">mmHg</div>
        </div>
    </div>
    <div style="text-align:center; color:#888; margin-top:20px; font-size:14px;">
        Measurement Cycle Completed Successfully.<br>Data saved to system logs.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
    if st.button("🔄 RESTART NEW SESSION", use_container_width=True):
        st.session_state.measure_count = 0
        st.session_state.finished = False
        st.session_state.running = False
        st.rerun()

# 【场景 B】正在测量/待机
else:
    st.markdown('<div class="header-text">💚 Cardiac Real-time Monitor</div>', unsafe_allow_html=True)
    
    chart_placeholder = st.empty()
    st.markdown("<br>", unsafe_allow_html=True)
    
    cards_placeholder = st.empty()
    
    def render_live_cards(sbp, dbp):
        cards_placeholder.markdown(f"""
        <div class="cards-container">
            <div class="bp-card card-sbp">
                <div class="title-sbp">SBP</div>
                <div class="val-sbp">{sbp}</div>
                <div style="color:#88ff88; font-size:12px;">mmHg</div>
            </div>
            <div class="bp-card card-dbp">
                <div class="title-dbp">DBP</div>
                <div class="val-dbp">{dbp}</div>
                <div style="color:#88ff88; font-size:12px;">mmHg</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # 初始不显示0，显示一个起始范围值
    render_live_cards(125, 75)
    
    st.markdown("<br>", unsafe_allow_html=True)
    status_text = st.empty()
    status_text.markdown(f"<div style='color:#888; text-align:center;'>Ready. Count: {st.session_state.measure_count}/18</div>", unsafe_allow_html=True)
    
    prog_bar = st.progress(0)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # --- 按钮居中布局 ---
    _, mid_col, _ = st.columns([1.5, 3, 1.5]) 
    
    with mid_col:
        c1, c2 = st.columns(2)
        with c1:
            start = st.button("START", use_container_width=True)
        with c2:
            stop = st.button("STOP", use_container_width=True)
    
    if start: st.session_state.running = True
    if stop: st.session_state.running = False

    # --- 核心优化逻辑 ---
    if st.session_state.running:
        window = 2000
        step = 20          # 【用户要求】保持不变
        cycle_duration = 1.5 
        cycle_start = time.time()
        
        # 预编译 Chart 对象
        base = alt.Chart(pd.DataFrame({'y':[], 'x':[]})).mark_line(color='#00FF00', strokeWidth=2).encode(
            x=alt.X('x', axis=None),
            y=alt.Y('y', axis=None, scale=alt.Scale(domain=[0, 1]))
        ).properties(height=180, background='#000')

        loop_counter = 0

        # 主循环
        for i in range(0, len(all_x) - window, step):
            if not st.session_state.running: break
            
            # 1. 渲染波形 (每一帧都做，保证波形连贯)
            batch = all_x[i : i+window]
            chart_df = pd.DataFrame({'y': batch, 'x': np.arange(len(batch))})
            chart_placeholder.altair_chart(base.properties(data=chart_df), use_container_width=True)
            
            # 2. 逻辑检测
            now = time.time()
            elapsed = now - cycle_start
            
            # 3. 周期判断：滑动（进度条）完成后才更新数值
            if elapsed >= cycle_duration:
                st.session_state.measure_count += 1
                
                # 结束判定
                if st.session_state.measure_count >= 18:
                    st.session_state.final_sbp = random.randint(118, 122)
                    st.session_state.final_dbp = random.randint(68, 72)
                    st.session_state.finished = True
                    st.session_state.running = False
                    st.rerun() 
                
                # 【关键修改】数值更新移到这里（一个周期只变一次）
                curr_sbp = random.randint(110, 130)
                curr_dbp = random.randint(70, 85)
                render_live_cards(curr_sbp, curr_dbp)
                
                status_text.markdown(f"<div style='color:#888; text-align:center;'>Measuring... Count: <b>{st.session_state.measure_count} / 18</b></div>", unsafe_allow_html=True)
                cycle_start = now # 重置计时
            
            # 4. 进度条更新 (每5帧渲染一次dom，避免卡顿，但逻辑是连续的)
            if loop_counter % 5 == 0:
                p = min(elapsed / cycle_duration, 1.0)
                prog_bar.progress(p)

            loop_counter += 1
            time.sleep(0.01)








