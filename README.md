# Caption-checker
An efficient, keyboard-driven dataset tagging and translation tool for AI image generation. Features non-destructive metadata tracking, batch operations, and smart UI language detection.


Dataset Tagger & Translator

一個專為 AI 圖像資料集（Dataset）製作流程設計的桌面工具，整合：

圖像預覽
標籤（Tags / Caption）編輯
多語系翻譯
搜尋 / 取代
資料集整理
完成狀態管理
快捷鍵操作
批次複製貼上

適合用於：

Stable Diffusion Dataset 製作
LoRA / LyCORIS 訓練前整理
Danbooru Tags 整理
自動 Caption 後人工修正
多語系 Prompt 翻譯
AI 圖像資料清洗與校正

<img width="2559" height="1390" alt="image" src="https://github.com/user-attachments/assets/70fb9e29-8bd3-42b1-87e4-9e568ee5a77f" />
<img width="2560" height="1392" alt="image" src="https://github.com/user-attachments/assets/17a3104b-44f9-4911-a9d6-df459acc8898" />

核心功能說明
1. 圖像資料集瀏覽系統

支援以下圖片格式：

PNG
JPG / JPEG
WEBP
BMP

開啟資料夾後會：

自動掃描所有圖片
建立左側圖片列表
對應讀取同名 .txt
顯示最後編輯時間
自動套用完成狀態

例如：

image_001.png
image_001.txt

會自動配對。

2. 即時圖片預覽

選擇圖片後：

即時顯示圖片
自動縮圖（thumbnail）
支援大尺寸圖片
保持操作流暢

功能特點：

雙擊圖片可自動定位左側列表
支援快速上下切換圖片
可作為 Dataset QA 檢查工具使用

<img width="2560" height="1392" alt="image" src="https://github.com/user-attachments/assets/05a99556-751d-4c88-8c95-03b38f294218" />

3. 三欄式標籤工作區

程式核心設計之一。

右上：原始標籤（唯讀）

用途：

保留原始 Caption
防止誤覆寫
可作為還原來源

特性：

唯讀保護
不可直接修改

左下：標籤編輯區

主要工作區。

可進行：
Caption 修正
Tags 清理
Prompt 補完

支援：

Undo
Copy / Paste
搜尋
取代


右下：翻譯預覽區

用途：
翻譯結果檢視
多語系 Caption 編輯
Prompt 翻譯

可與編輯區互相覆寫。

4. 多語系介面系統

內建：

繁體中文
簡體中文
English

程式會：

自動偵測系統語言
Windows 使用 UI Language API
Linux / macOS 使用 locale 偵測

會自動切換：

UI
提示文字
Tooltip
熱鍵說明
功能名稱

使用：

Google Translate

支援：

自動語言偵測
正向翻譯
反向翻譯
一鍵覆寫
支援語言

包含：

英文
繁中
簡中
日文
韓文
法文
德文
西班牙文


翻譯工作流
正向翻譯
編輯區 → 翻譯區

適合：

英文 tags → 中文說明
Dataset 檢查
更正LLM自動標註Caption的錯誤內容

反向翻譯
翻譯區 → 編輯區

適合：

特定語系 caption 譯文 → 英文訓練 caption
多語系資料集統一


6. Metadata 狀態管理系統

程式會建立：

.tagger_meta.json

用途：

儲存完成狀態
編輯時間
檔案標記
狀態類型

completed
已完成。

reviewed
不需修改。

none
未處理。

特殊功能
最近編輯的前五個檔案：

會自動高亮
使用不同顏色排名
方便快速回到工作區

7. 自動刷新監控：

可視需要選用
自動更新目前資料集文件夾內容，適合在LLM進行自動標記，持續產生新文件檔案時，同時使用

功能：
每 5 分鐘掃描資料夾
自動同步新圖片
更新列表

適合：
自動 Caption Pipeline
批次生成流程
外部程式持續輸出 Dataset


8. 檔案搜尋系統
<img width="2559" height="1392" alt="image" src="https://github.com/user-attachments/assets/1f637589-c8c8-46d8-bb96-af59347baef9" />

快捷鍵：

Ctrl + Alt + F

功能：

即時搜尋檔名
自動定位
支援上下跳轉

適合：

大型 Dataset
特定檔案
針對性編輯

9. 內文搜尋 / 取代系統
<img width="2559" height="1391" alt="image" src="https://github.com/user-attachments/assets/4c2edd6f-ea1d-4ed0-8c78-789e6c097a8d" />

快捷鍵：

Ctrl + F

支援：

尋找下一個
單次取代
全部取代
高亮特定文字

<img width="2559" height="1288" alt="image" src="https://github.com/user-attachments/assets/f90b70cd-1cb9-4608-a6c9-8cc1856144bf" />


可搜尋：

編輯區
翻譯區

適合：

Tag 標準化
批次修正
Prompt 清洗

例如：

1girl → solo female

10. 批次標籤複製貼上

功能：

Copy Tags

複製目前 Tags。

Paste Tags to Selection

將 Tags 批次套用到多張圖片。
<img width="1557" height="1392" alt="image" src="https://github.com/user-attachments/assets/86e0865b-89aa-4a30-96bb-b5c2210405de" />

適合：

同角色
同場景
同系列圖片

大幅降低重複工作量。

11. 字體縮放系統

快捷鍵：

Ctrl + Alt + +
Ctrl + Alt + -
Ctrl + Alt + *

功能：

放大文字
縮小文字
重設字體

適合：

長 Caption
高 DPI 螢幕
多螢幕工作環境
12. 完整快捷鍵系統
基本操作
快捷鍵	功能
Ctrl + S	儲存
Ctrl + T	正向翻譯
Alt + T	反向翻譯
Ctrl + H	顯示/隱藏列表
導航
快捷鍵	功能
Alt + ↑	上一張
Alt + ↓	下一張
Alt + L	跳到最後編輯
狀態管理
快捷鍵	功能
Alt + M	標記完成
Alt + N	標記不需修改
Alt + U	清除標記
搜尋
快捷鍵	功能
Ctrl + F	搜尋/取代
Ctrl + Alt + F	搜尋檔案
13. Dataset 工作流定位

這個工具非常明顯是為：

Stable Diffusion
LoRA
Anime Dataset
Booru Tagging
AI Caption Cleanup

設計的。

典型工作流程
LoRA Dataset 製作
BLIP / WD14 自動 Caption
        ↓
匯入本工具
        ↓
人工修正
        ↓
翻譯與標準化
        ↓
完成標記
        ↓
輸出 Dataset
技術架構
GUI
tkinter
ttk
圖像處理
Pillow (PIL)
翻譯
deep_translator
GoogleTranslator
MyMemoryTranslator
程式特色

針對 Dataset Workflow 設計
可以同時檢視圖片與caption，並直接編輯，不需要在多個視窗間反覆切換，提昇人工訂正caption的工作效率

適用於

Caption
不同語言caption標註的翻譯
大量資料的編輯狀態管理
Dataset 建立


高效率鍵盤導向

快捷鍵設計用意：

高頻率資料處理
長時間標記工作
Dataset 工廠式流程
對大型資料集友善
能有效處理大量圖片。

適合的使用者
AI 訓練資料集製作者
LoRA 訓練工作室
AI 美術工作流
Dataset 清洗人員
Prompt 工程師
多語系 Caption 整理者
