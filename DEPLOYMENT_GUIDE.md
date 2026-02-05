# 部署指南：Ubuntu + Streamlit + Nginx

本指南適用於 Ubuntu 22.04+ 環境，建議使用 **Web Mode (多人隔離模式)** 以支援多用戶操作。

## 1. 系統環境準備 (Installation)
安裝 Python 3.10 與必要的虛擬環境工具：

```bash
# 1. 更新套件清單
sudo apt update

# 2. 安裝 pip 與 venv (python 3.10)
sudo apt install -y python3-pip python3.10-venv

# 3. 建立專案目錄
sudo mkdir -p /opt/pptxgantt
sudo chown $USER:$USER /opt/pptxgantt  # 暫時改為目前用戶以便上傳
```

## 2. 專案檔案部署
請將下列檔案上傳至 `/opt/pptxgantt/`：
- `gantt_app.py`
- `pptx_generator.py`
- `tasks.json` (若沒有請建立空檔 `echo "{}" > tasks.json`)

**目錄結構確認**:
```text
/opt/pptxgantt/
├── venv/                 # (稍後建立)
├── gantt_app.py          # 主程式
├── pptx_generator.py     # 核心邏輯
└── tasks.json            # 僅為相容性保留
```

## 3. 安裝 Python 套件
```bash
cd /opt/pptxgantt

# 1. 建立虛擬環境
python3 -m venv venv

# 2. 安裝相依套件
./venv/bin/pip install streamlit pandas python-pptx
```

## 4. Systemd Service 設定
設定開機自啟服務，並**啟用 Web Mode**。

**建立檔案**: `sudo nano /etc/systemd/system/pptxgantt.service`

```ini
[Unit]
Description=Streamlit PPTX Gantt Service (Web Mode)
After=network.target

[Service]
# 建議使用一般使用者，例如 ubuntu
User=ubuntu
WorkingDirectory=/opt/pptxgantt

# [關鍵] 啟動指令：加入 -- --web 參數啟用多用戶 Web 模式
# Web 模式功能：不寫入硬碟、啟用上傳/下載、Session 隔離
ExecStart=/opt/pptxgantt/venv/bin/streamlit run gantt_app.py --server.port 8501 --server.baseUrlPath /pptxgantt --server.headless true -- --web

Restart=always

[Install]
WantedBy=multi-user.target
```

**啟動服務**:
```bash
sudo systemctl daemon-reload
sudo systemctl enable pptxgantt
sudo systemctl start pptxgantt
```

## 5. Nginx 反向代理設定
**編輯**: `sudo nano /etc/nginx/sites-available/default`

```nginx
location /pptxgantt/ {
    proxy_pass http://127.0.0.1:8501/pptxgantt/;
    proxy_http_version 1.1;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header Host $host;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_read_timeout 86400;
}
```

**重啟 Nginx**:
```bash
sudo systemctl restart nginx
```

## 6. 使用權限說明
- **Web Mode** (`-- --web`):
  - 伺服器**不儲存**任何資料，`tasks.json` 僅作為佔位符或預設值讀取。
  - 不需要特殊的寫入權限，安全性最高。
  - 使用者必須透過 **「📥 下載專案檔」** 保存進度。

- **Local Mode** (移除 start 指令中的 `-- --web`):
  - 伺服器會嘗試寫入 `tasks.json`。
  - 需確保 Service User (如 ubuntu) 對該檔案有寫入權限：
    ```bash
    sudo chown ubuntu:ubuntu /opt/pptxgantt/tasks.json
    sudo chmod 664 /opt/pptxgantt/tasks.json
    ```

