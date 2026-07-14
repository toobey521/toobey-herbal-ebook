#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Toobey本草食蔬 v1.0
蔬菜性味寒热属性与药用价值电子书
"""

import tkinter as tk
from tkinter import ttk, font
import json
import sys
import os

# ── 图片支持 ──
try:
    from PIL import Image, ImageTk
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

# ── 从JSON加载蔬菜食材数据库 ──
def _load_data():
    """加载蔬菜数据，支持PyInstaller打包后的路径"""
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(base, 'veggies_data.json')
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

VEGGIES = _load_data()

# ── 按寒热属性分类 ──
CATEGORIES = {
    "寒性": sorted([v for v in VEGGIES if v["nature"] == "寒"], key=lambda x: x["name"]),
    "凉性": sorted([v for v in VEGGIES if v["nature"] == "凉"], key=lambda x: x["name"]),
    "平性": sorted([v for v in VEGGIES if v["nature"] == "平"], key=lambda x: x["name"]),
    "温性": sorted([v for v in VEGGIES if v["nature"] == "温"], key=lambda x: x["name"]),
    "热性": sorted([v for v in VEGGIES if v["nature"] == "热"], key=lambda x: x["name"]),
}

# 属性颜色
NATURE_COLORS = {
    "寒": "#3b82f6",  # 蓝
    "凉": "#60a5fa",  # 浅蓝
    "平": "#22c55e",  # 绿
    "温": "#f59e0b",  # 橙
    "热": "#ef4444",  # 红
}

NATURE_BG = {
    "寒": "#eff6ff",
    "凉": "#f0f9ff",
    "平": "#f0fdf4",
    "温": "#fffbeb",
    "热": "#fef2f2",
}


class VeggieEbook(tk.Tk):
    """Toobey本草食蔬 - 蔬菜性味寒热属性电子书"""

    def __init__(self):
        super().__init__()
        self.title("Toobey本草食蔬 v1.0")
        self.geometry("900x680")
        self.minsize(750, 550)

        # ── 窗口图标 ──
        try:
            self.iconbitmap(default=os.path.join(self.resource_path(), "icon.ico"))
        except Exception:
            pass

        # ── 配色方案 ──
        self.bg = "#fafaf9"
        self.sidebar_bg = "#1e293b"
        self.accent = "#10b981"
        self.card_bg = "#ffffff"
        self.text_color = "#1e293b"
        self.config(bg=self.bg)

        # ── 字体 ──
        self.title_font = font.nametofont("TkHeadingFont").copy()
        self.title_font.configure(size=16, weight="bold")

        self.head_font = font.nametofont("TkHeadingFont").copy()
        self.head_font.configure(size=13, weight="bold")

        self.body_font = font.nametofont("TkDefaultFont").copy()
        self.body_font.configure(size=11)

        self.small_font = font.nametofont("TkDefaultFont").copy()
        self.small_font.configure(size=9)

        # ── UI构建 ──
        self._build_ui()

        # 默认选中第一个分类
        self.cat_listbox.selection_set(0)
        self._on_category_select(None)

    def resource_path(self):
        if getattr(sys, "frozen", False):
            return sys._MEIPASS
        return os.path.dirname(os.path.abspath(__file__))

    def _build_ui(self):
        # ── 主布局：左侧分类 + 右侧内容 ──
        self.grid_columnconfigure(0, weight=0, minsize=160)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ═══ 左侧：分类导航 ═══
        left_frame = tk.Frame(self, bg=self.sidebar_bg)
        left_frame.grid(row=0, column=0, sticky="nsew")

        # 标题
        logo = tk.Label(left_frame, text="🥬 本草食蔬",
                        font=("Microsoft YaHei", 14, "bold"),
                        bg=self.sidebar_bg, fg="#f8fafc", pady=15)
        logo.pack(fill="x")

        tk.Label(left_frame, text="蔬菜性味寒热分类",
                 font=self.small_font,
                 bg=self.sidebar_bg, fg="#94a3b8").pack(fill="x", pady=(0, 10))

        # 分类列表
        self.cat_listbox = tk.Listbox(left_frame,
                                      bg="#334155", fg="#f1f5f9",
                                      selectbackground=self.accent,
                                      selectforeground="white",
                                      relief="flat", borderwidth=0,
                                      highlightthickness=0,
                                      font=("Microsoft YaHei", 11),
                                      activestyle="none")
        categories_display = [
            "❄️ 寒性  (%d)" % len(CATEGORIES["寒性"]),
            "🌊 凉性  (%d)" % len(CATEGORIES["凉性"]),
            "🌿 平性  (%d)" % len(CATEGORIES["平性"]),
            "🔥 温性  (%d)" % len(CATEGORIES["温性"]),
            "⚡ 热性  (%d)" % len(CATEGORIES["热性"]),
        ]
        for c in categories_display:
            self.cat_listbox.insert("end", c)
        self.cat_listbox.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        self.cat_listbox.bind("<<ListboxSelect>>", self._on_category_select)

        # 底部信息
        tk.Label(left_frame, text=f"共收录 {len(VEGGIES)} 种蔬菜",
                 font=self.small_font,
                 bg=self.sidebar_bg, fg="#64748b", pady=10).pack(side="bottom", fill="x")

        # ═══ 右侧：内容区域 ═══
        right_frame = tk.Frame(self, bg=self.bg)
        right_frame.grid(row=0, column=1, sticky="nsew")
        right_frame.grid_columnconfigure(0, weight=1)
        right_frame.grid_rowconfigure(2, weight=1)

        # 搜索框
        search_frame = tk.Frame(right_frame, bg=self.bg, pady=10)
        search_frame.grid(row=0, column=0, sticky="ew", padx=20)
        search_frame.grid_columnconfigure(1, weight=1)

        tk.Label(search_frame, text="🔍 搜索蔬菜：",
                 font=self.body_font, bg=self.bg,
                 fg=self.text_color).grid(row=0, column=0, padx=(0, 8))

        self.search_var = tk.StringVar()
        self.search_var.trace("w", self._on_search)
        search_entry = tk.Entry(search_frame, textvariable=self.search_var,
                                font=self.body_font,
                                relief="solid", borderwidth=1,
                                highlightthickness=1,
                                highlightcolor=self.accent,
                                bg="white", fg=self.text_color)
        search_entry.grid(row=0, column=1, sticky="ew", padx=(0, 10), ipady=3)

        search_btn = tk.Button(search_frame, text="搜索",
                               command=self._on_search_click,
                               bg=self.accent, fg="white",
                               font=self.body_font,
                               relief="flat", padx=15, cursor="hand2")
        search_btn.grid(row=0, column=2)

        # 当前分类标题
        self.cat_title = tk.Label(right_frame, text="",
                                  font=self.title_font,
                                  bg=self.bg, fg=self.text_color,
                                  anchor="w", pady=5)
        self.cat_title.grid(row=1, column=0, sticky="ew", padx=20)

        # 蔬菜列表 + 详情 (左右分栏)
        content_frame = tk.Frame(right_frame, bg=self.bg)
        content_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0, 10))
        content_frame.grid_columnconfigure(0, weight=0, minsize=200)
        content_frame.grid_columnconfigure(1, weight=3)
        content_frame.grid_rowconfigure(0, weight=1)

        # 蔬菜名列表
        list_frame = tk.Frame(content_frame, bg=self.card_bg,
                              relief="solid", borderwidth=1,
                              highlightbackground="#e2e8f0", highlightthickness=1)
        list_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        list_frame.grid_rowconfigure(0, weight=1)

        self.veggie_list = tk.Listbox(list_frame,
                                      bg="white", fg=self.text_color,
                                      selectbackground="#d1fae5",
                                      selectforeground=self.text_color,
                                      relief="flat", borderwidth=0,
                                      highlightthickness=0,
                                      font=("Microsoft YaHei", 10),
                                      activestyle="none")
        self.veggie_list.pack(fill="both", expand=True, padx=5, pady=5)
        self.veggie_list.bind("<<ListboxSelect>>", self._on_veggie_select)

        # 详情面板（可滚动）
        detail_frame = tk.Frame(content_frame, bg=self.card_bg,
                                relief="solid", borderwidth=1,
                                highlightbackground="#e2e8f0", highlightthickness=1)
        detail_frame.grid(row=0, column=1, sticky="nsew")
        detail_frame.grid_rowconfigure(0, weight=1)
        detail_frame.grid_columnconfigure(0, weight=1)

        self.detail_canvas = tk.Canvas(detail_frame, bg=self.card_bg,
                                       highlightthickness=0,
                                       borderwidth=0)
        self.detail_scroll = tk.Scrollbar(detail_frame, orient="vertical",
                                          command=self.detail_canvas.yview)
        self.detail_canvas.configure(yscrollcommand=self.detail_scroll.set)
        self.detail_scroll.pack(side="right", fill="y")
        self.detail_canvas.pack(side="left", fill="both", expand=True)

        self.detail_inner = tk.Frame(self.detail_canvas, bg=self.card_bg,
                                     padx=20, pady=15)
        self.detail_inner.bind("<Configure>",
                               lambda e: self.detail_canvas.configure(
                                   scrollregion=self.detail_canvas.bbox("all")))
        self.detail_canvas.create_window((0, 0), window=self.detail_inner,
                                         anchor="nw", width=self.detail_canvas.winfo_width())

        def _configure_canvas(event):
            self.detail_canvas.itemconfig(
                self.detail_canvas.find_withtag("all")[0],
                width=event.width)
        self.detail_canvas.bind("<Configure>", _configure_canvas)

        # 绑定鼠标滚轮
        def _on_mousewheel(event):
            self.detail_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        self.detail_canvas.bind_all("<MouseWheel>", _on_mousewheel, add="+")

        # 初始占位
        self._show_placeholder()

    def _on_category_select(self, event):
        sel = self.cat_listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        cat_names = ["寒性", "凉性", "平性", "温性", "热性"]
        self.current_category = cat_names[idx]
        self.current_veggies = CATEGORIES[self.current_category]

        icons = {"寒性": "❄️", "凉性": "🌊", "平性": "🌿", "温性": "🔥", "热性": "⚡"}
        self.cat_title.config(text=f"{icons[self.current_category]} {self.current_category}蔬菜  ({len(self.current_veggies)}种)")

        # 清空搜索
        self.search_var.set("")
        self._populate_veggie_list(self.current_veggies)

        # 选中第一个蔬菜
        if self.current_veggies:
            self.veggie_list.selection_clear(0, "end")
            self.veggie_list.selection_set(0)
            self.veggie_list.see(0)
            self._show_veggie_detail(self.current_veggies[0])
        else:
            self._show_placeholder()

    def _populate_veggie_list(self, veggies):
        self.veggie_list.delete(0, "end")
        emojis = {"寒": "❄️", "凉": "🌊", "平": "🌿", "温": "🔥", "热": "⚡"}
        for v in veggies:
            e = emojis.get(v["nature"], "🥬")
            self.veggie_list.insert("end", f"  {e} {v['name']}")

    def _on_veggie_select(self, event):
        sel = self.veggie_list.curselection()
        if not sel or not hasattr(self, "current_veggies"):
            return
        idx = sel[0]
        if idx < len(self.current_veggies):
            self._show_veggie_detail(self.current_veggies[idx])

    def _on_search(self, *args):
        pass  # 打字时不做搜索

    def _on_search_click(self):
        query = self.search_var.get().strip()
        if not query:
            self._on_category_select(None)
            return

        results = [v for v in VEGGIES if query.lower() in v["name"].lower()
                   or query.lower() in v["effect"].lower()
                   or query.lower() in v["indications"].lower()]

        self.current_veggies = results
        self.cat_title.config(text=f"🔍 搜索结果：'{query}' ({len(results)}种)")
        self._populate_veggie_list(results)

        if results:
            self.veggie_list.selection_clear(0, "end")
            self.veggie_list.selection_set(0)
            self._show_veggie_detail(results[0])
        else:
            self._show_placeholder("未找到匹配的蔬菜，请换个关键词试试")

    def _show_placeholder(self, msg="请从左侧选择一个蔬菜分类"):
        for w in self.detail_inner.winfo_children():
            w.destroy()

        tk.Label(self.detail_inner,
                 text="🥗",
                 font=("Microsoft YaHei", 60),
                 bg=self.card_bg, fg="#cbd5e1").pack(pady=(60, 10))
        tk.Label(self.detail_inner,
                 text="Toobey 本草食蔬",
                 font=("Microsoft YaHei", 18, "bold"),
                 bg=self.card_bg, fg=self.text_color).pack()
        tk.Label(self.detail_inner,
                 text=msg,
                 font=self.body_font,
                 bg=self.card_bg, fg="#64748b").pack(pady=10)
        tk.Label(self.detail_inner,
                 text=f"收录 {len(VEGGIES)} 种常见蔬菜的性味归经、寒热属性和药用价值",
                 font=self.small_font,
                 bg=self.card_bg, fg="#94a3b8").pack()

    def _show_veggie_detail(self, veg):
        for w in self.detail_inner.winfo_children():
            w.destroy()

        nc = NATURE_COLORS.get(veg["nature"], "#6b7280")
        nb = NATURE_BG.get(veg["nature"], "#f8fafc")

        # ── 蔬菜名 + 性味标签 ──
        header = tk.Frame(self.detail_inner, bg=self.card_bg)
        header.pack(fill="x", pady=(0, 15))

        tk.Label(header, text=veg["name"],
                 font=("Microsoft YaHei", 22, "bold"),
                 bg=self.card_bg, fg=self.text_color).pack(side="left")

        nature_label = tk.Label(header,
                                text=f"  {veg['nature']}性  ",
                                font=("Microsoft YaHei", 13, "bold"),
                                bg=nc, fg="white",
                                padx=12, pady=3)
        nature_label.pack(side="left", padx=(12, 5))

        tk.Label(header, text=f"味{veg['taste']}",
                 font=("Microsoft YaHei", 13),
                 bg=self.card_bg, fg=nc).pack(side="left")

        # ── 蔬菜图片 ──
        if HAS_PIL and veg.get('image'):
            try:
                img_name = veg['image']
                if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
                    img_path = os.path.join(sys._MEIPASS, 'images', img_name)
                else:
                    img_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'images', img_name)
                
                if os.path.isfile(img_path):
                    pil_img = Image.open(img_path)
                    # 等比例缩放：宽280，高自适应
                    max_w, max_h = 280, 200
                    w, h = pil_img.size
                    ratio = min(max_w / w, max_h / h, 1.0)
                    new_w, new_h = int(w * ratio), int(h * ratio)
                    pil_img = pil_img.resize((new_w, new_h), Image.LANCZOS)
                    
                    photo = ImageTk.PhotoImage(pil_img)
                    
                    img_frame = tk.Frame(self.detail_inner, bg=self.card_bg)
                    img_frame.pack(fill="x", pady=(0, 10))
                    
                    img_label = tk.Label(img_frame, image=photo, bg=self.card_bg)
                    img_label.image = photo  # 保持引用
                    img_label.pack()
            except Exception:
                pass  # 图片加载失败不显示即可

        # ── 基本信息卡片 ──
        info_card = tk.Frame(self.detail_inner, bg=nb,
                             padx=15, pady=12,
                             highlightthickness=1,
                             highlightcolor=nc,
                             highlightbackground=nc)
        info_card.pack(fill="x", pady=(0, 12))

        info_items = [
            ("归经", veg["meridian"]),
            ("功效", veg["effect"]),
            ("主治", veg["indications"]),
            ("禁忌", veg["contra"]),
            ("建议食法", veg["usage"]),
        ]
        for label, value in info_items:
            row = tk.Frame(info_card, bg=nb)
            row.pack(fill="x", pady=2)
            tk.Label(row, text=f"▸ {label}：",
                     font=("Microsoft YaHei", 10, "bold"),
                     bg=nb, fg=self.text_color,
                     width=8, anchor="e").pack(side="left")
            tk.Label(row, text=value,
                     font=("Microsoft YaHei", 10),
                     bg=nb, fg="#334155",
                     wraplength=400, anchor="w",
                     justify="left").pack(side="left", padx=(5, 0))

        # ── 营养成分 ──
        tk.Label(self.detail_inner, text="📊 营养成分",
                 font=("Microsoft YaHei", 13, "bold"),
                 bg=self.card_bg, fg=self.text_color,
                 anchor="w").pack(fill="x", pady=(5, 3))

        nutr_bg = "#f8fafc"
        nutr_card = tk.Frame(self.detail_inner, bg=nutr_bg,
                             padx=15, pady=10,
                             highlightthickness=1,
                             highlightbackground="#e2e8f0")
        nutr_card.pack(fill="x", pady=(0, 12))
        tk.Label(nutr_card, text=veg["nutrition"],
                 font=("Microsoft YaHei", 10),
                 bg=nutr_bg, fg="#334155",
                 wraplength=420, anchor="w",
                 justify="left").pack()

        # ── 详细介绍 ──
        tk.Label(self.detail_inner, text="📖 详细介绍",
                 font=("Microsoft YaHei", 13, "bold"),
                 bg=self.card_bg, fg=self.text_color,
                 anchor="w").pack(fill="x", pady=(5, 3))

        tk.Label(self.detail_inner, text=veg["desc"],
                 font=("Microsoft YaHei", 10),
                 bg=self.card_bg, fg="#334155",
                 wraplength=420, anchor="w",
                 justify="left").pack(fill="x")

        # ── 底部留白 ──
        tk.Label(self.detail_inner, text="",
                 bg=self.card_bg).pack(pady=10)


if __name__ == "__main__":
    app = VeggieEbook()
    app.mainloop()
