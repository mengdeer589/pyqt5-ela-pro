"""
测试 Chrome 多 --app 窗口共享 Browser 进程可行性。

通过同一 --remote-debugging-port 启动多个 --app，
观察 Chrome 是否将新窗口路由到已有 Browser 进程。
"""

import subprocess
import time
import json
import urllib.request
import os
import shutil

CHROME_PATH = os.environ.get(
    "ELA_BROWSER_PATH",
    r"Supermium\chrome.exe",
)
PROFILE_DIR = os.path.join(os.path.dirname(__file__), ".test_shared_profile")
DEBUG_PORT = 9555
TEST_URLS = [
    "https://www.bilibili.com",
    "https://www.baidu.com",
    "https://www.qq.com",
]


def get_cdp_targets():
    try:
        with urllib.request.urlopen(
            f"http://127.0.0.1:{DEBUG_PORT}/json", timeout=3
        ) as resp:
            return json.loads(resp.read())
    except Exception as e:
        print(f"  [CDP] 查询失败: {e}")
        return []


def launch_app(url, label):
    print(f"\n{'='*60}")
    print(f"[{label}] 启动 --app={url}")
    print(f"{'='*60}")

    args = [
        str(CHROME_PATH),
        f"--app={url}",
        f"--user-data-dir={PROFILE_DIR}",
        f"--remote-debugging-port={DEBUG_PORT}",
        "--no-first-run",
        "--incognito",
    ]

    proc = subprocess.Popen(
        args,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    print(f"  进程 PID: {proc.pid}")

    time.sleep(3)
    running = proc.poll() is None
    print(f"  进程状态: {'运行中' if running else f'已退出 (code={proc.returncode})'}")

    targets = get_cdp_targets()
    print(f"  CDP targets: {len(targets)}")
    for t in targets:
        title = t.get("title", "")[:30]
        t_url = t.get("url", "")[:50]
        print(f"    - {title:30s} {t_url}")

    return proc


def main():
    if not os.path.isdir(PROFILE_DIR):
        os.makedirs(PROFILE_DIR, exist_ok=True)

    print(f"测试模式: 同一 debug_port={DEBUG_PORT} 启动多个 --app 窗口")
    print(f"Chrome: {CHROME_PATH}\n")

    processes = []
    try:
        for i, url in enumerate(TEST_URLS, 1):
            proc = launch_app(url, f"窗口{i}")
            processes.append(proc)

        print(f"\n{'='*60}")
        print("最终分析")
        print(f"{'='*60}")
        print(f"启动窗口数: {len(TEST_URLS)}")
        print(f"仍在运行的进程: {sum(1 for p in processes if p.poll() is None)}")
        print(f"已退出的进程: {sum(1 for p in processes if p.poll() is not None)}")

        targets = get_cdp_targets()
        print(f"\nCDP target 数量: {len(targets)}")

        exited = [p for p in processes if p.poll() is not None]
        if len(exited) >= len(processes) - 1:
            print("\nTEST PASSED: --app 窗口被路由到同一 Browser 进程，方案可行")
            print("后续窗口启动后会立即退出，窗口由首个进程管理。")
        else:
            print("\nTEST FAILED: 每个 --app 启动了独立进程")
    except KeyboardInterrupt:
        print("\n用户中断")
    finally:
        print("\n清理所有 Chrome 进程...")
        for p in processes:
            if p.poll() is None:
                p.terminate()
                try:
                    p.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    p.kill()
        if os.path.isdir(PROFILE_DIR):
            try:
                shutil.rmtree(PROFILE_DIR)
            except PermissionError:
                pass


if __name__ == "__main__":
    main()
