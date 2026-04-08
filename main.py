import tkinter as tk
from tkinter import ttk, filedialog
import subprocess
import threading
import keyword
import re
import os

# ----------------- THEME -----------------
BG_DARK = "#1e1e1e"
BG_DARKER = "#151515"
FG_TEXT = "#d4d4d4"
FG_GREEN = "#00ff7f"
FG_TITLE = "#a0ffa0"
CURSOR_COLOR = "#00ff7f"
TERMINAL_BG = "#111111"
TERMINAL_FG = "#00ff7f"
FONT = ("Consolas", 12)

PY_KEYWORDS = set(keyword.kwlist)


# ----------------- MAIN EDITOR: kaaXpy -----------------
class kaaXpy(tk.Tk):
    def __init__(self):
        super().__init__()

        self.overrideredirect(True)
        self.configure(bg=BG_DARKER)
        self.title("kaaXpy beta1.0")

        # Center window
        w, h = 1200, 700
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

        self.drag = {"x": 0, "y": 0}
        self.tabs_files = {}  # tab -> filename

        self._make_titlebar()
        self._make_toolbar()
        self._make_notebook()
        self._make_terminal()
        self._make_statusbar()

        self._create_tab()

    # ----------------- TITLEBAR -----------------
    def _make_titlebar(self):
        bar = tk.Frame(self, bg=BG_DARK, height=32)
        bar.pack(fill="x", side="top")

        label = tk.Label(
            bar, text="kaaXpy beta1.0", bg=BG_DARK, fg=FG_TITLE,
            font=("Consolas", 10, "bold")
        )
        label.pack(side="left", padx=10)

        close_btn = tk.Button(
            bar, text="✕", command=self.destroy,
            bg=BG_DARK, fg="#ff5555", bd=0,
            activebackground=BG_DARKER, activeforeground="#ff7777",
            font=("Consolas", 10, "bold"), width=3
        )
        close_btn.pack(side="right")

        for w in (bar, label):
            w.bind("<Button-1>", self._start_move)
            w.bind("<B1-Motion>", self._do_move)

    def _start_move(self, e):
        self.drag["x"] = e.x
        self.drag["y"] = e.y

    def _do_move(self, e):
        x = self.winfo_pointerx() - self.drag["x"]
        y = self.winfo_pointery() - self.drag["y"]
        self.geometry(f"+{x}+{y}")

    # ----------------- TOOLBAR -----------------
    def _make_toolbar(self):
        bar = tk.Frame(self, bg=BG_DARKER, height=28)
        bar.pack(fill="x", side="top")

        def btn(text, cmd):
            tk.Button(
                bar, text=text, command=cmd,
                bg=BG_DARKER, fg=FG_GREEN, bd=0,
                activebackground=BG_DARK, activeforeground=FG_GREEN,
                font=("Consolas", 10), padx=8
            ).pack(side="left")

        btn("New Tab", self._create_tab)
        btn("Open", self._open_file)
        btn("Save", self._save_file)
        btn("Save As", self._save_as)
        btn("Run ▶", self._run_code)

    # ----------------- NOTEBOOK / TABS -----------------
    def _make_notebook(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)
        style = ttk.Style()
        style.theme_use("default")
        style.configure("TNotebook", background=BG_DARKER, borderwidth=0)
        style.configure("TNotebook.Tab", background=BG_DARK, foreground=FG_GREEN)
        style.map("TNotebook.Tab", background=[("selected", BG_DARKER)])

    def _create_tab(self):
        frame = tk.Frame(self.notebook, bg=BG_DARKER)

        # Line numbers
        ln_frame = tk.Frame(frame, bg=BG_DARKER)
        ln_frame.pack(side="left", fill="y")
        ln = tk.Text(
            ln_frame, width=4, bg=BG_DARKER, fg=FG_GREEN,
            state="disabled", relief="flat", font=FONT
        )
        ln.pack(fill="y", expand=False)

        # Editor
        editor_frame = tk.Frame(frame, bg=BG_DARKER)
        editor_frame.pack(side="left", fill="both", expand=True)

        text = tk.Text(
            editor_frame, bg=BG_DARK, fg=FG_TEXT,
            insertbackground=CURSOR_COLOR,
            font=FONT, wrap="none", undo=True,
            relief="flat"
        )
        text.pack(side="left", fill="both", expand=True, padx=4, pady=4)

        scroll = tk.Scrollbar(editor_frame, command=text.yview)
        scroll.pack(side="right", fill="y")
        text.configure(yscrollcommand=scroll.set)

        # Bindings
        text.bind("<KeyPress>", lambda e, t=text: self._auto_pair(e, t))
        text.bind("<Return>", lambda e, t=text: self._auto_indent(e, t))
        text.bind("<<Modified>>", lambda e, t=text, l=ln: self._on_modified(e, t, l))
        text.bind("<KeyRelease>", lambda e, t=text: self._on_key_release(e, t))

        # Autocomplete popup
        text.autocomplete_window = None

        # Syntax highlight tags
        text.tag_configure("keyword", foreground="#ff9d00")
        text.tag_configure("string", foreground="#ce9178")
        text.tag_configure("comment", foreground="#6a9955")

        self.notebook.add(frame, text="Untitled")
        self.notebook.select(frame)
        self.tabs_files[frame] = None

    # ----------------- TERMINAL -----------------
    def _make_terminal(self):
        label = tk.Label(
            self, text="Terminal Output", bg=BG_DARK, fg=FG_GREEN, anchor="w"
        )
        label.pack(fill="x")

        self.terminal = tk.Text(
            self, bg=TERMINAL_BG, fg=TERMINAL_FG,
            height=10, font=("Consolas", 11),
            insertbackground=FG_GREEN, relief="flat"
        )
        self.terminal.pack(fill="x")

    # ----------------- STATUS BAR -----------------
    def _make_statusbar(self):
        self.status = tk.Label(
            self, text="Ln 1, Col 1", bg=BG_DARK, fg=FG_GREEN, anchor="w"
        )
        self.status.pack(fill="x", side="bottom")

    # ----------------- HELPERS -----------------
    def _current_text(self):
        tab = self.notebook.select()
        if not tab:
            return None, None, None
        frame = self.nametowidget(tab)
        editor_frame = frame.winfo_children()[1]
        text = editor_frame.winfo_children()[0]
        ln = frame.winfo_children()[0].winfo_children()[0]
        return frame, text, ln

    # ----------------- AUTO PAIR -----------------
    def _auto_pair(self, event, text):
        pairs = {"(": ")", "\"": "\"", "'": "'"}
        if event.char in pairs:
            idx = text.index("insert")
            text.insert(idx, event.char + pairs[event.char])
            text.mark_set("insert", f"{idx}+1c")
            return "break"

    # ----------------- AUTO INDENT -----------------
    def _auto_indent(self, event, text):
        idx = text.index("insert")
        line = idx.split(".")[0]
        prev_line = str(int(line) - 1)
        prev_text = text.get(prev_line + ".0", prev_line + ".end")
        indent = re.match(r"[ \t]*", prev_text).group(0)

        text.insert(idx, "\n" + indent)
        return "break"

    # ----------------- MODIFIED: LINE NUMBERS + STATUS + HIGHLIGHT -----------------
    def _on_modified(self, event, text, ln):
        text.edit_modified(False)
        self._update_line_numbers(text, ln)
        self._update_status(text)
        self._syntax_highlight(text)

    def _update_line_numbers(self, text, ln):
        ln.config(state="normal")
        ln.delete("1.0", "end")
        line_count = int(text.index("end-1c").split(".")[0])
        nums = "\n".join(str(i) for i in range(1, line_count + 1))
        ln.insert("1.0", nums)
        ln.config(state="disabled")

    def _update_status(self, text):
        line, col = text.index("insert").split(".")
        self.status.config(text=f"Ln {line}, Col {int(col)+1}")

    # ----------------- SYNTAX HIGHLIGHT -----------------
    def _syntax_highlight(self, text):
        content = text.get("1.0", "end-1c")
        text.tag_remove("keyword", "1.0", "end")
        text.tag_remove("string", "1.0", "end")
        text.tag_remove("comment", "1.0", "end")

        # Comments
        for m in re.finditer(r"#.*", content):
            start = f"1.0+{m.start()}c"
            end = f"1.0+{m.end()}c"
            text.tag_add("comment", start, end)

        # Strings
        for m in re.finditer(r"(\".*?\"|\'.*?\')", content):
            start = f"1.0+{m.start()}c"
            end = f"1.0+{m.end()}c"
            text.tag_add("string", start, end)

        # Keywords
        for m in re.finditer(r"\b[a-zA-Z_][a-zA-Z0-9_]*\b", content):
            if m.group(0) in PY_KEYWORDS:
                start = f"1.0+{m.start()}c"
                end = f"1.0+{m.end()}c"
                text.tag_add("keyword", start, end)

    # ----------------- AUTOCOMPLETE -----------------
    def _on_key_release(self, event, text):
        if event.keysym in ("Up", "Down", "Return", "Escape"):
            self._handle_autocomplete_nav(event, text)
            return

        if not event.char.isalpha() and event.keysym != "BackSpace":
            self._close_autocomplete(text)
            return

        idx = text.index("insert")
        line_start = f"{idx.split('.')[0]}.0"
        current_line = text.get(line_start, idx)
        match = re.search(r"[a-zA-Z_][a-zA-Z0-9_]*$", current_line)
        if not match:
            self._close_autocomplete(text)
            return

        prefix = match.group(0)
        suggestions = [w for w in PY_KEYWORDS if w.startswith(prefix)]
        if not suggestions:
            self._close_autocomplete(text)
            return

        self._show_autocomplete(text, suggestions, prefix)

    def _show_autocomplete(self, text, suggestions, prefix):
        self._close_autocomplete(text)

        bbox = text.bbox("insert")
        if not bbox:
            return
        x, y, _, _ = bbox
        x += text.winfo_rootx()
        y += text.winfo_rooty() + 20

        win = tk.Toplevel(text)
        win.wm_overrideredirect(True)
        win.geometry(f"+{x}+{y}")
        win.configure(bg=BG_DARK)

        lb = tk.Listbox(
            win, bg=BG_DARK, fg=FG_GREEN,
            selectbackground="#333333", selectforeground=FG_GREEN,
            activestyle="none", font=("Consolas", 10),
            height=min(6, len(suggestions))
        )
        lb.pack()
        for s in suggestions:
            lb.insert("end", s)

        text.autocomplete_window = win
        text.autocomplete_listbox = lb
        text.autocomplete_prefix = prefix

        lb.bind("<Button-1>", lambda e, t=text: self._insert_autocomplete(t))
        lb.bind("<Return>", lambda e, t=text: self._insert_autocomplete(t))

    def _close_autocomplete(self, text):
        win = getattr(text, "autocomplete_window", None)
        if win is not None:
            win.destroy()
            text.autocomplete_window = None

    def _handle_autocomplete_nav(self, event, text):
        win = getattr(text, "autocomplete_window", None)
        lb = getattr(text, "autocomplete_listbox", None)
        if not win or not lb:
            return

        if event.keysym == "Escape":
            self._close_autocomplete(text)
        elif event.keysym == "Down":
            if lb.curselection():
                idx = (lb.curselection()[0] + 1) % lb.size()
            else:
                idx = 0
            lb.selection_clear(0, "end")
            lb.selection_set(idx)
            lb.activate(idx)
        elif event.keysym == "Up":
            if lb.curselection():
                idx = (lb.curselection()[0] - 1) % lb.size()
            else:
                idx = lb.size() - 1
            lb.selection_clear(0, "end")
            lb.selection_set(idx)
            lb.activate(idx)
        elif event.keysym == "Return":
            self._insert_autocomplete(text)

    def _insert_autocomplete(self, text):
        lb = getattr(text, "autocomplete_listbox", None)
        prefix = getattr(text, "autocomplete_prefix", "")
        if not lb or not lb.curselection():
            self._close_autocomplete(text)
            return
        choice = lb.get(lb.curselection()[0])

        idx = text.index("insert")
        line_start = f"{idx.split('.')[0]}.0"
        current_line = text.get(line_start, idx)
        start = len(current_line) - len(prefix)
        text.delete(f"{idx.split('.')[0]}.0+{start}c", idx)
        text.insert("insert", choice)
        self._close_autocomplete(text)

    # ----------------- FILE OPS -----------------
    def _open_file(self):
        frame, text, ln = self._current_text()
        if not text:
            return
        path = filedialog.askopenfilename(
            filetypes=[("Python Files", "*.py"), ("All Files", "*.*")]
        )
        if not path:
            return
        with open(path, "r", encoding="utf-8") as f:
            text.delete("1.0", "end")
            text.insert("1.0", f.read())
        self.tabs_files[frame] = path
        self.notebook.tab(frame, text=os.path.basename(path))
        self._syntax_highlight(text)
        self._update_line_numbers(text, ln)

    def _save_file(self):
        frame, text, ln = self._current_text()
        if not text:
            return
        path = self.tabs_files.get(frame)
        if not path:
            return self._save_as()
        with open(path, "w", encoding="utf-8") as f:
            f.write(text.get("1.0", "end-1c"))

    def _save_as(self):
        frame, text, ln = self._current_text()
        if not text:
            return
        path = filedialog.asksaveasfilename(defaultextension=".py")
        if not path:
            return
        with open(path, "w", encoding="utf-8") as f:
            f.write(text.get("1.0", "end-1c"))
        self.tabs_files[frame] = path
        self.notebook.tab(frame, text=os.path.basename(path))

    # ----------------- RUN CODE -----------------
    def _run_code(self):
        frame, text, ln = self._current_text()
        if not text:
            return
        path = self.tabs_files.get(frame)
        if not path:
            self._save_as()
            path = self.tabs_files.get(frame)
        if not path:
            return

        self._save_file()
        self.terminal.delete("1.0", "end")

        def execute():
            try:
                cmd = ["python", path]
                process = subprocess.Popen(
                    cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
                )
                out, err = process.communicate()
                self.terminal.insert("end", out)
                self.terminal.insert("end", err)
            except Exception as e:
                self.terminal.insert("end", f"Error: {e}")

        threading.Thread(target=execute, daemon=True).start()


