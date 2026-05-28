import os
import sys
import time
import json
import locale
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, ttk, simpledialog, messagebox
from PIL import Image, ImageTk
from deep_translator import GoogleTranslator, MyMemoryTranslator

class ToolTip:
    """輕量級滑鼠懸浮提示元件 (Tooltip)"""
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        widget.bind("<Enter>", self.show_tip)
        widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        if self.tip_window or not self.text:
            return
        x, y, cx, cy = self.widget.bbox("insert")
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + 30
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                         background="#fffffe", relief=tk.SOLID, borderwidth=1,
                         font=("Microsoft JhengHei", 9, "normal"), padx=6, pady=4)
        label.pack()

    def hide_tip(self, event=None):
        tw = self.tip_window
        self.tip_window = None
        if tw:
            tw.destroy()

class DatasetTaggerApp:
    def __init__(self, root):
        self.root = root
        
        # 1. 系統語言精準偵測
        self.current_lang = "English"
        try:
            if sys.platform == 'win32':
                import ctypes
                lang_id = ctypes.windll.kernel32.GetUserDefaultUILanguage()
                if lang_id in (1028, 3076, 5124): self.current_lang = "繁體中文"
                elif lang_id in (2052, 4100): self.current_lang = "簡體中文"
            else:
                sys_lang = str(locale.getdefaultlocale()[0]).lower()
                if any(x in sys_lang for x in ["tw", "hk", "hant", "cht"]): self.current_lang = "繁體中文"
                elif any(x in sys_lang for x in ["zh", "hans", "chs"]): self.current_lang = "簡體中文"
        except Exception:
            pass

        # 2. 介面多國語言詞庫
        self.i18n = {
            "繁體中文": {
                "title": "專業資料集標記與翻譯工具 - [按 F1 顯示/關閉熱鍵列表]", 
                "open": "開啟資料夾", "show_unmarked": "顯示無標記圖檔", "auto_refresh": "自動更新 (5分鐘)",
                "save": "儲存 (Ctrl+S)", "trans": "翻譯", "overwrite": "直接覆寫", 
                "rev_trans": "反向翻譯", "lang": "介面語言:", "api": "自訂API Key:", 
                "toggle_list": "列表 (Ctrl+H)", "search_file": "搜尋檔案", "search_text": "搜尋內文", "hotkey": "熱鍵(F1)", "swap": "互換",
                "col_name": "檔名", "col_time": "最後編輯", 
                "menu_mark_completed": "標記為已完成 (Alt+M)", "menu_mark_reviewed": "標記為不需修改 (Alt+N)", "menu_clear_mark": "清除標記狀態 (Alt+U)",
                "copy_tags": "複製標籤", "paste_tags": "貼上標籤至選取項",
                "lbl_orig": "【原始標籤內容】(唯讀保護)", "lbl_edit": "【標籤編輯區】", "lbl_trans": "【翻譯顯示區】",
                "tip_search_file": "依檔名搜尋檔案 (Ctrl + Alt + F)", "tip_search_text": "在當前圖片尋找/取代文字 (Ctrl + F)",
                "tip_font_in": "放大所有文字視窗字體 (Ctrl + Alt + +)",
                "tip_font_out": "縮小所有文字視窗字體 (Ctrl + Alt + -)",
                "tip_font_rst": "重設字體大小為預設 (Ctrl + Alt + *)",
                "find_lbl": "尋找目標:", "replace_lbl": "取代為:", "target_lbl": "搜尋範圍:",
                "btn_find_prev": "找上一個", "btn_find_next": "找下一個", "btn_replace": "取代", "btn_replace_all": "全部取代", "btn_highlight": "標示全部",
                "hotkey_text": (
                    "【熱鍵列表】\n\n"
                    "Ctrl + S : 儲存當前標記\n"
                    "Ctrl + T : 啟動正向翻譯\n"
                    "Alt + T : 啟動反向翻譯並覆寫\n"
                    "Ctrl + Alt + L : 恢復編輯區為原始讀入狀態\n"
                    "Alt + M : 標記選取項為已完成\n"
                    "Alt + N : 標記選取項為不需修改\n"
                    "Alt + U : 清除選取項標記狀態\n"
                    "Ctrl + H : 顯示/隱藏左側檔案列表\n"
                    "Ctrl + Alt + F : 搜尋檔案名稱\n"
                    "Ctrl + F : 搜尋/取代內文\n"
                    "Alt + L : 跳至最後編輯的檔案\n"
                    "Alt + ↑ : 上一張圖片\n"
                    "Alt + ↓ : 下一張圖片\n"
                    "滑鼠雙擊圖片 : 定位並置中顯示列表檔案\n"
                    "Ctrl + Alt + + : 放大三大文字視窗字體\n"
                    "Ctrl + Alt + - : 縮小三大文字視窗字體\n"
                    "Ctrl + Alt + * : 重設文字視窗字體\n"
                    "Ctrl + C / V : 複製 / 貼上\n"
                    "F1 : 顯示/關閉 此熱鍵列表"
                )
            },
            "簡體中文": {
                "title": "专业数据集标记与翻译工具 - [按 F1 显示/关闭快捷键列表]", 
                "open": "打开文件夹", "show_unmarked": "显示无标记图档", "auto_refresh": "自动更新 (5分钟)",
                "save": "保存 (Ctrl+S)", "trans": "翻译", "overwrite": "直接覆盖", 
                "rev_trans": "反向翻译", "lang": "界面语言:", "api": "自定义API Key:", 
                "toggle_list": "列表 (Ctrl+H)", "search_file": "搜索文件", "search_text": "搜索内文", "hotkey": "快捷键(F1)", "swap": "互换",
                "col_name": "文件名", "col_time": "最后编辑", 
                "menu_mark_completed": "标记为已完成 (Alt+M)", "menu_mark_reviewed": "标记为不需修改 (Alt+N)", "menu_clear_mark": "清除标记状态 (Alt+U)",
                "copy_tags": "复制标签", "paste_tags": "粘贴标签至选中项",
                "lbl_orig": "【原始标签内容】(唯读保护)", "lbl_edit": "【标签编辑区】", "lbl_trans": "【翻译显示区】",
                "tip_search_file": "依文件名搜索文件 (Ctrl + Alt + F)", "tip_search_text": "在当前图片寻找/替换文字 (Ctrl + F)",
                "tip_font_in": "放大所有文字窗口字体 (Ctrl + Alt + +)",
                "tip_font_out": "缩小所有文字窗口字体 (Ctrl + Alt + -)",
                "tip_font_rst": "重置字体大小为默认 (Ctrl + Alt + *)",
                "find_lbl": "查找目标:", "replace_lbl": "替换为:", "target_lbl": "搜索范围:",
                "btn_find_prev": "找上一个", "btn_find_next": "找下一个", "btn_replace": "替换", "btn_replace_all": "全部替换", "btn_highlight": "标示全部",
                "hotkey_text": (
                    "【快捷键列表】\n\n"
                    "Ctrl + S : 保存当前标记\n"
                    "Ctrl + T : 启动正向翻译\n"
                    "Alt + T : 启动反向翻译并覆盖\n"
                    "Ctrl + Alt + L : 恢复编辑区为原始读入状态\n"
                    "Alt + M : 标记选中项为已完成\n"
                    "Alt + N : 标记选中项为不需修改\n"
                    "Alt + U : 清除选中项标记状态\n"
                    "Ctrl + H : 显示/隐藏左侧文件列表\n"
                    "Ctrl + Alt + F : 搜索文件名称\n"
                    "Ctrl + F : 搜索/替换内文\n"
                    "Alt + L : 跳至最后编辑的文件\n"
                    "Alt + ↑ : 上一张图片\n"
                    "Alt + ↓ : 下一张图片\n"
                    "鼠标双击图片 : 定位并居中显示列表文件\n"
                    "Ctrl + Alt + + : 放大三大文字窗口字体\n"
                    "Ctrl + Alt + - : 缩小三大文字窗口字体\n"
                    "Ctrl + Alt + * : 重置文字窗口字体\n"
                    "Ctrl + C / V : 复制 / 粘贴\n"
                    "F1 : 显示/关闭 此快捷键列表"
                )
            },
            "English": {
                "title": "Pro Dataset Tagger & Translator - [Press F1 to Toggle Hotkeys]", 
                "open": "Open Dir", "show_unmarked": "Show unmarked", "auto_refresh": "Auto-Refresh (5m)",
                "save": "Save (Ctrl+S)", "trans": "Translate", "overwrite": "Overwrite", 
                "rev_trans": "Rev. Trans", "lang": "UI Lang:", "api": "API Key:", 
                "toggle_list": "List (Ctrl+H)", "search_file": "Search Files", "search_text": "Find/Replace", "hotkey": "Hotkeys(F1)", "swap": "Swap",
                "col_name": "File Name", "col_time": "Last Edited", 
                "menu_mark_completed": "Mark as Completed (Alt+M)", "menu_mark_reviewed": "Mark No Changes Needed (Alt+N)", "menu_clear_mark": "Clear Status Mark (Alt+U)",
                "copy_tags": "Copy Tags", "paste_tags": "Paste Tags to Selection",
                "lbl_orig": "【Original Tags】(Read-Only)", "lbl_edit": "【Edit Tags Area】", "lbl_trans": "【Translation Preview】",
                "tip_search_file": "Search file by name (Ctrl + Alt + F)", "tip_search_text": "Find and replace text in current image (Ctrl + F)",
                "tip_font_in": "Zoom In Text Windows (Ctrl + Alt + +)",
                "tip_font_out": "Zoom Out Text Windows (Ctrl + Alt + -)",
                "tip_font_rst": "Reset Font Size (Ctrl + Alt + *)",
                "find_lbl": "Find what:", "replace_lbl": "Replace with:", "target_lbl": "Scope:",
                "btn_find_prev": "Find Prev", "btn_find_next": "Find Next", "btn_replace": "Replace", "btn_replace_all": "Replace All", "btn_highlight": "Highlight All",
                "hotkey_text": (
                    "[Hotkeys]\n\n"
                    "Ctrl + S : Save & Mark Completed\n"
                    "Ctrl + T : Forward Translation\n"
                    "Alt + T : Reverse Translation & Overwrite\n"
                    "Ctrl + Alt + L : Restore Original Tags\n"
                    "Alt + M : Mark Selected as Completed\n"
                    "Alt + N : Mark Selected as Reviewed\n"
                    "Alt + U : Clear Status Mark\n"
                    "Ctrl + H : Toggle file list\n"
                    "Ctrl + Alt + F : Search file name\n"
                    "Ctrl + F : Find/Replace Text\n"
                    "Alt + L : Jump to last edited file\n"
                    "Alt + ↑ : Previous image\n"
                    "Alt + ↓ : Next image\n"
                    "Double Click Image : Locate & center file in list\n"
                    "Ctrl + Alt + + : Zoom In Text View\n"
                    "Ctrl + Alt + - : Zoom Out Text View\n"
                    "Ctrl + Alt + * : Reset Text View Font\n"
                    "Ctrl + C / V : Copy / Paste\n"
                    "F1 : Toggle this hotkey list"
                )
            }
        }
        
        self.root.title(self.i18n[self.current_lang]["title"])
        self.root.geometry("1400x850")
        
        # 3. 狀態與變數初始化
        self.all_image_files = []      
        self.display_filenames = []    
        self.current_dir = ""
        self.current_filename = ""
        self.clipboard_tags = ""
        self.supported_formats = ('.png', '.jpg', '.jpeg', '.webp', '.bmp')
        
        self.var_show_unmarked = tk.BooleanVar(value=True)
        self.var_auto_refresh = tk.BooleanVar(value=False)
        
        self.is_list_visible = True  
        self.last_list_width = 300
        self.hotkey_window = None 
        self.sr_window = None          # 內文搜尋取代視窗
        self.fs_window = None          # 檔案名稱搜尋視窗
        self.text_font_size = 11
        
        # 檔案搜尋狀態追蹤
        self.file_search_matches = []
        self.file_search_idx = -1
        
        self.metadata = {} 
        self.sort_col = "time"
        self.sort_reverse = True
        
        self.lang_map = {"自動偵測": "auto", "英文": "en", "繁體中文": "zh-TW", "簡體中文": "zh-CN", 
                         "日文": "ja", "韓文": "ko", "法文": "fr", "德文": "de", "西班牙文": "es"}
        
        self.setup_ui()
        self.bind_shortcuts()
        self.auto_refresh_loop()

    # ================= 系統背景排程 =================
    def auto_refresh_loop(self):
        if self.var_auto_refresh.get() and self.current_dir:
            try:
                self.load_metadata()
                new_files = sorted([f for f in os.listdir(self.current_dir) if f.lower().endswith(self.supported_formats)])
                if new_files != self.all_image_files:
                    self.all_image_files = new_files
                    self.refresh_listbox()
                    self.show_toast("已自動同步資料夾最新狀態", bg_color="#0984e3")
            except Exception as e:
                print(f"Auto-refresh error: {e}")
                
        self.root.after(300000, self.auto_refresh_loop)

    # ================= 元資料 (Metadata) 管理 =================
    def load_metadata(self):
        if not self.current_dir: return
        meta_path = os.path.join(self.current_dir, ".tagger_meta.json")
        if os.path.exists(meta_path):
            try:
                with open(meta_path, 'r', encoding='utf-8') as f:
                    self.metadata = json.load(f)
            except:
                self.metadata = {}
        else:
            self.metadata = {}

    def save_metadata(self):
        if not self.current_dir: return
        meta_path = os.path.join(self.current_dir, ".tagger_meta.json")
        try:
            with open(meta_path, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Meta save failed: {e}")

    def update_file_meta(self, filename, status):
        self.metadata[filename] = {
            "status": status,
            "time": time.time() if status != "none" else 0
        }
        self.save_metadata()

    # ================= UI 構建 =================
    def setup_ui(self):
        self.top_bar = tk.Frame(self.root, bg="#f0f0f0")
        self.top_bar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        self.btn_open = tk.Button(self.top_bar, text=self.i18n[self.current_lang]["open"], command=self.load_directory)
        self.btn_open.pack(side=tk.LEFT, padx=5)
        
        self.chk_unmarked = tk.Checkbutton(self.top_bar, text=self.i18n[self.current_lang]["show_unmarked"], 
                                           variable=self.var_show_unmarked, command=self.refresh_listbox, bg="#f0f0f0")
        self.chk_unmarked.pack(side=tk.LEFT, padx=5)

        self.chk_auto_refresh = tk.Checkbutton(self.top_bar, text=self.i18n[self.current_lang]["auto_refresh"], 
                                           variable=self.var_auto_refresh, bg="#f0f0f0")
        self.chk_auto_refresh.pack(side=tk.LEFT, padx=10)

        self.combo_ui = ttk.Combobox(self.top_bar, values=["繁體中文", "簡體中文", "English"], width=10, state="readonly")
        self.combo_ui.set(self.current_lang)
        self.combo_ui.bind("<<ComboboxSelected>>", self.change_ui_lang)
        self.combo_ui.pack(side=tk.RIGHT, padx=5)
        self.lbl_ui_lang = tk.Label(self.top_bar, text=self.i18n[self.current_lang]["lang"], bg="#f0f0f0")
        self.lbl_ui_lang.pack(side=tk.RIGHT)
        
        self.entry_api = ttk.Entry(self.top_bar, width=20)
        self.entry_api.pack(side=tk.RIGHT, padx=15)
        self.lbl_api = tk.Label(self.top_bar, text=self.i18n[self.current_lang]["api"], bg="#f0f0f0")
        self.lbl_api.pack(side=tk.RIGHT)

        self.bot_bar = tk.Frame(self.root, bg="#ddd")
        self.bot_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.btn_toggle_list = tk.Button(self.bot_bar, text=self.i18n[self.current_lang]["toggle_list"], command=self.toggle_list_panel)
        self.btn_toggle_list.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.btn_search_file = tk.Button(self.bot_bar, text=self.i18n[self.current_lang]["search_file"], command=self.open_search_file)
        self.btn_search_file.pack(side=tk.LEFT, padx=5)
        self.btn_search_text = tk.Button(self.bot_bar, text=self.i18n[self.current_lang]["search_text"], command=self.open_search_replace)
        self.btn_search_text.pack(side=tk.LEFT, padx=2)

        self.btn_save = tk.Button(self.bot_bar, text=self.i18n[self.current_lang]["save"], command=self.save_tags, bg="#dff0d8")
        self.btn_save.pack(side=tk.LEFT, padx=15)
        
        self.combo_engine = ttk.Combobox(self.bot_bar, values=["Google", "MyMemory"], width=8, state="readonly")
        self.combo_engine.set("Google")
        self.combo_engine.pack(side=tk.LEFT, padx=5)
        
        self.combo_src = ttk.Combobox(self.bot_bar, values=list(self.lang_map.keys()), width=8, state="readonly")
        self.combo_src.set("自動偵測")
        self.combo_src.pack(side=tk.LEFT, padx=2)
        
        self.btn_swap = tk.Button(self.bot_bar, text=self.i18n[self.current_lang]["swap"], command=self.swap_languages)
        self.btn_swap.pack(side=tk.LEFT, padx=2)
        
        tgt_default = "英文"
        if self.current_lang in ("繁體中文", "簡體中文"): tgt_default = self.current_lang
            
        self.combo_tgt = ttk.Combobox(self.bot_bar, values=list(self.lang_map.keys())[1:], width=8, state="readonly")
        self.combo_tgt.set(tgt_default)
        self.combo_tgt.pack(side=tk.LEFT, padx=2)

        self.btn_trans = tk.Button(self.bot_bar, text=self.i18n[self.current_lang]["trans"], command=lambda: self.translate_text(False), bg="#d9edf7")
        self.btn_trans.pack(side=tk.LEFT, padx=8)
        
        self.btn_rev_trans = tk.Button(self.bot_bar, text=self.i18n[self.current_lang]["rev_trans"], command=lambda: self.translate_text(True), bg="#ffe0b2")
        self.btn_rev_trans.pack(side=tk.LEFT, padx=5)
        
        self.btn_overwrite = tk.Button(self.bot_bar, text=self.i18n[self.current_lang]["overwrite"], command=self.overwrite_edit_area)
        self.btn_overwrite.pack(side=tk.LEFT, padx=5)

        font_frame = tk.Frame(self.bot_bar, bg="#ddd")
        font_frame.pack(side=tk.LEFT, padx=10)
        self.btn_font_in = tk.Button(font_frame, text=" A+ ", command=lambda: self.change_font_size(1))
        self.btn_font_in.pack(side=tk.LEFT, padx=1)
        self.btn_font_out = tk.Button(font_frame, text=" A- ", command=lambda: self.change_font_size(-1))
        self.btn_font_out.pack(side=tk.LEFT, padx=1)
        self.btn_font_rst = tk.Button(font_frame, text=" 重設 ", command=lambda: self.change_font_size(reset=True))
        self.btn_font_rst.pack(side=tk.LEFT, padx=1)

        ToolTip(self.btn_search_file, self.i18n[self.current_lang]["tip_search_file"])
        ToolTip(self.btn_search_text, self.i18n[self.current_lang]["tip_search_text"])
        ToolTip(self.btn_font_in, self.i18n[self.current_lang]["tip_font_in"])
        ToolTip(self.btn_font_out, self.i18n[self.current_lang]["tip_font_out"])
        ToolTip(self.btn_font_rst, self.i18n[self.current_lang]["tip_font_rst"])

        self.btn_hotkey = tk.Button(self.bot_bar, text=self.i18n[self.current_lang]["hotkey"], command=self.show_hotkeys, bg="#e0e0e0")
        self.btn_hotkey.pack(side=tk.RIGHT, padx=10)

        self.paned = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, sashwidth=8, bg="#999")
        self.paned.pack(fill=tk.BOTH, expand=True)
        
        self.f_left = tk.Frame(self.paned, width=self.last_list_width)
        self.paned.add(self.f_left, minsize=200)
        
        style = ttk.Style()
        style.configure("Treeview", font=("Microsoft JhengHei", 10), rowheight=24)
        style.configure("Treeview.Heading", font=("Microsoft JhengHei", 10, "bold"))
        
        self.tree = ttk.Treeview(self.f_left, columns=("file", "time"), show="headings")
        self.tree.heading("file", text=self.i18n[self.current_lang]["col_name"], command=lambda: self.sort_tree("file"))
        self.tree.heading("time", text=self.i18n[self.current_lang]["col_time"], command=lambda: self.sort_tree("time"))
        self.tree.column("file", width=180, anchor=tk.W)
        self.tree.column("time", width=100, anchor=tk.CENTER)
        
        self.tree.tag_configure("top1", background="#ffcccc")
        self.tree.tag_configure("top2", background="#ffe6cc")
        self.tree.tag_configure("top3", background="#ffffcc")
        self.tree.tag_configure("top4", background="#e6ffcc")
        self.tree.tag_configure("top5", background="#ccffcc")
        self.tree.tag_configure("completed", background="#d4edda") 
        self.tree.tag_configure("reviewed", background="#fff3cd")  
        self.tree.tag_configure("normal", background="white")
        
        self.scrollbar = ttk.Scrollbar(self.f_left, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.tree.bind('<<TreeviewSelect>>', self.on_file_select)
        
        self.menu_tree = tk.Menu(self.root, tearoff=0)
        self.menu_tree.add_command(label=self.i18n[self.current_lang]["menu_mark_completed"], command=lambda: self.manual_mark_file("completed"))
        self.menu_tree.add_command(label=self.i18n[self.current_lang]["menu_mark_reviewed"], command=lambda: self.manual_mark_file("reviewed"))
        self.menu_tree.add_command(label=self.i18n[self.current_lang]["menu_clear_mark"], command=lambda: self.manual_mark_file("none"))
        self.menu_tree.add_separator()
        self.menu_tree.add_command(label=self.i18n[self.current_lang]["copy_tags"], command=self.copy_tags)
        self.menu_tree.add_command(label=self.i18n[self.current_lang]["paste_tags"], command=self.paste_tags)
        self.tree.bind("<Button-3>", self.show_tree_menu)

        self.f_right = tk.Frame(self.paned)
        self.paned.add(self.f_right, minsize=500)
        
        for i in range(2): 
            self.f_right.columnconfigure(i, weight=1)
            self.f_right.rowconfigure(i, weight=1)
        
        self.f_image_container = tk.Frame(self.f_right, bg="black")
        self.f_image_container.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
        self.lbl_filename = tk.Label(self.f_image_container, text="[目前無圖片]", bg="#2d3436", fg="#f1c40f", font=("Microsoft JhengHei", 11, "bold"), pady=4)
        self.lbl_filename.pack(side=tk.TOP, fill=tk.X)
        self.lbl_image = tk.Label(self.f_image_container, text="Preview", bg="black", fg="white")
        self.lbl_image.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        self.lbl_image.bind("<Double-1>", self.sync_list_to_image)
        self.lbl_filename.bind("<Double-1>", self.sync_list_to_image)
        self.f_image_container.bind("<Double-1>", self.sync_list_to_image)
        
        self.f_orig_wrapper = tk.Frame(self.f_right)
        self.f_orig_wrapper.grid(row=0, column=1, sticky="nsew", padx=2, pady=2)
        self.lbl_orig_title = tk.Label(self.f_orig_wrapper, text=self.i18n[self.current_lang]["lbl_orig"], font=("Microsoft JhengHei", 10, "bold"), anchor="w", fg="#7f8c8d")
        self.lbl_orig_title.pack(side=tk.TOP, fill=tk.X, pady=2)
        self.text_original = tk.Text(self.f_orig_wrapper, bg="#f5f5f5", state=tk.DISABLED, font=("Arial", self.text_font_size))
        self.text_original.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        self.f_edit_wrapper = tk.Frame(self.f_right)
        self.f_edit_wrapper.grid(row=1, column=0, sticky="nsew", padx=2, pady=2)
        self.lbl_edit_title = tk.Label(self.f_edit_wrapper, text=self.i18n[self.current_lang]["lbl_edit"], font=("Microsoft JhengHei", 10, "bold"), anchor="w", fg="#2980b9")
        self.lbl_edit_title.pack(side=tk.TOP, fill=tk.X, pady=2)
        self.text_edit = tk.Text(self.f_edit_wrapper, undo=True, font=("Arial", self.text_font_size))
        self.text_edit.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        self.f_trans_wrapper = tk.Frame(self.f_right)
        self.f_trans_wrapper.grid(row=1, column=1, sticky="nsew", padx=2, pady=2)
        self.lbl_trans_title = tk.Label(self.f_trans_wrapper, text=self.i18n[self.current_lang]["lbl_trans"], font=("Microsoft JhengHei", 10, "bold"), anchor="w", fg="#27ae60")
        self.lbl_trans_title.pack(side=tk.TOP, fill=tk.X, pady=2)
        self.text_translated = tk.Text(self.f_trans_wrapper, bg="#fffde7", undo=True, font=("Arial", self.text_font_size))
        self.text_translated.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        for text_widget in (self.text_edit, self.text_translated):
            text_widget.tag_configure("search_match", background="#ffeaa7", foreground="#d35400")
            text_widget.bind("<Control-c>", lambda e: text_widget.event_generate("<<Copy>>"))
            text_widget.bind("<Control-v>", lambda e: text_widget.event_generate("<<Paste>>"))

    # ================= 檔案名稱搜尋功能 (Ctrl+Alt+F) =================
    def open_search_file(self, event=None):
        if hasattr(self, 'fs_window') and self.fs_window and self.fs_window.winfo_exists():
            self.fs_window.lift()
            return "break"

        self.fs_window = tk.Toplevel(self.root)
        self.fs_window.title(self.i18n[self.current_lang]["search_file"])
        self.fs_window.attributes("-topmost", True)
        self.fs_window.geometry("360x120")
        self.fs_window.resizable(False, False)

        self.var_file_search = tk.StringVar()
        self.var_file_status = tk.StringVar(value="0 / 0")
        self.file_search_matches = []
        self.file_search_idx = -1

        f_main = tk.Frame(self.fs_window, padx=15, pady=15)
        f_main.pack(fill=tk.BOTH, expand=True)

        ttk.Entry(f_main, textvariable=self.var_file_search, width=28).grid(row=0, column=0, columnspan=2, sticky="w", pady=4)
        tk.Label(f_main, textvariable=self.var_file_status, fg="#2980b9", font=("Arial", 10, "bold")).grid(row=0, column=2, padx=10, sticky="w")

        btn_f = tk.Frame(f_main)
        btn_f.grid(row=1, column=0, columnspan=3, pady=10, sticky="w")
        tk.Button(btn_f, text=self.i18n[self.current_lang]["btn_find_prev"], command=self.file_search_prev).pack(side=tk.LEFT, padx=3)
        tk.Button(btn_f, text=self.i18n[self.current_lang]["btn_find_next"], command=self.file_search_next).pack(side=tk.LEFT, padx=3)

        self.var_file_search.trace_add("write", self.update_file_search_matches)
        self.fs_window.protocol("WM_DELETE_WINDOW", self.close_file_search)
        
        # 將視窗置中顯示
        self.fs_window.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (self.fs_window.winfo_width() // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (self.fs_window.winfo_height() // 2)
        self.fs_window.geometry(f"+{x}+{y}")
        
        return "break"

    def update_file_search_matches(self, *args):
        query = self.var_file_search.get().lower()
        self.file_search_matches = []
        self.file_search_idx = -1
        
        if query:
            for idx, filename in enumerate(self.display_filenames):
                if query in filename.lower():
                    self.file_search_matches.append(idx)
        
        if self.file_search_matches:
            self.file_search_idx = 0
            self.jump_to_file_match()
        else:
            self.var_file_status.set("0 / 0")

    def file_search_prev(self):
        if not self.file_search_matches: return
        self.file_search_idx -= 1
        if self.file_search_idx < 0:
            self.file_search_idx = len(self.file_search_matches) - 1
        self.jump_to_file_match()

    def file_search_next(self):
        if not self.file_search_matches: return
        self.file_search_idx += 1
        if self.file_search_idx >= len(self.file_search_matches):
            self.file_search_idx = 0
        self.jump_to_file_match()

    def jump_to_file_match(self):
        total = len(self.file_search_matches)
        current = self.file_search_idx + 1
        self.var_file_status.set(f"{current} / {total}")
        
        idx = self.file_search_matches[self.file_search_idx]
        item_id = self.tree.get_children()[idx]
        self.center_tree_item(idx, item_id)
        self.on_file_select()

    def close_file_search(self):
        if self.fs_window:
            self.fs_window.destroy()
            self.fs_window = None

    # ================= 內文尋找與取代功能 (Ctrl+F) =================
    def open_search_replace(self, event=None):
        if hasattr(self, 'sr_window') and self.sr_window and self.sr_window.winfo_exists():
            self.sr_window.lift()
            return "break"

        self.sr_window = tk.Toplevel(self.root)
        self.sr_window.title(self.i18n[self.current_lang]["search_text"])
        self.sr_window.attributes("-topmost", True)
        self.sr_window.geometry("380x180")
        self.sr_window.resizable(False, False)

        self.var_find = tk.StringVar()
        self.var_replace = tk.StringVar()
        self.var_target = tk.StringVar(value=self.i18n[self.current_lang]["lbl_edit"])

        f_main = tk.Frame(self.sr_window, padx=15, pady=15)
        f_main.pack(fill=tk.BOTH, expand=True)

        tk.Label(f_main, text=self.i18n[self.current_lang]["find_lbl"]).grid(row=0, column=0, sticky="e", pady=4)
        ttk.Entry(f_main, textvariable=self.var_find, width=28).grid(row=0, column=1, columnspan=3, sticky="w", pady=4)

        tk.Label(f_main, text=self.i18n[self.current_lang]["replace_lbl"]).grid(row=1, column=0, sticky="e", pady=4)
        ttk.Entry(f_main, textvariable=self.var_replace, width=28).grid(row=1, column=1, columnspan=3, sticky="w", pady=4)

        tk.Label(f_main, text=self.i18n[self.current_lang]["target_lbl"]).grid(row=2, column=0, sticky="e", pady=4)
        cb_target = ttk.Combobox(f_main, textvariable=self.var_target, values=[self.i18n[self.current_lang]["lbl_edit"], self.i18n[self.current_lang]["lbl_trans"]], state="readonly", width=18)
        cb_target.grid(row=2, column=1, columnspan=3, sticky="w", pady=4)

        btn_f = tk.Frame(f_main)
        btn_f.grid(row=3, column=0, columnspan=4, pady=10)
        tk.Button(btn_f, text=self.i18n[self.current_lang]["btn_find_next"], command=self.find_next).pack(side=tk.LEFT, padx=3)
        tk.Button(btn_f, text=self.i18n[self.current_lang]["btn_replace"], command=self.replace_text).pack(side=tk.LEFT, padx=3)
        tk.Button(btn_f, text=self.i18n[self.current_lang]["btn_replace_all"], command=self.replace_all).pack(side=tk.LEFT, padx=3)
        tk.Button(btn_f, text=self.i18n[self.current_lang]["btn_highlight"], command=self.highlight_all).pack(side=tk.LEFT, padx=3)

        focused = self.root.focus_get()
        if focused == self.text_translated:
            cb_target.set(self.i18n[self.current_lang]["lbl_trans"])
            try: self.var_find.set(focused.selection_get())
            except: pass
        elif focused == self.text_edit:
            try: self.var_find.set(focused.selection_get())
            except: pass

        self.sr_window.protocol("WM_DELETE_WINDOW", self.close_search_replace)
        
        self.sr_window.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (self.sr_window.winfo_width() // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (self.sr_window.winfo_height() // 2)
        self.sr_window.geometry(f"+{x}+{y}")
        
        return "break"

    def get_search_target(self):
        val = self.var_target.get()
        if val == self.i18n[self.current_lang]["lbl_trans"]: return self.text_translated
        return self.text_edit

    def find_next(self):
        target = self.get_search_target()
        target.tag_remove("search_match", "1.0", tk.END)
        s_str = self.var_find.get()
        if not s_str: return

        start_pos = target.index(tk.INSERT)
        pos = target.search(s_str, f"{start_pos}+1c", stopindex=tk.END)
        if not pos:
            pos = target.search(s_str, "1.0", stopindex=tk.END)
        
        if pos:
            end_pos = f"{pos}+{len(s_str)}c"
            target.mark_set(tk.INSERT, end_pos)
            target.tag_add("search_match", pos, end_pos)
            target.see(pos)
        else:
            self.show_toast("找不到相符字串", bg_color="#f44336")

    def replace_text(self):
        target = self.get_search_target()
        s_str = self.var_find.get()
        r_str = self.var_replace.get()
        if not s_str: return

        ranges = target.tag_ranges("search_match")
        if ranges:
            start_idx, end_idx = ranges[0], ranges[1]
            if target.get(start_idx, end_idx) == s_str:
                target.delete(start_idx, end_idx)
                target.insert(start_idx, r_str)
                target.mark_set(tk.INSERT, f"{start_idx}+{len(r_str)}c")
        self.find_next()

    def replace_all(self):
        target = self.get_search_target()
        s_str = self.var_find.get()
        r_str = self.var_replace.get()
        if not s_str: return

        target.tag_remove("search_match", "1.0", tk.END)
        idx = "1.0"
        count = 0
        while True:
            idx = target.search(s_str, idx, stopindex=tk.END)
            if not idx: break
            end_idx = f"{idx}+{len(s_str)}c"
            target.delete(idx, end_idx)
            target.insert(idx, r_str)
            idx = f"{idx}+{len(r_str)}c"
            count += 1
        self.show_toast(f"已替換 {count} 處")

    def highlight_all(self):
        target = self.get_search_target()
        target.tag_remove("search_match", "1.0", tk.END)
        s_str = self.var_find.get()
        if not s_str: return

        idx = "1.0"
        count = 0
        while True:
            idx = target.search(s_str, idx, stopindex=tk.END)
            if not idx: break
            end_idx = f"{idx}+{len(s_str)}c"
            target.tag_add("search_match", idx, end_idx)
            idx = end_idx
            count += 1
        self.show_toast(f"共標示 {count} 處")

    def close_search_replace(self):
        self.text_edit.tag_remove("search_match", "1.0", tk.END)
        self.text_translated.tag_remove("search_match", "1.0", tk.END)
        if self.sr_window:
            self.sr_window.destroy()
            self.sr_window = None

    # ================= 文字還原功能 =================
    def restore_original_text(self, event=None):
        if not self.current_filename: return "break"
        orig_text = self.text_original.get("1.0", tk.END).strip()
        self.text_edit.delete("1.0", tk.END)
        self.text_edit.insert("1.0", orig_text)
        self.show_toast("已恢復原始標籤內容")
        return "break"

    # ================= UI 輔助功能: 置中演算法 =================
    def center_tree_item(self, idx, item_id):
        self.tree.selection_set(item_id)
        self.tree.focus(item_id)
        self.tree.update_idletasks() 
        total_items = len(self.display_filenames)
        if total_items > 0:
            yv = self.tree.yview()
            visible_proportion = yv[1] - yv[0]
            item_fraction = idx / total_items
            target_fraction = item_fraction - (visible_proportion / 2)
            self.tree.yview_moveto(max(0.0, min(target_fraction, 1.0)))

    # ================= 批次處理功能 =================
    def copy_tags(self):
        self.clipboard_tags = self.text_edit.get("1.0", tk.END).strip()
        self.show_toast("標籤已複製")

    def paste_tags(self):
        if not self.clipboard_tags: 
            self.show_toast("剪貼簿為空", bg_color="#f44336")
            return
        selected = self.tree.selection()
        if not selected: return
        
        for item in selected:
            idx = self.tree.index(item)
            filename = self.display_filenames[idx]
            txt_path = os.path.join(self.current_dir, f"{os.path.splitext(filename)[0]}.txt")
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write(self.clipboard_tags)
            self.update_file_meta(filename, "completed")
            
        self.refresh_listbox()
        self.show_toast(f"已套用至 {len(selected)} 個檔案")

    # ================= 字體縮放控制功能 =================
    def change_font_size(self, delta=0, reset=False, event=None):
        if reset:
            self.text_font_size = 11
        else:
            self.text_font_size += delta
            if self.text_font_size < 7: self.text_font_size = 7
            if self.text_font_size > 32: self.text_font_size = 32
            
        self.text_original.config(state=tk.NORMAL)
        self.text_original.configure(font=("Arial", self.text_font_size))
        self.text_original.config(state=tk.DISABLED)
        
        self.text_edit.configure(font=("Arial", self.text_font_size))
        self.text_translated.configure(font=("Arial", self.text_font_size))
        
        self.show_toast(f"字體大小: {self.text_font_size}")
        return "break"

    # ================= 檔案與列表操作邏輯 =================
    def load_directory(self):
        path = filedialog.askdirectory()
        if not path: return
        self.current_dir = path
        self.load_metadata()
        self.all_image_files = sorted([f for f in os.listdir(path) if f.lower().endswith(self.supported_formats)])
        self.refresh_listbox()

    def sort_tree(self, col):
        if self.sort_col == col:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_col = col
            self.sort_reverse = False
        self.refresh_listbox()

    def refresh_listbox(self):
        current_selection_file = self.current_filename

        data_list = []
        for f in self.all_image_files:
            txt_path = os.path.join(self.current_dir, f"{os.path.splitext(f)[0]}.txt")
            has_txt = os.path.exists(txt_path)
            meta = self.metadata.get(f, {})
            
            if "edited" in meta:
                status = "completed" if meta["edited"] else "none"
            else:
                status = meta.get("status", "none")
                
            edit_time = meta.get("time", 0)
            
            if not self.var_show_unmarked.get() and not has_txt and status == "none":
                continue
                
            time_str = datetime.fromtimestamp(edit_time).strftime('%m-%d %H:%M') if edit_time > 0 else "-"
            data_list.append((f, time_str, edit_time, status))

        if self.sort_col == "file":
            data_list.sort(key=lambda x: x[0].lower(), reverse=self.sort_reverse)
        else:
            data_list.sort(key=lambda x: x[2], reverse=self.sort_reverse)

        recent_files = [x[0] for x in sorted([d for d in data_list if d[3] != "none"], key=lambda x: x[2], reverse=True)[:5]]

        self.tree.delete(*self.tree.get_children())
        self.display_filenames.clear()

        for d in data_list:
            f, time_str, edit_time, status = d
            tag = "normal"
            if f in recent_files:
                rank = recent_files.index(f)
                tag = f"top{rank+1}"
                f_display = f"[{rank+1}] {f}"
            elif status == "completed":
                tag = "completed"
                f_display = f
            elif status == "reviewed":
                tag = "reviewed"
                f_display = f
            else:
                f_display = f

            self.tree.insert("", tk.END, values=(f_display, time_str), tags=(tag,))
            self.display_filenames.append(f)

        if current_selection_file in self.display_filenames:
            idx = self.display_filenames.index(current_selection_file)
            item_id = self.tree.get_children()[idx]
            self.center_tree_item(idx, item_id)

    def show_tree_menu(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            if item not in self.tree.selection():
                self.tree.selection_set(item)
            self.menu_tree.post(event.x_root, event.y_root)

    def manual_mark_file(self, status):
        selected = self.tree.selection()
        if not selected: return
        for item in selected:
            idx = self.tree.index(item)
            actual_filename = self.display_filenames[idx]
            self.update_file_meta(actual_filename, status)
        self.refresh_listbox()
        
        state_map = {"completed": "已完成", "reviewed": "不需修改", "none": "已清除標記"}
        self.show_toast(f"已將 {len(selected)} 個檔案設為: {state_map.get(status)}")

    def manual_mark_file_hotkey(self, status):
        self.manual_mark_file(status)
        return "break"

    def on_file_select(self, e=None):
        selected = self.tree.selection()
        if not selected: return
        idx = self.tree.index(selected[0])
        val = self.display_filenames[idx]
        
        self.current_filename = val
        self.lbl_filename.config(text=f" 檔案: {val} ")
        txt_path = os.path.join(self.current_dir, f"{os.path.splitext(val)[0]}.txt")
        
        try:
            img = Image.open(os.path.join(self.current_dir, val))
            img.thumbnail((700, 700))
            photo = ImageTk.PhotoImage(img)
            self.lbl_image.config(image=photo, text="")
            self.lbl_image.image = photo
        except Exception:
            self.lbl_image.config(image='', text="Image Preview Error")

        self.text_original.config(state=tk.NORMAL)
        self.text_original.delete("1.0", tk.END)
        self.text_edit.delete("1.0", tk.END)
        self.text_translated.delete("1.0", tk.END)
        
        if os.path.exists(txt_path):
            with open(txt_path, 'r', encoding='utf-8') as f:
                content = f.read()
                self.text_original.insert("1.0", content)
                self.text_edit.insert("1.0", content)
                
        self.text_original.config(state=tk.DISABLED)
        
        # 換圖片時自動清除之前的搜尋高亮標記
        self.text_edit.tag_remove("search_match", "1.0", tk.END)
        self.text_translated.tag_remove("search_match", "1.0", tk.END)

    def save_tags(self, event=None):
        selected = self.tree.selection()
        if not selected: 
            self.show_toast("存檔失敗：請先在左側列表選擇一個檔案", bg_color="#f44336")
            return "break"
            
        idx = self.tree.index(selected[0])
        actual_filename = self.display_filenames[idx]
        txt_name = f"{os.path.splitext(actual_filename)[0]}.txt"
        txt_path = os.path.join(self.current_dir, txt_name)
        
        is_new = not os.path.exists(txt_path)
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(self.text_edit.get("1.0", tk.END).strip())
            
        self.update_file_meta(actual_filename, "completed")
        self.refresh_listbox()
        
        msg = f"新建完成: {txt_name}" if is_new else f"儲存完成: {txt_name}"
        self.show_toast(msg, bg_color="#4CAF50")
        return "break"

    def sync_list_to_image(self, event=None):
        if not self.current_filename: return
        if not self.is_list_visible:
            self.toggle_list_panel()
            
        if self.current_filename in self.display_filenames:
            idx = self.display_filenames.index(self.current_filename)
            item_id = self.tree.get_children()[idx]
            self.center_tree_item(idx, item_id)
            self.show_toast(f"已定位檔案: {self.current_filename}", bg_color="#0984e3")

    # ================= 翻譯邏輯 =================
    def translate_text_hotkey(self, is_reverse=False):
        self.translate_text(is_reverse)
        return "break"

    def translate_text(self, is_reverse=False):
        if not is_reverse:
            content = self.text_edit.get("1.0", tk.END).strip()
            src_lang = self.lang_map[self.combo_src.get()]
            tgt_lang = self.lang_map[self.combo_tgt.get()]
            target_widget = self.text_translated
        else:
            content = self.text_translated.get("1.0", tk.END).strip()
            src_lang = self.lang_map[self.combo_tgt.get()]
            tgt_lang = self.lang_map[self.combo_src.get()]
            if src_lang == 'auto': tgt_lang = 'en'
            target_widget = self.text_edit

        if not content: return
        
        try:
            res = GoogleTranslator(source=src_lang, target=tgt_lang).translate(content)
            target_widget.delete("1.0", tk.END)
            target_widget.insert("1.0", res)
            if is_reverse: self.show_toast("反向翻譯並覆寫完成")
        except Exception as e:
            target_widget.insert("1.0", f"Translate Error: {e}")

    def overwrite_edit_area(self):
        content = self.text_translated.get("1.0", tk.END).strip()
        self.text_edit.delete("1.0", tk.END)
        self.text_edit.insert("1.0", content)

    def swap_languages(self):
        src = self.combo_src.get()
        tgt = self.combo_tgt.get()
        if src != "自動偵測":
            self.combo_src.set(tgt)
            self.combo_tgt.set(src)
        else:
            self.show_toast("來源為自動偵測時無法互換", bg_color="#f44336")

    # ================= 其他面板控制 =================
    def toggle_list_panel(self, event=None):
        if self.is_list_visible:
            current_width = self.f_left.winfo_width()
            self.last_list_width = current_width if current_width > 10 else 300
            self.paned.forget(self.f_left)
            self.is_list_visible = False
        else:
            self.paned.forget(self.f_right)
            self.paned.add(self.f_left, minsize=200)
            self.paned.add(self.f_right, minsize=500)
            self.paned.paneconfig(self.f_left, width=self.last_list_width)
            self.is_list_visible = True
        return "break"

    def jump_last_edited(self, event=None):
        if not self.metadata:
            self.show_toast("尚未有編輯紀錄")
            return "break"
            
        latest_file = max(self.metadata.keys(), key=lambda k: self.metadata[k].get('time', 0), default=None)
        if latest_file and latest_file in self.display_filenames:
            idx = self.display_filenames.index(latest_file)
            item_id = self.tree.get_children()[idx]
            self.center_tree_item(idx, item_id)
            self.on_file_select()
        return "break"

    def nav_prev(self, event=None):
        selected = self.tree.selection()
        if not selected: return "break"
        idx = self.tree.index(selected[0])
        if idx > 0:
            item_id = self.tree.get_children()[idx - 1]
            self.center_tree_item(idx - 1, item_id)
            self.on_file_select()
        return "break"

    def nav_next(self, event=None):
        selected = self.tree.selection()
        if not selected: return "break"
        idx = self.tree.index(selected[0])
        if idx < len(self.display_filenames) - 1:
            item_id = self.tree.get_children()[idx + 1]
            self.center_tree_item(idx + 1, item_id)
            self.on_file_select()
        return "break"

    def show_toast(self, message, bg_color="#333333"):
        toast = tk.Label(self.root, text=message, bg=bg_color, fg="white", 
                         font=("Microsoft JhengHei", 12, "bold"), padx=20, pady=10)
        toast.place(relx=0.5, rely=0.85, anchor="center")
        self.root.after(2000, toast.destroy)

    def show_hotkeys(self, event=None):
        if self.hotkey_window and self.hotkey_window.winfo_exists():
            self.hotkey_window.destroy()
            self.hotkey_window = None
            return "break"
            
        self.hotkey_window = tk.Toplevel(self.root)
        self.hotkey_window.title(self.i18n[self.current_lang]["hotkey"])
        self.hotkey_window.attributes("-topmost", True)
        
        keys = self.i18n[self.current_lang]["hotkey_text"]
        lbl = tk.Label(self.hotkey_window, text=keys, font=("Microsoft JhengHei", 11), justify=tk.LEFT, padx=30, pady=20)
        lbl.pack()
        
        self.hotkey_window.bind("<F1>", self.show_hotkeys)
        self.hotkey_window.bind("<Escape>", self.show_hotkeys)
        
        self.hotkey_window.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (self.hotkey_window.winfo_width() // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (self.hotkey_window.winfo_height() // 2)
        self.hotkey_window.geometry(f"+{x}+{y}")
        return "break"

    def change_ui_lang(self, event=None):
        self.current_lang = self.combo_ui.get()
        cfg = self.i18n[self.current_lang]
        self.root.title(cfg["title"])
        self.btn_open.config(text=cfg["open"])
        self.chk_unmarked.config(text=cfg["show_unmarked"])
        self.chk_auto_refresh.config(text=cfg["auto_refresh"])
        self.lbl_ui_lang.config(text=cfg["lang"])
        self.lbl_api.config(text=cfg["api"])
        self.btn_toggle_list.config(text=cfg["toggle_list"])
        self.btn_search_file.config(text=cfg["search_file"])
        self.btn_search_text.config(text=cfg["search_text"])
        self.btn_save.config(text=cfg["save"])
        self.btn_swap.config(text=cfg["swap"])
        self.btn_trans.config(text=cfg["trans"])
        self.btn_rev_trans.config(text=cfg["rev_trans"])
        self.btn_overwrite.config(text=cfg["overwrite"])
        self.btn_hotkey.config(text=cfg["hotkey"])
        
        self.lbl_orig_title.config(text=cfg["lbl_orig"])
        self.lbl_edit_title.config(text=cfg["lbl_edit"])
        self.lbl_trans_title.config(text=cfg["lbl_trans"])

        ToolTip(self.btn_search_file, cfg["tip_search_file"])
        ToolTip(self.btn_search_text, cfg["tip_search_text"])
        ToolTip(self.btn_font_in, cfg["tip_font_in"])
        ToolTip(self.btn_font_out, cfg["tip_font_out"])
        ToolTip(self.btn_font_rst, cfg["tip_font_rst"])
        
        self.tree.heading("file", text=cfg["col_name"])
        self.tree.heading("time", text=cfg["col_time"])
        self.menu_tree.entryconfig(0, label=cfg["menu_mark_completed"])
        self.menu_tree.entryconfig(1, label=cfg["menu_mark_reviewed"])
        self.menu_tree.entryconfig(2, label=cfg["menu_clear_mark"])
        self.menu_tree.entryconfig(4, label=cfg["copy_tags"])
        self.menu_tree.entryconfig(5, label=cfg["paste_tags"])
        
        if self.current_lang in ("繁體中文", "簡體中文"):
            self.combo_tgt.set(self.current_lang)
        else:
            self.combo_tgt.set("英文")
        
        if self.hotkey_window and self.hotkey_window.winfo_exists():
            self.hotkey_window.title(cfg["hotkey"])
            for child in self.hotkey_window.winfo_children():
                if isinstance(child, tk.Label): child.config(text=cfg["hotkey_text"])

    def bind_shortcuts(self):
        self.root.bind("<Control-s>", self.save_tags)
        self.root.bind("<Control-S>", self.save_tags)
        self.root.bind("<Control-h>", self.toggle_list_panel)
        self.root.bind("<Control-H>", self.toggle_list_panel)
        
        self.root.bind("<Control-Alt-f>", self.open_search_file)
        self.root.bind("<Control-Alt-F>", self.open_search_file)
        self.root.bind("<Control-f>", self.open_search_replace)
        self.root.bind("<Control-F>", self.open_search_replace)

        self.root.bind("<Alt-l>", self.jump_last_edited)
        self.root.bind("<Alt-L>", self.jump_last_edited)
        self.root.bind("<Alt-Up>", self.nav_prev)
        self.root.bind("<Alt-Down>", self.nav_next)
        
        self.root.bind("<Control-t>", lambda e: self.translate_text_hotkey(is_reverse=False))
        self.root.bind("<Control-T>", lambda e: self.translate_text_hotkey(is_reverse=False))
        self.root.bind("<Alt-t>", lambda e: self.translate_text_hotkey(is_reverse=True))
        self.root.bind("<Alt-T>", lambda e: self.translate_text_hotkey(is_reverse=True))
        
        self.root.bind("<Control-Alt-l>", self.restore_original_text)
        self.root.bind("<Control-Alt-L>", self.restore_original_text)

        self.root.bind("<Alt-m>", lambda e: self.manual_mark_file_hotkey("completed"))
        self.root.bind("<Alt-M>", lambda e: self.manual_mark_file_hotkey("completed"))
        self.root.bind("<Alt-n>", lambda e: self.manual_mark_file_hotkey("reviewed"))
        self.root.bind("<Alt-N>", lambda e: self.manual_mark_file_hotkey("reviewed"))
        self.root.bind("<Alt-u>", lambda e: self.manual_mark_file_hotkey("none"))
        self.root.bind("<Alt-U>", lambda e: self.manual_mark_file_hotkey("none"))
        
        self.root.bind("<Control-Alt-plus>", lambda e: self.change_font_size(1))
        self.root.bind("<Control-Alt-KP_Add>", lambda e: self.change_font_size(1))
        self.root.bind("<Control-Alt-equal>", lambda e: self.change_font_size(1))
        self.root.bind("<Control-Alt-minus>", lambda e: self.change_font_size(-1))
        self.root.bind("<Control-Alt-KP_Subtract>", lambda e: self.change_font_size(-1))
        self.root.bind("<Control-Alt-asterisk>", lambda e: self.change_font_size(reset=True))
        self.root.bind("<Control-Alt-KP_Multiply>", lambda e: self.change_font_size(reset=True))
        
        self.root.bind("<F1>", self.show_hotkeys)

if __name__ == "__main__":
    root = tk.Tk()
    app = DatasetTaggerApp(root)
    root.mainloop()