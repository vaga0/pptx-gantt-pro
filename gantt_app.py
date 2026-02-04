
import streamlit as st
import pandas as pd
import datetime
import pptx_generator
import os
import json

# --- Persistence Logic ---
DATA_FILE = "tasks.json"

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get('topic', '專案進度報告'), data.get('base_date', str(datetime.date.today())), data.get('tasks', [])
        except Exception as e:
            st.error(f"讀取資料失敗: {e}")
    return "專案進度報告", str(datetime.date.today()), []

def save_data(topic, base_date, tasks):
    data = {
        "topic": topic,
        "base_date": str(base_date),
        "tasks": tasks
    }
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        st.error(f"儲存資料失敗: {e}")

st.set_page_config(layout="wide", page_title="PPTX 甘特圖產生器")

# Hide Streamlit menu (Keep Hamburger as requested: Rerun/Settings, hide Footer/Deploy)
# "Record a screencast": Streamlit builtin to record screen video.
# "Clear cache": Clears internal cache (rarely needed for this app).
hide_menu_style = """
        <style>
        footer {visibility: hidden;}
        .stAppDeployButton {display: none;}
        </style>
        """
st.markdown(hide_menu_style, unsafe_allow_html=True)

# --- Session State Initialization ---
# Load data ONCE on startup
if 'data_loaded' not in st.session_state:
    saved_topic, saved_date, saved_tasks = load_data()
    st.session_state['topic'] = saved_topic
    st.session_state['base_date'] = datetime.datetime.strptime(saved_date, "%Y-%m-%d").date()
    st.session_state['tasks'] = saved_tasks
    st.session_state['data_loaded'] = True
    
# Init New Task fields
defaults = {
    'new_subject': '', 'new_user': '', 'new_it': '', 'new_req_id': '', 
    'new_desc': '', 'new_status': '待處理',
    'new_start': datetime.date.today(), 
    'new_end': datetime.date.today() + datetime.timedelta(days=7),
    'new_bar_text': ''
}
for k, v in defaults.items():
    if k not in st.session_state: st.session_state[k] = v

if 'edit_index' not in st.session_state: st.session_state['edit_index'] = None

# --- Callbacks ---
def auto_save():
    save_data(st.session_state['topic'], st.session_state['base_date'], st.session_state['tasks'])

def add_task_callback():
    new_task = {
        'subject': st.session_state.new_subject,
        'user': st.session_state.new_user,
        'it_contact': st.session_state.new_it,
        'req_id': st.session_state.new_req_id,
        'task_desc': st.session_state.new_desc.split('\n') if st.session_state.new_desc else [],
        'status': st.session_state.new_status,
        'start_date': st.session_state.new_start.strftime('%Y-%m-%d'),
        'end_date': st.session_state.new_end.strftime('%Y-%m-%d'),
        'bar_text': st.session_state.new_bar_text
    }
    st.session_state['tasks'].append(new_task)
    auto_save() # Auto Save on Add

def update_task_callback(idx, updated_task):
    st.session_state['tasks'][idx] = updated_task
    st.session_state['edit_index'] = None
    auto_save() # Auto Save on Edit

def delete_task_callback(idx):
    st.session_state['tasks'].pop(idx)
    if st.session_state['edit_index'] == idx:
        st.session_state['edit_index'] = None
    auto_save() # Auto Save on Delete

def reset_input_fields():
    # Only reset Session State keys for input fields
    for k, v in defaults.items():
        st.session_state[k] = v

def generate_pptx():
    if not st.session_state['tasks']:
        st.error("請先新增任務")
        return
    
    # Save before generate just in case
    auto_save()
    data = {
        'topic': st.session_state['topic'],
        'base_date': st.session_state['base_date'].strftime('%Y-%m-%d'),
        'tasks': st.session_state['tasks']
    }
    try:
        output_path = "output_gantt.pptx"
        prs = pptx_generator.create_pptx(data)
        prs.save(output_path)
        with open(output_path, "rb") as f:
            st.download_button("下載 .pptx", f, "gantt.pptx", "application/vnd.openxmlformats-officedocument.presentationml.presentation", key='top_dl')
        st.success("完成！")
    except Exception as e:
        st.error(f"錯誤: {e}")

# --- UI Layout ---
st.title("PPTX 甘特圖產生器")

col1, col2, col3 = st.columns([3, 1.5, 1.5])
with col1:
    # Bind directly to session_state keys not supported fully for text_input without on_change 
    # to update other vars. But here we just want to load initial.
    # We use key='topic_input' and on_change to sync.
    def update_meta():
        st.session_state['topic'] = st.session_state.topic_input
        st.session_state['base_date'] = st.session_state.date_input
        auto_save()

    st.text_input("專案主題", value=st.session_state['topic'], key="topic_input", on_change=update_meta, placeholder="輸入專案標題...")
with col2:
    st.date_input("基準日期", value=st.session_state['base_date'], key="date_input", on_change=update_meta)
with col3:
    st.write("") # Spacer to align button with inputs (inputs have label height)
    st.write("") 
    if st.button("🚀 產生 PPTX", type="primary", use_container_width=True):
        generate_pptx()

st.markdown("---")

# --- New Task Button & Form (Toggle) ---
if 'show_add_task' not in st.session_state:
    st.session_state['show_add_task'] = False

col_add_btn, col_spacer = st.columns([1, 5])
if st.session_state['show_add_task']:
    if col_add_btn.button("隱藏新增區塊", type="secondary"):
        st.session_state['show_add_task'] = False
        st.rerun()
