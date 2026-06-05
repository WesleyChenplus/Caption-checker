import os
import sys
import time
import json
import locale
import shutil
import textwrap
import subprocess
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, ttk, simpledialog, messagebox
from PIL import Image, ImageTk, ImageOps, ImageDraw, ImageFont
from deep_translator import GoogleTranslator

class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        self.widget.bind("<Enter>", self.show_tip)
        self.widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        if self.tip_window or not self.text:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + 30
        self.tip_window = tk.Toplevel(self.widget)
        self.tip_window.wm_overrideredirect(1)
        self.tip_window.wm_geometry(f"+{x}+{y}")
        tk.Label(self.tip_window, text=self.text, justify=tk.LEFT, background="#fffffe", relief=tk.SOLID, bd=1, font=("TkDefaultFont", 9), padx=6, pady=4).pack()

    def hide_tip(self, event=None):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None

class DatasetTaggerApp:
    def __init__(self, root):
        self.root = root
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.current_lang = "English"
        try:
            if sys.platform == 'win32':
                import ctypes
                lid = ctypes.windll.kernel32.GetUserDefaultUILanguage()
                if lid in (1028, 3076, 5124):
                    self.current_lang = "繁體中文"
                elif lid in (2052, 4100):
                    self.current_lang = "简体中文"
            else:
                slang = str(locale.getdefaultlocale()[0]).lower()
                if any(x in slang for x in ["tw", "hk", "hant", "cht"]):
                    self.current_lang = "繁體中文"
                elif any(x in slang for x in ["zh", "hans", "chs"]):
                    self.current_lang = "简体中文"
        except:
            pass

        hk_tc = (
            "【熱鍵列表】\n\n"
            "Ctrl + S : 儲存標記並自動跳下一張\n"
            "Ctrl + T : 啟動正向翻譯\n"
            "Alt + T : 啟動反向翻譯並覆寫\n"
            "Ctrl + Alt + L : 恢復編輯區為原始讀入狀態\n"
            "Alt + M : 標記為已完成 (跳下一張)\n"
            "Alt + N : 標記為不需修改\n"
            "Alt + U : 清除標記狀態\n"
            "Ctrl + H : 顯示/隱藏左側檔案列表\n"
            "Ctrl + Alt + F : 顯示/關閉 檔案過濾搜尋\n"
            "Ctrl + F : 顯示/關閉 搜尋內文\n"
            "Alt + L : 跳至最後編輯的檔案\n"
            "Alt + ↑ / ↓ : 上/下一張圖片\n"
            "滑鼠雙擊圖片 : 定位並置中顯示列表檔案\n"
            "Ctrl + Alt + +/-/* : 文字視窗字體縮放/重設\n\n"
            "【列表專屬熱鍵 (需點擊左側列表)】\n"
            "Del : 刪除選定檔案\n"
            "Ctrl + M : 搬移檔案\n"
            "F2 : 重新命名\n\n"
            "【系統功能】\n"
            "Ctrl + P : 常用提示詞管理\n"
            "Alt + O : 載入資料夾\n"
            "Ctrl + Alt + C / V : 複製 / 貼上標籤\n"
            "F1 : 顯示/關閉 此熱鍵列表"
        )
        hk_sc = (
            "【快捷键列表】\n\n"
            "Ctrl + S : 保存标记并自动跳下一张\n"
            "Ctrl + T : 启动正向翻译\n"
            "Alt + T : 启动反向翻译并覆盖\n"
            "Ctrl + Alt + L : 恢复编辑区为原始读入状态\n"
            "Alt + M : 标记为已完成 (跳下一张)\n"
            "Alt + N : 标记为不需修改\n"
            "Alt + U : 清除标记状态\n"
            "Ctrl + H : 显示/隐藏左侧文件列表\n"
            "Ctrl + Alt + F : 显示/关闭 文件过滤搜索\n"
            "Ctrl + F : 显示/关闭 搜索内文\n"
            "Alt + L : 跳至最后编辑的文件\n"
            "Alt + ↑ / ↓ : 上/下一张图片\n"
            "鼠标双击图片 : 定位并居中显示列表文件\n"
            "Ctrl + Alt + +/-/* : 文字窗口字体缩放/重置\n\n"
            "【列表专属快捷键 (需点击左侧列表)】\n"
            "Del : 删除选定文件\n"
            "Ctrl + M : 移动文件\n"
            "F2 : 重命名\n\n"
            "【系统功能】\n"
            "Ctrl + P : 常用提示词管理\n"
            "Alt + O : 载入文件夹\n"
            "Ctrl + Alt + C / V : 复制 / 粘贴标签\n"
            "F1 : 显示/关闭 此快捷键列表"
        )
        hk_en = (
            "[Hotkeys]\n\n"
            "Ctrl + S : Save tags and Auto-next\n"
            "Ctrl + T : Forward Translation\n"
            "Alt + T : Reverse Translation & Overwrite\n"
            "Ctrl + Alt + L : Restore original text\n"
            "Alt + M : Mark as Completed (Auto-next)\n"
            "Alt + N : Mark as No Changes Needed\n"
            "Alt + U : Clear status mark\n"
            "Ctrl + H : Toggle File List visibility\n"
            "Ctrl + Alt + F : Toggle File Filter/Search\n"
            "Ctrl + F : Toggle Find/Replace\n"
            "Alt + L : Jump to last edited file\n"
            "Alt + ↑ / ↓ : Previous/Next Image\n"
            "Double Click Image : Locate and Center in List\n"
            "Ctrl + Alt + +/-/* : Zoom In/Out/Reset Font Size\n\n"
            "[List-Only Hotkeys]\n"
            "Del : Delete selected file\n"
            "Ctrl + M : Move files\n"
            "F2 : Rename file\n\n"
            "[System Functions]\n"
            "Ctrl + P : Prompt Manager\n"
            "Alt + O : Load Dataset Folder\n"
            "Ctrl + Alt + C / V : Copy / Paste Tags\n"
            "F1 : Toggle Hotkey List"
        )

        self.i18n = {
            "繁體中文": {
                "title": "專業資料集標記與翻譯工具", "open": "開啟(Alt+O)", "show_unmarked": "顯示無標記", "hide_completed": "隱藏已完成",
                "hide_reviewed": "隱藏不需修改", "auto_refresh": "自動更新", "show_stats": "顯示統計", "enable_filter": "啟用篩選",
                "save": "儲存(Ctrl+S)", "trans": "翻譯(Ctrl+T)", "overwrite": "直接覆寫", "rev_trans": "反向翻譯(Alt+T)",
                "lang": "語言:", "api": "API Key:", "toggle_list": "列表(Ctrl+H)", "view_thumb": "縮圖模式", "view_list": "列表模式",
                "thumb_cfg": "縮圖設定", "search_file": "搜尋檔案", "search_text": "搜尋內文", "hotkey": "熱鍵(F1)", "swap": "互換",
                "col_idx": "#", "col_name": "檔名", "col_group": "群組", "col_time": "最後編輯",
                "menu_mark_completed": "標記為已完成", "menu_mark_reviewed": "標記為不需修改", "menu_clear_mark": "清除標記",
                "menu_group": "設定群組...", "menu_group_adv": "進階管理與多選...", "copy_grp": "複製群組", "paste_grp": "貼上群組",
                "menu_rename": "重新命名", "menu_move": "搬移檔案", "menu_delete": "刪除檔案", "menu_explorer": "在資料夾中顯示",
                "menu_insert_prompt": "插入提示詞", "menu_prompt_mgr": "提示詞管理", "copy_tags": "複製標籤", "paste_tags": "貼上標籤",
                "lbl_orig": "【原始標籤】(唯讀)", "lbl_edit": "【編輯區】", "lbl_trans": "【翻譯區】",
                "tip_search_file": "搜尋與過濾", "tip_search_text": "尋找取代", "tip_font_in": "放大字體", "tip_font_out": "縮小字體", "tip_font_rst": "重設字體",
                "find_lbl": "尋找:", "replace_lbl": "取代:", "target_lbl": "範圍:", "btn_find_prev": "上一個", "btn_find_next": "下一個",
                "btn_replace": "取代", "btn_replace_all": "全部取代", "btn_highlight": "標示全部", "lbl_file_prefix": " 檔案: ",
                "img_err": "圖片錯誤", "no_img": "[無圖片]", "toast_auto_sync": "已同步", "toast_restore_orig": "已恢復", "toast_copied": "已複製",
                "toast_clip_empty": "剪貼簿空", "toast_applied": "已套用", "toast_copied_grp": "群組已複製", "toast_not_found": "找不到",
                "toast_replaced": "已替換{}處", "toast_highlighted": "標示{}處", "toast_new_ok": "新建完成", "toast_save_ok": "儲存成功",
                "toast_save_fail": "存檔失敗: 請先選擇檔案", "toast_located": "已定位:", "toast_swap_err": "無法互換", "toast_no_history": "無紀錄",
                "toast_font_size": "字體:", "status_completed": "已完成", "status_reviewed": "不需修改", "status_none": "已清除",
                "toast_mark_ok": "已設為", "msg_del_title": "刪除?", "msg_del_body": "刪除{}個項目?", "msg_sel_one": "請選單一檔案",
                "dlg_rename": "重新命名", "dlg_new_name": "新檔名:", "dlg_err": "錯誤", "dlg_err_dir": "無效路徑",
                "pm_target": "目標:", "pm_browse": "瀏覽", "pm_move": "搬移", "pm_select": "選擇提示詞:", "pm_new_file": "新檔",
                "pm_save_file": "儲存", "pm_apply": "插入編輯區", "dlg_grp_mgr": "群組與標籤管理", "btn_add": "新增/修改",
                "btn_clear": "清空", "btn_del": "刪除", "btn_ok": "確定", "btn_apply_grp": "套用(含標籤)", "btn_apply_grp_only": "套用(僅分組)",
                "dlg_thumb_cfg": "縮圖設定", "lbl_idle_time": "閒置分鐘數:", "btn_gen_all": "啟動背景生成", "lbl_thumb_prog": "未處理:",
                "msg_thumb_done": "縮圖已完成", "btn_save_cfg": "儲存", "search_keyword": "檔名:", "search_group": "群組:",
                "btn_filter": "套用", "btn_clear_filter": "清除", "all_groups": "全部", "stat_unreviewed": "未檢視:{}",
                "stat_processed": "已處理:{}", "hotkey_text": hk_tc
            },
            "简体中文": {
                "title": "专业数据集标记与翻译工具", "open": "打开(Alt+O)", "show_unmarked": "显示无标记", "hide_completed": "隐藏已完成",
                "hide_reviewed": "隐藏不需修改", "auto_refresh": "自动更新", "show_stats": "显示统计", "enable_filter": "启用筛选",
                "save": "保存(Ctrl+S)", "trans": "翻译(Ctrl+T)", "overwrite": "直接覆盖", "rev_trans": "反向翻译(Alt+T)",
                "lang": "语言:", "api": "API Key:", "toggle_list": "列表(Ctrl+H)", "view_thumb": "缩略图模式", "view_list": "列表模式",
                "thumb_cfg": "缩略图设置", "search_file": "搜索文件", "search_text": "搜索内文", "hotkey": "快捷键(F1)", "swap": "互换",
                "col_idx": "#", "col_name": "文件名", "col_group": "群组", "col_time": "最后编辑",
                "menu_mark_completed": "标记为已完成", "menu_mark_reviewed": "标记为不需修改", "menu_clear_mark": "清除标记",
                "menu_group": "设置群组...", "menu_group_adv": "高级管理与多选...", "copy_grp": "复制群组", "paste_grp": "粘贴群组",
                "menu_rename": "重命名", "menu_move": "移动文件", "menu_delete": "删除文件", "menu_explorer": "在文件夹中显示",
                "menu_insert_prompt": "插入提示词", "menu_prompt_mgr": "提示词管理", "copy_tags": "复制标签", "paste_tags": "粘贴标签",
                "lbl_orig": "【原始标签】(唯读)", "lbl_edit": "【编辑区】", "lbl_trans": "【翻译区】",
                "tip_search_file": "搜索与过滤", "tip_search_text": "寻找替换", "tip_font_in": "放大字体", "tip_font_out": "缩小字体", "tip_font_rst": "重置字体",
                "find_lbl": "寻找:", "replace_lbl": "替换:", "target_lbl": "范围:", "btn_find_prev": "上一个", "btn_find_next": "下一个",
                "btn_replace": "替换", "btn_replace_all": "全部替换", "btn_highlight": "标示全部", "lbl_file_prefix": " 文件: ",
                "img_err": "图片错误", "no_img": "[无图片]", "toast_auto_sync": "已同步", "toast_restore_orig": "已恢复", "toast_copied": "已复制",
                "toast_clip_empty": "剪贴板空", "toast_applied": "已应用", "toast_copied_grp": "群组已复制", "toast_not_found": "找不到",
                "toast_replaced": "已替换{}处", "toast_highlighted": "标示{}处", "toast_new_ok": "新建完成", "toast_save_ok": "保存成功",
                "toast_save_fail": "保存失败: 请先选择文件", "toast_located": "已定位:", "toast_swap_err": "无法互换", "toast_no_history": "无纪录",
                "toast_font_size": "字体:", "status_completed": "已完成", "status_reviewed": "不需修改", "status_none": "已清除",
                "toast_mark_ok": "已设为", "msg_del_title": "删除?", "msg_del_body": "删除{}个项目?", "msg_sel_one": "请选单一文件",
                "dlg_rename": "重命名", "dlg_new_name": "新文件名:", "dlg_err": "错误", "dlg_err_dir": "无效路径",
                "pm_target": "目标:", "pm_browse": "浏览", "pm_move": "移动", "pm_select": "选择提示词:", "pm_new_file": "新档",
                "pm_save_file": "保存", "pm_apply": "插入编辑区", "dlg_grp_mgr": "群组与标签管理", "btn_add": "新增/修改",
                "btn_clear": "清空", "btn_del": "删除", "btn_ok": "确定", "btn_apply_grp": "应用(含标签)", "btn_apply_grp_only": "应用(仅群组)",
                "dlg_thumb_cfg": "缩略图设置", "lbl_idle_time": "闲置分钟数:", "btn_gen_all": "启动背景生成", "lbl_thumb_prog": "未处理:",
                "msg_thumb_done": "缩略图已完成", "btn_save_cfg": "保存", "search_keyword": "文件名:", "search_group": "群组:",
                "btn_filter": "应用", "btn_clear_filter": "清除", "all_groups": "全部", "stat_unreviewed": "未检视:{}",
                "stat_processed": "已处理:{}", "hotkey_text": hk_sc
            },
            "English": {
                "title": "Dataset Tagger & Translator", "open": "Open(Alt+O)", "show_unmarked": "Unmarked", "hide_completed": "Hide Done",
                "hide_reviewed": "Hide Rev", "auto_refresh": "Auto-Ref", "show_stats": "Stats", "enable_filter": "Filter",
                "save": "Save(Ctrl+S)", "trans": "Translate(Ctrl+T)", "overwrite": "Overwrite", "rev_trans": "Rev Trans(Alt+T)",
                "lang": "Lang:", "api": "API Key:", "toggle_list": "List(Ctrl+H)", "view_thumb": "Thumb Mode", "view_list": "List Mode",
                "thumb_cfg": "Thumb Cfg", "search_file": "Search Files", "search_text": "Find in Text", "hotkey": "Hotkeys(F1)", "swap": "Swap",
                "col_idx": "#", "col_name": "File Name", "col_group": "Group", "col_time": "Edited",
                "menu_mark_completed": "Mark Completed", "menu_mark_reviewed": "Mark Reviewed", "menu_clear_mark": "Clear Mark",
                "menu_group": "Set Group...", "menu_group_adv": "Group Manager...", "copy_grp": "Copy Group", "paste_grp": "Paste Group",
                "menu_rename": "Rename", "menu_move": "Move", "menu_delete": "Delete", "menu_explorer": "Show Explorer",
                "menu_insert_prompt": "Insert Prompt", "menu_prompt_mgr": "Prompt Manager", "copy_tags": "Copy Tags", "paste_tags": "Paste Tags",
                "lbl_orig": "[Original]", "lbl_edit": "[Edit Area]", "lbl_trans": "[Translation]",
                "tip_search_file": "Filter/Search", "tip_search_text": "Find/Replace", "tip_font_in": "Zoom In", "tip_font_out": "Zoom Out", "tip_font_rst": "Reset Font",
                "find_lbl": "Find:", "replace_lbl": "Replace:", "target_lbl": "Scope:", "btn_find_prev": "Prev", "btn_find_next": "Next",
                "btn_replace": "Replace", "btn_replace_all": "Rep All", "btn_highlight": "Highlight All", "lbl_file_prefix": " File: ",
                "img_err": "Img Error", "no_img": "[No Image]", "toast_auto_sync": "Synced", "toast_restore_orig": "Restored", "toast_copied": "Copied",
                "toast_clip_empty": "Empty", "toast_applied": "Applied", "toast_copied_grp": "Grp Copied", "toast_not_found": "Not Found",
                "toast_replaced": "Replaced {}", "toast_highlighted": "Highlighted {}", "toast_new_ok": "Created", "toast_save_ok": "Saved",
                "toast_save_fail": "Save Fail", "toast_located": "Located:", "toast_swap_err": "Swap Err", "toast_no_history": "No History",
                "toast_font_size": "Size:", "status_completed":"Done", "status_reviewed":"Reviewed", "status_none":"None",
                "toast_mark_ok":"Set to", "msg_del_title":"Delete?", "msg_del_body":"Delete {} items?", "msg_sel_one":"Select 1 file.",
                "dlg_rename":"Rename", "dlg_new_name":"New Name:", "dlg_err":"Error", "dlg_err_dir":"Invalid Dir",
                "pm_target":"Target:", "pm_browse":"Browse", "pm_move":"Move", "pm_select":"Prompt:", "pm_new_file":"New",
                "pm_save_file":"Save", "pm_apply":"Insert", "dlg_grp_mgr":"Group Mgr", "btn_add":"Add/Edit",
                "btn_clear":"Clear", "btn_del":"Del", "btn_ok":"OK", "btn_apply_grp":"Apply w/ Tag", "btn_apply_grp_only":"Apply Grp Only",
                "dlg_thumb_cfg":"Thumb Cfg", "lbl_idle_time":"Idle Mins:", "btn_gen_all":"Start Gen", "lbl_thumb_prog":"Pending:",
                "msg_thumb_done":"Thumbs Done", "btn_save_cfg":"Save", "search_keyword":"Filename:", "search_group":"Group:",
                "btn_filter":"Apply", "btn_clear_filter":"Clear", "all_groups":"All", "stat_unreviewed":"Unrev:{}",
                "stat_processed":"Done:{}", "hotkey_text": hk_en
            }
        }

        self.root.title(self.i18n[self.current_lang]["title"])
        self.root.geometry("1200x700")
        try:
            self.root.state('zoomed')
        except:
            pass

        self.config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app_config.json")
        self.prompt_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "prompt")
        if not os.path.exists(self.prompt_dir):
            os.makedirs(self.prompt_dir)

        self.app_config = {"last_dir": "", "move_history": [], "group_list": [], "idle_minutes": 3}
        self.load_app_config()

        self.all_image_files = []
        self.display_filenames = []
        self.current_dir = self.app_config.get("last_dir", "")
        self.thumb_dir = ""
        self.current_filename = ""
        self.clipboard_tags = ""
        self.clipboard_group = None
        self.supported_formats = ('.png', '.jpg', '.jpeg', '.webp', '.bmp')

        self.var_show_unmarked = tk.BooleanVar(value=True)
        self.var_hide_completed = tk.BooleanVar(value=False)
        self.var_hide_reviewed = tk.BooleanVar(value=False)
        self.var_auto_refresh = tk.BooleanVar(value=False)
        self.var_show_stats = tk.BooleanVar(value=True)
        self.var_enable_filter = tk.BooleanVar(value=False)
        self.var_view_mode = tk.StringVar(value="list")

        self.filter_keyword = ""
        self.filter_group = ""
        self.is_list_visible = True
        self.last_list_width = 380

        self.hk_window = None
        self.sr_window = None
        self.fs_window = None
        self.pm_window = None
        self.mv_window = None
        self.grp_window = None
        self.tc_window = None

        self.hover_timer = None
        self.hover_item = None
        self.hover_tooltip = None
        self.thumb_timer = None

        self.thumb_cache = {}
        self.loaded_thumb_items = set()
        self.missing_thumbs = []
        self.priority_thumbs = []
        self.is_manual_generating = False
        self.stealth_tick_counter = 0
        
        self.last_visible_items = []
        self.last_thumb_update = 0

        self.text_font_size = 11
        self.metadata = {}
        self.sort_col = "time"
        self.sort_reverse = True
        
        # 擴充為支援多國主流語系的對照表
        self.lang_map = {
            "Auto": "auto", 
            "English": "en", 
            "繁體中文": "zh-TW", 
            "简体中文": "zh-CN",
            "日本語": "ja",
            "한국어": "ko",
            "Español": "es",
            "Français": "fr",
            "Deutsch": "de",
            "Русский": "ru"
        }

        self.ui_elements_registry = []
        self.tree_menu_indices = {
            0: "menu_mark_completed", 1: "menu_mark_reviewed", 2: "menu_clear_mark",
            4: "menu_group", 5: "copy_grp", 6: "paste_grp",
            7: "menu_insert_prompt", 9: "menu_rename", 10: "menu_move",
            11: "menu_delete", 13: "menu_explorer", 15: "copy_tags", 16: "paste_tags"
        }

        self._create_placeholder_image()
        self.setup_ui()
        self.bind_shortcuts()
        self.auto_refresh_loop()

        if self.current_dir and os.path.exists(self.current_dir):
            self.load_directory(self.current_dir)
            
        self.process_thumb_tasks()

    def _create_placeholder_image(self):
        """建立內存中的佔位圖 (Generating... / 縮圖生成中)"""
        self.placeholder_img = Image.new('RGB', (100, 100), color='#2d3436')
        draw = ImageDraw.Draw(self.placeholder_img)
        
        draw.rectangle([20, 15, 80, 65], outline="#7f8c8d", width=2)
        draw.polygon([(20, 65), (35, 45), (55, 60), (65, 50), (80, 65)], fill="#7f8c8d")
        draw.ellipse([30, 25, 40, 35], fill="#f1c40f")
        
        try:
            if sys.platform == 'win32':
                font = ImageFont.truetype("msjh.ttc", 13)
                draw.text((26, 75), "生成中...", fill="#ecf0f1", font=font)
            else:
                draw.text((26, 75), "Loading...", fill="#ecf0f1")
        except:
            draw.text((26, 75), "Loading...", fill="#ecf0f1")
            
        self.placeholder_photo = ImageTk.PhotoImage(self.placeholder_img)

    def on_closing(self):
        try:
            self.save_app_config()
            self.save_metadata()
        except:
            pass
        os._exit(0)

    def load_app_config(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        self.app_config.update(data)
            except:
                pass

        raw_grp = self.app_config.get("group_list", [])
        if not isinstance(raw_grp, list):
            raw_grp = []

        migrated_list = []
        for g in raw_grp:
            if isinstance(g, str):
                migrated_list.append({"name": g, "tag": "", "pos": "start"})
            elif isinstance(g, dict) and "name" in g:
                migrated_list.append({"name": g["name"], "tag": g.get("tag", ""), "pos": g.get("pos", "start")})

        self.app_config["group_list"] = migrated_list
        self.app_config["idle_minutes"] = self.app_config.get("idle_minutes", 3)

    def save_app_config(self):
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.app_config, f, ensure_ascii=False)
        except:
            pass

    def load_metadata(self):
        if not self.current_dir:
            return
        mp = os.path.join(self.current_dir, ".tagger_meta.json")
        if os.path.exists(mp):
            try:
                with open(mp, 'r', encoding='utf-8') as f:
                    self.metadata = json.load(f)
            except:
                self.metadata = {}
        else:
            self.metadata = {}

    def save_metadata(self):
        if not self.current_dir:
            return
        try:
            with open(os.path.join(self.current_dir, ".tagger_meta.json"), 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, ensure_ascii=False, indent=2)
        except:
            pass

    def update_file_meta(self, filename, status=None, group=None):
        if filename not in self.metadata:
            self.metadata[filename] = {}
        if status is not None:
            self.metadata[filename]["status"] = status
            self.metadata[filename]["time"] = time.time() if status != "none" else 0
        if group is not None:
            self.metadata[filename]["group"] = group
        self.save_metadata()

    def _create_btn(self, parent, key, callback, side=tk.LEFT, padx=2, **kw):
        btn = tk.Button(parent, text=self.i18n[self.current_lang].get(key, ""), command=callback, **kw)
        btn.pack(side=side, padx=padx)
        self.ui_elements_registry.append((btn, key))
        return btn

    def _create_chk(self, parent, key, var, callback=None, side=tk.LEFT, padx=2, **kw):
        bg_col = "#f0f0f0" if parent.cget("bg") == "#f0f0f0" else "#ddd"
        chk = tk.Checkbutton(parent, text=self.i18n[self.current_lang].get(key, ""), variable=var, command=callback, bg=bg_col, **kw)
        chk.pack(side=side, padx=padx)
        self.ui_elements_registry.append((chk, key))
        return chk

    def _create_lbl(self, parent, key, side=tk.LEFT, padx=0, **kw):
        lbl = tk.Label(parent, text=self.i18n[self.current_lang].get(key, ""), **kw)
        lbl.pack(side=side, padx=padx)
        self.ui_elements_registry.append((lbl, key))
        return lbl

    def setup_ui(self):
        tb = tk.Frame(self.root, bg="#f0f0f0")
        tb.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        ftl = tk.Frame(tb, bg="#f0f0f0")
        ftr = tk.Frame(tb, bg="#f0f0f0")
        ftl.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ftr.pack(side=tk.RIGHT)

        self.btn_open = self._create_btn(ftl, "open", lambda: self.ask_directory(), padx=3)
        self.chk_unmarked = self._create_chk(ftl, "show_unmarked", self.var_show_unmarked, self.refresh_listbox)
        self.chk_hide_completed = self._create_chk(ftl, "hide_completed", self.var_hide_completed, self.refresh_listbox)
        self.chk_hide_reviewed = self._create_chk(ftl, "hide_reviewed", self.var_hide_reviewed, self.refresh_listbox)
        self.chk_auto_refresh = self._create_chk(ftl, "auto_refresh", self.var_auto_refresh)
        self.chk_show_stats = self._create_chk(ftl, "show_stats", self.var_show_stats, self.refresh_listbox, padx=4)

        self.combo_ui = ttk.Combobox(ftr, values=["繁體中文", "简体中文", "English"], width=10, state="readonly")
        self.combo_ui.set(self.current_lang)
        self.combo_ui.bind("<<ComboboxSelected>>", self.change_ui_lang)
        self.combo_ui.pack(side=tk.RIGHT, padx=5)

        self.lbl_ui_lang = self._create_lbl(ftr, "lang", tk.RIGHT, bg="#f0f0f0")
        self.entry_api = ttk.Entry(ftr, width=15)
        self.entry_api.pack(side=tk.RIGHT, padx=10)
        self.lbl_api = self._create_lbl(ftr, "api", tk.RIGHT, bg="#f0f0f0")

        bb = tk.Frame(self.root, bg="#ddd")
        bb.pack(side=tk.BOTTOM, fill=tk.X)
        fbl = tk.Frame(bb, bg="#ddd")
        fbr = tk.Frame(bb, bg="#ddd")
        fbl.pack(side=tk.LEFT, fill=tk.X, expand=True)
        fbr.pack(side=tk.RIGHT)

        self.btn_toggle_list = self._create_btn(fbl, "toggle_list", self.toggle_list_panel, padx=5, pady=5)
        self.btn_view_mode = self._create_btn(fbl, "view_thumb" if self.var_view_mode.get()=="list" else "view_list", self.toggle_view_mode)
        self.btn_thumb_cfg = self._create_btn(fbl, "thumb_cfg", self.open_thumb_cfg)
        self.btn_search_file = self._create_btn(fbl, "search_file", self.open_search_file, padx=5)
        self.chk_enable_filter = self._create_chk(fbl, "enable_filter", self.var_enable_filter, self.refresh_listbox, state=tk.DISABLED)
        self.btn_search_text = self._create_btn(fbl, "search_text", self.open_search_replace)
        self.btn_save = self._create_btn(fbl, "save", self.save_tags, padx=15, bg="#dff0d8")

        self.combo_engine = ttk.Combobox(fbl, values=["Google", "DeepL (API)"], width=12, state="readonly")
        self.combo_engine.set("Google")
        self.combo_engine.pack(side=tk.LEFT, padx=5)

        # 加寬度至 12 以配合多國語言名稱
        self.combo_src = ttk.Combobox(fbl, values=list(self.lang_map.keys()), width=12, state="readonly")
        self.combo_src.set("Auto")
        self.combo_src.pack(side=tk.LEFT, padx=2)

        self.btn_swap = self._create_btn(fbl, "swap", self.swap_languages)

        tgt_def = "English" if self.current_lang == "English" else self.current_lang
        self.combo_tgt = ttk.Combobox(fbl, values=list(self.lang_map.keys())[1:], width=12, state="readonly")
        self.combo_tgt.set(tgt_def)
        self.combo_tgt.pack(side=tk.LEFT, padx=2)

        self.btn_trans = self._create_btn(fbl, "trans", lambda: self.translate_text(False), padx=8, bg="#d9edf7")
        self.btn_rev_trans = self._create_btn(fbl, "rev_trans", lambda: self.translate_text(True), padx=5, bg="#ffe0b2")
        self.btn_overwrite = self._create_btn(fbl, "overwrite", self.overwrite_edit_area)

        ff = tk.Frame(fbl, bg="#ddd")
        ff.pack(side=tk.LEFT, padx=10)
        tk.Button(ff, text="A+", command=lambda: self.change_font_size(1)).pack(side=tk.LEFT, padx=1)
        tk.Button(ff, text="A-", command=lambda: self.change_font_size(-1)).pack(side=tk.LEFT, padx=1)
        tk.Button(ff, text="Rst", command=lambda: self.change_font_size(reset=True)).pack(side=tk.LEFT, padx=1)

        self.btn_hotkey = self._create_btn(fbr, "hotkey", self.show_hotkeys, tk.RIGHT, padx=10, bg="#e0e0e0")

        self.lbl_stats = tk.Label(fbr, fg="#555", bg="#ddd", font=("TkDefaultFont", 10, "bold"))
        self.lbl_stats.pack(side=tk.RIGHT, padx=10)

        self.paned = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, sashwidth=8, bg="#999")
        self.paned.pack(fill=tk.BOTH, expand=True)
        self.f_left = tk.Frame(self.paned, width=self.last_list_width)
        self.paned.add(self.f_left, minsize=250)

        self.style = ttk.Style()
        self.style.configure("Main.Treeview", font=("TkDefaultFont", 10), rowheight=24)
        self.style.configure("Main.Treeview.Heading", font=("TkDefaultFont", 10, "bold"))
        self.style.configure("Group.Treeview", font=("TkDefaultFont", 10), rowheight=24)
        self.style.configure("Group.Treeview.Heading", font=("TkDefaultFont", 10, "bold"))

        self.tree = ttk.Treeview(self.f_left, columns=("idx", "file", "group", "time"), show="headings", style="Main.Treeview")
        
        self.tree.heading("idx", command=lambda: self.sort_tree("idx"))
        self.tree.heading("file", command=lambda: self.sort_tree("file"))
        self.tree.heading("group", command=lambda: self.sort_tree("group"))
        self.tree.heading("time", command=lambda: self.sort_tree("time"))
        
        self.tree.column("#0", width=300, minwidth=200, stretch=True)
        self.tree.column("idx", width=40, anchor=tk.CENTER)
        self.tree.column("file", width=140, anchor=tk.W)
        self.tree.column("group", width=100, anchor=tk.CENTER)
        self.tree.column("time", width=80, anchor=tk.CENTER)

        self.tree.tag_configure("top1", background="#ffcccc")
        self.tree.tag_configure("completed", background="#d4edda")
        self.tree.tag_configure("reviewed", background="#fff3cd")
        self.tree.tag_configure("normal", background="white")

        self.scrollbar = ttk.Scrollbar(self.f_left, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.tree.bind('<<TreeviewSelect>>', self.on_file_select)
        self.tree.bind("<Motion>", self.on_tree_motion)
        self.tree.bind("<Leave>", self.cancel_tree_hover)

        self.menu_tree = tk.Menu(self.root, tearoff=0)
        self.menu_tree.add_command(command=lambda: self.manual_mark_file("completed"))
        self.menu_tree.add_command(command=lambda: self.manual_mark_file("reviewed"))
        self.menu_tree.add_command(command=lambda: self.manual_mark_file("none"))
        self.menu_tree.add_separator()

        self.menu_group = tk.Menu(self.menu_tree, tearoff=0)
        self.menu_tree.add_cascade(menu=self.menu_group)
        self.menu_tree.add_command(command=self.copy_group_settings)
        self.menu_tree.add_command(command=self.paste_group_settings)

        self.menu_prompt = tk.Menu(self.menu_tree, tearoff=0)
        self.menu_tree.add_cascade(menu=self.menu_prompt)
        self.menu_tree.add_separator()

        self.menu_tree.add_command(command=self.rename_file)
        self.menu_tree.add_command(command=self.move_files)
        self.menu_tree.add_command(command=self.delete_files)
        self.menu_tree.add_separator()

        self.menu_tree.add_command(command=self.open_in_explorer)
        self.menu_tree.add_separator()

        self.menu_tree.add_command(command=self.copy_tags)
        self.menu_tree.add_command(command=self.paste_tags)
        self.tree.bind("<Button-3>", self.show_tree_menu)

        self.f_right = tk.Frame(self.paned)
        self.paned.add(self.f_right, minsize=500)
        for i in range(2):
            self.f_right.columnconfigure(i, weight=1)
            self.f_right.rowconfigure(i, weight=1)

        self.f_image_container = tk.Frame(self.f_right, bg="black")
        self.f_image_container.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)

        self.lbl_filename = tk.Label(self.f_image_container, bg="#2d3436", fg="#f1c40f", font=("TkDefaultFont", 11, "bold"), pady=4)
        self.lbl_filename.pack(side=tk.TOP, fill=tk.X)
        self.lbl_image = tk.Label(self.f_image_container, text="Preview", bg="black", fg="white")
        self.lbl_image.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.lbl_image.bind("<Double-1>", self.sync_list_to_image)
        self.lbl_filename.bind("<Double-1>", self.sync_list_to_image)

        self.f_orig_wrapper = tk.Frame(self.f_right)
        self.f_orig_wrapper.grid(row=0, column=1, sticky="nsew", padx=2, pady=2)
        self.lbl_orig_title = self._create_lbl(self.f_orig_wrapper, "lbl_orig", tk.TOP, font=("TkDefaultFont", 10, "bold"), anchor="w", fg="#7f8c8d", pady=2)
        self.text_original = tk.Text(self.f_orig_wrapper, bg="#f5f5f5", state=tk.DISABLED, font=("TkTextFont", self.text_font_size))
        self.text_original.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.f_edit_wrapper = tk.Frame(self.f_right)
        self.f_edit_wrapper.grid(row=1, column=0, sticky="nsew", padx=2, pady=2)
        self.lbl_edit_title = self._create_lbl(self.f_edit_wrapper, "lbl_edit", tk.TOP, font=("TkDefaultFont", 10, "bold"), anchor="w", fg="#2980b9", pady=2)
        self.text_edit = tk.Text(self.f_edit_wrapper, undo=True, font=("TkTextFont", self.text_font_size))
        self.text_edit.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.f_trans_wrapper = tk.Frame(self.f_right)
        self.f_trans_wrapper.grid(row=1, column=1, sticky="nsew", padx=2, pady=2)
        self.lbl_trans_title = self._create_lbl(self.f_trans_wrapper, "lbl_trans", tk.TOP, font=("TkDefaultFont", 10, "bold"), anchor="w", fg="#27ae60", pady=2)
        self.text_translated = tk.Text(self.f_trans_wrapper, bg="#fffde7", undo=True, font=("TkTextFont", self.text_font_size))
        self.text_translated.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        for tw in (self.text_edit, self.text_translated):
            tw.tag_configure("sm", background="#ffeaa7", foreground="#d35400")

        self.change_ui_lang()

    def change_ui_lang(self, event=None):
        if hasattr(self, 'combo_ui'):
            self.current_lang = self.combo_ui.get()
        cfg = self.i18n.get(self.current_lang, self.i18n["English"])

        self.root.title(cfg["title"])

        for element, key in self.ui_elements_registry:
            if element.winfo_exists():
                element.config(text=cfg.get(key, ""))

        self.btn_view_mode.config(text=cfg["view_thumb"] if self.var_view_mode.get() == "list" else cfg["view_list"])
        
        if hasattr(self, 'tt_search_file') and self.tt_search_file:
            self.tt_search_file.text = cfg.get("tip_search_file", "")
        if hasattr(self, 'tt_search_text') and self.tt_search_text:
            self.tt_search_text.text = cfg.get("tip_search_text", "")

        for win_ref in ['filter_search_window', 'search_replace_window', 'group_manager_window', 'prompt_manager_window', 'thumb_config_window', 'hotkey_window', 'move_files_window']:
            w = getattr(self, win_ref, None)
            if w and w.winfo_exists():
                w.destroy()
                setattr(self, win_ref, None)

        for c_id, k in zip(("idx","file","group","time"), ("col_idx","col_name","col_group","col_time")):
            self.tree.heading(c_id, text=cfg[k])

        for idx, k in self.tree_menu_indices.items():
            self.menu_tree.entryconfig(idx, label=cfg.get(k, ""))

        if not self.current_filename:
            self.lbl_filename.config(text=cfg["no_img"])
        else:
            i = self.display_filenames.index(self.current_filename) if self.current_filename in self.display_filenames else -1
            if i != -1:
                self.lbl_filename.config(text=f"{cfg['lbl_file_prefix']} [{i+1}] {self.current_filename} ")
        self.refresh_listbox()

    def on_tree_motion(self, event):
        item = self.tree.identify_row(event.y)
        if item != self.hover_item:
            self.cancel_tree_hover()
            self.hover_item = item
            if item:
                self.hover_timer = self.root.after(1000, lambda: self.show_tree_tooltip(event.x_root, event.y_root, item))

    def cancel_tree_hover(self, event=None):
        if self.hover_timer:
            self.root.after_cancel(self.hover_timer)
            self.hover_timer = None
        if self.hover_tooltip:
            self.hover_tooltip.destroy()
            self.hover_tooltip = None
        self.hover_item = None

    def show_tree_tooltip(self, x, y, item):
        if not self.tree.exists(item): return

        idx = self.tree.index(item)
        filename = self.display_filenames[idx]
        txt_path = os.path.join(self.current_dir, f"{os.path.splitext(filename)[0]}.txt")
        tags = "（無標記內容）"

        if os.path.exists(txt_path):
            with open(txt_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content:
                    tags = content

        group = self.metadata.get(filename, {}).get("group", "（無分類）")
        if not group:
            group = "（無分類）"

        wrapped_tags = textwrap.fill(tags, width=60)
        cfg = self.i18n[self.current_lang]
        info_text = f"【{cfg['col_group']}】: {group}\n【{cfg['lbl_edit']}】:\n{wrapped_tags}"

        self.hover_tooltip = tk.Toplevel(self.root)
        self.hover_tooltip.wm_overrideredirect(True)
        self.hover_tooltip.attributes("-topmost", True)

        tk.Label(self.hover_tooltip, text=info_text, justify=tk.LEFT, bg="#ffffe0", fg="#333", relief=tk.SOLID, bd=1, font=("TkDefaultFont", 10), padx=8, pady=8).pack()

        self.hover_tooltip.update_idletasks()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        tw = self.hover_tooltip.winfo_width()
        th = self.hover_tooltip.winfo_height()

        rx, ry = x + 15, y + 15
        if rx + tw > sw: rx = sw - tw - 5
        if ry + th > sh: ry = sh - th - 5
        self.hover_tooltip.geometry(f"+{rx}+{ry}")

    def get_idle_time(self):
        try:
            if sys.platform == "win32":
                import ctypes
                class LASTINPUTINFO(ctypes.Structure):
                    _fields_ = [("cbSize", ctypes.c_uint), ("dwTime", ctypes.c_uint)]
                lii = LASTINPUTINFO()
                lii.cbSize = ctypes.sizeof(LASTINPUTINFO)
                ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lii))
                millis = ctypes.windll.kernel32.GetTickCount() - lii.dwTime
                return millis / 1000.0
            else:
                current_ptr = self.root.winfo_pointerxy()
                if not hasattr(self, 'last_ptr'):
                    self.last_ptr = current_ptr
                    self.last_ptr_time = time.time()
                if current_ptr != self.last_ptr:
                    self.last_ptr = current_ptr
                    self.last_ptr_time = time.time()
                return time.time() - self.last_ptr_time
        except:
            return 0

    def open_thumb_cfg(self, event=None):
        if hasattr(self, 'tc_window') and self.tc_window and self.tc_window.winfo_exists():
            self.tc_window.lift()
            return

        cfg = self.i18n[self.current_lang]
        self.tc_window = win = tk.Toplevel(self.root)
        win.title(cfg["thumb_cfg"])
        win.geometry("380x150")
        win.attributes("-topmost", True)

        f1 = tk.Frame(win, pady=10)
        f1.pack(fill=tk.X)
        tk.Label(f1, text=cfg["lbl_idle_time"]).pack(side=tk.LEFT, padx=10)
        var_idle = tk.StringVar(value=str(self.app_config.get("idle_minutes", 3)))
        tk.Entry(f1, textvariable=var_idle, width=5).pack(side=tk.LEFT)

        def save_idle():
            try:
                self.app_config["idle_minutes"] = int(var_idle.get())
                self.save_app_config()
                self.show_toast(cfg["toast_applied"], bg_color="#4CAF50")
            except:
                pass

        tk.Button(f1, text=cfg["btn_save_cfg"], command=save_idle).pack(side=tk.LEFT, padx=10)

        f2 = tk.Frame(win, pady=10)
        f2.pack(fill=tk.X)

        total = len(self.all_image_files)
        pending = len(self.missing_thumbs)
        self.lbl_thumb_prog = tk.Label(f2, text=f"{cfg['lbl_thumb_prog']} {pending} / {total}")
        self.lbl_thumb_prog.pack(side=tk.LEFT, padx=10)

        def start_manual():
            self.is_manual_generating = True
            self.show_toast("Background generation started...", bg_color="#0984e3")

        tk.Button(f2, text=cfg["btn_gen_all"], command=start_manual, bg="#d9edf7").pack(side=tk.RIGHT, padx=10)
        win.protocol("WM_DELETE_WINDOW", lambda: (win.destroy(), setattr(self, 'tc_window', None)))

    def toggle_view_mode(self):
        cfg = self.i18n[self.current_lang]
        if self.var_view_mode.get() == "list":
            self.var_view_mode.set("thumb")
            self.btn_view_mode.config(text=cfg["view_list"])
        else:
            self.var_view_mode.set("list")
            self.btn_view_mode.config(text=cfg["view_thumb"])
        self.refresh_listbox()

    def create_thumb_file(self, filename):
        thumb_path = os.path.join(self.thumb_dir, f"{filename}.thumb.jpg")
        if os.path.exists(thumb_path):
            return True
        orig_path = os.path.join(self.current_dir, filename)
        try:
            img = Image.open(orig_path)
            try:
                img = ImageOps.exif_transpose(img)
            except:
                pass
            img.thumbnail((100, 100))
            if img.mode != "RGB":
                img = img.convert("RGB")
            img.save(thumb_path, "JPEG")
            return True
        except:
            return False

    def process_thumb_tasks(self):
        current_time = time.time()
        
        if self.var_view_mode.get() == "thumb":
            children = self.tree.get_children()
            total_items = len(children)
            if total_items > 0:
                yv = self.tree.yview()
                start_idx = max(0, int(yv[0] * total_items) - 3)
                end_idx = min(total_items, int(yv[1] * total_items) + 3)

                visible_items = []
                first_idx = -1
                for i in range(start_idx, end_idx):
                    item = children[i]
                    if self.tree.bbox(item):
                        if first_idx == -1:
                            first_idx = i
                        visible_items.append(item)

                viewport_changed = (visible_items != self.last_visible_items)
                
                if viewport_changed or (current_time - self.last_thumb_update >= 0.5):
                    self.last_visible_items = visible_items
                    self.last_thumb_update = current_time
                    
                    if first_idx != -1:
                        visible_count = len(visible_items)
                        last_idx = first_idx + visible_count
                        
                        target_items = visible_items + list(children[last_idx : last_idx + visible_count])
                        target_ids = set(target_items)

                        unload_ids = self.loaded_thumb_items - target_ids
                        for uid in unload_ids:
                            if self.tree.exists(uid):
                                self.tree.item(uid, image="")
                                try:
                                    idx_uid = self.tree.index(uid)
                                    if idx_uid < len(self.display_filenames):
                                        filename_to_remove = self.display_filenames[idx_uid]
                                        self.thumb_cache.pop(filename_to_remove, None)
                                except:
                                    pass

                        self.loaded_thumb_items = target_ids
                        new_priority = []
                        
                        for item_id in visible_items:
                            idx = self.tree.index(item_id)
                            if idx >= len(self.display_filenames): continue
                            filename = self.display_filenames[idx]
                            thumb_path = os.path.join(self.thumb_dir, f"{filename}.thumb.jpg")
                            
                            if not os.path.exists(thumb_path):
                                if self.tree.item(item_id, "image") != str(self.placeholder_photo):
                                    self.tree.item(item_id, image=self.placeholder_photo)
                                new_priority.append(filename)
                            else:
                                if filename not in self.thumb_cache:
                                    try: self.thumb_cache[filename] = ImageTk.PhotoImage(Image.open(thumb_path))
                                    except: self.thumb_cache[filename] = self.placeholder_photo
                                if self.tree.item(item_id, "image") != str(self.thumb_cache[filename]):
                                    self.tree.item(item_id, image=self.thumb_cache[filename])
                        
                        for item_id in target_items[len(visible_items):]:
                            idx = self.tree.index(item_id)
                            if idx >= len(self.display_filenames): continue
                            filename = self.display_filenames[idx]
                            thumb_path = os.path.join(self.thumb_dir, f"{filename}.thumb.jpg")
                            
                            if not os.path.exists(thumb_path):
                                if self.tree.item(item_id, "image") != str(self.placeholder_photo):
                                    self.tree.item(item_id, image=self.placeholder_photo)
                                new_priority.append(filename)
                            else:
                                if filename not in self.thumb_cache:
                                    try: self.thumb_cache[filename] = ImageTk.PhotoImage(Image.open(thumb_path))
                                    except: self.thumb_cache[filename] = self.placeholder_photo
                                if self.tree.item(item_id, "image") != str(self.thumb_cache[filename]):
                                    self.tree.item(item_id, image=self.thumb_cache[filename])
                        
                        self.priority_thumbs = new_priority

        im = self.app_config.get("idle_minutes", 3)
        idl = False
        if im > 0 and self.get_idle_time() > (im * 60):
            idl = True

        if self.missing_thumbs or self.priority_thumbs:
            if self.is_manual_generating or idl:
                gen_limit = 5
                skip_limit = 100
            else:
                self.stealth_tick_counter += 1
                if self.stealth_tick_counter < 5:
                    self.thumb_timer = self.root.after(100, self.process_thumb_tasks)
                    return 
                self.stealth_tick_counter = 0
                gen_limit = 1
                skip_limit = 20

            gen_count = 0
            skip_count = 0
            while (self.priority_thumbs or self.missing_thumbs):
                if self.priority_thumbs:
                    filename = self.priority_thumbs.pop(0)
                    if filename in self.missing_thumbs:
                        self.missing_thumbs.remove(filename)
                else:
                    filename = self.missing_thumbs.pop(0)
                    
                thumb_path = os.path.join(self.thumb_dir, f"{filename}.thumb.jpg")
                if not os.path.exists(thumb_path):
                    self.create_thumb_file(filename)
                    gen_count += 1
                    
                    try:
                        if filename in self.display_filenames:
                            idx = self.display_filenames.index(filename)
                            if idx < len(self.tree.get_children()):
                                item_id = self.tree.get_children()[idx]
                                if self.tree.bbox(item_id):
                                    photo = ImageTk.PhotoImage(Image.open(thumb_path))
                                    self.thumb_cache[filename] = photo
                                    self.tree.item(item_id, image=photo)
                    except:
                        pass
                    
                    if hasattr(self, 'lbl_thumb_prog') and self.lbl_thumb_prog.winfo_exists():
                        cfg = self.i18n[self.current_lang]
                        self.lbl_thumb_prog.config(text=f"{cfg['lbl_thumb_prog']} {len(self.missing_thumbs)} / {len(self.all_image_files)}")
                        
                    if gen_count >= gen_limit:
                        break
                else:
                    skip_count += 1
                    if skip_count >= skip_limit:
                        break

            if self.is_manual_generating and not self.missing_thumbs and not self.priority_thumbs:
                self.is_manual_generating = False
                self.show_toast(self.i18n[self.current_lang]["msg_thumb_done"], bg_color="#4CAF50")

        self.thumb_timer = self.root.after(100, self.process_thumb_tasks)

    def toggle_group_for_selected(self, group_obj, only_group=False):
        selected = self.tree.selection()
        if not selected: return

        sel_files = [self.display_filenames[self.tree.index(i)] for i in selected]

        for filename in sel_files:
            txt_path = os.path.join(self.current_dir, f"{os.path.splitext(filename)[0]}.txt")
            meta = self.metadata.get(filename, {})
            current_groups = [g.strip() for g in meta.get("group", "").split('+') if g.strip()]
            g_name = group_obj["name"]

            is_adding = False
            if g_name in current_groups:
                current_groups.remove(g_name)
            else:
                current_groups.append(g_name)
                is_adding = True

            self.update_file_meta(filename, group=" + ".join(current_groups))

            if not only_group and group_obj.get("tag"):
                tag_to_apply = group_obj["tag"].strip()
                content = ""
                if os.path.exists(txt_path):
                    with open(txt_path, 'r', encoding='utf-8') as f:
                        content = f.read().strip()

                tags = [t.strip() for t in content.split(',') if t.strip()]
                tags = [t for t in tags if t.lower() != tag_to_apply.lower()]

                if is_adding:
                    if group_obj.get("pos") == "end":
                        tags.append(tag_to_apply)
                    else:
                        tags.insert(0, tag_to_apply)

                new_content = ", ".join(tags)
                with open(txt_path, 'w', encoding='utf-8') as fw:
                    fw.write(new_content)
                self.update_file_meta(filename, status="completed")

        self.refresh_listbox()
        if self.current_filename in sel_files:
            self.on_file_select()

    def show_tree_menu(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            if item not in self.tree.selection():
                self.tree.selection_set(item)
            cfg = self.i18n[self.current_lang]

            self.menu_group.delete(0, tk.END)
            for g in self.app_config.get("group_list", []):
                if g.get("tag"):
                    sub = tk.Menu(self.menu_group, tearoff=0)
                    sub.add_command(label=cfg.get("btn_apply_grp_only", "Apply Group Only"), command=lambda x=g: self.toggle_group_for_selected(x, only_group=True))
                    sub.add_command(label=cfg.get("btn_apply_grp", "Apply w/ Tags"), command=lambda x=g: self.toggle_group_for_selected(x, only_group=False))
                    self.menu_group.add_cascade(label=g["name"], menu=sub)
                else:
                    self.menu_group.add_command(label=g["name"], command=lambda x=g: self.toggle_group_for_selected(x, only_group=True))

            self.menu_group.add_separator()
            self.menu_group.add_command(label=cfg["menu_group_adv"], command=self.open_group_manager)

            self.menu_prompt.delete(0, tk.END)
            prompt_files = [f for f in os.listdir(self.prompt_dir) if f.endswith('.txt')]
            for pf in prompt_files:
                self.menu_prompt.add_command(label=pf, command=lambda x=pf: self.insert_prompt_to_editor(x))
            self.menu_prompt.add_separator()
            self.menu_prompt.add_command(label=cfg["menu_prompt_mgr"], command=self.open_prompt_manager)

            self.menu_tree.post(event.x_root, event.y_root)

    def copy_group_settings(self):
        selected = self.tree.selection()
        if not selected: return
        idx = self.tree.index(selected[0])
        filename = self.display_filenames[idx]
        self.clipboard_group = self.metadata.get(filename, {}).get("group", "")
        self.show_toast(self.i18n[self.current_lang]["toast_copied_grp"])

    def paste_group_settings(self):
        if self.clipboard_group is None: return
        selected = self.tree.selection()
        if not selected: return
        for item in selected:
            idx = self.tree.index(item)
            self.update_file_meta(self.display_filenames[idx], group=self.clipboard_group)
        self.refresh_listbox()
        self.show_toast(self.i18n[self.current_lang]["toast_applied"])

    def insert_prompt_to_editor(self, prompt_filename):
        if not self.current_filename: return
        prompt_path = os.path.join(self.prompt_dir, prompt_filename)
        if not os.path.exists(prompt_path): return

        with open(prompt_path, 'r', encoding='utf-8') as f:
            prompt_text = f.read().strip()

        if not prompt_text: return

        current_text = self.text_edit.get("1.0", tk.END).strip()
        new_text = f"{prompt_text}, {current_text}" if current_text else prompt_text
        self.text_edit.delete("1.0", tk.END)
        self.text_edit.insert("1.0", new_text)
        self.show_toast(self.i18n[self.current_lang]["toast_applied"])

    def copy_tags(self, event=None):
        self.clipboard_tags = self.text_edit.get("1.0", tk.END).strip()
        self.show_toast(self.i18n[self.current_lang]["toast_copied"])
        return "break"

    def paste_tags(self, event=None):
        if not self.clipboard_tags:
            self.show_toast(self.i18n[self.current_lang]["toast_clip_empty"], bg_color="#f44336")
            return "break"
        selected = self.tree.selection()
        if not selected: return "break"
        for item in selected:
            idx = self.tree.index(item)
            filename = self.display_filenames[idx]
            txt_path = os.path.join(self.current_dir, f"{os.path.splitext(filename)[0]}.txt")
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write(self.clipboard_tags)
            self.update_file_meta(filename, status="completed")
        self.refresh_listbox()
        self.show_toast(self.i18n[self.current_lang]["toast_applied"])
        return "break"

    def delete_files(self, event=None):
        selected = self.tree.selection()
        if not selected: return "break"
        cfg = self.i18n[self.current_lang]
        if not messagebox.askyesno(cfg["msg_del_title"], cfg["msg_del_body"].format(len(selected))): return "break"
        for item in selected:
            idx = self.tree.index(item)
            filename = self.display_filenames[idx]
            base = os.path.splitext(filename)[0]
            try:
                os.remove(os.path.join(self.current_dir, filename))
                txt_path = os.path.join(self.current_dir, f"{base}.txt")
                if os.path.exists(txt_path):
                    os.remove(txt_path)
            except Exception as e:
                print(f"Delete failed: {e}")
        self.load_directory(self.current_dir)
        return "break"

    def move_files(self, event=None):
        if hasattr(self, 'move_files_window') and self.move_files_window and self.move_files_window.winfo_exists():
            self.move_files_window.destroy()
            self.move_files_window = None
            return "break"

        selected = self.tree.selection()
        if not selected: return "break"
        cfg = self.i18n[self.current_lang]

        self.move_files_window = win = tk.Toplevel(self.root)
        win.title(cfg["menu_move"])
        win.geometry("450x120")
        win.attributes("-topmost", True)
        tk.Label(win, text=cfg["pm_target"]).pack(pady=5)

        cb_target = ttk.Combobox(win, values=self.app_config.get("move_history", []), width=50)
        cb_target.pack(pady=5)
        if self.app_config.get("move_history"):
            cb_target.set(self.app_config["move_history"][0])

        def do_move():
            target = cb_target.get()
            if not target or not os.path.exists(target):
                messagebox.showerror(cfg["dlg_err"], cfg["dlg_err_dir"])
                return
            for item in selected:
                idx = self.tree.index(item)
                filename = self.display_filenames[idx]
                base = os.path.splitext(filename)[0]
                try:
                    shutil.move(os.path.join(self.current_dir, filename), os.path.join(target, filename))
                    txt_path = os.path.join(self.current_dir, f"{base}.txt")
                    if os.path.exists(txt_path):
                        shutil.move(txt_path, os.path.join(target, f"{base}.txt"))
                except Exception as e:
                    print(e)

            history = self.app_config.get("move_history", [])
            if target in history:
                history.remove(target)
            history.insert(0, target)
            self.app_config["move_history"] = history[:5]
            self.save_app_config()

            win.destroy()
            self.move_files_window = None
            self.load_directory(self.current_dir)

        def browse():
            d = filedialog.askdirectory()
            if d:
                cb_target.set(d)

        btn_f = tk.Frame(win)
        btn_f.pack(pady=5)
        tk.Button(btn_f, text=cfg["pm_browse"], command=browse).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_f, text=cfg["pm_move"], command=do_move, bg="#ffcccc").pack(side=tk.LEFT, padx=5)
        win.protocol("WM_DELETE_WINDOW", lambda: (win.destroy(), setattr(self, 'move_files_window', None)))
        return "break"

    def rename_file(self, event=None):
        selected = self.tree.selection()
        cfg = self.i18n[self.current_lang]
        if not selected or len(selected) > 1:
            messagebox.showinfo("Info", cfg["msg_sel_one"])
            return "break"
        idx = self.tree.index(selected[0])
        old_file = self.display_filenames[idx]
        old_base, ext = os.path.splitext(old_file)
        new_base = simpledialog.askstring(cfg["dlg_rename"], cfg["dlg_new_name"], initialvalue=old_base)
        if new_base and new_base != old_base:
            new_file = new_base + ext
            try:
                os.rename(os.path.join(self.current_dir, old_file), os.path.join(self.current_dir, new_file))
                old_txt = os.path.join(self.current_dir, f"{old_base}.txt")
                if os.path.exists(old_txt):
                    os.rename(old_txt, os.path.join(self.current_dir, f"{new_base}.txt"))
                if old_file in self.metadata:
                    self.metadata[new_file] = self.metadata.pop(old_file)
                    self.save_metadata()
                self.load_directory(self.current_dir)
            except Exception as e:
                messagebox.showerror(cfg["dlg_err"], str(e))
        return "break"

    def open_group_manager(self, event=None):
        if hasattr(self, 'group_manager_window') and self.group_manager_window and self.group_manager_window.winfo_exists():
            self.group_manager_window.destroy()
            self.group_manager_window = None
            return "break"

        cfg = self.i18n[self.current_lang]
        self.group_manager_window = win = tk.Toplevel(self.root)
        win.title(cfg["dlg_grp_mgr"])
        win.geometry("480x350")
        win.attributes("-topmost", True)

        columns = ("name", "tag", "pos")
        tree_grp = ttk.Treeview(win, columns=columns, show="headings", selectmode="extended", style="Group.Treeview")
        tree_grp.heading("name", text="群組名稱")
        tree_grp.heading("tag", text="綁定 TAG")
        tree_grp.heading("pos", text="寫入位置")
        tree_grp.column("name", width=150)
        tree_grp.column("tag", width=180)
        tree_grp.column("pos", width=100, anchor=tk.CENTER)
        tree_grp.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        def refresh_list():
            tree_grp.delete(*tree_grp.get_children())
            for g in self.app_config.get("group_list", []):
                tree_grp.insert("", tk.END, values=(g["name"], g.get("tag", ""), g.get("pos", "start")))

        refresh_list()

        f_add = tk.Frame(win)
        f_add.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(f_add, text="名稱:").pack(side=tk.LEFT)
        ent_new = ttk.Entry(f_add, width=12)
        ent_new.pack(side=tk.LEFT, padx=(0,5))

        tk.Label(f_add, text="TAG:").pack(side=tk.LEFT)
        ent_tag = ttk.Entry(f_add, width=15)
        ent_tag.pack(side=tk.LEFT, padx=(0,5))

        cb_pos = ttk.Combobox(f_add, values=["start", "end"], width=6, state="readonly")
        cb_pos.set("start")
        cb_pos.pack(side=tk.LEFT, padx=(0,5))

        def on_tree_select(e):
            selected = tree_grp.selection()
            if not selected: return
            vals = tree_grp.item(selected[0], "values")
            if vals:
                ent_new.delete(0, tk.END)
                ent_new.insert(0, vals[0])
                ent_tag.delete(0, tk.END)
                ent_tag.insert(0, vals[1] if vals[1] else "")
                cb_pos.set(vals[2] if len(vals) > 2 and vals[2] else "start")

        tree_grp.bind("<<TreeviewSelect>>", on_tree_select)

        def add_grp():
            val = ent_new.get().strip()
            tag_val = ent_tag.get().strip()
            pos_val = cb_pos.get()

            if val:
                for g in self.app_config["group_list"]:
                    if g["name"] == val:
                        g["tag"] = tag_val
                        g["pos"] = pos_val
                        self.save_app_config()
                        refresh_list()
                        ent_new.delete(0, tk.END)
                        ent_tag.delete(0, tk.END)
                        cb_pos.set("start")
                        return
                self.app_config["group_list"].append({"name": val, "tag": tag_val, "pos": pos_val})
                self.save_app_config()
                refresh_list()
                ent_new.delete(0, tk.END)
                ent_tag.delete(0, tk.END)
                cb_pos.set("start")

        def clear_inputs():
            ent_new.delete(0, tk.END)
            ent_tag.delete(0, tk.END)
            cb_pos.set("start")

        def del_grp():
            selected = tree_grp.selection()
            if not selected: return
            names_to_del = [tree_grp.item(i, "values")[0] for i in selected]
            self.app_config["group_list"] = [g for g in self.app_config["group_list"] if g["name"] not in names_to_del]
            self.save_app_config()
            refresh_list()

        def apply_grp(only_group=False):
            selected = tree_grp.selection()
            if not selected: return
            names_to_apply = [tree_grp.item(i, "values")[0] for i in selected]

            for g_name in names_to_apply:
                g_obj = next((x for x in self.app_config["group_list"] if x["name"] == g_name), None)
                if g_obj:
                    self.toggle_group_for_selected(g_obj, only_group=only_group)
            win.destroy()

        tk.Button(f_add, text=cfg.get("btn_add", "Add / Edit"), command=add_grp).pack(side=tk.LEFT, padx=2)
        tk.Button(f_add, text=cfg.get("btn_clear", "Clear"), command=clear_inputs).pack(side=tk.LEFT, padx=2)

        btn_f = tk.Frame(win)
        btn_f.pack(fill=tk.X, padx=10, pady=5)
        tk.Button(btn_f, text=cfg["btn_del"], command=del_grp).pack(side=tk.LEFT, padx=5)

        tk.Button(btn_f, text=cfg.get("btn_apply_grp", "Apply w/ Tags"), command=lambda: apply_grp(False), bg="#ccffcc").pack(side=tk.RIGHT, padx=5)
        tk.Button(btn_f, text=cfg.get("btn_apply_grp_only", "Apply Group Only"), command=lambda: apply_grp(True)).pack(side=tk.RIGHT, padx=5)

        win.protocol("WM_DELETE_WINDOW", lambda: (win.destroy(), setattr(self, 'group_manager_window', None)))
        return "break"

    def open_prompt_manager(self, event=None):
        if hasattr(self, 'prompt_manager_window') and self.prompt_manager_window and self.prompt_manager_window.winfo_exists():
            self.prompt_manager_window.destroy()
            self.prompt_manager_window = None
            return "break"

        cfg = self.i18n[self.current_lang]
        self.prompt_manager_window = win = tk.Toplevel(self.root)
        win.title(cfg["menu_prompt_mgr"])
        win.geometry("550x450")

        f_top = tk.Frame(win)
        f_top.pack(fill=tk.X, padx=5, pady=5)
        tk.Label(f_top, text=cfg["pm_select"]).pack(side=tk.LEFT)
        cb_prompts = ttk.Combobox(f_top, state="readonly", width=25)
        cb_prompts.pack(side=tk.LEFT, padx=5)

        text_preview = tk.Text(win, height=12, font=("TkTextFont", self.text_font_size))
        text_preview.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        def refresh_combo(select_name=None):
            files = [f for f in os.listdir(self.prompt_dir) if f.endswith('.txt')]
            cb_prompts['values'] = files
            if select_name and select_name in files:
                cb_prompts.set(select_name)
            elif files:
                cb_prompts.set(files[0])
            else:
                cb_prompts.set('')
            load_preview()

        def load_preview(*args):
            sel = cb_prompts.get()
            text_preview.delete("1.0", tk.END)
            if sel and os.path.exists(os.path.join(self.prompt_dir, sel)):
                with open(os.path.join(self.prompt_dir, sel), 'r', encoding='utf-8') as f:
                    text_preview.insert("1.0", f.read())

        cb_prompts.bind("<<ComboboxSelected>>", load_preview)

        def create_new():
            name = simpledialog.askstring(cfg["pm_new_file"], cfg["dlg_new_name"])
            if not name: return
            if not name.endswith('.txt'): name += '.txt'
            path = os.path.join(self.prompt_dir, name)
            if not os.path.exists(path):
                with open(path, 'w', encoding='utf-8') as f:
                    f.write("")
            refresh_combo(name)

        def save_file():
            sel = cb_prompts.get()
            if not sel:
                create_new()
                return
            with open(os.path.join(self.prompt_dir, sel), 'w', encoding='utf-8') as f:
                f.write(text_preview.get("1.0", tk.END).strip())
            self.show_toast(cfg["toast_save_ok"], bg_color="#4CAF50")

        def apply_to_editor():
            prompt = text_preview.get("1.0", tk.END).strip()
            if not prompt or not self.current_filename: return
            current_text = self.text_edit.get("1.0", tk.END).strip()
            new_text = f"{prompt}, {current_text}" if current_text else prompt
            self.text_edit.delete("1.0", tk.END)
            self.text_edit.insert("1.0", new_text)
            self.show_toast(cfg["toast_applied"], bg_color="#4CAF50")
            win.destroy()
            self.prompt_manager_window = None

        win.protocol("WM_DELETE_WINDOW", lambda: (win.destroy(), setattr(self, 'prompt_manager_window', None)))

        f_bot = tk.Frame(win)
        f_bot.pack(fill=tk.X, padx=5, pady=5)
        tk.Button(f_bot, text=cfg["pm_new_file"], command=create_new, bg="#d9edf7").pack(side=tk.LEFT, padx=5)
        tk.Button(f_bot, text=cfg["pm_save_file"], command=save_file).pack(side=tk.LEFT, padx=5)
        tk.Button(f_bot, text=cfg["pm_apply"], command=apply_to_editor, bg="#ccffcc").pack(side=tk.RIGHT, padx=5)

        refresh_combo()
        return "break"

    def open_in_explorer(self):
        selected = self.tree.selection()
        if not selected: return
        idx = self.tree.index(selected[0])
        filepath = os.path.join(self.current_dir, self.display_filenames[idx])
        if os.name == 'nt':
            subprocess.Popen(f'explorer /select,"{os.path.normpath(filepath)}"')
        else:
            if sys.platform == 'darwin':
                subprocess.Popen(['open', self.current_dir])
            else:
                subprocess.Popen(['xdg-open', self.current_dir])

    def open_search_file(self, event=None):
        if hasattr(self, 'filter_search_window') and self.filter_search_window and self.filter_search_window.winfo_exists():
            self.filter_search_window.destroy()
            self.filter_search_window = None
            return "break"

        cfg = self.i18n[self.current_lang]
        self.filter_search_window = win = tk.Toplevel(self.root)
        win.title(cfg["search_file"])
        win.attributes("-topmost", True)
        win.geometry("380x150")
        win.resizable(False, False)

        f_main = tk.Frame(win, padx=15, pady=15)
        f_main.pack(fill=tk.BOTH, expand=True)

        tk.Label(f_main, text=cfg["search_keyword"]).grid(row=0, column=0, sticky="e", pady=5, padx=5)
        self.var_filter_kw = tk.StringVar(value=getattr(self, 'filter_keyword', ''))
        ttk.Entry(f_main, textvariable=self.var_filter_kw, width=25).grid(row=0, column=1, sticky="w", pady=5)

        tk.Label(f_main, text=cfg["search_group"]).grid(row=1, column=0, sticky="e", pady=5, padx=5)

        group_names = [cfg["all_groups"]] + [g["name"] for g in self.app_config.get("group_list", [])]
        self.cb_filter_grp = ttk.Combobox(f_main, values=group_names, state="readonly", width=23)
        current_g = getattr(self, 'filter_group', '')
        self.cb_filter_grp.set(current_g if current_g in group_names else cfg["all_groups"])
        self.cb_filter_grp.grid(row=1, column=1, sticky="w", pady=5)

        btn_f = tk.Frame(f_main)
        btn_f.grid(row=2, column=0, columnspan=2, pady=10)
        tk.Button(btn_f, text=cfg["btn_filter"], command=self.apply_filter, bg="#d9edf7").pack(side=tk.LEFT, padx=5)
        tk.Button(btn_f, text=cfg["btn_clear_filter"], command=self.clear_filter).pack(side=tk.LEFT, padx=5)

        win.protocol("WM_DELETE_WINDOW", lambda: (win.destroy(), setattr(self, 'filter_search_window', None)))

        win.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (win.winfo_width() // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (win.winfo_height() // 2)
        win.geometry(f"+{x}+{y}")
        return "break"

    def apply_filter(self):
        self.filter_keyword = self.var_filter_kw.get()
        self.filter_group = self.cb_filter_grp.get()
        self.var_enable_filter.set(True)
        self.chk_enable_filter.config(state=tk.NORMAL)
        self.refresh_listbox()

    def clear_filter(self):
        self.filter_keyword = ""
        self.filter_group = self.i18n[self.current_lang]["all_groups"]
        if hasattr(self, 'var_filter_kw'): self.var_filter_kw.set("")
        if hasattr(self, 'cb_filter_grp'): self.cb_filter_grp.set(self.filter_group)
        self.var_enable_filter.set(False)
        self.chk_enable_filter.config(state=tk.DISABLED)
        self.refresh_listbox()

    def refresh_listbox(self):
        sel_fs = [self.display_filenames[self.tree.index(i)] for i in self.tree.selection()] if self.display_filenames else []
        cs = self.current_filename
        dl = []
        cn = 0
        cp = 0
        c = self.i18n[self.current_lang]
        tm = self.var_view_mode.get() == "thumb"

        for f in self.all_image_files:
            ht = os.path.exists(os.path.join(self.current_dir, f"{os.path.splitext(f)[0]}.txt"))
            mt = self.metadata.get(f, {})
            st = "completed" if mt.get("edited") else mt.get("status", "none")
            g = mt.get("group", "")
            et = mt.get("time", 0)
            im = ht or st in ("completed", "reviewed")

            if st in ("completed", "reviewed"):
                cp += 1
            else:
                cn += 1

            if not self.var_show_unmarked.get() and not im: continue
            if self.var_hide_completed.get() and st == "completed": continue
            if self.var_hide_reviewed.get() and st == "reviewed": continue

            if self.var_enable_filter.get():
                if self.filter_keyword and self.filter_keyword.lower() not in f.lower(): continue
                ag_texts = [self.i18n[lang].get("all_groups", "All") for lang in self.i18n]
                if self.filter_group and self.filter_group not in ag_texts:
                    igs = [gx.strip() for gx in g.split('+') if gx.strip()]
                    if self.filter_group not in igs: continue

            ts = datetime.fromtimestamp(et).strftime('%m-%d %H:%M') if et > 0 else "-"
            dl.append((f, g, ts, et, st))

        if self.var_show_stats.get():
            self.lbl_stats.config(text=f"{c['stat_unreviewed'].format(cn)} | {c['stat_processed'].format(cp)}")
        else:
            self.lbl_stats.config(text="")

        if self.sort_col == "file": dl.sort(key=lambda x: x[0].lower(), reverse=self.sort_reverse)
        elif self.sort_col == "time": dl.sort(key=lambda x: x[3], reverse=self.sort_reverse)
        elif self.sort_col == "group": dl.sort(key=lambda x: x[1].lower(), reverse=self.sort_reverse)
        elif self.sort_col == "idx":
            if self.sort_reverse:
                dl.reverse()

        self.tree.delete(*self.tree.get_children())
        self.display_filenames.clear()
        self.loaded_thumb_items.clear()
        
        self.last_visible_items = []
        self.last_thumb_update = 0

        if tm:
            self.style.configure("Main.Treeview", rowheight=110)
            self.tree.configure(show="tree", displaycolumns=[]) 
        else:
            self.style.configure("Main.Treeview", rowheight=24)
            self.tree.configure(show="headings", displaycolumns=("idx", "file", "group", "time")) 

        for di, d in enumerate(dl, 1):
            f, g, ts, _, st = d
            tg = "completed" if st == "completed" else "reviewed" if st == "reviewed" else "normal"
            it = f" [{di}] {f}" if tm else ""

            iid = self.tree.insert("", tk.END, text=it, values=(str(di), f, g, ts), tags=(tg,))
            self.display_filenames.append(f)

            if f in sel_fs:
                self.tree.selection_add(iid)

            if tm and f in self.thumb_cache and self.thumb_cache[f]:
                self.tree.item(iid, image=self.thumb_cache[f])

        if cs in self.display_filenames:
            i = self.display_filenames.index(cs)
            self.center_tree_item(i, self.tree.get_children()[i])

    def auto_refresh_loop(self):
        if self.var_auto_refresh.get() and self.current_dir:
            try:
                self.load_metadata()
                nf = sorted([f for f in os.listdir(self.current_dir) if f.lower().endswith(self.supported_formats)])
                if nf != self.all_image_files:
                    self.all_image_files = nf
                    for f in self.all_image_files:
                        if f not in self.missing_thumbs and not os.path.exists(os.path.join(self.thumb_dir, f"{f}.thumb.jpg")):
                            self.missing_thumbs.append(f)
                    self.refresh_listbox()
            except:
                pass
        self.root.after(300000, self.auto_refresh_loop)

    def ask_directory(self, event=None):
        path = filedialog.askdirectory()
        if path:
            self.load_directory(path)

    def load_directory(self, path):
        self.current_dir = path
        self.app_config["last_dir"] = path
        self.save_app_config()
        self.load_metadata()

        self.thumb_dir = os.path.join(self.current_dir, ".thumbnails")
        if not os.path.exists(self.thumb_dir):
            try:
                os.makedirs(self.thumb_dir)
            except:
                pass

        self.thumb_cache.clear()
        self.is_manual_generating = False
        self.all_image_files = sorted([f for f in os.listdir(path) if f.lower().endswith(self.supported_formats)])

        self.missing_thumbs = []
        for f in self.all_image_files:
            if not os.path.exists(os.path.join(self.thumb_dir, f"{f}.thumb.jpg")):
                self.missing_thumbs.append(f)

        self.refresh_listbox()

    def sort_tree(self, col):
        if self.sort_col == col:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_col = col
            self.sort_reverse = False
        self.refresh_listbox()

    def manual_mark_file(self, status):
        selected = self.tree.selection()
        if not selected: return
        last_file = ""
        for item in selected:
            idx = self.tree.index(item)
            last_file = self.display_filenames[idx]
            self.update_file_meta(last_file, status=status)

        if status in ("completed", "reviewed") and last_file:
            self.advance_to_next(last_file)
        else:
            self.refresh_listbox()

    def manual_mark_file_hotkey(self, status):
        self.manual_mark_file(status)
        return "break"

    def advance_to_next(self, current_filename):
        idx = self.display_filenames.index(current_filename) if current_filename in self.display_filenames else -1
        next_file = self.display_filenames[idx + 1] if idx != -1 and (idx + 1) < len(self.display_filenames) else None
        self.refresh_listbox()
        if next_file and next_file in self.display_filenames:
            new_idx = self.display_filenames.index(next_file)
            self.center_tree_item(new_idx, self.tree.get_children()[new_idx])
            self.on_file_select()

    def on_file_select(self, e=None):
        selected = self.tree.selection()
        if not selected: return
        idx = self.tree.index(selected[0])
        val = self.display_filenames[idx]
        self.current_filename = val
        self.lbl_filename.config(text=f"[{idx+1}] {val}")

        try:
            img = Image.open(os.path.join(self.current_dir, val))
            try:
                img = ImageOps.exif_transpose(img)
            except:
                pass
            img.thumbnail((700, 700))
            photo = ImageTk.PhotoImage(img)
            self.lbl_image.config(image=photo, text="")
            self.lbl_image.image = photo
        except:
            self.lbl_image.config(image='', text=self.i18n[self.current_lang]["img_err"])

        self.text_original.config(state=tk.NORMAL)
        self.text_original.delete("1.0", tk.END)
        self.text_edit.delete("1.0", tk.END)
        self.text_translated.delete("1.0", tk.END)

        txt_path = os.path.join(self.current_dir, f"{os.path.splitext(val)[0]}.txt")
        if os.path.exists(txt_path):
            with open(txt_path, 'r', encoding='utf-8') as f:
                content = f.read()
                self.text_original.insert("1.0", content)
                self.text_edit.insert("1.0", content)
        self.text_original.config(state=tk.DISABLED)

    def save_tags(self, event=None):
        selected = self.tree.selection()
        if not selected:
            self.show_toast(self.i18n[self.current_lang]["toast_save_fail"], bg_color="#f44336")
            return "break"
            
        idx = self.tree.index(selected[0])
        filename = self.display_filenames[idx]
        txt_path = os.path.join(self.current_dir, f"{os.path.splitext(filename)[0]}.txt")

        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(self.text_edit.get("1.0", tk.END).strip())

        self.update_file_meta(filename, status="completed")
        self.show_toast(self.i18n[self.current_lang]["toast_save_ok"], bg_color="#4CAF50")
        self.advance_to_next(filename)
        return "break"

    def translate_text(self, is_reverse=False):
        tgt = self.text_edit if is_reverse else self.text_translated
        src_text = self.text_translated.get("1.0", tk.END).strip() if is_reverse else self.text_edit.get("1.0", tk.END).strip()
        if not src_text: return

        sl = self.lang_map[self.combo_tgt.get() if is_reverse else self.combo_src.get()]
        tl = self.lang_map[self.combo_src.get() if is_reverse else self.combo_tgt.get()]
        if sl == 'auto' and is_reverse:
            tl = 'en'

        engine = self.combo_engine.get()
        try:
            if "Google" in engine:
                res = GoogleTranslator(source=sl, target=tl).translate(src_text)
            else:
                res = f"[{engine}] Translation requires API key configuration."
            tgt.delete("1.0", tk.END)
            tgt.insert("1.0", res)
        except Exception as e:
            tgt.insert("1.0", f"Error: {e}")

    def translate_text_hotkey(self, is_reverse=False):
        self.translate_text(is_reverse)
        return "break"

    def overwrite_edit_area(self):
        self.text_edit.delete("1.0", tk.END)
        self.text_edit.insert("1.0", self.text_translated.get("1.0", tk.END).strip())

    def swap_languages(self):
        src, tgt = self.combo_src.get(), self.combo_tgt.get()
        if src != "Auto":
            self.combo_src.set(tgt)
            self.combo_tgt.set(src)

    def center_tree_item(self, idx, item_id):
        self.tree.selection_set(item_id)
        self.tree.focus(item_id)
        self.tree.update_idletasks()
        if len(self.display_filenames) > 0:
            yv = self.tree.yview()
            self.tree.yview_moveto(max(0.0, min((idx / len(self.display_filenames)) - ((yv[1] - yv[0]) / 2), 1.0)))

    def change_font_size(self, delta=0, reset=False):
        self.text_font_size = 11 if reset else max(7, min(32, self.text_font_size + delta))
        self.text_original.config(state=tk.NORMAL)
        self.text_original.configure(font=("TkTextFont", self.text_font_size))
        self.text_original.config(state=tk.DISABLED)
        self.text_edit.configure(font=("TkTextFont", self.text_font_size))
        self.text_translated.configure(font=("TkTextFont", self.text_font_size))
        return "break"

    def show_toast(self, message, bg_color="#333333"):
        toast = tk.Label(self.root, text=message, bg=bg_color, fg="white", font=("TkDefaultFont", 12, "bold"), padx=20, pady=10)
        toast.place(relx=0.5, rely=0.85, anchor="center")
        self.root.after(2000, toast.destroy)

    def sync_list_to_image(self, event=None):
        if not self.current_filename: return
        if not self.is_list_visible:
            self.toggle_list_panel()
        if self.current_filename in self.display_filenames:
            idx = self.display_filenames.index(self.current_filename)
            item_id = self.tree.get_children()[idx]
            self.center_tree_item(idx, item_id)
            self.show_toast(f"{self.i18n[self.current_lang]['toast_located']}{self.current_filename}", bg_color="#0984e3")

    def jump_last_edited(self, event=None):
        if not self.metadata:
            self.show_toast(self.i18n[self.current_lang]["toast_no_history"])
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

    def restore_original_text(self, event=None):
        if not self.current_filename: return "break"
        orig_text = self.text_original.get("1.0", tk.END).strip()
        self.text_edit.delete("1.0", tk.END)
        self.text_edit.insert("1.0", orig_text)
        self.show_toast(self.i18n[self.current_lang]["toast_restore_orig"])
        return "break"

    def show_hotkeys(self, event=None):
        if hasattr(self, 'search_replace_window') and self.search_replace_window and self.search_replace_window.winfo_exists():
            self.search_replace_window.destroy()
            self.search_replace_window = None

        if hasattr(self, 'hk_window') and self.hk_window and self.hk_window.winfo_exists():
            self.hk_window.destroy()
            self.hk_window = None
            return "break"

        self.hk_window = win = tk.Toplevel(self.root)
        win.title(self.i18n[self.current_lang]["hotkey"])
        win.attributes("-topmost", True)

        lbl = tk.Label(win, text=self.i18n[self.current_lang]["hotkey_text"], font=("TkDefaultFont", 11), justify=tk.LEFT, padx=30, pady=20)
        lbl.pack()

        win.bind("<F1>", self.show_hotkeys)
        win.bind("<Escape>", self.show_hotkeys)
        win.protocol("WM_DELETE_WINDOW", lambda: (win.destroy(), setattr(self, 'hk_window', None)))
        win.update_idletasks()

        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (win.winfo_width() // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (win.winfo_height() // 2)
        win.geometry(f"+{x}+{y}")
        return "break"

    def open_search_replace(self, event=None):
        if hasattr(self, 'hk_window') and self.hk_window and self.hk_window.winfo_exists():
            self.hk_window.destroy()
            self.hk_window = None

        if hasattr(self, 'sr_window') and self.sr_window and self.sr_window.winfo_exists():
            self.sr_window.destroy()
            self.sr_window = None
            return "break"

        cfg = self.i18n[self.current_lang]
        self.sr_window = win = tk.Toplevel(self.root)
        win.title(cfg["search_text"])
        win.attributes("-topmost", True)
        win.geometry("380x180")
        win.resizable(False, False)

        fm = tk.Frame(win, padx=15, pady=15)
        fm.pack(fill=tk.BOTH, expand=True)

        tk.Label(fm, text=cfg["find_lbl"]).grid(row=0, column=0, sticky="e", pady=4)
        self.var_find = tk.StringVar()
        ttk.Entry(fm, textvariable=self.var_find, width=28).grid(row=0, column=1, columnspan=3, sticky="w", pady=4)

        tk.Label(fm, text=cfg["replace_lbl"]).grid(row=1, column=0, sticky="e", pady=4)
        self.var_rep = tk.StringVar()
        ttk.Entry(fm, textvariable=self.var_rep, width=28).grid(row=1, column=1, columnspan=3, sticky="w", pady=4)

        tk.Label(fm, text=cfg["target_lbl"]).grid(row=2, column=0, sticky="e", pady=4)
        self.var_tgt = tk.StringVar(value=cfg["lbl_edit"])
        cb_target = ttk.Combobox(fm, textvariable=self.var_tgt, values=[cfg["lbl_edit"], cfg["lbl_trans"]], state="readonly", width=18)
        cb_target.grid(row=2, column=1, columnspan=3, sticky="w", pady=4)

        bf = tk.Frame(fm)
        bf.grid(row=3, column=0, columnspan=4, pady=10)
        tk.Button(bf, text=cfg["btn_find_prev"], command=self.fn_nxt).pack(side=tk.LEFT, padx=3)
        tk.Button(bf, text=cfg["btn_replace"], command=self.rp_txt).pack(side=tk.LEFT, padx=3)
        tk.Button(bf, text=cfg["btn_replace_all"], command=self.rp_all).pack(side=tk.LEFT, padx=3)
        tk.Button(bf, text=cfg["btn_highlight"], command=self.hl_all).pack(side=tk.LEFT, padx=3)

        fo = self.root.focus_get()
        if fo in (self.text_edit, self.text_translated):
            cb_target.set(cfg["lbl_trans"] if fo == self.text_translated else cfg["lbl_edit"])
            try:
                self.var_find.set(fo.selection_get())
            except:
                pass

        def oc():
            self.text_edit.tag_remove("sm", "1.0", tk.END)
            self.text_translated.tag_remove("sm", "1.0", tk.END)
            win.destroy()
            self.sr_window = None

        win.protocol("WM_DELETE_WINDOW", oc)
        win.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width()//2) - (w.winfo_width()//2)
        y = self.root.winfo_y() + (self.root.winfo_height()//2) - (w.winfo_height()//2)
        win.geometry(f"+{x}+{y}")
        return "break"

    def get_stgt(self):
        if self.var_tgt.get() == self.i18n[self.current_lang]["lbl_trans"]:
            return self.text_translated
        return self.text_edit

    def fn_nxt(self):
        target = self.get_stgt()
        target.tag_remove("sm", "1.0", tk.END)
        ss = self.var_find.get()
        if not ss: return

        start_pos = target.index(tk.INSERT)
        pos = target.search(ss, f"{start_pos}+1c", stopindex=tk.END)
        if not pos:
            pos = target.search(ss, "1.0", stopindex=tk.END)

        if pos:
            end_pos = f"{pos}+{len(ss)}c"
            target.mark_set(tk.INSERT, end_pos)
            target.tag_add("sm", pos, end_pos)
            target.see(pos)
        else:
            self.show_toast(self.i18n[self.current_lang]["toast_not_found"], bg_color="#f44336")

    def rp_txt(self):
        target = self.get_stgt()
        ss = self.var_find.get()
        rs = self.var_rep.get()
        if not ss: return

        ranges = target.tag_ranges("sm")
        if ranges:
            start_idx, end_idx = ranges[0], ranges[1]
            if target.get(start_idx, end_idx) == ss:
                target.delete(start_idx, end_idx)
                target.insert(start_idx, rs)
                target.mark_set(tk.INSERT, f"{start_idx}+{len(rs)}c")
        self.fn_nxt()

    def rp_all(self):
        target = self.get_stgt()
        ss = self.var_find.get()
        rs = self.var_rep.get()
        if not ss: return

        target.tag_remove("sm", "1.0", tk.END)
        idx = "1.0"
        count = 0
        while True:
            idx = target.search(ss, idx, stopindex=tk.END)
            if not idx: break
            end_idx = f"{idx}+{len(ss)}c"
            target.delete(idx, end_idx)
            target.insert(idx, rs)
            idx = f"{idx}+{len(rs)}c"
            count += 1

        self.show_toast(self.i18n[self.current_lang]["toast_replaced"].format(count))

    def hl_all(self):
        target = self.get_stgt()
        target.tag_remove("sm", "1.0", tk.END)
        ss = self.var_find.get()
        if not ss: return

        idx = "1.0"
        count = 0
        while True:
            idx = target.search(ss, idx, stopindex=tk.END)
            if not idx: break
            end_idx = f"{idx}+{len(ss)}c"
            target.tag_add("sm", idx, end_idx)
            idx = end_idx
            count += 1

        self.show_toast(self.i18n[self.current_lang]["toast_highlighted"].format(count))

    def bind_shortcuts(self):
        tb = {
            "<Delete>": self.delete_files, 
            "<F2>": self.rename_file, 
            "<Control-m>": self.move_files, 
            "<Control-M>": self.move_files
        }
        for k, v in tb.items():
            self.tree.bind(k, v)

        gb = {
            "<Control-s>": self.save_tags, "<Control-S>": self.save_tags,
            "<Control-p>": self.open_prompt_manager, "<Control-P>": self.open_prompt_manager,
            "<Alt-o>": lambda e: (self.ask_directory(), "break"), "<Alt-O>": lambda e: (self.ask_directory(), "break"),
            "<Control-Alt-c>": self.copy_tags, "<Control-Alt-C>": self.copy_tags,
            "<Control-Alt-v>": self.paste_tags, "<Control-Alt-V>": self.paste_tags,
            "<Control-t>": lambda e: self.translate_text_hotkey(False), "<Control-T>": lambda e: self.translate_text_hotkey(False),
            "<Alt-t>": lambda e: self.translate_text_hotkey(True), "<Alt-T>": lambda e: self.translate_text_hotkey(True),
            "<Alt-m>": lambda e: self.manual_mark_file_hotkey("completed"), "<Alt-M>": lambda e: self.manual_mark_file_hotkey("completed"),
            "<Alt-n>": lambda e: self.manual_mark_file_hotkey("reviewed"), "<Alt-N>": lambda e: self.manual_mark_file_hotkey("reviewed"),
            "<Alt-u>": lambda e: self.manual_mark_file_hotkey("none"), "<Alt-U>": lambda e: self.manual_mark_file_hotkey("none"),
            "<Control-h>": self.toggle_list_panel, "<Control-H>": self.toggle_list_panel,
            "<Control-Alt-f>": self.open_search_file, "<Control-Alt-F>": self.open_search_file,
            "<Control-f>": self.open_search_replace, "<Control-F>": self.open_search_replace,
            "<Alt-l>": self.jump_last_edited, "<Alt-L>": self.jump_last_edited,
            "<Alt-Up>": self.nav_prev, "<Alt-Down>": self.nav_next,
            "<Control-Alt-l>": self.restore_original_text, "<Control-Alt-L>": self.restore_original_text,
            "<Control-Alt-plus>": lambda e: self.change_font_size(1), "<Control-Alt-KP_Add>": lambda e: self.change_font_size(1),
            "<Control-Alt-equal>": lambda e: self.change_font_size(1), "<Control-Alt-minus>": lambda e: self.change_font_size(-1),
            "<Control-Alt-KP_Subtract>": lambda e: self.change_font_size(-1),
            "<Control-Alt-asterisk>": lambda e: self.change_font_size(reset=True), "<Control-Alt-KP_Multiply>": lambda e: self.change_font_size(reset=True),
            "<F1>": self.show_hotkeys
        }
        for k, v in gb.items():
            self.root.bind(k, v)

if __name__ == "__main__":
    root = tk.Tk()
    app = DatasetTaggerApp(root)
    root.mainloop()