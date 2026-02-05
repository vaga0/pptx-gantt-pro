# 部署指南：Ubuntu + Streamlit + Nginx

本指南適用於 Ubuntu 22.04+ 環境，並啟用 **Web Mode (多人隔離模式)**。

## 1. 系統環境準備 (Installation)
安裝 Python 3.10 基礎環境：

```bash
# 1. 更新套件清單
sudo apt update

# 2. 安裝 pip 與 venv
sudo apt install -y python3-pip python3.10-venv

# 3. 建立專案目錄
sudo mkdir -p /opt/pptxgantt
sudo chown $USER:$USER /opt/pptxgantt
```

## 2. 專案檔案部署
上傳下列檔案至 `/opt/pptxgantt/`：
- `gantt_app.py`
- `pptx_generator.py`
- `requirements.txt` (若有)

*注意：Web Mode 不需要 `tasks.json`，也不需要對該檔案的寫入權限。*

## 3. 安裝 Python 套件
```bash
cd /opt/pptxgantt
python3 -m venv venv
./venv/bin/pip install streamlit pandas python-pptx
```

## 4. Systemd Service 設定
設定開機自啟服務，透過 `-- --web` 參數啟用 Web Mode。

**建立檔案**: `sudo nano /etc/systemd/system/pptxgantt.service`

```ini
[Unit]
Description=Streamlit PPTX Gantt Service (Web Mode)
After=network.target

[Service]
# 建議建立專用使用者，例如 magento 或 www-data
User=magento
WorkingDirectory=/opt/pptxgantt

# 啟動指令：加入 -- --web 參數啟用 Web Mode
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
sudo systemctl status pptxgantt
```

## 5. Nginx 反向代理設定
**編輯設定**: `sudo nano /etc/nginx/sites-available/default`

在 `server { ... }` 區塊中加入：

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

## 6. 使用說明 (Web Mode)
- **資料儲存**: 伺服器**不儲存**任何資料。
- **保存進度**: 請使用者點擊側邊欄的 **「📥 下載專案檔」**。
- **恢復進度**: 下次使用時，請點擊 **「📤 上傳專案檔」** 還原工作。

## 7. 使用 local Mode 的權限除錯
如果網頁顯示無法儲存資料，請修正 `tasks.json` 權限：
```bash
# 確保 Service 使用者 (如 ubuntu) 對檔案有寫入權限
sudo chown ubuntu:ubuntu /opt/pptxgantt/tasks.json
sudo chmod 664 /opt/pptxgantt/tasks.json
```
