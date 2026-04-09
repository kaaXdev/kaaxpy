"""
kaaXpy v2.0 — Python Code Editor
Requires: pip install customtkinter
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import threading
import keyword
import re
import os
import json

try:
    import customtkinter as ctk
except ImportError:
    import subprocess as sp
    sp.check_call(["pip", "install", "customtkinter"])
    import customtkinter as ctk

# ─────────────────────────────────────────────
#  THEME DEFINITIONS
# ─────────────────────────────────────────────
THEMES = {
    "Matrix": {
        "bg":         "#0d0d0d",
        "bg2":        "#141414",
        "bg3":        "#1a1a1a",
        "fg":         "#00ff7f",
        "fg2":        "#00cc66",
        "accent":     "#00ff7f",
        "cursor":     "#00ff7f",
        "sel_bg":     "#003322",
        "term_bg":    "#080808",
        "term_fg":    "#00ff7f",
        "kw":         "#ff9d00",
        "string":     "#ce9178",
        "comment":    "#5a8a5a",
        "builtin":    "#4ec9b0",
        "number":     "#b5cea8",
        "ln_fg":      "#336644",
    },
    "Nord": {
        "bg":         "#2e3440",
        "bg2":        "#3b4252",
        "bg3":        "#434c5e",
        "fg":         "#d8dee9",
        "fg2":        "#e5e9f0",
        "accent":     "#88c0d0",
        "cursor":     "#88c0d0",
        "sel_bg":     "#4c566a",
        "term_bg":    "#242933",
        "term_fg":    "#a3be8c",
        "kw":         "#81a1c1",
        "string":     "#a3be8c",
        "comment":    "#616e88",
        "builtin":    "#88c0d0",
        "number":     "#b48ead",
        "ln_fg":      "#4c566a",
    },
    "Dracula": {
        "bg":         "#282a36",
        "bg2":        "#1e1f29",
        "bg3":        "#313342",
        "fg":         "#f8f8f2",
        "fg2":        "#cdd6f4",
        "accent":     "#bd93f9",
        "cursor":     "#f8f8f2",
        "sel_bg":     "#44475a",
        "term_bg":    "#21222c",
        "term_fg":    "#50fa7b",
        "kw":         "#ff79c6",
        "string":     "#f1fa8c",
        "comment":    "#6272a4",
        "builtin":    "#8be9fd",
        "number":     "#bd93f9",
        "ln_fg":      "#6272a4",
    },
    "Solarized": {
        "bg":         "#fdf6e3",
        "bg2":        "#eee8d5",
        "bg3":        "#e8e0cc",
        "fg":         "#657b83",
        "fg2":        "#586e75",
        "accent":     "#268bd2",
        "cursor":     "#268bd2",
        "sel_bg":     "#ddd8c6",
        "term_bg":    "#fdf6e3",
        "term_fg":    "#2aa198",
        "kw":         "#859900",
        "string":     "#2aa198",
        "comment":    "#93a1a1",
        "builtin":    "#268bd2",
        "number":     "#d33682",
        "ln_fg":      "#93a1a1",
    },
    "Monokai": {
        "bg":         "#272822",
        "bg2":        "#1e1f1c",
        "bg3":        "#2f3024",
        "fg":         "#f8f8f2",
        "fg2":        "#cfcfc2",
        "accent":     "#a6e22e",
        "cursor":     "#f8f8f0",
        "sel_bg":     "#49483e",
        "term_bg":    "#1a1b16",
        "term_fg":    "#a6e22e",
        "kw":         "#f92672",
        "string":     "#e6db74",
        "comment":    "#75715e",
        "builtin":    "#66d9e8",
        "number":     "#ae81ff",
        "ln_fg":      "#5a5a4a",
    },
}

# ─────────────────────────────────────────────
#  LANGUAGE SYNTAX RULES
# ─────────────────────────────────────────────
PYTHON_KEYWORDS = set(keyword.kwlist)
PYTHON_BUILTINS = {
    "print", "len", "range", "int", "str", "float", "list", "dict",
    "set", "tuple", "bool", "type", "input", "open", "enumerate",
    "zip", "map", "filter", "sorted", "reversed", "sum", "min", "max",
    "abs", "round", "isinstance", "hasattr", "getattr", "setattr",
    "super", "property", "staticmethod", "classmethod", "any", "all",
    "None", "True", "False", "self", "cls",
}

JS_KEYWORDS = {
    "var", "let", "const", "function", "return", "if", "else", "for",
    "while", "do", "break", "continue", "switch", "case", "default",
    "class", "extends", "import", "export", "from", "new", "this",
    "typeof", "instanceof", "try", "catch", "finally", "throw",
    "async", "await", "yield", "delete", "in", "of", "void", "null",
    "undefined", "true", "false",
}
JS_BUILTINS = {
    "console", "window", "document", "Math", "JSON", "Array", "Object",
    "String", "Number", "Boolean", "Promise", "setTimeout", "setInterval",
    "clearTimeout", "clearInterval", "fetch", "localStorage", "sessionStorage",
}

JAVA_KEYWORDS = {
    "abstract", "assert", "boolean", "break", "byte", "case", "catch",
    "char", "class", "const", "continue", "default", "do", "double",
    "else", "enum", "extends", "final", "finally", "float", "for",
    "goto", "if", "implements", "import", "instanceof", "int", "interface",
    "long", "native", "new", "package", "private", "protected", "public",
    "return", "short", "static", "strictfp", "super", "switch",
    "synchronized", "this", "throw", "throws", "transient", "try",
    "void", "volatile", "while", "true", "false", "null",
}

CPP_KEYWORDS = {
    "auto", "break", "case", "char", "const", "continue", "default",
    "do", "double", "else", "enum", "extern", "float", "for", "goto",
    "if", "int", "long", "register", "return", "short", "signed",
    "sizeof", "static", "struct", "switch", "typedef", "union",
    "unsigned", "void", "volatile", "while", "class", "namespace",
    "new", "delete", "this", "virtual", "override", "template",
    "typename", "public", "private", "protected", "true", "false",
    "nullptr", "include", "define", "ifdef", "ifndef", "endif",
}

RUST_KEYWORDS = {
    "as", "break", "const", "continue", "crate", "else", "enum",
    "extern", "false", "fn", "for", "if", "impl", "in", "let",
    "loop", "match", "mod", "move", "mut", "pub", "ref", "return",
    "self", "Self", "static", "struct", "super", "trait", "true",
    "type", "unsafe", "use", "where", "while", "async", "await",
    "dyn", "union",
}

LANG_RULES = {
    "Python": {
        "keywords": PYTHON_KEYWORDS,
        "builtins": PYTHON_BUILTINS,
        "comment_line": "#",
        "string_patterns": [r'"""[\s\S]*?"""', r"'''[\s\S]*?'''",
                             r'"(?:[^"\\]|\\.)*"', r"'(?:[^'\\]|\\.)*'"],
        "extensions": [".py"],
    },
    "JavaScript": {
        "keywords": JS_KEYWORDS,
        "builtins": JS_BUILTINS,
        "comment_line": "//",
        "string_patterns": [r'`[\s\S]*?`', r'"(?:[^"\\]|\\.)*"', r"'(?:[^'\\]|\\.)*'"],
        "extensions": [".js", ".jsx", ".ts", ".tsx"],
    },
    "Java": {
        "keywords": JAVA_KEYWORDS,
        "builtins": set(),
        "comment_line": "//",
        "string_patterns": [r'"(?:[^"\\]|\\.)*"'],
        "extensions": [".java"],
    },
    "C++": {
        "keywords": CPP_KEYWORDS,
        "builtins": set(),
        "comment_line": "//",
        "string_patterns": [r'"(?:[^"\\]|\\.)*"', r"'(?:[^'\\]|\\.)*'"],
        "extensions": [".cpp", ".cc", ".cxx", ".c", ".h", ".hpp"],
    },
    "Rust": {
        "keywords": RUST_KEYWORDS,
        "builtins": set(),
        "comment_line": "//",
        "string_patterns": [r'"(?:[^"\\]|\\.)*"'],
        "extensions": [".rs"],
    },
    "Plain Text": {
        "keywords": set(),
        "builtins": set(),
        "comment_line": None,
        "string_patterns": [],
        "extensions": [".txt", ".md"],
    },
}

FONT_SIZES = [9, 10, 11, 12, 13, 14, 16, 18, 20]
FONTS = ["Consolas", "Courier New", "Fira Code", "JetBrains Mono", "Source Code Pro", "Cascadia Code"]

# ─────────────────────────────────────────────
#  SETTINGS  (persistent JSON)
# ─────────────────────────────────────────────
SETTINGS_FILE = os.path.join(os.path.expanduser("~"), ".kaaXpy_settings.json")
DEFAULT_SETTINGS = {
    "theme": "Matrix",
    "language": "Python",
    "font_family": "Consolas",
    "font_size": 12,
    "tab_size": 4,
    "word_wrap": False,
    "show_line_numbers": True,
    "auto_pair": True,
    "auto_indent": True,
}

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                s = json.load(f)
            for k, v in DEFAULT_SETTINGS.items():
                s.setdefault(k, v)
            return s
        except Exception:
            pass
    return dict(DEFAULT_SETTINGS)

def save_settings(s):
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump(s, f, indent=2)
    except Exception:
        pass

# ─────────────────────────────────────────────
#  SETTINGS DIALOG
# ─────────────────────────────────────────────
class SettingsDialog(ctk.CTkToplevel):
    def __init__(self, parent, settings, on_apply):
        super().__init__(parent)
        self.title("⚙ Settings")
        self.geometry("520x560")
        self.resizable(False, False)
        self.grab_set()

        T = THEMES[settings["theme"]]
        self.configure(fg_color=T["bg"])

        self.settings = dict(settings)
        self.on_apply = on_apply
        self._vars = {}

        self._build(T)

    def _row(self, parent, label_text, T):
        frame = ctk.CTkFrame(parent, fg_color=T["bg3"], corner_radius=8)
        frame.pack(fill="x", pady=4, padx=8)
        lbl = ctk.CTkLabel(frame, text=label_text, text_color=T["fg2"],
                           font=("Consolas", 11), anchor="w", width=180)
        lbl.pack(side="left", padx=12, pady=8)
        return frame

    def _build(self, T):
        title = ctk.CTkLabel(self, text="⚙ Settings",
                             text_color=T["accent"], font=("Consolas", 16, "bold"))
        title.pack(pady=(18, 8))

        scroll = ctk.CTkScrollableFrame(self, fg_color=T["bg2"], corner_radius=12)
        scroll.pack(fill="both", expand=True, padx=16, pady=8)

        # ── Theme ──
        row = self._row(scroll, "🎨 Theme", T)
        v = ctk.StringVar(value=self.settings["theme"])
        self._vars["theme"] = v
        ctk.CTkOptionMenu(row, values=list(THEMES.keys()), variable=v,
                          fg_color=T["bg2"], button_color=T["accent"],
                          button_hover_color=T["fg2"], text_color=T["fg"],
                          font=("Consolas", 11)).pack(side="right", padx=12, pady=6)

        # ── Language ──
        row = self._row(scroll, "💻 Language", T)
        v = ctk.StringVar(value=self.settings["language"])
        self._vars["language"] = v
        ctk.CTkOptionMenu(row, values=list(LANG_RULES.keys()), variable=v,
                          fg_color=T["bg2"], button_color=T["accent"],
                          button_hover_color=T["fg2"], text_color=T["fg"],
                          font=("Consolas", 11)).pack(side="right", padx=12, pady=6)

        # ── Font Family ──
        row = self._row(scroll, "🔤 Font", T)
        v = ctk.StringVar(value=self.settings["font_family"])
        self._vars["font_family"] = v
        ctk.CTkOptionMenu(row, values=FONTS, variable=v,
                          fg_color=T["bg2"], button_color=T["accent"],
                          button_hover_color=T["fg2"], text_color=T["fg"],
                          font=("Consolas", 11)).pack(side="right", padx=12, pady=6)

        # ── Font Size ──
        row = self._row(scroll, "📏 Font Size", T)
        v = ctk.IntVar(value=self.settings["font_size"])
        self._vars["font_size"] = v
        ctk.CTkOptionMenu(row, values=[str(s) for s in FONT_SIZES],
                          variable=ctk.StringVar(value=str(self.settings["font_size"])),
                          fg_color=T["bg2"], button_color=T["accent"],
                          button_hover_color=T["fg2"], text_color=T["fg"],
                          font=("Consolas", 11),
                          command=lambda val: v.set(int(val))).pack(
                              side="right", padx=12, pady=6)

        # ── Tab Size ──
        row = self._row(scroll, "↹ Tab Size", T)
        v = ctk.IntVar(value=self.settings["tab_size"])
        self._vars["tab_size"] = v
        ctk.CTkOptionMenu(row, values=["2", "4", "8"],
                          variable=ctk.StringVar(value=str(self.settings["tab_size"])),
                          fg_color=T["bg2"], button_color=T["accent"],
                          button_hover_color=T["fg2"], text_color=T["fg"],
                          font=("Consolas", 11),
                          command=lambda val: v.set(int(val))).pack(
                              side="right", padx=12, pady=6)

        # ── Toggles ──
        for key, label in [
            ("word_wrap",         "↩ Word Wrap"),
            ("show_line_numbers", "🔢 Line Numbers"),
            ("auto_pair",         "🔧 Auto Pair Brackets"),
            ("auto_indent",       "⤵ Auto Indent"),
        ]:
            row = self._row(scroll, label, T)
            v = ctk.BooleanVar(value=self.settings[key])
            self._vars[key] = v
            ctk.CTkSwitch(row, text="", variable=v,
                          progress_color=T["accent"],
                          button_color=T["fg2"]).pack(side="right", padx=16, pady=6)

        # ── Buttons ──
        btn_frame = ctk.CTkFrame(self, fg_color=T["bg"], corner_radius=0)
        btn_frame.pack(fill="x", padx=16, pady=12)

        ctk.CTkButton(btn_frame, text="✓ Apply",
                      fg_color=T["accent"], text_color=T["bg"],
                      hover_color=T["fg2"], font=("Consolas", 12, "bold"),
                      command=self._apply).pack(side="right", padx=4)
        ctk.CTkButton(btn_frame, text="✕ Cancel",
                      fg_color=T["bg3"], text_color=T["fg"],
                      hover_color=T["bg2"], font=("Consolas", 12),
                      command=self.destroy).pack(side="right", padx=4)

    def _apply(self):
        for k, v in self._vars.items():
            self.settings[k] = v.get()
        save_settings(self.settings)
        self.on_apply(self.settings)
        self.destroy()

# ─────────────────────────────────────────────
#  FIND & REPLACE DIALOG
# ─────────────────────────────────────────────
class FindReplaceDialog(ctk.CTkToplevel):
    def __init__(self, parent, get_text_widget, T):
        super().__init__(parent)
        self.title("Find & Replace")
        self.geometry("480x220")
        self.resizable(False, False)
        self.get_text = get_text_widget
        self.configure(fg_color=T["bg"])
        self._matches = []
        self._match_idx = 0
        self._build(T)

    def _build(self, T):
        pad = {"padx": 12, "pady": 6}

        ctk.CTkLabel(self, text="Find:", text_color=T["fg2"],
                     font=("Consolas", 11)).grid(row=0, column=0, sticky="e", **pad)
        self.find_var = ctk.StringVar()
        self.find_entry = ctk.CTkEntry(self, textvariable=self.find_var, width=280,
                                       fg_color=T["bg3"], text_color=T["fg"],
                                       border_color=T["accent"], font=("Consolas", 11))
        self.find_entry.grid(row=0, column=1, columnspan=2, **pad, sticky="ew")

        ctk.CTkLabel(self, text="Replace:", text_color=T["fg2"],
                     font=("Consolas", 11)).grid(row=1, column=0, sticky="e", **pad)
        self.replace_var = ctk.StringVar()
        self.replace_entry = ctk.CTkEntry(self, textvariable=self.replace_var, width=280,
                                          fg_color=T["bg3"], text_color=T["fg"],
                                          border_color=T["accent"], font=("Consolas", 11))
        self.replace_entry.grid(row=1, column=1, columnspan=2, **pad, sticky="ew")

        self.case_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(self, text="Match Case", variable=self.case_var,
                        text_color=T["fg2"], font=("Consolas", 10),
                        fg_color=T["accent"], hover_color=T["fg2"]).grid(
            row=2, column=1, sticky="w", padx=12)

        ctk.CTkButton(self, text="◀ Previous", width=110,
                      fg_color=T["bg3"], text_color=T["fg"], hover_color=T["bg2"],
                      font=("Consolas", 11), command=self._prev).grid(
            row=3, column=0, **pad)
        ctk.CTkButton(self, text="Next ▶", width=110,
                      fg_color=T["bg3"], text_color=T["fg"], hover_color=T["bg2"],
                      font=("Consolas", 11), command=self._next).grid(
            row=3, column=1, **pad)
        ctk.CTkButton(self, text="Replace All", width=110,
                      fg_color=T["accent"], text_color=T["bg"],
                      hover_color=T["fg2"], font=("Consolas", 11, "bold"),
                      command=self._replace_all).grid(row=3, column=2, **pad)

        self.status = ctk.CTkLabel(self, text="", text_color=T["fg2"],
                                   font=("Consolas", 10))
        self.status.grid(row=4, column=0, columnspan=3, **pad)

        self.find_entry.bind("<Return>", lambda e: self._next())
        self.find_entry.bind("<KeyRelease>", lambda e: self._search())
        self.find_entry.focus()

    def _search(self):
        text = self.get_text()
        if not text:
            return
        text.tag_remove("found", "1.0", "end")
        needle = self.find_var.get()
        if not needle:
            self._matches = []
            self.status.configure(text="")
            return

        flags = 0 if self.case_var.get() else re.IGNORECASE
        content = text.get("1.0", "end-1c")
        self._matches = list(re.finditer(re.escape(needle), content, flags))
        self._match_idx = 0

        for m in self._matches:
            s = f"1.0+{m.start()}c"
            e = f"1.0+{m.end()}c"
            text.tag_add("found", s, e)
            text.tag_configure("found", background="#ffff00", foreground="#000000")

        self.status.configure(text=f"{len(self._matches)} found")

    def _jump(self, idx):
        text = self.get_text()
        if not text or not self._matches:
            return
        m = self._matches[idx % len(self._matches)]
        text.mark_set("insert", f"1.0+{m.start()}c")
        text.see("insert")

    def _next(self):
        self._search()
        if self._matches:
            self._match_idx = (self._match_idx + 1) % len(self._matches)
            self._jump(self._match_idx)

    def _prev(self):
        self._search()
        if self._matches:
            self._match_idx = (self._match_idx - 1) % len(self._matches)
            self._jump(self._match_idx)

    def _replace_all(self):
        text = self.get_text()
        if not text:
            return
        needle = self.find_var.get()
        replacement = self.replace_var.get()
        if not needle:
            return
        content = text.get("1.0", "end-1c")
        flags = 0 if self.case_var.get() else re.IGNORECASE
        new_content, count = re.subn(re.escape(needle), replacement, content, flags=flags)
        text.delete("1.0", "end")
        text.insert("1.0", new_content)
        self.status.configure(text=f"Replaced {count} time(s)")

# ─────────────────────────────────────────────
#  SPLASH SCREEN
# ─────────────────────────────────────────────
class Splash(tk.Tk):
    def __init__(self):
        super().__init__()
        self.overrideredirect(True)
        w, h = 440, 260
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")
        self.configure(bg="#0a0a0a")

        canvas = tk.Canvas(self, width=w, height=h, bg="#0a0a0a", highlightthickness=0)
        canvas.pack()

        # Decorative corner accents
        for x1, y1, x2, y2 in [(0,0,40,2),(0,0,2,40),(w-40,0,w,2),(w-2,0,w,40),
                                 (0,h-2,40,h),(0,h-40,2,h),(w-40,h-2,w,h),(w-2,h-40,w,h)]:
            canvas.create_rectangle(x1, y1, x2, y2, fill="#00ff7f", outline="")

        canvas.create_text(w//2, 90, text="kaaXpy", fill="#00ff7f",
                           font=("Consolas", 44, "bold"))
        canvas.create_text(w//2, 145, text="v2.0", fill="#00cc66",
                           font=("Consolas", 18))
        canvas.create_text(w//2, 200, text="Python Code Editor", fill="#336644",
                           font=("Consolas", 12))

        self.alpha = 0.0
        self.attributes("-alpha", 0.0)
        self._phase = "in"
        self.after(20, self._fade)

    def _fade(self):
        if not self.winfo_exists():
            return
        if self._phase == "in":
            self.alpha = min(1.0, self.alpha + 0.05)
            self.attributes("-alpha", self.alpha)
            if self.alpha >= 1.0:
                self._phase = "hold"
                self.after(1400, self._fade)
            else:
                self.after(20, self._fade)
        elif self._phase == "hold":
            self._phase = "out"
            self.after(20, self._fade)
        else:
            self.alpha = max(0.0, self.alpha - 0.05)
            self.attributes("-alpha", self.alpha)
            if self.alpha <= 0.0:
                self.destroy()
            else:
                self.after(20, self._fade)

# ─────────────────────────────────────────────
#  WELCOME SCREEN
# ─────────────────────────────────────────────
class WelcomeScreen(tk.Tk):
    """Shown after the splash. User picks New File or Open File."""

    def __init__(self):
        super().__init__()
        self.overrideredirect(True)
        self.result = None          # "new" | "open" | path-string
        self._open_path = None

        w, h = 540, 400
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")
        self.configure(bg="#0d0d0d")

        self.alpha = 0.0
        self.attributes("-alpha", 0.0)
        self._build(w, h)
        self.after(20, self._fade_in)

    # ── Build ──────────────────────────────────
    def _build(self, w, h):
        canvas = tk.Canvas(self, width=w, height=h,
                           bg="#0d0d0d", highlightthickness=0)
        canvas.place(x=0, y=0)

        # Corner accents
        for x1, y1, x2, y2 in [
            (0,0,50,2),(0,0,2,50),(w-50,0,w,2),(w-2,0,w,50),
            (0,h-2,50,h),(0,h-50,2,h),(w-50,h-2,w,h),(w-2,h-50,w,h),
        ]:
            canvas.create_rectangle(x1, y1, x2, y2, fill="#00ff7f", outline="")

        # Subtle grid lines (decorative)
        for x in range(0, w, 40):
            canvas.create_line(x, 0, x, h, fill="#0d2a1a", width=1)
        for y in range(0, h, 40):
            canvas.create_line(0, y, w, y, fill="#0d2a1a", width=1)

        # Logo / title
        canvas.create_text(w//2, 72, text="⬡ kaaXpy", fill="#00ff7f",
                           font=("Consolas", 34, "bold"))
        canvas.create_text(w//2, 116, text="v2.0  ·  Code Editor",
                           fill="#336644", font=("Consolas", 13))

        # Divider
        canvas.create_line(60, 145, w-60, 145, fill="#003322", width=1)

        # Subtitle
        canvas.create_text(w//2, 172, text="Welcome  —  what would you like to do?",
                           fill="#00cc66", font=("Consolas", 11))

        # ── Buttons ──
        btn_cfg = dict(
            font=("Consolas", 13, "bold"),
            relief="flat", cursor="hand2", bd=0,
        )

        # New File button
        new_btn = tk.Button(
            self, text="  📄   New File",
            bg="#003322", fg="#00ff7f",
            activebackground="#00ff7f", activeforeground="#0d0d0d",
            width=18, height=2,
            command=self._new_file, **btn_cfg
        )
        new_btn.place(x=w//2 - 210, y=210)
        new_btn.bind("<Enter>", lambda e: new_btn.configure(bg="#004d33"))
        new_btn.bind("<Leave>", lambda e: new_btn.configure(bg="#003322"))

        # Open File button
        open_btn = tk.Button(
            self, text="  📂   Open File",
            bg="#001a33", fg="#00ccff",
            activebackground="#00ccff", activeforeground="#0d0d0d",
            width=18, height=2,
            command=self._open_file, **btn_cfg
        )
        open_btn.place(x=w//2 + 10, y=210)
        open_btn.bind("<Enter>", lambda e: open_btn.configure(bg="#002244"))
        open_btn.bind("<Leave>", lambda e: open_btn.configure(bg="#001a33"))

        # Keyboard hints
        canvas.create_text(w//2, 310,
                           text="New File  [N]   ·   Open File  [O]   ·   Quit  [Esc]",
                           fill="#1a4d2e", font=("Consolas", 10))

        # Version / build tag
        canvas.create_text(w//2, h - 22,
                           text="kaaXpy v2.0  —  github-ready build",
                           fill="#1a3326", font=("Consolas", 9))

        # Key bindings
        self.bind("<n>", lambda e: self._new_file())
        self.bind("<N>", lambda e: self._new_file())
        self.bind("<o>", lambda e: self._open_file())
        self.bind("<O>", lambda e: self._open_file())
        self.bind("<Escape>", lambda e: self._quit())

    # ── Fade in ───────────────────────────────
    def _fade_in(self):
        if not self.winfo_exists():
            return
        self.alpha = min(1.0, self.alpha + 0.07)
        self.attributes("-alpha", self.alpha)
        if self.alpha < 1.0:
            self.after(16, self._fade_in)

    # ── Actions ───────────────────────────────
    def _new_file(self):
        self.result = "new"
        self.destroy()

    def _open_file(self):
        path = filedialog.askopenfilename(
            title="Open File",
            filetypes=[
                ("Python",     "*.py"),
                ("JavaScript", "*.js *.ts *.jsx *.tsx"),
                ("Java",       "*.java"),
                ("C/C++",      "*.c *.cpp *.h *.hpp"),
                ("Rust",       "*.rs"),
                ("All Files",  "*.*"),
            ]
        )
        if path:
            self._open_path = path
            self.result = "open"
            self.destroy()
        # If cancelled, stay on welcome screen

    def _quit(self):
        self.result = "quit"
        self.destroy()


# ─────────────────────────────────────────────
#  MAIN EDITOR
# ─────────────────────────────────────────────
class KaaXpy(ctk.CTk):
    def __init__(self, open_path=None):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        super().__init__()
        self.overrideredirect(True)
        self._drag_x = 0
        self._drag_y = 0
        self.settings = load_settings()
        T = self._T()
        self.title("kaaXpy v2.0")
        w, h = 1300, 780
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")
        self.configure(fg_color=T["bg"])

        self.tabs_data = {}
        self._find_dialog = None
        self._open_path = open_path   # file to load after UI is ready

        self._build_ui()
        self._create_tab()

        # If a file was chosen on the welcome screen, load it now
        if self._open_path:
            self.after(100, lambda: self._load_file(self._open_path))

    def _T(self):
        return THEMES.get(self.settings["theme"], THEMES["Matrix"])

    def _font(self, bold=False):
        style = "bold" if bold else "normal"
        return (self.settings["font_family"], self.settings["font_size"], style)

    # ─── BUILD UI ───────────────────────────────
    def _build_ui(self):
        T = self._T()

        # ── Title bar ──
        self.titlebar = ctk.CTkFrame(self, height=38, fg_color=T["bg2"], corner_radius=0)
        self.titlebar.pack(fill="x")
        self.titlebar.pack_propagate(False)

        self.title_lbl = ctk.CTkLabel(
            self.titlebar, text="⬡ kaaXpy v2.0",
            text_color=T["accent"], font=("Consolas", 12, "bold")
        )
        self.title_lbl.pack(side="left", padx=14)

        for text, cmd, col in [
            ("✕", self.destroy, "#ff5555"),
            ("▢", self._toggle_maximize, T["fg2"]),
            ("—", self.iconify, T["fg2"]),
        ]:
            b = ctk.CTkButton(self.titlebar, text=text, width=32, height=28,
                              fg_color=T["bg2"], text_color=col,
                              hover_color=T["bg3"], font=("Consolas", 13),
                              corner_radius=4, command=cmd)
            b.pack(side="right", padx=2, pady=4)

        for w in (self.titlebar, self.title_lbl):
            w.bind("<Button-1>",        self._drag_start)
            w.bind("<B1-Motion>",       self._drag_move)
            w.bind("<Double-Button-1>", lambda e: self._toggle_maximize())

        # ── Toolbar ──
        self.toolbar = ctk.CTkFrame(self, height=36, fg_color=T["bg3"], corner_radius=0)
        self.toolbar.pack(fill="x")
        self.toolbar.pack_propagate(False)
        self._build_toolbar(T)

        # ── Main area ──
        self.paned = tk.PanedWindow(self, orient="vertical",
                                    bg=T["bg"], sashwidth=4,
                                    sashrelief="flat", sashpad=0)
        self.paned.pack(fill="both", expand=True)

        self.editor_pane = ctk.CTkFrame(self.paned, fg_color=T["bg"], corner_radius=0)
        self.paned.add(self.editor_pane, minsize=200)

        self.notebook = ctk.CTkTabview(self.editor_pane,
                                       fg_color=T["bg2"],
                                       segmented_button_fg_color=T["bg3"],
                                       segmented_button_selected_color=T["accent"],
                                       segmented_button_selected_hover_color=T["fg2"],
                                       segmented_button_unselected_color=T["bg3"],
                                       segmented_button_unselected_hover_color=T["bg2"],
                                       text_color=T["fg"],
                                       text_color_disabled=T["fg2"],
                                       corner_radius=8)
        self.notebook.pack(fill="both", expand=True, padx=4, pady=4)

        self.term_pane = ctk.CTkFrame(self.paned, fg_color=T["bg"], corner_radius=0)
        self.paned.add(self.term_pane, minsize=80)
        self._build_terminal(T)

        # ── Status bar ──
        self.statusbar = ctk.CTkFrame(self, height=24, fg_color=T["bg2"], corner_radius=0)
        self.statusbar.pack(fill="x", side="bottom")
        self.statusbar.pack_propagate(False)
        self.status_lbl = ctk.CTkLabel(
            self.statusbar, text="Ln 1, Col 1", text_color=T["fg2"],
            font=("Consolas", 10), anchor="w"
        )
        self.status_lbl.pack(side="left", padx=10)
        self.lang_lbl = ctk.CTkLabel(
            self.statusbar, text=self.settings["language"],
            text_color=T["accent"], font=("Consolas", 10), anchor="e"
        )
        self.lang_lbl.pack(side="right", padx=10)
        self.theme_lbl = ctk.CTkLabel(
            self.statusbar, text=self.settings["theme"],
            text_color=T["fg2"], font=("Consolas", 10), anchor="e"
        )
        self.theme_lbl.pack(side="right", padx=10)

    def _drag_start(self, event):
        self._drag_x = event.x_root - self.winfo_x()
        self._drag_y = event.y_root - self.winfo_y()

    def _drag_move(self, event):
        x = event.x_root - self._drag_x
        y = event.y_root - self._drag_y
        self.geometry(f"+{x}+{y}")

    def _toggle_maximize(self):
        try:
            if getattr(self, "_maximized", False):
                self._maximized = False
                w, h = 1300, 780
                sw = self.winfo_screenwidth()
                sh = self.winfo_screenheight()
                self.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")
            else:
                self._maximized = True
                sw = self.winfo_screenwidth()
                sh = self.winfo_screenheight()
                self.geometry(f"{sw}x{sh}+0+0")
        except Exception:
            pass

    def _build_toolbar(self, T):
        for w in self.toolbar.winfo_children():
            w.destroy()

        sep = lambda: ctk.CTkLabel(self.toolbar, text="|", text_color=T["bg"],
                                   font=("Consolas", 12)).pack(side="left", padx=2)

        def tbtn(icon, text, cmd, accent=False):
            col   = T["accent"] if accent else T["fg"]
            hover = T["bg2"] if not accent else T["fg2"]
            b = ctk.CTkButton(
                self.toolbar, text=f"{icon} {text}",
                fg_color=T["bg3"], text_color=col,
                hover_color=hover, font=("Consolas", 10),
                corner_radius=6, height=26, width=90,
                command=cmd
            )
            b.pack(side="left", padx=3, pady=4)
            return b

        tbtn("📄", "New",      self._create_tab)
        tbtn("📂", "Open",     self._open_file)
        tbtn("💾", "Save",     self._save_file)
        tbtn("🖫", "Save As",  self._save_as)
        sep()
        tbtn("▶", "Run",      self._run_code, accent=True)
        sep()
        tbtn("🔍", "Find",     self._open_find)
        tbtn("⚙", "Settings", self._open_settings)
        sep()
        tbtn("🗑", "Clear Term", self._clear_terminal)

    def _build_terminal(self, T):
        for w in self.term_pane.winfo_children():
            w.destroy()

        hdr = ctk.CTkFrame(self.term_pane, fg_color=T["bg3"], height=24, corner_radius=0)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        ctk.CTkLabel(hdr, text="▣ Terminal", text_color=T["accent"],
                     font=("Consolas", 10, "bold")).pack(side="left", padx=8)

        self.terminal = tk.Text(
            self.term_pane, bg=T["term_bg"], fg=T["term_fg"],
            font=("Consolas", 11), insertbackground=T["term_fg"],
            relief="flat", wrap="word", state="normal"
        )
        term_scroll = tk.Scrollbar(self.term_pane, command=self.terminal.yview)
        term_scroll.pack(side="right", fill="y")
        self.terminal.configure(yscrollcommand=term_scroll.set)
        self.terminal.pack(fill="both", expand=True, padx=4, pady=4)

    # ─── TAB CREATION ───────────────────────────
    def _create_tab(self):
        T = self._T()
        idx = len(self.tabs_data) + 1
        tab_name = f"Untitled {idx}"

        self.notebook.add(tab_name)
        tab_frame = self.notebook.tab(tab_name)

        container = tk.Frame(tab_frame, bg=T["bg2"])
        container.pack(fill="both", expand=True)

        if self.settings["show_line_numbers"]:
            self.ln_frame = tk.Frame(container, bg=T["bg2"], width=44)
            self.ln_frame.pack(side="left", fill="y")
            self.ln_frame.pack_propagate(False)
            ln = tk.Text(self.ln_frame, width=4, bg=T["bg2"], fg=T["ln_fg"],
                         state="disabled", relief="flat",
                         font=self._font(), selectbackground=T["bg2"],
                         cursor="arrow")
            ln.pack(fill="y", expand=True, pady=4)
        else:
            ln = None

        text = tk.Text(
            container, bg=T["bg"], fg=T["fg"],
            insertbackground=T["cursor"],
            font=self._font(), wrap="word" if self.settings["word_wrap"] else "none",
            undo=True, relief="flat",
            selectbackground=T["sel_bg"], selectforeground=T["fg"],
            padx=8, pady=4,
        )
        char_px = self.settings["font_size"] * self.settings["tab_size"]
        text.configure(tabs=(char_px,))
        v_scroll = tk.Scrollbar(container, command=text.yview)
        v_scroll.pack(side="right", fill="y")
        text.configure(yscrollcommand=v_scroll.set)
        text.pack(side="left", fill="both", expand=True)

        if ln:
            text.configure(yscrollcommand=lambda *a: (v_scroll.set(*a),
                                                       ln.yview_moveto(a[0])))

        text.tag_configure("keyword",  foreground=T["kw"])
        text.tag_configure("builtin",  foreground=T["builtin"])
        text.tag_configure("string",   foreground=T["string"])
        text.tag_configure("comment",  foreground=T["comment"])
        text.tag_configure("number",   foreground=T["number"])
        text.tag_configure("found",    background="#ffff00", foreground="#000000")

        text.bind("<KeyPress>",    lambda e: self._on_keypress(e, text))
        text.bind("<Return>",      lambda e: self._on_return(e, text))
        text.bind("<<Modified>>",  lambda e: self._on_modified(e, text, ln, tab_name))
        text.bind("<KeyRelease>",  lambda e: self._on_keyrelease(e, text))
        text.autocomplete_window  = None

        self.tabs_data[tab_name] = {"path": None, "text": text, "ln": ln}
        self.notebook.set(tab_name)

    # ─── HELPERS ────────────────────────────────
    def _current(self):
        try:
            name = self.notebook.get()
            data = self.tabs_data.get(name)
            if not data:
                return None, None, None
            return name, data["text"], data["ln"]
        except Exception:
            return None, None, None

    def _current_text(self):
        _, text, _ = self._current()
        return text

    # ─── KEY HANDLERS ───────────────────────────
    def _on_keypress(self, event, text):
        if not self.settings["auto_pair"]:
            return
        pairs = {"(": ")", "[": "]", "{": "}", '"': '"', "'": "'"}
        if event.char in pairs:
            idx = text.index("insert")
            text.insert(idx, event.char + pairs[event.char])
            text.mark_set("insert", f"{idx}+1c")
            return "break"

    def _on_return(self, event, text):
        if not self.settings["auto_indent"]:
            return
        idx = text.index("insert")
        line = idx.split(".")[0]
        prev = text.get(f"{line}.0", f"{line}.end")
        indent = re.match(r"[ \t]*", prev).group(0)
        if prev.rstrip().endswith((":", "{", "(")):
            indent += " " * self.settings["tab_size"]
        text.insert(idx, "\n" + indent)
        return "break"

    def _on_modified(self, event, text, ln, tab_name):
        text.edit_modified(False)
        if ln:
            self._update_ln(text, ln)
        self._update_status(text)
        self._syntax_highlight(text)

    def _on_keyrelease(self, event, text):
        if event.keysym in ("Up", "Down", "Return", "Escape"):
            self._autocomplete_nav(event, text)
            return
        if not event.char.isalpha() and event.keysym != "BackSpace":
            self._close_ac(text)
            return
        lang = LANG_RULES.get(self.settings["language"], LANG_RULES["Python"])
        all_words = lang["keywords"] | lang["builtins"]
        idx = text.index("insert")
        line_start = f"{idx.split('.')[0]}.0"
        cur_line = text.get(line_start, idx)
        m = re.search(r"[a-zA-Z_][a-zA-Z0-9_]*$", cur_line)
        if not m:
            self._close_ac(text)
            return
        prefix = m.group(0)
        if len(prefix) < 2:
            self._close_ac(text)
            return
        suggestions = sorted(w for w in all_words if w.startswith(prefix) and w != prefix)
        if not suggestions:
            self._close_ac(text)
            return
        self._show_ac(text, suggestions[:8], prefix)

    # ─── AUTOCOMPLETE ────────────────────────────
    def _show_ac(self, text, suggestions, prefix):
        self._close_ac(text)
        bbox = text.bbox("insert")
        if not bbox:
            return
        x, y, _, h = bbox
        T = self._T()
        x += text.winfo_rootx()
        y += text.winfo_rooty() + h + 2

        win = tk.Toplevel(text, bg=T["bg3"])
        win.wm_overrideredirect(True)
        win.geometry(f"+{x}+{y}")
        win.attributes("-topmost", True)

        lb = tk.Listbox(win, bg=T["bg3"], fg=T["fg"],
                        selectbackground=T["accent"], selectforeground=T["bg"],
                        activestyle="none", font=("Consolas", 10),
                        height=min(7, len(suggestions)),
                        relief="flat", bd=0, width=24)
        lb.pack(padx=1, pady=1)
        for s in suggestions:
            lb.insert("end", s)
        lb.selection_set(0)

        text.autocomplete_window   = win
        text.autocomplete_listbox  = lb
        text.autocomplete_prefix   = prefix
        lb.bind("<Button-1>", lambda e: self._insert_ac(text))

    def _close_ac(self, text):
        win = getattr(text, "autocomplete_window", None)
        if win:
            win.destroy()
            text.autocomplete_window = None

    def _autocomplete_nav(self, event, text):
        win = getattr(text, "autocomplete_window", None)
        lb  = getattr(text, "autocomplete_listbox", None)
        if not win or not lb:
            return
        if event.keysym == "Escape":
            self._close_ac(text)
        elif event.keysym == "Down":
            i = (lb.curselection()[0] + 1) % lb.size() if lb.curselection() else 0
            lb.selection_clear(0, "end"); lb.selection_set(i); lb.activate(i)
        elif event.keysym == "Up":
            i = (lb.curselection()[0] - 1) % lb.size() if lb.curselection() else lb.size()-1
            lb.selection_clear(0, "end"); lb.selection_set(i); lb.activate(i)
        elif event.keysym == "Return":
            self._insert_ac(text)
            return "break"

    def _insert_ac(self, text):
        lb     = getattr(text, "autocomplete_listbox", None)
        prefix = getattr(text, "autocomplete_prefix", "")
        if not lb or not lb.curselection():
            self._close_ac(text)
            return
        choice = lb.get(lb.curselection()[0])
        idx = text.index("insert")
        line_start = f"{idx.split('.')[0]}.0"
        cur_line = text.get(line_start, idx)
        start = len(cur_line) - len(prefix)
        text.delete(f"{idx.split('.')[0]}.{start}", idx)
        text.insert("insert", choice)
        self._close_ac(text)

    # ─── LINE NUMBERS ───────────────────────────
    def _update_ln(self, text, ln):
        ln.config(state="normal")
        ln.delete("1.0", "end")
        count = int(text.index("end-1c").split(".")[0])
        ln.insert("1.0", "\n".join(str(i) for i in range(1, count + 1)))
        ln.config(state="disabled")

    def _update_status(self, text):
        try:
            line, col = text.index("insert").split(".")
            self.status_lbl.configure(text=f"Ln {line}, Col {int(col)+1}")
        except Exception:
            pass

    # ─── SYNTAX HIGHLIGHT ───────────────────────
    def _syntax_highlight(self, text):
        content = text.get("1.0", "end-1c")
        for tag in ("keyword", "builtin", "string", "comment", "number"):
            text.tag_remove(tag, "1.0", "end")

        lang = LANG_RULES.get(self.settings["language"], LANG_RULES["Python"])

        def mark(pattern, tag, flags=re.DOTALL):
            for m in re.finditer(pattern, content, flags):
                text.tag_add(tag, f"1.0+{m.start()}c", f"1.0+{m.end()}c")

        if lang["comment_line"]:
            mark(re.escape(lang["comment_line"]) + r".*", "comment", 0)

        for pat in lang["string_patterns"]:
            mark(pat, "string")

        mark(r"\b\d+(\.\d+)?\b", "number")

        for m in re.finditer(r"\b[a-zA-Z_][a-zA-Z0-9_]*\b", content):
            word = m.group(0)
            s = f"1.0+{m.start()}c"
            e = f"1.0+{m.end()}c"
            if word in lang["keywords"]:
                text.tag_add("keyword", s, e)
            elif word in lang["builtins"]:
                text.tag_add("builtin", s, e)

    # ─── FILE OPS ───────────────────────────────
    def _detect_language(self, path):
        ext = os.path.splitext(path)[1].lower()
        for lang, rules in LANG_RULES.items():
            if ext in rules["extensions"]:
                return lang
        return "Plain Text"

    def _load_file(self, path):
        """Load a file into the current tab (used by welcome screen open)."""
        name, text, ln = self._current()
        if not text:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
        except UnicodeDecodeError:
            with open(path, "r", encoding="latin-1") as f:
                content = f.read()
        text.delete("1.0", "end")
        text.insert("1.0", content)
        self.tabs_data[name]["path"] = path
        self.tabs_data[name]["display_name"] = os.path.basename(path)
        self.settings["language"] = self._detect_language(path)
        self._syntax_highlight(text)
        if ln:
            self._update_ln(text, ln)
        self.lang_lbl.configure(text=self.settings["language"])
        self.title_lbl.configure(text=f"⬡ kaaXpy  —  {os.path.basename(path)}")

    def _open_file(self):
        name, text, ln = self._current()
        if not text:
            return
        path = filedialog.askopenfilename(
            title="Open File",
            filetypes=[
                ("Python",     "*.py"),
                ("JavaScript", "*.js *.ts *.jsx *.tsx"),
                ("Java",       "*.java"),
                ("C/C++",      "*.c *.cpp *.h *.hpp"),
                ("Rust",       "*.rs"),
                ("All Files",  "*.*"),
            ]
        )
        if not path:
            return
        self._load_file(path)

    def _save_file(self):
        name, text, _ = self._current()
        if not text:
            return
        path = self.tabs_data[name]["path"]
        if not path:
            self._save_as()
            return
        with open(path, "w", encoding="utf-8") as f:
            f.write(text.get("1.0", "end-1c"))

    def _save_as(self):
        name, text, _ = self._current()
        if not text:
            return
        path = filedialog.asksaveasfilename(
            title="Save File As",
            defaultextension=".py",
            filetypes=[("Python", "*.py"), ("All Files", "*.*")]
        )
        if not path:
            return
        with open(path, "w", encoding="utf-8") as f:
            f.write(text.get("1.0", "end-1c"))
        self.tabs_data[name]["path"] = path
        self.tabs_data[name]["display_name"] = os.path.basename(path)
        self.title(f"kaaXpy v2.0 — {os.path.basename(path)}")

    # ─── RUN CODE ───────────────────────────────
    def _run_code(self):
        name, text, _ = self._current()
        if not text:
            return
        path = self.tabs_data[name]["path"]
        if not path:
            self._save_as()
            path = self.tabs_data[name]["path"]
        if not path:
            return
        self._save_file()
        self.terminal.config(state="normal")
        self.terminal.delete("1.0", "end")

        lang = self.settings["language"]
        runners = {
            "Python":     ["python", path],
            "JavaScript": ["node", path],
            "Rust":       ["rustc", path, "-o", path + ".out"],
        }
        cmd = runners.get(lang, ["python", path])

        def execute():
            self.terminal.insert("end", f"▶ {' '.join(cmd)}\n")
            try:
                proc = subprocess.Popen(
                    cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
                )
                out, err = proc.communicate(timeout=30)
                if out:
                    self.terminal.insert("end", out)
                if err:
                    self.terminal.insert("end", err)
                rc = proc.returncode
                self.terminal.insert("end",
                    f"\n{'✓ Done' if rc == 0 else '✗ Error'} (exit {rc})\n")
            except subprocess.TimeoutExpired:
                self.terminal.insert("end", "\n⚠ Timeout (30s)\n")
            except FileNotFoundError:
                self.terminal.insert("end",
                    f"\n✗ Command not found: {cmd[0]}\n")
            except Exception as e:
                self.terminal.insert("end", f"\n✗ Error: {e}\n")
            self.terminal.see("end")

        threading.Thread(target=execute, daemon=True).start()

    def _clear_terminal(self):
        self.terminal.config(state="normal")
        self.terminal.delete("1.0", "end")

    # ─── DIALOGS ────────────────────────────────
    def _open_find(self):
        if self._find_dialog and self._find_dialog.winfo_exists():
            self._find_dialog.focus()
            return
        T = self._T()
        self._find_dialog = FindReplaceDialog(self, self._current_text, T)

    def _open_settings(self):
        SettingsDialog(self, self.settings, self._apply_settings)

    def _apply_settings(self, new_settings):
        self.settings = new_settings
        self._rebuild_ui()

    def _rebuild_ui(self):
        T = self._T()
        self.configure(fg_color=T["bg"])
        self.titlebar.configure(fg_color=T["bg2"])
        self.title_lbl.configure(text_color=T["accent"])
        self.toolbar.configure(fg_color=T["bg3"])
        self._build_toolbar(T)
        self._build_terminal(T)
        self.statusbar.configure(fg_color=T["bg2"])
        self.status_lbl.configure(text_color=T["fg2"])
        self.lang_lbl.configure(text_color=T["accent"],
                                 text=self.settings["language"])
        self.theme_lbl.configure(text=self.settings["theme"])

        for name, data in self.tabs_data.items():
            text = data["text"]
            ln   = data["ln"]
            text.configure(
                bg=T["bg"], fg=T["fg"],
                insertbackground=T["cursor"],
                selectbackground=T["sel_bg"],
                font=self._font(),
                wrap="word" if self.settings["word_wrap"] else "none",
            )
            if ln:
                ln.configure(bg=T["bg2"], fg=T["ln_fg"], font=self._font())
            text.tag_configure("keyword",  foreground=T["kw"])
            text.tag_configure("builtin",  foreground=T["builtin"])
            text.tag_configure("string",   foreground=T["string"])
            text.tag_configure("comment",  foreground=T["comment"])
            text.tag_configure("number",   foreground=T["number"])
            self._syntax_highlight(text)

# ─────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────
if __name__ == "__main__":
    # 1. Splash screen
    splash = Splash()
    splash.mainloop()

    # 2. Welcome screen — New File or Open File
    welcome = WelcomeScreen()
    welcome.mainloop()

    if welcome.result == "quit" or welcome.result is None:
        raise SystemExit(0)

    open_path = welcome._open_path if welcome.result == "open" else None

    # 3. Main editor
    app = KaaXpy(open_path=open_path)
    app.mainloop()
