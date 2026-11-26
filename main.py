#!/usr/bin/env python
import ctypes
from ctypes import wintypes
import json
from os.path import abspath, dirname, exists, join
from random import uniform
import sys
from threading import Event, Thread
from time import perf_counter
import tkinter as tk
import customtkinter as ctk

# Made By PETEROLO 291©

_kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
_user32 = ctypes.WinDLL("user32", use_last_error=True)
_winmm = ctypes.WinDLL("winmm")

_mutex = _kernel32.CreateMutexW(None, False, "Local\\FlameAutoClicker_SingleInstance")
if ctypes.get_last_error() == 183:
    raise SystemExit(0)

class MOUSEINPUT(ctypes.Structure):
    _fields_ = [("dx", wintypes.LONG), ("dy", wintypes.LONG), ("mouseData", wintypes.DWORD),
                ("dwFlags", wintypes.DWORD), ("time", wintypes.DWORD), ("dwExtraInfo", ctypes.c_size_t)]

class _INPUTU(ctypes.Union):
    _fields_ = [("mi", MOUSEINPUT)]

class INPUT(ctypes.Structure):
    _fields_ = [("type", wintypes.DWORD), ("u", _INPUTU)]

class CURSORINFO(ctypes.Structure):
    _fields_ = [("cbSize", wintypes.DWORD), ("flags", wintypes.DWORD),
                ("hCursor", wintypes.HANDLE), ("ptScreenPos", wintypes.POINT)]

class MSG(ctypes.Structure):
    _fields_ = [("hwnd", wintypes.HWND), ("message", wintypes.UINT), ("wParam", wintypes.WPARAM),
                ("lParam", wintypes.LPARAM), ("time", wintypes.DWORD), ("pt", wintypes.POINT)]

_user32.SendInput.argtypes = (wintypes.UINT, ctypes.POINTER(INPUT), ctypes.c_int)
_user32.VkKeyScanW.argtypes = (ctypes.c_wchar,)
_user32.VkKeyScanW.restype = ctypes.c_short
_user32.PostThreadMessageW.argtypes = (wintypes.DWORD, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM)
_user32.LoadImageW.argtypes = (wintypes.HINSTANCE, wintypes.LPCWSTR, wintypes.UINT, ctypes.c_int, ctypes.c_int, wintypes.UINT)
_user32.LoadImageW.restype = wintypes.HANDLE
_user32.SendMessageW.argtypes = (wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM)
_send_input = _user32.SendInput
_icon_handles = []

def set_sharp_icon(win, path):
    if not path:
        return
    try:
        win.iconbitmap(path)
    except Exception:
        pass
    try:
        win.update_idletasks()
        hwnd = _user32.GetParent(win.winfo_id()) or win.winfo_id()
        sm_x = _user32.GetSystemMetrics(49) or 16
        lg_x = max(_user32.GetSystemMetrics(11) or 32, 48)
        h_sm = _user32.LoadImageW(None, path, 1, sm_x, sm_x, 0x0010)
        h_lg = _user32.LoadImageW(None, path, 1, lg_x, lg_x, 0x0010)
        if h_sm:
            _icon_handles.append(h_sm)
            _user32.SendMessageW(hwnd, 0x0080, 0, h_sm)
        if h_lg:
            _icon_handles.append(h_lg)
            _user32.SendMessageW(hwnd, 0x0080, 1, h_lg)
    except Exception:
        pass

def _mk_click(down, up, dbl=False):
    base = (down, up, down, up) if dbl else (down, up)
    b_ops = 4 if dbl else 8
    sz = ctypes.sizeof(INPUT)
    arr = (INPUT * len(base))()
    for i, f in enumerate(base):
        arr[i].u.mi.dwFlags = f
    b_flags = base * b_ops
    b_arr = (INPUT * len(b_flags))()
    for i, f in enumerate(b_flags):
        b_arr[i].u.mi.dwFlags = f
    return len(base), arr, sz, b_ops, len(b_flags), b_arr

CLICKS = {
    ("Left Click", "Single Click"): _mk_click(0x0002, 0x0004),
    ("Left Click", "Double Click"): _mk_click(0x0002, 0x0004, True),
    ("Right Click", "Single Click"): _mk_click(0x0008, 0x0010),
    ("Right Click", "Double Click"): _mk_click(0x0008, 0x0010, True),
}

