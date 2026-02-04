# PPTX 甘特圖產生器 (Gantt to PPTX Generator)

這是一個基於 Streamlit 開發的網頁應用程式，用於快速產生專業且對齊精準的 PowerPoint 甘特圖報告。

## 🚀 快速啟動

### 1. 安裝環境
確保您的系統已安裝 Python 3.8+，並安裝相關依賴套件：
```bash
pip install streamlit pandas python-pptx
```

### 2. 執行程式
在終端機執行：
```bash
streamlit run gantt_app.py
```
或在 Windows 環境下直接執行 `run_gantt.bat`。

---

## 🌐 伺服器配置與通訊埠 (Port) 設定

本程式基於 Streamlit 框架，預設使用 **8501** 通訊埠。

### 1. 自動通訊埠切換
如果系統偵測到 **8501** 已被其他程式佔用，Streamlit 會**自動嘗試下一個可用通訊埠**（例如 8502, 8503...），並在啟動時的終端機畫面上顯示當前使用的 URL。

### 2. 手動指定通訊埠 (SOP)
若您需要固定在特定的通訊埠執行，請在啟動指令中加入 `--server.port` 參數：

- **命令列方式**：
  ```bash
  # 方式 A: 直接使用 streamlit 指令
  streamlit run gantt_app.py --server.port 8080

  # 方式 B: 使用 python -m 啟動 (推薦，最穩定)
  python -m streamlit run gantt_app.py --server.port 8080
  ```
- **EXE 封裝後**：
  執行檔亦支援參數傳遞，打開 CMD 並輸入：
  ```bash
  GanttGenerator.exe --server.port 8080
  ```

---

## 📂 檔案架構與作用

- **`gantt_app.py`**: 
  - 主程式介面（Streamlit）。
  - 負責使用者輸入、資料 CRUD、以及呼叫產生邏輯。
  - 實作資料自動持久化，所有異動都會即時同步至 `tasks.json`。
- **`pptx_generator.py`**:
  - 核心 PPTX 產生引擎。
  - 使用 `python-pptx` 函式庫。
  - 採用 **Grid-Based (儲存格網格化)** 渲染策略，解決傳統浮動圖形容易跑版的問題。
- **`build_tool.py`**:
  - 自動封裝工具。執行後可產生不需安裝 Python 即可執行的 `.exe` 檔。
- **`exe_wrapper.py`**:
  - 封裝用的啟動入口腳本。
- **`tasks.json`**:
  - 本地資料庫。以 JSON 格式儲存專案主題、基準日期及所有任務內容。
- **`run_gantt.bat`**:
  - Windows 方便啟動指令檔。

---

## 📦 如何打包成獨立執行檔 (.exe)

如果您希望將程式交給沒有安裝 Python 的使用者，可以將其封裝為轉執行檔：

### 1. 安裝封裝工具
```bash
pip install pyinstaller
```

### 2. 執行封裝指令
在 `pptxGenerate` 目錄下執行：
```bash
python build_tool.py
```

### 3. 取得成果
執行完成後，您會在產生的 **`dist`** 資料夾中找到 **`GanttGenerator.exe`**。將此檔案交給使用者即可直接執行。

> **注意：** 由於 Streamlit 包含網頁伺服器組件，單一 EXE 檔案較大（約 150MB+），且啟動時需要解壓縮，初次執行約需等待 5-10 秒。

### 4. 疑難排解 (Troubleshooting)

如果您在執行 `.exe` 時遇到 `ImportError`（尤其是關於 `numpy` 或 `pandas`）：
1. **升級工具**：確保您的 PyInstaller 是最新版本：
   ```bash
   pip install --upgrade pyinstaller
   ```
2. **重新封裝**：刪除 `build` 與 `dist` 資料夾後，再次執行 `python build_tool.py`。
3. **環境建議**：建議在乾淨的虛擬環境 (venv) 中進行封裝，以避免系統路徑衝突。

---

## 🤖 給未來 AI / 開發者的技術筆記

### 1. 排版策略 (Alignment Strategy)
為了在 PowerPoint 行高自動撐開（例如文字過長換行）時仍能維持對齊，本程式棄用了直接計算座標的「浮動圖形」方案。
- **表格結構**：產生一個固定 31 欄的表格（6 欄資訊 + 25 欄日期格）。
- **進度條實作**：使用儲存格背景填色 (`cell.fill`) 與合併 (`cell.merge`)。這保證了進度條永遠與該列的文字內容同步收縮，100% 不跑版。

### 2. 日期邏輯 (Date Logic)
- **視覺範圍**：以「基準日期」為中心，自動檢索前後共 5 週的範圍（週一至週五）。
- **進度分段**：進度條會根據「今天」進行分段渲染：
  - 今天之前：深藍色。
  - 今天之後：淡藍色。
- **排除假日**：網格僅顯示工作天（Mon-Fri），日期計算時會自動跳過週末。

### 3. 未來擴充建議
- 若要調整欄位寬度，請修改 `pptx_generator.py` 中的 `INFO_COL_WIDTHS` 常數。
- 專案目前的投影片設定為 Widescreen (16:9)，尺寸為 13.33 x 7.5 英吋。