else:
    if col_add_btn.button("＋ 新增任務", type="primary"):
        st.session_state['show_add_task'] = True
        st.session_state['edit_index'] = None # Close edit if open
        st.rerun()

if st.session_state['show_add_task']:
    with st.container(border=True):
        st.caption("新增任務")
        c1, c2, c3 = st.columns([2, 1, 1])
        c1.text_input("主旨", key="new_subject", placeholder="例如：新系統開發")
        c2.text_input("用戶", key="new_user")
        c3.text_input("IT窗口", key="new_it")

        c4, c5, c6 = st.columns([1, 2, 1])
        c4.text_input("需求單號", key="new_req_id")
        c5.text_area("Task 描述", key="new_desc", help="可輸入多行，輸出時將自動轉為條列項目")
        c6.selectbox("狀態", ["待處理", "開發中", "已完成"], key="new_status")

        c7, c8, c9 = st.columns([1, 1, 1])
        c7.date_input("開始日期", key="new_start")
        c8.date_input("結束日期", key="new_end")
        c9.text_input("進度條文字", key="new_bar_text", placeholder="例如: 2/5 啟動")
        
        bn1, bn2 = st.columns([1, 5])
        if bn1.button("確認新增", type="primary", on_click=add_task_callback):
            pass 
        if bn2.button("重置欄位", type="secondary", on_click=reset_input_fields):
            pass

st.markdown("---")



# --- Task List ---
if st.session_state['tasks']:
    # Headers: Subject, User, Time, Status, Action
    h_cols = st.columns([2, 1, 2, 1, 1])
    h_cols[0].write("主題")
    h_cols[1].write("用戶")
    h_cols[2].write("時間區間")
    h_cols[3].write("狀態")
    h_cols[4].write("操作")
    
    for i, task in enumerate(st.session_state['tasks']):
        # Separator line (minimal)
        st.markdown("<hr style='margin: 5px 0; border-top: 1px solid #eee;'>", unsafe_allow_html=True)
        
        if st.session_state['edit_index'] == i:
            # --- Editing Mode ---
            with st.container(border=True):
                st.caption(f"編輯中: 任務 #{i+1}")
                r1_c1, r1_c2, r1_c3 = st.columns([2, 1, 1])
                e_subj = r1_c1.text_input("主旨", value=task.get('subject', ''), key=f"e_sub_{i}")
                e_user = r1_c2.text_input("用戶", value=task['user'], key=f"e_u_{i}")
                e_it = r1_c3.text_input("IT", value=task['it_contact'], key=f"e_it_{i}")
                
                r2_c1, r2_c2, r2_c3 = st.columns([1, 2, 1])
                e_req = r2_c1.text_input("單號", value=task['req_id'], key=f"e_req_{i}")
                e_desc = r2_c2.text_area("Task描述", value="\n".join(task['task_desc']) if isinstance(task['task_desc'], list) else task['task_desc'], key=f"e_desc_{i}")
                e_stats = r2_c3.selectbox("狀態", ["待處理", "開發中", "已完成"], index=["待處理", "開發中", "已完成"].index(task.get('status', '待處理')) if task.get('status') in ["待處理", "開發中", "已完成"] else 0, key=f"e_st_{i}")
                
                r3_c1, r3_c2, r3_c3 = st.columns([1, 1, 1])
                sd = datetime.datetime.strptime(task['start_date'], '%Y-%m-%d').date()
                ed = datetime.datetime.strptime(task['end_date'], '%Y-%m-%d').date()
                e_start = r3_c1.date_input("開始", value=sd, key=f"e_sd_{i}")
                e_end = r3_c2.date_input("結束", value=ed, key=f"e_ed_{i}")
                e_bar = r3_c3.text_input("Bar文字", value=task['bar_text'], key=f"e_bt_{i}")

                b1, b2 = st.columns([1, 1])
                if b1.button("儲存", key=f"save_{i}"):
                    updated = {
                        'subject': e_subj, 'user': e_user, 'it_contact': e_it, 'req_id': e_req,
                        'task_desc': e_desc.split('\n') if e_desc else [], 'status': e_stats,
                        'start_date': e_start.strftime('%Y-%m-%d'),
                        'end_date': e_end.strftime('%Y-%m-%d'),
                        'bar_text': e_bar
                    }
                    update_task_callback(i, updated)
                    st.rerun()
                if b2.button("取消", key=f"cancel_{i}"):
                    st.session_state['edit_index'] = None
                    st.rerun()

        else:
            # --- View Mode (Compact) ---
            cols = st.columns([2, 1, 2, 1, 1])
            
            # 1. Subject
            cols[0].write(f"**{task.get('subject','')}**")
            
            # 2. User
            cols[1].write(f"{task['user']}\n({task['it_contact']})")
            
            # 3. Time
            cols[2].write(f"{task['start_date']} ~ {task['end_date']}")
            if task.get('bar_text'): cols[2].caption(f"Bar: {task.get('bar_text')}")
            
            # 4. Status
            cols[3].write(f"{task['status']}")
            
            # 5. Action
            btn_c1, btn_c2 = cols[4].columns(2)
            if btn_c1.button("✏️", key=f"edit_{i}"):
                st.session_state['edit_index'] = i
                st.session_state['show_add_task'] = False # Hide add form when editing
                st.rerun()
            if btn_c2.button("🗑️", key=f"del_{i}"):
                delete_task_callback(i)
                st.rerun()

else:
    st.info("尚無資料，請點擊上方「＋ 新增任務」。")