VK_TO_NAME = {
    **{i: chr(i) for i in range(0x30, 0x3A)},
    **{i: chr(i) for i in range(0x41, 0x5B)},
    **{0x60 + i: f"NUM{i}" for i in range(10)},
    **{0x70 + i: f"F{i + 1}" for i in range(24)},
    0x08: "BACKSPACE", 0x09: "TAB", 0x0D: "ENTER", 0x13: "PAUSE", 0x14: "CAPSLOCK",
    0x1B: "ESC", 0x20: "SPACE", 0x21: "PGUP", 0x22: "PGDN", 0x23: "END", 0x24: "HOME",
    0x25: "LEFT", 0x26: "UP", 0x27: "RIGHT", 0x28: "DOWN", 0x2D: "INS", 0x2E: "DEL",
    0x6A: "NUM*", 0x6B: "NUM+", 0x6D: "NUM-", 0x6E: "NUM.", 0x6F: "NUM/", 0x90: "NUMLOCK",
}
NAME_TO_VK = {v: k for k, v in VK_TO_NAME.items()}
MOD_VKS = {0x10, 0x11, 0x12, 0x5B, 0x5C, 0xA0, 0xA1, 0xA2, 0xA3, 0xA4, 0xA5}

def vk_to_name(vk):
    if vk in VK_TO_NAME:
        return VK_TO_NAME[vk]
    ch = _user32.MapVirtualKeyW(vk, 2) & 0xFFFF
    return chr(ch).upper() if 33 <= ch <= 255 else f"VK_{vk}"

def name_to_vk(name):
    n = str(name).strip().upper()
    if n in NAME_TO_VK:
        return NAME_TO_VK[n]
    if n.startswith("VK_") and n[3:].isdigit():
        return int(n[3:])
    if len(n) == 1:
        r = _user32.VkKeyScanW(n)
        if r != -1:
            return r & 0xFF
    return None

def is_failsafe():
    ci = CURSORINFO(cbSize=ctypes.sizeof(CURSORINFO))
    return bool(_user32.GetCursorInfo(ctypes.byref(ci)) and (ci.flags & 1)
                and 0 <= ci.ptScreenPos.x <= 2 and 0 <= ci.ptScreenPos.y <= 2)

def measure_pc_floor():
    noop = (INPUT * 2)()
    noop[0].u.mi.dwFlags = 0x0001
    noop[1].u.mi.dwFlags = 0x0001
    sz = ctypes.sizeof(INPUT)
    ev = Event()
    _winmm.timeBeginPeriod(1)
    try:
        for _ in range(5):
            _send_input(2, noop, sz)
            ev.wait(0.0001)
        t0, iters = perf_counter(), 0
        while iters < 120 and (iters < 10 or (perf_counter() - t0) < 0.18):
            _send_input(2, noop, sz)
            ev.wait(0.0001)
            iters += 1
        elapsed = perf_counter() - t0
    finally:
        _winmm.timeEndPeriod(1)
    return round(max(0.1, (elapsed / iters) * 1000.0), 2)

BASE_DIR = dirname(sys.executable if getattr(sys, "frozen", False) else abspath(__file__))
RES_DIR = getattr(sys, "_MEIPASS", BASE_DIR)
CFG_PATH = join(BASE_DIR, "config.json")
ICON = next((p for p in (join(RES_DIR, "ico.ico"), join(BASE_DIR, "ico.ico")) if exists(p)), None)

DEFAULTS = {
    "start_key": "F6", "stop_key": "F4", "opacity": 1.0,
    "interval": "100", "repeat": "1000", "on_top": False,
    "until_stopped": False, "button": "Left Click", "click_type": "Single Click",
    "jitter": False, "jitter_pct": 15, "failsafe": True, "bench_ms": None,
}
JIT_TIP = "Adds a random ±% variation to each click interval so the rhythm isn't robotic (helps avoid detection in games)."
FS_TIP = "Stops clicking instantly if the visible cursor hits the top-left corner (0, 0). Safe in FPS games with hidden cursor."
KEY_TIP = "Click and press any key to assign."
BENCH_TIP = "Measures your PC's real minimum timed delay (Win32 timer + SendInput overhead) without sending any real clicks."

