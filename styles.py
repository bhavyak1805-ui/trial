GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {
    --bg:       #04040a;
    --surface:  #0d0d18;
    --surface2: #13131f;
    --surface3: #1c1c2e;
    --border:   #ffffff0f;
    --border2:  #ffffff18;
    --accent:   #7c6fff;
    --accent2:  #ff6b9d;
    --cyan:     #22d3ee;
    --text:     #f0f0fa;
    --text2:    #a0a0c0;
    --muted:    #606080;
    --success:  #10b981;
    --error:    #f43f5e;
    --warn:     #f59e0b;
    --gold:     #fbbf24;
}

*, *::before, *::after { box-sizing: border-box; }

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}
.stApp { background: var(--bg) !important; }
.main .block-container { padding-top: 1.5rem !important; max-width: 1400px !important; }

::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: var(--surface); }
::-webkit-scrollbar-thumb { background: var(--accent); border-radius: 4px; }

.stTabs [data-baseweb="tab-list"] {
    background: var(--surface2) !important; border-radius: 14px !important;
    border: 1px solid var(--border2) !important; padding: 5px !important; gap: 3px !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 10px !important; color: var(--muted) !important;
    font-weight: 500 !important; font-size: 0.82rem !important;
    padding: 9px 22px !important; transition: all 0.2s !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, var(--accent), #9b8fff) !important;
    color: white !important; box-shadow: 0 4px 15px #7c6fff44 !important;
}
.stTabs [data-baseweb="tab-panel"] { padding-top: 1.5rem !important; }

.stTextInput input, .stTextArea textarea, .stSelectbox > div > div, .stNumberInput input {
    background: var(--surface3) !important; border: 1px solid var(--border2) !important;
    border-radius: 10px !important; color: var(--text) !important;
    font-family: 'Inter', sans-serif !important; font-size: 0.875rem !important;
    transition: all 0.2s !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: var(--accent) !important; box-shadow: 0 0 0 3px #7c6fff22 !important;
    background: var(--surface2) !important;
}
label { color: var(--text2) !important; font-size: 0.8rem !important; font-weight: 500 !important; }

