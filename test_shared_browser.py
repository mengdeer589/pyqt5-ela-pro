"""
Test: Chrome --app multi-window shared Browser process feasibility
"""
import subprocess
import sys
import time
import json
import os
import ctypes
import urllib.request
import tempfile
import shutil

try:
    import win32gui, win32con, win32process
except ImportError:
    print("Need pywin32: uv pip install pywin32")
    sys.exit(1)

CHROME_PATH = os.environ.get("ELA_BROWSER_PATH", r"Supermium\chrome.exe")
DEBUG_PORT = int(os.environ.get("TEST_DEBUG_PORT", "9777"))
PROFILE_DIR = os.path.join(tempfile.gettempdir(), "pyqt5_ela_test_shared")

TEST_URLS = [
    ("https://www.bilibili.com", "哔哩哔哩"),
    ("https://www.baidu.com", "百度"),
    ("https://www.qq.com", "腾讯"),
]

os.makedirs(PROFILE_DIR, exist_ok=True)

def cdp_targets():
    try:
        resp = urllib.request.urlopen(f"http://127.0.0.1:{DEBUG_PORT}/json", timeout=3)
        return json.loads(resp.read())
    except Exception:
        return []

def find_hwnd(title):
    results = []
    def cb(hwnd, _):
        try:
            if win32gui.IsWindow(hwnd) and win32gui.IsWindowVisible(hwnd):
                if title in win32gui.GetWindowText(hwnd):
                    results.append(hwnd)
        except Exception:
            pass
        return True
    win32gui.EnumWindows(cb, None)
    return results[0] if results else 0

processes = []

# --- Test 1: Launch first --app ---
print(f"Chrome: {CHROME_PATH}")
print(f"Profile: {PROFILE_DIR}")
print(f"Debug Port: {DEBUG_PORT}")
print()
print("=== Test 1: First --app window ===")

common_args = [
    f"--user-data-dir={PROFILE_DIR}",
    f"--remote-debugging-port={DEBUG_PORT}",
    "--no-first-run", "--incognito",
]

p1 = subprocess.Popen(
    [str(CHROME_PATH), f"--app={TEST_URLS[0][0]}"] + common_args,
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
)
processes.append(p1)
print(f"Launched PID={p1.pid}")
time.sleep(5)
print(f"Status: {'running' if p1.poll() is None else f'exited(code={p1.returncode})'}")

# Find hwnd
hwnd1 = 0
for i in range(10):
    hwnd1 = find_hwnd(TEST_URLS[0][1])
    if hwnd1:
        break
    time.sleep(0.5)
if hwnd1:
    _, pid1 = win32process.GetWindowThreadProcessId(hwnd1)
    print(f"HWND: 0x{hwnd1:X} PID={pid1} Class={win32gui.GetClassName(hwnd1)}")
else:
    print("Window NOT found")

# CDP
targets = cdp_targets()
pages = [t for t in targets if t.get("type") == "page"]
print(f"CDP page targets: {len(pages)}")

# --- Test 2: Launch second --app (same debug_port) ---
print()
print("=== Test 2: Second --app window (same debug port) ===")

p2 = subprocess.Popen(
    [str(CHROME_PATH), f"--app={TEST_URLS[1][0]}"] + common_args,
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
)
processes.append(p2)
print(f"Launched PID={p2.pid}")
time.sleep(5)
p2_running = p2.poll() is None
print(f"Status: {'running' if p2_running else f'exited(code={p2.returncode})'}")

# Find hwnd
hwnd2 = 0
for i in range(10):
    hwnd2 = find_hwnd(TEST_URLS[1][1])
    if hwnd2:
        break
    time.sleep(0.5)
if hwnd2:
    _, pid2 = win32process.GetWindowThreadProcessId(hwnd2)
    print(f"HWND: 0x{hwnd2:X} PID={pid2} Class={win32gui.GetClassName(hwnd2)}")
    # Check if same process
    if hwnd1:
        _, pid1 = win32process.GetWindowThreadProcessId(hwnd1)
        same = (pid1 == pid2)
        print(f"Same Browser PID as Window1? {same} (Window1 PID={pid1}, Window2 PID={pid2})")
else:
    print("Window NOT found")

# CDP
targets = cdp_targets()
pages = [t for t in targets if t.get("type") == "page"]
print(f"CDP page targets: {len(pages)}")
for t in pages[-2:]:
    print(f"  - {t.get('title','?')[:30]:30s} id={t.get('id','?')[:20]}...")

# --- Test 3: Launch third --app ---
print()
print("=== Test 3: Third --app window ===")

p3 = subprocess.Popen(
    [str(CHROME_PATH), f"--app={TEST_URLS[2][0]}"] + common_args,
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
)
processes.append(p3)
print(f"Launched PID={p3.pid}")
time.sleep(5)
print(f"Status: {'running' if p3.poll() is None else f'exited(code={p3.returncode})'}")

hwnd3 = 0
for i in range(10):
    hwnd3 = find_hwnd(TEST_URLS[2][1])
    if hwnd3:
        break
    time.sleep(0.5)
if hwnd3:
    print(f"HWND: 0x{hwnd3:X}")
else:
    print("Window NOT found")

targets = cdp_targets()
pages = [t for t in targets if t.get("type") == "page"]
print(f"CDP page targets: {len(pages)}")

# --- Summary ---
print()
print("=" * 60)
print("SUMMARY")
print("=" * 60)
print(f"Windows created: 3")
print(f"Processes that exited (routed): {sum(1 for p in processes if p.poll() is not None)}")
print(f"Processes still running: {sum(1 for p in processes if p.poll() is None)}")

if hwnd1 and hwnd2 and hwnd3:
    _, pid1 = win32process.GetWindowThreadProcessId(hwnd1)
    _, pid2 = win32process.GetWindowThreadProcessId(hwnd2)
    _, pid3 = win32process.GetWindowThreadProcessId(hwnd3)
    all_same = (pid1 == pid2 == pid3)
    print(f"All windows share same PID? {all_same} (PIDs: {pid1}, {pid2}, {pid3})")

    if all_same:
        print()
        print("SUCCESS: All --app windows share one Browser PID")
        print("Multi-window with shared Browser process is FEASIBLE")
    else:
        print()
        print("FAILED: Windows have different Browser PIDs")
else:
    print("Could not verify (some windows not found)")

# Cleanup
print()
print("Cleanup...")
for p in processes:
    if p.poll() is None:
        p.terminate()
        try:
            p.wait(timeout=3)
        except subprocess.TimeoutExpired:
            p.kill()

time.sleep(2)
try:
    shutil.rmtree(PROFILE_DIR)
    print(f"Deleted {PROFILE_DIR}")
except PermissionError:
    print(f"Could not delete {PROFILE_DIR}")

print("Done")