# ----------------- SPLASH SCREEN -----------------
class KaaXSplash(tk.Tk):
    def __init__(self):
        super().__init__()
        self.overrideredirect(True)
        self.configure(bg="#0a0a0a")

        w, h = 420, 220
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

        self.label = tk.Label(
            self,
            text="kaaXpy",
            fg="#00ff7f",
            bg="#0a0a0a",
            font=("Consolas", 36, "bold")
        )
        self.label.pack(expand=True)

        self.sub = tk.Label(
            self,
            text="beta1.0",
            fg="#00ff7f",
            bg="#0a0a0a",
            font=("Consolas", 14)
        )
        self.sub.pack()

        self.attributes("-alpha", 0.0)
        self._fade_in_step = 0
        self._fade_out_step = 20
        self.after(10, self.fade_in)

    def fade_in(self):
        if self._fade_in_step <= 20:
            alpha = self._fade_in_step / 20
            self.attributes("-alpha", alpha)
            self._fade_in_step += 1
            self.after(30, self.fade_in)
        else:
            self.after(1200, self.fade_out)

    def fade_out(self):
        if self._fade_out_step >= 0:
            alpha = self._fade_out_step / 20
            self.attributes("-alpha", alpha)
            self._fade_out_step -= 1
            self.after(30, self.fade_out)
        else:
            self.destroy()


# ----------------- MAIN -----------------
if __name__ == "__main__":
    # Show splash
    splash = KaaXSplash()
    splash.mainloop()

    # Then launch editor
    app = kaaXpy()
    app.mainloop()
