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
    .bp-
