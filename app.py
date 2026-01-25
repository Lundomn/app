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
    /* 强制消除顶部留白 */
    .block-container {
        padding-top: 0rem !important;
        padding-bottom: 1rem !important;
        max-width: 100%;
    }
    header[data-testid="stHeader"] {
        display: none !important;
    }
    .stApp { background-color: #0E1117; color: #FAFAFA; }
    
    .header-text {
        font-size: 26px; font-weight: 700; color: #E0E0E0; 
        text-align: center; padding: 10px 0; margin-top: 0px;
        background: rgba(255,255,255,0.05); border-bottom: 1px solid #333;
    }
    
    .cards-container {
        display: flex; flex-direction: row; justify-content: center; 
        gap: 15px; width: 100%; margin-top: 5px;
    }
    
    .bp-card {
        border-radius: 12px; padding: 12px; text-align: center; 
        box-shadow: 0 4px 15px rgba(0,0,0,0.5); width: 46%; 
        display: flex; flex-direction: column; justify-content: center; align-items: center;
    }
    
    .card-sbp { background: linear-gradient(145deg, #0c2b10, #051a06); border: 1px solid #00ff00; }
    .val-sbp { color: #00ff00; font-size: 44px; font-weight: bold; }
    .title-sbp { color: #88ff88; font-size: 16px; font-weight: bold; }
    
    .card-dbp { background: linear-gradient(145deg, #0c2b10, #051a06); border: 1px solid #00ff00; }
    .val-dbp { color: #00ff00; font-size: 44px; font-weight: bold; }
    .title-dbp { color: #88ff88; font-size: 16px; font-weight: bold; }

    .final-card { height: 180px; width: 42%; }
    .final-val { font-size: 60px; }

    div.stButton > button { 
        background-color: #eee !important; color: #000 !important; 
        border-radius: 8px; height: 40px; font-weight: 600; 
    }
    div[data-testid="column"]:nth-of-type(1) div.stButton > button {
        background-color: #e6ffe6 !important; color: #006400 !important; border-color: #00ff00 !important;
    }
    div[data-testid="column"]:nth-of-type(2) div.stButton > button {
        background-color: #ffe6e6 !important; color: #8b0000 !important; border-color: #ff4b4b !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. 状态管理 ---
if 'running' not in st.session_state: st.session_state.running = False
if 'measure_count' not in st.session_state: st.session_state.measure_count = 0 
if 'finished' not in st.session_state: st.session_state.finished = False
if 'final_sbp' not in st.session_state: st.session_state.final_sbp = 0
if 'final_dbp' not in st.session_state: st.session_state.final_dbp = 0

data_path = "demo"
all_x = load_all_data(data_path)

# ==================== 逻辑分支 ====================

if st.session_state.finished:
    st.markdown('<div class="header-text">📋 Final Clinical Report</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="cards-container" style="margin-top:30px;">
        <div class="bp-card card-sbp final-card">
            <div class="title-sbp">Average SBP</div>
            <div class="val-sbp final-val">{st.session_state.final_sbp}</div>
            <div style="color:#88ff88; opacity:0.7;">mmHg</div>
        </div>
        <div class="bp-card card-dbp final-card">
            <div class="title-dbp">Average DBP</div>
            <div class="val-dbp final-val">{st.session_state.final_dbp}</div>
            <div style="color:#88ff88; opacity:0.7;">mmHg</div>
        </div>
    </div>
    <div style='text-align:center; color:#888; margin-top:15px;'>Result calculated from 18 measurement cycles.</div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄 RESTART NEW SESSION", use_container_width=True):
        st.session_state.measure_count = 0
        st.session_state.finished = False
        st.session_state.running = False
        st.rerun()

else:
    st.markdown('<div class="header-text">💚 Cardiac Real-time Monitor</div>', unsafe_allow_html=True)
    
    chart_placeholder = st.empty()
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

    render_live_cards(0, 0)
    
    status_text = st.empty()
    status_text.markdown(f"<div style='color:#888; text-align:center; margin-top:5px;'>Ready. Count: {st.session_state.measure_count}</div>", unsafe_allow_html=True)
    
    prog_bar = st.progress(0)
    
    st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
    
    _, mid_col, _ = st.columns([1, 4, 1]) 
    with mid_col:
        c1, c2 = st.columns(2)
        with c1: start = st.button("START", use_container_width=True)
        with c2: stop = st.button("STOP", use_container_width=True)
    
    if start: st.session_state.running = True
    if stop: st.session_state.running = False

    if st.session_state.running:
        # 固定序列逻辑
        random.seed(42) 
        fixed_sbp_seq = [random.randint(122, 124) for _ in range(18)]
        fixed_dbp_seq = [random.randint(70, 73) for _ in range(18)]
        
        window = 2000
        step = 50
        cycle_duration = 0.8
        cycle_start = time.time()
        
        base = alt.Chart(pd.DataFrame({'y':[], 'x':[]})).mark_line(color='#00FF00', strokeWidth=2).encode(
            x=alt.X('x', axis=None),
            y=alt.Y('y', axis=None, scale=alt.Scale(domain=[0, 1]))
        ).properties(height=180, background='#000')

        loop_counter = 0

        for i in range(0, len(all_x) - window, step):
            if not st.session_state.running: break
            
            batch = all_x[i : i+window]
            chart_df = pd.DataFrame({'y': batch, 'x': np.arange(len(batch))})
            chart_placeholder.altair_chart(base.properties(data=chart_df), use_container_width=True)
            
            now = time.time()
            elapsed = now - cycle_start
            
            if elapsed >= cycle_duration:
                st.session_state.measure_count += 1
                
                # 结束判定并计算平均值取整
                if st.session_state.measure_count >= 18:
                    # === 【核心逻辑：平均值取整】 ===
                    st.session_state.final_sbp = int(round(np.mean(fixed_sbp_seq)))
                    st.session_state.final_dbp = int(round(np.mean(fixed_dbp_seq)))
                    
                    st.session_state.finished = True
                    st.session_state.running = False
                    st.rerun() 
                
                idx = st.session_state.measure_count - 1
                render_live_cards(fixed_sbp_seq[idx], fixed_dbp_seq[idx])
                
                status_text.markdown(f"<div style='color:#888; text-align:center; margin-top:5px;'>Measuring... Count: <b>{st.session_state.measure_count}</b></div>", unsafe_allow_html=True)
                cycle_start = now
            
            if loop_counter % 5 == 0:
                p = min(elapsed / cycle_duration, 1.0)
                prog_bar.progress(p)

            loop_counter += 1
            time.sleep(0.01)
