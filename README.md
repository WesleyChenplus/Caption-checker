# Caption Checker

Professional AI Dataset Caption Editing & Translation Tool
專業 AI Dataset Caption 編輯與翻譯工具

---

## Features / 功能特色

* Image Preview / 圖像預覽
* Dataset Caption Editing / Dataset 標籤編輯
* Multi-language Translation / 多語系翻譯
* Search & Replace / 搜尋與取代
* Dataset Metadata Management / Dataset 狀態管理
* Batch Tag Copy & Paste / 批次標籤複製貼上
* Keyboard Shortcut Workflow / 快捷鍵工作流
* Auto Folder Refresh / 自動資料夾同步

---

## Supported Formats / 支援格式

```text
PNG
JPG / JPEG
WEBP
BMP
```

---

## Screenshot / 程式畫面

### Main UI

```markdown
![Main UI](https://raw.githubusercontent.com/WesleyChenplus/Caption-checker/main/screenshots/main_ui.png)
```

### Translation Workflow

```markdown
![Translation](https://raw.githubusercontent.com/WesleyChenplus/Caption-checker/main/screenshots/translation_ui.png)
```

### Search & Replace

```markdown
![Search](https://raw.githubusercontent.com/WesleyChenplus/Caption-checker/main/screenshots/search_replace.png)
```

> Put your screenshots inside:
>
> ```text
> /screenshots/
> ```
>
> 請將畫面截圖放入：
>
> ```text
> /screenshots/
> ```

---

## Installation / 安裝方式

### Clone Repository

```bash
git clone https://github.com/WesleyChenplus/Caption-checker.git
```

---

### Install Dependencies

```bash
pip install pillow deep-translator
```

---

### Run

```bash
python dataset_tagger.py
```

---

## Main Functions / 主要功能

### Dataset Caption Editing / Dataset 標籤編輯

* Edit captions directly

* Original caption protection

* Translation preview panel

* 直接編輯 Caption

* 原始內容唯讀保護

* 翻譯預覽區

---

### Translation System / 翻譯系統

Supports:

* Google Translator
* MyMemory Translator

支援：

* Google 翻譯
* MyMemory 翻譯

---

### Search & Replace / 搜尋與取代

Shortcut:

```text
Ctrl + F
```

Supports:

* Find
* Replace
* Replace All
* Highlight All

支援：

* 尋找
* 取代
* 全部取代
* 全部高亮

---

### File Search / 檔案搜尋

Shortcut:

```text
Ctrl + Alt + F
```

Quickly locate files inside large datasets.

快速搜尋大型 Dataset 中的檔案。

---

### Status Management / 狀態管理

Supports:

* Completed
* Reviewed
* Unmarked

支援：

* 已完成
* 不需修改
* 未標記

---

### Batch Tag Operations / 批次標籤操作

* Copy tags

* Paste tags to multiple files

* 複製標籤

* 批次貼上到多個檔案

---

## Hotkeys / 快捷鍵

| Shortcut       | Function              |
| -------------- | --------------------- |
| Ctrl + S       | Save                  |
| Ctrl + T       | Translate             |
| Alt + T        | Reverse Translate     |
| Ctrl + F       | Find / Replace        |
| Ctrl + Alt + F | Search File           |
| Alt + ↑ / ↓    | Previous / Next Image |
| Ctrl + H       | Toggle File List      |

---

## Designed For / 適用用途

* Stable Diffusion Dataset

* LoRA Training Dataset

* Caption Cleanup

* Prompt Translation

* AI Dataset Workflow

* Stable Diffusion Dataset

* LoRA 訓練資料集

* Caption 清洗

* Prompt 翻譯

* AI Dataset 工作流

---

## Dependencies / 相依套件

```text
Pillow
deep-translator
tkinter
```

---

## License / 授權

MIT License

---

## Repository

GitHub:

```text
https://github.com/WesleyChenplus/Caption-checker
```