# Paleta Flame Dark
BG, CARD, INPUT_BG, BORDER = "#18181B", "#222227", "#1A1A1F", "#34343C"
ACCENT, ACCENT_H = "#FF5722", "#E64A19"
BTN_BG, BTN_H = "#2E2E35", "#3C3C46"
RED, RED_H, GREEN, AMBER, MUTED = "#D32F2F", "#B71C1C", "#00E676", "#FFB74D", "#9A9AA6"
FONT = "Segoe UI"

def load_cfg():
    try:
        with open(CFG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            out = {**DEFAULTS, **data}
            b = out.get("bench_ms")
            if not isinstance(b, (int, float)) or isinstance(b, bool) or b <= 0:
                out["bench_ms"] = None
            return out
    except (FileNotFoundError, ValueError, OSError):
        pass
    return DEFAULTS.copy()

def save_cfg():
    with open(CFG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)

cfg = load_cfg()
if not exists(CFG_PATH):
    save_cfg()

class Tooltip:
    def __init__(self, widget, text):
        self.w, self.text, self.tip = widget, text, None
        for ev, fn in (("<Enter>", self.show), ("<Leave>", self.hide),
                       ("<ButtonPress>", self.hide), ("<Destroy>", self.hide)):
            widget.bind(ev, fn, add="+")

    def show(self, _=None):
        if self.tip:
            return
        x = self.w.winfo_rootx() + 10
        y = self.w.winfo_rooty() + self.w.winfo_height() + 6
        self.tip = tk.Toplevel(self.w)
        self.tip.overrideredirect(True)
        self.tip.attributes("-topmost", True)
        self.tip.geometry(f"+{x}+{y}")
        tk.Label(
            self.tip, text=self.text, bg="#111114", fg="#E4E4E7",
            font=(FONT, 9), justify="left", wraplength=240, padx=9, pady=6,
            highlightthickness=1, highlightbackground="#3F3F46", bd=0
        ).pack()

    def hide(self, _=None):
        if self.tip:
            self.tip.destroy()
            self.tip = None

class FlameDropdown(ctk.CTkFrame):
    def __init__(self, master, values, initial, command=None):
        super().__init__(master, fg_color="transparent", height=34)
        self.grid_propagate(False)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.values, self.val, self.command, self.pop = list(values), initial, command, None

        self.btn = ctk.CTkButton(
            self, text=f"{initial}   ▾", height=34, corner_radius=8,
            fg_color=INPUT_BG, hover_color=BTN_BG, border_width=1, border_color=BORDER,
            text_color="#FFFFFF", font=(FONT, 12), anchor="center", command=self.toggle
        )
        self.btn.grid(row=0, column=0, sticky="nsew")

    def get(self):
        return self.val

    def set(self, v):
        self.val = v
        self.btn.configure(text=f"{v}   ▾")

    def close(self, _=None):
        if self.pop:
            try:
                self.pop.destroy()
            except Exception:
                pass
            self.pop = None

    def toggle(self):
        if self.pop and self.pop.winfo_exists():
            self.close()
            return
        self.update_idletasks()
        w = self.winfo_width()
        x = self.winfo_rootx()
        y = self.winfo_rooty() + self.winfo_height() + 4

        pop = tk.Toplevel(self)
        pop.overrideredirect(True)
        pop.attributes("-topmost", True)
        pop.configure(bg=BORDER)
        pop.geometry(f"{w}x{len(self.values) * 34 + 10}+{x}+{y}")
        self.pop = pop

        box = ctk.CTkFrame(pop, fg_color=CARD, corner_radius=0, border_width=0)
        box.pack(fill="both", expand=True, padx=1, pady=1)

        for v in self.values:
            is_cur = (v == self.val)
            b = ctk.CTkButton(
                box, text=v, height=30, corner_radius=6,
                fg_color=BTN_BG if is_cur else "transparent", hover_color=BTN_H,
                text_color="#FFFFFF", font=(FONT, 12, "bold" if is_cur else "normal"),
                command=lambda val=v: self._pick(val)
            )
            b.pack(fill="x", padx=4, pady=2)

        pop.focus_force()
        pop.bind("<FocusOut>", self.close)
        pop.bind("<Escape>", self.close)

    def _pick(self, v):
        self.set(v)
        self.close()
        if self.command:
            self.command(v)

running, startable, bench_busy = True, True, False
delay, repeat, last_t, start_delay = 0.1, 1000, 0.0, 0.05
click_payload = CLICKS.get((cfg["button"], cfg["click_type"]), CLICKS[("Left Click", "Single Click")])
click_evt, stop_evt, hk_ready = Event(), Event(), Event()
stop_evt.set()
hk_tid = 0

def update_state_ui(active):
    lbl_stat.configure(text="● Clicking" if active else "● Idle", text_color=GREEN if active else MUTED)
    btn_stop.configure(fg_color=RED if active else BTN_BG, hover_color=RED_H if active else BTN_H)

def set_clicking(on, wait=0.05):
    global start_delay
    if on:
        if not click_evt.is_set():
            start_delay = wait
            stop_evt.clear()
            click_evt.set()
            try:
                app.after(0, update_state_ui, True)
            except Exception:
                pass
    elif click_evt.is_set() or not stop_evt.is_set():
        click_evt.clear()
        stop_evt.set()
        try:
            app.after(0, update_state_ui, False)
        except Exception:
            pass

def run_bench_async(on_done=None):
    global bench_busy
    if bench_busy:
        return
    bench_busy = True
    set_clicking(False)

    def worker():
        ms = measure_pc_floor()
        def finish():
            global bench_busy
            bench_busy = False
            cfg["bench_ms"] = ms
            save_cfg()
            validate()
            if on_done:
                on_done(ms)
        try:
            app.after(0, finish)
        except Exception:
            bench_busy = False

    Thread(target=worker, daemon=True).start()

def post_hk(msg_id):
    if hk_tid:
        _user32.PostThreadMessageW(hk_tid, msg_id, 0, 0)

def hotkey_loop():
    global hk_tid, last_t
    msg = MSG()
    _user32.PeekMessageW(ctypes.byref(msg), None, 0, 0, 0)
    hk_tid = _kernel32.GetCurrentThreadId()

    def unreg():
        _user32.UnregisterHotKey(None, 1)
        _user32.UnregisterHotKey(None, 2)

    def reg():
        unreg()
        v1, v2 = name_to_vk(cfg["start_key"]), name_to_vk(cfg["stop_key"])
        if v1:
            _user32.RegisterHotKey(None, 1, 0x4000, v1)
        if v2 and v2 != v1:
            _user32.RegisterHotKey(None, 2, 0x4000, v2)

    reg()
    hk_ready.set()
    while _user32.GetMessageW(ctypes.byref(msg), None, 0, 0) > 0:
        if msg.message == 0x0312:
            if msg.wParam == 2:
                set_clicking(False)
            elif msg.wParam == 1 and startable:
                now = perf_counter()
                if now - last_t >= 0.3:
                    last_t = now
                    set_clicking(not click_evt.is_set() if cfg["start_key"] == cfg["stop_key"] else True)
        elif msg.message == 0x8000:
            reg()
        elif msg.message == 0x8001:
            unreg()
    unreg()

def click_loop():
    wait_stop, is_stopped = stop_evt.wait, stop_evt.is_set
    send, check_fs = _send_input, is_failsafe
    while click_evt.wait() and running:
        if wait_stop(start_delay):
            continue
        d, rem, inf, fs = delay, repeat, cfg["until_stopped"], cfg["failsafe"]
        n, arr, sz, b_ops, b_n, b_arr = click_payload
        if d == 0:
            try:
                cnt = 0
                if inf:
                    while not is_stopped():
                        if fs:
                            if cnt == 0:
                                if check_fs():
                                    break
                                cnt = 200
                            cnt -= 1
                        send(b_n, b_arr, sz)
                else:
                    while rem >= b_ops and not is_stopped():
                        if fs:
                            if cnt == 0:
                                if check_fs():
                                    rem = 0
                                    break
                                cnt = 200
                            cnt -= 1
                        send(b_n, b_arr, sz)
                        rem -= b_ops
                    while rem > 0 and not is_stopped():
                        if fs and check_fs():
                            break
                        send(n, arr, sz)
                        rem -= 1
            finally:
                set_clicking(False)
        else:
            _winmm.timeBeginPeriod(1)
            try:
                j = (cfg["jitter_pct"] / 100.0) if cfg["jitter"] else 0.0
                lo, hi = 1.0 - j, 1.0 + j
                while not is_stopped():
                    if fs and check_fs():
                        break
                    send(n, arr, sz)
                    if not inf:
                        rem -= 1
                        if rem <= 0:
                            break
                    if wait_stop(d * uniform(lo, hi) if j else d):
                        break
            finally:
                _winmm.timeEndPeriod(1)
                set_clicking(False)

def open_settings():
    post_hk(0x8001)
    tmp_s, tmp_e = cfg["start_key"], cfg["stop_key"]
    cap_target = None

    pop = ctk.CTkToplevel(app, fg_color=BG)
    pop.title("Settings")
    pop.resizable(False, False)
    pop.transient(app)
    pop.attributes("-topmost", True)
    pop.grab_set()
    if ICON:
        pop.after(250, lambda: pop.winfo_exists() and set_sharp_icon(pop, ICON))

    box = ctk.CTkFrame(pop, fg_color=CARD, corner_radius=12, border_width=1, border_color=BORDER)
    box.pack(padx=16, pady=16, fill="both")

    # Teclas
    kf = ctk.CTkFrame(box, fg_color="transparent")
    kf.pack(padx=16, pady=(14, 10), fill="x")
    kf.grid_columnconfigure((0, 1), weight=1, uniform="k")

    ctk.CTkLabel(kf, text="Start Key", font=(FONT, 12, "bold"), text_color=MUTED).grid(row=0, column=0, pady=(0, 4))
    ctk.CTkLabel(kf, text="Stop Key", font=(FONT, 12, "bold"), text_color=MUTED).grid(row=0, column=1, pady=(0, 4))

    def start_cap(target):
        nonlocal cap_target
        b_k1.configure(text=tmp_s, border_color=BORDER)
        b_k2.configure(text=tmp_e, border_color=BORDER)
        cap_target = target
        (b_k1 if target == "s" else b_k2).configure(text="Press key...", border_color=ACCENT)
        pop.focus_set()

    b_k1 = ctk.CTkButton(kf, text=tmp_s, width=110, height=34, corner_radius=8, fg_color=INPUT_BG,
                         hover_color=BTN_BG, border_width=1, border_color=BORDER, font=(FONT, 13, "bold"),
                         command=lambda: start_cap("s"))
    b_k2 = ctk.CTkButton(kf, text=tmp_e, width=110, height=34, corner_radius=8, fg_color=INPUT_BG,
                         hover_color=BTN_BG, border_width=1, border_color=BORDER, font=(FONT, 13, "bold"),
                         command=lambda: start_cap("e"))
    b_k1.grid(row=1, column=0, padx=(0, 6))
    b_k2.grid(row=1, column=1, padx=(6, 0))
    Tooltip(b_k1, KEY_TIP)
    Tooltip(b_k2, KEY_TIP)

    ctk.CTkFrame(box, height=1, fg_color=BORDER).pack(fill="x", padx=16, pady=6)

    # Opacidad en vivo
    opa_hdr = ctk.CTkFrame(box, fg_color="transparent")
    opa_hdr.pack(fill="x", padx=16, pady=(4, 0))
    ctk.CTkLabel(opa_hdr, text="Opacity", font=(FONT, 12, "bold")).pack(side="left")
    lbl_opa = ctk.CTkLabel(opa_hdr, text=f"{int(cfg['opacity'] * 100)}%", font=(FONT, 12), text_color=MUTED)
    lbl_opa.pack(side="right")

    def on_opa(val):
        v = int(round(val))
        lbl_opa.configure(text=f"{v}%")
        app.attributes("-alpha", v / 100.0)

    sli_opa = ctk.CTkSlider(box, from_=10, to=100, number_of_steps=90, width=230,
                            progress_color=ACCENT, button_color=ACCENT, button_hover_color=ACCENT_H, command=on_opa)
    sli_opa.set(cfg["opacity"] * 100)
    sli_opa.pack(padx=16, pady=(6, 10))

    ctk.CTkFrame(box, height=1, fg_color=BORDER).pack(fill="x", padx=16, pady=6)

    # Jitter
    jit_var = ctk.BooleanVar(value=cfg["jitter"])
    jit_hdr = ctk.CTkFrame(box, fg_color="transparent")
    jit_hdr.pack(fill="x", padx=16, pady=(4, 0))
    sw_jit = ctk.CTkSwitch(jit_hdr, text="Random Jitter", variable=jit_var, font=(FONT, 12, "bold"),
                           progress_color=ACCENT, button_color="#FFFFFF")
    sw_jit.pack(side="left")
    lbl_jit = ctk.CTkLabel(jit_hdr, text=f"±{cfg['jitter_pct']}%", font=(FONT, 12), text_color=MUTED)
    lbl_jit.pack(side="right")

    sli_jit = ctk.CTkSlider(box, from_=1, to=50, number_of_steps=49, width=230,
                            progress_color=ACCENT, button_color=ACCENT, button_hover_color=ACCENT_H,
                            command=lambda v: lbl_jit.configure(text=f"±{int(round(v))}%"))
    sli_jit.set(cfg["jitter_pct"])
    sli_jit.pack(padx=16, pady=(8, 10))

    def sync_jit():
        on = jit_var.get()
        sli_jit.configure(state="normal" if on else "disabled",
                          progress_color=ACCENT if on else "#44444E",
                          button_color=ACCENT if on else "#555560")

    sw_jit.configure(command=sync_jit)
    sync_jit()
    Tooltip(sw_jit, JIT_TIP)
    Tooltip(sli_jit, JIT_TIP)

    ctk.CTkFrame(box, height=1, fg_color=BORDER).pack(fill="x", padx=16, pady=6)

    # Failsafe
    fs_var = ctk.BooleanVar(value=cfg["failsafe"])
    sw_fs = ctk.CTkSwitch(box, text="Corner Failsafe (0, 0)", variable=fs_var, font=(FONT, 12, "bold"),
                          progress_color=ACCENT, button_color="#FFFFFF")
    sw_fs.pack(anchor="w", padx=16, pady=(6, 10))
    Tooltip(sw_fs, FS_TIP)

    ctk.CTkFrame(box, height=1, fg_color=BORDER).pack(fill="x", padx=16, pady=6)

    # Benchmark límite PC
    bf = ctk.CTkFrame(box, fg_color="transparent")
    bf.pack(fill="x", padx=16, pady=(4, 14))
    b_txt = f"PC Limit: ≈ {cfg['bench_ms']:.1f} ms" if cfg["bench_ms"] else "PC Limit: Testing..."
    lbl_bench = ctk.CTkLabel(bf, text=b_txt, font=(FONT, 12, "bold"), text_color="#D4D4D8")
    lbl_bench.pack(side="left")

    def retest():
        lbl_bench.configure(text="PC Limit: Testing...", text_color=AMBER)
        btn_retest.configure(state="disabled", text="...")
        def done(ms):
            if pop.winfo_exists():
                lbl_bench.configure(text=f"PC Limit: ≈ {ms:.1f} ms", text_color="#D4D4D8")
                btn_retest.configure(state="normal", text="Re-test")
        run_bench_async(done)

    btn_retest = ctk.CTkButton(bf, text="Re-test", width=76, height=28, corner_radius=7, fg_color=BTN_BG,
                               hover_color=BTN_H, font=(FONT, 11, "bold"), command=retest)
    btn_retest.pack(side="right")
    if bench_busy:
        btn_retest.configure(state="disabled", text="...")
    Tooltip(lbl_bench, BENCH_TIP)
    Tooltip(btn_retest, BENCH_TIP)

    def close_cancel():
        app.attributes("-alpha", cfg["opacity"])
        pop.destroy()
        post_hk(0x8000)

    def save_and_close():
        cfg["start_key"], cfg["stop_key"] = tmp_s, tmp_e
        cfg["opacity"] = int(round(sli_opa.get())) / 100.0
        cfg["jitter"] = jit_var.get()
        cfg["jitter_pct"] = int(round(sli_jit.get()))
        cfg["failsafe"] = fs_var.get()
        save_cfg()
        app.attributes("-alpha", cfg["opacity"])
        btn_start.configure(text=f"Start  ({tmp_s})")
        btn_stop.configure(text=f"Stop  ({tmp_e})")
        pop.destroy()
        post_hk(0x8000)

    def on_tk_key(ev):
        nonlocal cap_target, tmp_s, tmp_e
        if not cap_target or ev.keycode in MOD_VKS:
            return
        name = vk_to_name(ev.keycode)
        if cap_target == "s":
            tmp_s = name
            b_k1.configure(text=name, border_color=BORDER)
        else:
            tmp_e = name
            b_k2.configure(text=name, border_color=BORDER)
        cap_target = None
        return "break"

    pop.bind("<KeyPress>", on_tk_key)
    pop.protocol("WM_DELETE_WINDOW", close_cancel)

    ctk.CTkButton(pop, text="Save", height=36, corner_radius=8, fg_color=ACCENT, hover_color=ACCENT_H,
                  font=(FONT, 13, "bold"), command=save_and_close).pack(padx=16, pady=(0, 16), fill="x")

    pop.update_idletasks()
    px = app.winfo_x() + (app.winfo_width() - pop.winfo_width()) // 2
    py = app.winfo_y() + (app.winfo_height() - pop.winfo_height()) // 2
    pop.geometry(f"+{max(0, px)}+{max(0, py)}")

# Interfaz principal
ctk.set_appearance_mode("dark")
app = ctk.CTk(fg_color=BG)
app.title("Flame Auto Clicker")
app.resizable(False, False)
app.attributes("-alpha", cfg["opacity"])
app.attributes("-topmost", cfg["on_top"])
if ICON:
    set_sharp_icon(app, ICON)
    app.after(250, lambda: set_sharp_icon(app, ICON))

# Cabecera
hdr = ctk.CTkFrame(app, fg_color="transparent")
hdr.pack(fill="x", padx=20, pady=(16, 10))
ctk.CTkLabel(hdr, text="Flame Auto Clicker", font=(FONT, 22, "bold"), text_color="#FFFFFF").pack(side="left")
lbl_stat = ctk.CTkLabel(hdr, text="● Idle", font=(FONT, 12, "bold"), text_color=MUTED)
lbl_stat.pack(side="right", pady=(4, 0))

# Tarjeta principal (2 columnas simétricas)
card = ctk.CTkFrame(app, fg_color=CARD, corner_radius=12, border_width=1, border_color=BORDER)
card.pack(fill="x", padx=20, pady=(0, 14))
card.grid_columnconfigure((0, 1), weight=1, uniform="col")

ctk.CTkLabel(card, text="Click Interval (ms)", font=(FONT, 12, "bold"), text_color=MUTED).grid(row=0, column=0, sticky="w", padx=(16, 8), pady=(14, 4))
ctk.CTkLabel(card, text="Repeat × Times", font=(FONT, 12, "bold"), text_color=MUTED).grid(row=0, column=1, sticky="w", padx=(8, 16), pady=(14, 4))

int_var = ctk.StringVar(value=str(cfg["interval"]))
rep_var = ctk.StringVar(value=str(cfg["repeat"]))

e_int = ctk.CTkEntry(card, textvariable=int_var, width=195, height=36, corner_radius=8, justify="center",
                     fg_color=INPUT_BG, border_color=BORDER, border_width=1, font=(FONT, 14))
e_rep = ctk.CTkEntry(card, textvariable=rep_var, width=195, height=36, corner_radius=8, justify="center",
                     fg_color=INPUT_BG, border_color=BORDER, border_width=1, font=(FONT, 14))
e_int.grid(row=1, column=0, padx=(16, 8), sticky="ew")
e_rep.grid(row=1, column=1, padx=(8, 16), sticky="ew")
Tooltip(e_int, "Delay between clicks in milliseconds (e.g. 0, 50, 100, 500, 1000).")

lbl_cps = ctk.CTkLabel(card, text="", font=(FONT, 11), text_color=MUTED)
lbl_cps.grid(row=2, column=0, columnspan=2, sticky="w", padx=(18, 16), pady=(2, 8))

ontop_var = ctk.BooleanVar(value=cfg["on_top"])
cb_var = ctk.BooleanVar(value=cfg["until_stopped"])

sw_ontop = ctk.CTkSwitch(card, text="Always On Top", variable=ontop_var, font=(FONT, 12),
                         progress_color=ACCENT, button_color="#FFFFFF",
                         command=lambda: (cfg.__setitem__("on_top", ontop_var.get()), app.attributes("-topmost", cfg["on_top"])))
sw_cb = ctk.CTkSwitch(card, text="Click until stopped", variable=cb_var, font=(FONT, 12),
                      progress_color=ACCENT, button_color="#FFFFFF")
sw_ontop.grid(row=3, column=0, sticky="w", padx=(16, 8), pady=(2, 12))
sw_cb.grid(row=3, column=1, sticky="w", padx=(8, 16), pady=(2, 12))

ctk.CTkFrame(card, height=1, fg_color=BORDER).grid(row=4, column=0, columnspan=2, sticky="ew", padx=16, pady=(0, 12))

def sync_menus(_=None):
    global click_payload
    cfg["button"], cfg["click_type"] = opt_btn.get(), opt_type.get()
    click_payload = CLICKS[(cfg["button"], cfg["click_type"])]

opt_btn = FlameDropdown(card, values=["Left Click", "Right Click"], initial=cfg["button"], command=sync_menus)
opt_type = FlameDropdown(card, values=["Single Click", "Double Click"], initial=cfg["click_type"], command=sync_menus)
opt_btn.grid(row=5, column=0, sticky="ew", padx=(16, 8), pady=(0, 16))
opt_type.grid(row=5, column=1, sticky="ew", padx=(8, 16), pady=(0, 16))

# Botones de acción
acts = ctk.CTkFrame(app, fg_color="transparent")
acts.pack(fill="x", padx=20, pady=(0, 10))
acts.grid_columnconfigure((0, 1), weight=1, uniform="act")

btn_start = ctk.CTkButton(acts, text=f"Start  ({cfg['start_key']})", height=42, corner_radius=9,
                          fg_color=ACCENT, hover_color=ACCENT_H, font=(FONT, 14, "bold"),
                          command=lambda: startable and set_clicking(True, 0.3))
btn_stop = ctk.CTkButton(acts, text=f"Stop  ({cfg['stop_key']})", height=42, corner_radius=9,
                         fg_color=BTN_BG, hover_color=BTN_H, font=(FONT, 14, "bold"),
                         command=lambda: set_clicking(False))
btn_start.grid(row=0, column=0, sticky="ew", padx=(0, 6))
btn_stop.grid(row=0, column=1, sticky="ew", padx=(6, 0))

ctk.CTkButton(app, text="Settings", height=34, corner_radius=8, fg_color="transparent",
              hover_color=CARD, border_width=1, border_color=BORDER, text_color="#D4D4D8",
              font=(FONT, 12, "bold"), command=open_settings).pack(fill="x", padx=20, pady=(0, 18))

def validate(*_):
    global startable, delay, repeat
    raw_d, raw_r, cb = int_var.get(), rep_var.get(), cb_var.get()
    cfg["interval"], cfg["repeat"], cfg["until_stopped"] = raw_d, raw_r, cb

    try:
        d_val = float(raw_d)
        ok_d = d_val >= 0 and "-" not in raw_d and " " not in raw_d
    except ValueError:
        ok_d = False

    e_int.configure(border_color=BORDER if ok_d else "#EF5350")
    if ok_d:
        delay = d_val / 1000.0
        bench = cfg["bench_ms"]
        if d_val == 0:
            lbl_cps.configure(text="Speed: Max CPS (0 ms batch mode)", text_color="#FF8A65")
        elif bench and d_val < bench:
            real_cps = int(round(1000.0 / bench))
            lbl_cps.configure(text=f"⚠ PC limit ~{bench:.1f} ms (≈ {real_cps} CPS) · Use 0 for Max", text_color=AMBER)
        else:
            cps = 1000.0 / d_val
            lbl_cps.configure(text=f"Speed: ≈ {cps:.1f} CPS" if cps < 100 else f"Speed: ≈ {int(round(cps))} CPS", text_color=MUTED)
    else:
        lbl_cps.configure(text="Invalid interval", text_color="#EF5350")

    if cb:
        ok_r = True
        e_rep.configure(state="disabled", fg_color="#16161A", text_color="#5A5A64", border_color="#26262C")
    else:
        try:
            ok_r = int(raw_r) > 0 and "-" not in raw_r and " " not in raw_r
        except ValueError:
            ok_r = False
        e_rep.configure(state="normal", fg_color=INPUT_BG, text_color="#FFFFFF", border_color=BORDER if ok_r else "#EF5350")
        if ok_r:
            repeat = int(raw_r)

    new_ok = ok_d and ok_r
    if new_ok != startable:
        startable = new_ok
        btn_start.configure(state="normal" if startable else "disabled",
                            fg_color=ACCENT if startable else "#4A2B22",
                            text_color="#FFFFFF" if startable else "#9E8A84")

int_var.trace_add("write", validate)
rep_var.trace_add("write", validate)
sw_cb.configure(command=validate)
validate()

def on_close():
    global running
    running = False
    post_hk(0x0012)
    stop_evt.set()
    click_evt.set()
    save_cfg()
    _kernel32.CloseHandle(_mutex)
    app.destroy()

app.protocol("WM_DELETE_WINDOW", on_close)

Thread(target=hotkey_loop, daemon=True).start()
hk_ready.wait()
Thread(target=click_loop, daemon=True).start()
if cfg["bench_ms"] is None:
    run_bench_async()

app.mainloop()