.stButton button {
    background: linear-gradient(135deg, var(--accent) 0%, #9b6fff 100%) !important;
    color: white !important; border: none !important; border-radius: 10px !important;
    font-weight: 600 !important; font-size: 0.85rem !important; letter-spacing: 0.3px !important;
    padding: 0.55rem 1.5rem !important; transition: all 0.25s cubic-bezier(0.4,0,0.2,1) !important;
    box-shadow: 0 2px 12px #7c6fff33 !important;
}
.stButton button:hover {
    transform: translateY(-2px) !important; box-shadow: 0 8px 28px #7c6fff55 !important;
    background: linear-gradient(135deg, #8b7fff 0%, #a87fff 100%) !important;
}
.stButton button:active { transform: translateY(0) !important; }

section[data-testid="stSidebar"] {
    background: var(--surface) !important; border-right: 1px solid var(--border2) !important;
}

.card {
    background: var(--surface2); border: 1px solid var(--border2);
    border-radius: 16px; padding: 1.4rem 1.6rem; margin-bottom: 1rem;
}
.card-sm {
    background: var(--surface3); border: 1px solid var(--border);
    border-radius: 12px; padding: 1rem 1.2rem; margin-bottom: 0.6rem;
}
.card-header {
    font-size: 0.65rem; font-family: 'JetBrains Mono', monospace;
    color: var(--accent); letter-spacing: 3px; text-transform: uppercase;
    margin-bottom: 1.1rem; display: flex; align-items: center; gap: 6px;
}
.card-header::before {
    content: ''; display: inline-block; width: 3px; height: 12px;
    background: var(--accent); border-radius: 2px;
}

.badge {
    display: inline-flex; align-items: center; background: #7c6fff18;
    color: #a78bfa; border: 1px solid #7c6fff33; border-radius: 20px;
    padding: 3px 11px; font-size: 0.7rem; font-family: 'JetBrains Mono', monospace;
    font-weight: 500; gap: 4px;
}
.badge.green  { background:#10b98118; color:#34d399; border-color:#10b98133; }
.badge.red    { background:#f43f5e18; color:#fb7185; border-color:#f43f5e33; }
.badge.orange { background:#f59e0b18; color:#fbbf24; border-color:#f59e0b33; }
.badge.cyan   { background:#22d3ee18; color:#67e8f9; border-color:#22d3ee33; }
.badge.pink   { background:#ff6b9d18; color:#f9a8d4; border-color:#ff6b9d33; }

.skill-chip {
    display: inline-flex; align-items: center;
    background: linear-gradient(135deg,#7c6fff15,#9b6fff15);
    color: #c4b5fd; border: 1px solid #7c6fff33; border-radius: 8px;
    padding: 4px 12px; font-size: 0.72rem; font-weight: 500;
    margin: 3px; transition: all 0.2s;
}
.skill-chip.green { background:#10b98115; color:#34d399; border-color:#10b98133; }
.skill-chip.red   { background:#f43f5e15; color:#fb7185; border-color:#f43f5e33; }

.divider {
    display: flex; align-items: center; gap: 1rem; margin: 1.2rem 0;
    color: var(--muted); font-size: 0.72rem;
    font-family: 'JetBrains Mono', monospace; letter-spacing: 1px;
}
.divider::before, .divider::after {
    content: ''; flex: 1; height: 1px;
    background: linear-gradient(90deg, transparent, var(--border2), transparent);
}

.progress-wrap { background: var(--surface3); border-radius: 20px; height: 6px; overflow: hidden; }
.progress-fill {
    height: 100%; border-radius: 20px;
    background: linear-gradient(90deg, var(--accent), var(--accent2));
    transition: width 0.8s cubic-bezier(0.4,0,0.2,1);
    position: relative; overflow: hidden;
}
.progress-fill::after {
    content: ''; position: absolute; top: 0; left: -100%;
    width: 100%; height: 100%;
    background: linear-gradient(90deg,transparent,rgba(255,255,255,0.3),transparent);
    animation: shimmer 2s infinite;
}
@keyframes shimmer { 0%{left:-100%} 100%{left:100%} }

.module-card {
    background: var(--surface2); border: 1px solid var(--border2);
    border-radius: 18px; padding: 1.4rem 1.6rem; margin-bottom: 0.8rem;
    transition: all 0.3s cubic-bezier(0.4,0,0.2,1);
    position: relative; overflow: hidden; cursor: pointer;
}
.module-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 12px 40px rgba(124,111,255,0.15);
}

.cam-hint {
    background: linear-gradient(135deg, var(--surface3), var(--surface2));
    border: 2px dashed var(--border2); border-radius: 14px;
    padding: 1.2rem; text-align: center; color: var(--muted);
    font-size: 0.82rem; margin-bottom: 0.8rem;
}
[data-testid="stCameraInput"] > div {
    background: var(--surface3) !important; border-radius: 14px !important;
    border: 1px solid var(--border2) !important;
}

.stat-card {
    background: var(--surface2); border: 1px solid var(--border2);
    border-radius: 14px; padding: 1.1rem; text-align: center; transition: all 0.2s;
}
.stat-card:hover {
    border-color: var(--accent); box-shadow: 0 4px 20px #7c6fff22;
    transform: translateY(-2px);
}
.stat-number {
    font-size: 2rem; font-weight: 800;
    background: linear-gradient(135deg, var(--accent), var(--accent2));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; line-height: 1.1;
}
.stat-label { font-size: 0.72rem; color: var(--muted); margin-top: 4px; }

.timeline-item {
    border-left: 2px solid var(--border2); padding-left: 1.2rem;
    margin-bottom: 1.2rem; position: relative;
}
.timeline-item::before {
    content: ''; position: absolute; left: -5px; top: 6px;
    width: 8px; height: 8px; border-radius: 50%;
    background: var(--accent); box-shadow: 0 0 8px var(--accent);
}
</style>
"""