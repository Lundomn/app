import streamlit as st
import numpy as np
import scipy.io
import os
import time
import random
import pandas as pd

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
    if not os.path.exists(data_folder):
        return None
    scg_dir = sorted([f for f in os.listdir(data_folder) if f.endswith('.mat')], key=sort_by_time)
    all_x_list = []
    # 读取前20个文件
    for scg_file in scg_dir[:20]: 
        x = scgload(os.path.join(data_folder, scg_file))
        if len(x) > 0:
            all_x_list.extend(x)
    return np.array(all_x_list)

# --- 2. 界面样式配置 (CSS) ---
st.set_page_config(page_title="SCG 监测系统", layout="centered")

st.markdown("""
<style>
    .card-sbp {
        background-color: #FFE4E1;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        margin-bottom: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    .card-dbp {
        background-color: #E0F2F1;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        margin-bottom: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    .card-title { font-size: 16px; font-weight: bold; margin-bottom: 5px; }
    .card-value { font-size: 36px; font-weight: bold; line-height: 1.2; }
    .card-unit { font-size: 12px; margin-top: 5px; }
</style>
""", unsafe_allow_html=True)

st.title("❤️ SCG 真实数据监测")

# 加载数据
data_path = "demo" # 请确保这里跟你的文件夹名一致
all_x = load_all_data(data_path)

if all_x is None or len(all_x) == 0:
    st.error(f"未在 '{data_path}' 文件夹中发现数据。")
    st.stop()

# --- 3. 控制区域 ---
st.markdown("---")
# 使用 checkbox 作为 开始/暂停 开关
run_monitor = st.checkbox('👉 开启实时监测 (Start/Pause)', value=False)

# 初始化占位符
st.subheader("Real-time Signal")
chart_placeholder = st.empty()

col1, col2 = st.columns(2)
with col1:
    sbp_placeholder = st.empty()
with col2:
    dbp_placeholder = st.empty()

# --- 4. 核心循环逻辑 ---
window_size = 500
step = 10         # 减小步长，让波形移动更细腻（减慢速度因素1）
sleep_time = 0.05 # 增加睡眠时间，减慢刷新频率（减慢速度因素2）

# 初始化血压数值（默认值）
current_sbp = 120
current_dbp = 60
last_bp_update_time = time.time() # 记录上一次更新血压的时间

# 如果用户没有勾选开始，就只显示静态画面或空
if not run_monitor:
    st.info("请勾选上方复选框开始监测。")
else:
    # 循环播放数据
    for i in range(0, len(all_x) - window_size, step):
        
        # 0. 检查是否被用户按了暂停
        # 这里的技巧是：Streamlit 每次交互都会重跑脚本，
        # 如果用户中途取消勾选，虽然这个 for 循环不会立即断开，
        # 但我们可以在这里强制让它停止更新图表，或者退出。
        # (注：Streamlit 原生机制里，取消勾选会直接重置整个脚本，所以循环会自动停掉)
        
        # 1. 更新波形
        batch_data = all_x[i : i + window_size]
        chart_placeholder.line_chart(
            pd.DataFrame(batch_data, columns=["SCG"]), 
            height=250,
            color="#555555"
        )

        # 2. 血压更新逻辑 (5秒一次)
        now = time.time()
        # 只有当 (当前时间 - 上次更新时间) > 5秒 时，才改变数值
        if now - last_bp_update_time > 5.0:
            current_sbp = random.randint(118, 122)
            current_dbp = random.randint(58, 62)
            last_bp_update_time = now # 重置计时器

        # 3. 渲染卡片 (每一帧都要渲染，否则卡片会消失，但数值只在5秒时变)
        sbp_placeholder.markdown(f"""
            <div class="card-sbp">
                <div class="card-title" style="color: #8B0000;">SBP</div>
                <div class="card-value" style="color: #8B0000;">{current_sbp}</div>
                <div class="card-unit" style="color: #8B0000;">mmHg<br>❤️ Raised</div>
            </div>
        """, unsafe_allow_html=True)

        dbp_placeholder.markdown(f"""
            <div class="card-dbp">
                <div class="card-title" style="color: #006400;">DBP</div>
                <div class="card-value" style="color: #006400;">{current_dbp}</div>
                <div class="card-unit" style="color: #006400;">mmHg<br>❤️ Normal</div>
            </div>
        """, unsafe_allow_html=True)

        # 4. 速度控制
        time.sleep(sleep_time)