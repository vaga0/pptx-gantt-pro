import os
import subprocess
import streamlit
import sys

def build():
    print("=== 開始封裝 執行檔 (.exe) ===")
    
    # 確保已安裝 PyInstaller
    try:
        import PyInstaller
    except ImportError:
        print("錯誤: 請先執行 'pip install pyinstaller' 以安裝封裝工具。")
        return

    # 取得 Streamlit 的路徑 (打包時需要包含靜態內容)
    st_path = os.path.dirname(streamlit.__file__)
    
    # 建構 PyInstaller 指令
    # --onefile: 封裝成單一檔案 (啟動較慢但好攜帶)
    # --additional-hooks-dir: 如果有特定套件需要 hook
    # --collect-all: 收集所有必要的 metadata
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--name", "GanttGenerator",
        f"--add-data={st_path}{os.pathsep}streamlit",
        "--add-data=gantt_app.py;.",
        "--add-data=pptx_generator.py;.",
        "--add-data=run_gantt.bat;.",
        "--collect-all", "streamlit",
        "--collect-all", "pptx",
        "--collect-all", "pandas",
        "--collect-all", "numpy",
        "exe_wrapper.py"
    ]
    
    print(f"執行指令: {' '.join(cmd)}")
    subprocess.run(cmd)
    
    print("\n=== 封裝完成 ===")
    print("執行檔位於: dist/GanttGenerator.exe")

if __name__ == "__main__":
    build()
