"""
对比多 --app 窗口在共享 Browser 进程 vs 独立进程方案下的内存占用。

测试方法：
  A) 独立进程: 每窗口不同 --user-data-dir，不同 --debug-port
  B) 共享进程: 同一 --user-data-dir，同一 --debug-port（窗口路由到首个 Browser 进程）
"""

import subprocess
import sys
import time
import os
import json
import ctypes
import shutil
import tempfile
import urllib.request

try:
    import psutil
except ImportError:
    print("需要 psutil: uv pip install psutil")
    sys.exit(1)

try:
    import win32gui
    import win32process
except ImportError:
    print("需要 pywin32: uv pip install pywin32")
    sys.exit(1)


CHROME_PATH = os.environ.get("ELA_BROWSER_PATH", r"Supermium\chrome.exe")
BASE_PROFILE = os.path.join(tempfile.gettempdir(), "pyqt5_ela_mem_test")
TEST_URLS = [
    "https://www.bilibili.com",
    "https://www.baidu.com",
    "https://www.qq.com",
]

# ── helpers ──────────────────────────────────────────

def _kill_all_chrome():
    for p in psutil.process_iter():
        try:
            if "chrome" in p.name().lower():
                p.kill()
        except Exception:
            pass
    time.sleep(2)


def _get_chrome_memory() -> tuple[int, int, int]:
    """返回 (total_mb, process_count, details)"""
    total = 0
    count = 0
    details = []
    for p in psutil.process_iter():
        try:
            if "chrome" in p.name().lower():
                mem = p.memory_info().rss / (1024 * 1024)
                total += mem
                count += 1
                details.append((p.pid, p.name(), round(mem, 1)))
        except Exception:
            pass
    return round(total, 1), count, details


def _launch_app(port: int, profile: str, url: str) -> subprocess.Popen:
    args = [
        str(CHROME_PATH), f"--app={url}",
        "--incognito", "--no-first-run", "--disable-sync",
        f"--user-data-dir={profile}",
        f"--remote-debugging-port={port}",
        "--remote-allow-origins=*",
        "--window-position=-9999,-9999",
    ]
    return subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def _wait_for_window(cls_name: str, count: int, timeout: float = 30):
    start = time.time()
    while time.time() - start < timeout:
        found = []
        def cb(hwnd, _):
            try:
                if win32gui.IsWindow(hwnd) and win32gui.IsWindowVisible(hwnd):
                    if win32gui.GetClassName(hwnd) == cls_name and win32gui.GetWindowText(hwnd):
                        found.append(hwnd)
            except Exception:
                pass
            return True
        win32gui.EnumWindows(cb, None)
        if len(found) >= count:
            return
        time.sleep(0.5)


def _cleanup_profiles():
    for item in os.listdir(BASE_PROFILE) if os.path.isdir(BASE_PROFILE) else []:
        path = os.path.join(BASE_PROFILE, item)
        try:
            if os.path.isdir(path):
                shutil.rmtree(path)
        except Exception:
            pass


# ── Test A: 独立进程 ─────────────────────────────────

print("=" * 60)
print("Test A: 独立进程（每窗口不同 profile + 不同 port）")
print("=" * 60)

_kill_all_chrome()
_cleanup_profiles()

procs_a = []
for i, url in enumerate(TEST_URLS):
    profile = os.path.join(BASE_PROFILE, f"independent_{i}")
    os.makedirs(profile, exist_ok=True)
    p = _launch_app(port=9800 + i, profile=profile, url=url)
    procs_a.append(p)
    time.sleep(3)

_wait_for_window("Chrome_WidgetWin_1", 3)
time.sleep(5)  # 等页面加载
mem_a, count_a, details_a = _get_chrome_memory()

print(f"Memory: {mem_a} MB")
print(f"Processes: {count_a}")
for pid, name, mb in sorted(details_a, key=lambda x: -x[2])[:5]:
    print(f"  PID={pid}: {mb:6.1f} MB  {name}")

print("(等 5 秒稳定...)")
time.sleep(5)
mem_a, count_a, _ = _get_chrome_memory()
print(f"Stable memory: {mem_a} MB, processes: {count_a}")

# ── Cleanup A ────────────────────────────────────────

_kill_all_chrome()
time.sleep(2)

# ── Test B: 共享进程 ─────────────────────────────────

print()
print("=" * 60)
print("Test B: 共享进程（同一 profile + 同一 port）")
print("=" * 60)

_cleanup_profiles()
profile_shared = os.path.join(BASE_PROFILE, "shared")
os.makedirs(profile_shared, exist_ok=True)

procs_b = []
for i, url in enumerate(TEST_URLS):
    p = _launch_app(port=9900, profile=profile_shared, url=url)
    procs_b.append(p)
    time.sleep(3)

_wait_for_window("Chrome_WidgetWin_1", 3)
time.sleep(5)
mem_b, count_b, details_b = _get_chrome_memory()

print(f"Memory: {mem_b} MB")
print(f"Processes: {count_b}")
for pid, name, mb in sorted(details_b, key=lambda x: -x[2])[:5]:
    print(f"  PID={pid}: {mb:6.1f} MB  {name}")

time.sleep(5)
mem_b, count_b, _ = _get_chrome_memory()
print(f"Stable memory: {mem_b} MB, processes: {count_b}")

# ── Summary ──────────────────────────────────────────

print()
print("=" * 60)
print("对比结果")
print("=" * 60)
print(f"{'指标':<20} {'独立进程 (A)':<20} {'共享进程 (B)':<20} {'节省':<15}")
print(f"{'内存 (MB)':<20} {mem_a:<20.1f} {mem_b:<20.1f} {mem_a - mem_b:<15.1f}")
print(f"{'进程数':<20} {count_a:<20} {count_b:<20} {count_a - count_b:<15}")
if mem_a > 0:
    print(f"{'节省比例':<20} {'':<20} {'':<20} {(mem_a - mem_b) / mem_a * 100:<14.1f}%")

# ── Cleanup ──────────────────────────────────────────

_kill_all_chrome()
_cleanup_profiles()
print("\nDone")
