import streamlit.web.cli as stcli
import os, sys

def resolve_path(path):
    # For PyInstaller's Temp folder during execution
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, path)
    return os.path.abspath(path)

if __name__ == "__main__":
    # Streamlit requires the script path to be absolute or relative to CWD
    # When bundled, we tell Streamlit to run the bundled gantt_app.py
    app_path = resolve_path("gantt_app.py")
    
    sys.argv = [
        "streamlit",
        "run",
        app_path,
        "--global.developmentMode=false",
    ]
    sys.exit(stcli.main())
