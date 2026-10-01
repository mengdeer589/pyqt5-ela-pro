"""划词助手 Win32 原生层（``pyqt5_ela_pro.selection_assistant``）。

- :class:`ElaMouseMonitor`：**轮询式**全局鼠标监视（``GetAsyncKeyState`` +
  ``GetCursorPos``，QTimer 在主线程，默认 15ms 一次）。刻意不使用
  ``WH_MOUSE_LL`` 全局钩子：钩子回调运行在独立线程且需要抢 GIL，一旦回调
  阻塞会拖住整个系统的鼠标输入（表现为机器卡死），还受杀软 / Win7 钩子
  超时影响；
- :func:`send_copy`：``SendInput`` 向当前前台窗口发送 Ctrl+C；
- :func:`to_logical_pos`：物理像素 → Qt 逻辑坐标（多屏 DPI 尽力而为）；
- :func:`window_pid_at` / :func:`foreground_pid`：窗口归属进程查询。

非 Windows 环境下 :meth:`ElaMouseMonitor.start` 抛 ``RuntimeError``，
由 :class:`~pyqt5_ela_pro.selection_assistant.assistant.ElaSelectionAssistant`
转换为 ``errorOccurred`` 信号。

命名规范与库内一致（``camelCase``）。
"""

from __future__ import annotations

import ctypes
import sys
import warnings
from ctypes import wintypes
from typing import Optional

from PyQt5.QtCore import QObject, QTimer, pyqtSignal

from .._internal import to_logical_pos  # noqa: F401  （重导出，实现见 _internal）

_IS_WINDOWS = sys.platform == "win32"

#: 轮询回调里已告警过的异常（同一异常只提示一次，避免每 15ms 刷屏）
_warned_poll_errors: set = set()


def safe_connect(obj, signal_name: str, slot, label: str = "") -> None:
    """连接一个**受保护**的槽：槽内异常被捕获并告警，不会杀掉进程。

    为什么要这个helper：PyQt5 里，槽（slot）抛出的 Python 异常**不会**
    传播给 ``signal.emit()`` 的调用方 —— PyQt5 打印 traceback 后直接
    ``abort()``（0xC0000409）。所以在 emit 外面包 ``try/except`` 是无效的，
    唯一的防线就在槽本身。

    划词助手的槽会走 ``capture()`` -> Win32 ``SendInput``，宿主一旦抛异常，
    整个应用连同助手一起消失。因此库内部一律用本helper连接。

    :param obj: 拥有信号的对象
    :param signal_name: 信号名
    :param slot: 槽（可调用）
    :param label: 告警标签
    """
    name = label or getattr(slot, "__name__", repr(slot))

    def _guarded(*args):
        try:
            return slot(*args)
        except Exception as exc:  # noqa: BLE001 - 槽内异常绝不能逃逸
            _warn_once("划词助手槽 %s 抛出异常，已忽略：" % name, exc)
            return None

    _guarded.__name__ = "guarded_%s" % name
    getattr(obj, signal_name).connect(_guarded)


def _warn_once(prefix: str, exc: BaseException) -> None:
    """同一个异常只提示一次（按类型去重），避免 15ms 一次地刷屏。"""
    key = type(exc)
    if key in _warned_poll_errors:
        return
    _warned_poll_errors.add(key)
    warnings.warn(f"{prefix} {type(exc).__name__}: {exc}", RuntimeWarning, stacklevel=3)


#: 默认轮询间隔（毫秒）
_DEFAULT_POLL_MS = 15
#: 虚拟键
_VK_LBUTTON = 0x01
_VK_RBUTTON = 0x02
_VK_MBUTTON = 0x04

_INPUT_KEYBOARD = 1
_KEYEVENTF_KEYUP = 0x0002
_VK_CONTROL = 0x11
_VK_C = 0x43

_ULONG_PTR = ctypes.c_uint64 if ctypes.sizeof(ctypes.c_void_p) == 8 else ctypes.c_uint32


class _POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]


class _KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", wintypes.WORD),
        ("wScan", wintypes.WORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", _ULONG_PTR),
    ]


class _MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", wintypes.LONG),
        ("dy", wintypes.LONG),
        ("mouseData", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", _ULONG_PTR),
    ]


class _HARDWAREINPUT(ctypes.Structure):
    _fields_ = [
        ("uMsg", wintypes.DWORD),
        ("wParamL", wintypes.WORD),
        ("wParamH", wintypes.WORD),
    ]


class _INPUTUNION(ctypes.Union):
    _fields_ = [("mi", _MOUSEINPUT), ("ki", _KEYBDINPUT), ("hi", _HARDWAREINPUT)]


class _INPUT(ctypes.Structure):
    _anonymous_ = ("u",)
    _fields_ = [("type", wintypes.DWORD), ("u", _INPUTUNION)]


if _IS_WINDOWS:  # pragma: no cover - 平台分支
    _user32 = ctypes.WinDLL("user32", use_last_error=True)
    _user32.SendInput.argtypes = [
        wintypes.UINT,
        ctypes.POINTER(_INPUT),
        ctypes.c_int,
    ]
    _user32.SendInput.restype = wintypes.UINT
    _user32.GetAsyncKeyState.argtypes = [ctypes.c_int]
    _user32.GetAsyncKeyState.restype = ctypes.c_short
    _user32.GetCursorPos.argtypes = [ctypes.POINTER(_POINT)]
    _user32.GetCursorPos.restype = wintypes.BOOL
    _user32.WindowFromPoint.argtypes = [_POINT]
    _user32.WindowFromPoint.restype = wintypes.HWND
    _user32.GetWindowThreadProcessId.argtypes = [
        wintypes.HWND,
        ctypes.POINTER(wintypes.DWORD),
    ]
    _user32.GetWindowThreadProcessId.restype = wintypes.DWORD
    _user32.GetForegroundWindow.restype = wintypes.HWND


def send_copy() -> None:
    """向当前前台窗口发送 Ctrl+C（``SendInput``，无 pywin32 依赖）。"""
    if not _IS_WINDOWS:  # pragma: no cover - 平台分支
        raise RuntimeError("send_copy 仅支持 Windows")

    def _key(vk: int, flags: int = 0) -> None:
        item = _INPUT(type=_INPUT_KEYBOARD)
        item.ki = _KEYBDINPUT(wVk=vk, wScan=0, dwFlags=flags, time=0, dwExtraInfo=0)
        _user32.SendInput(1, ctypes.byref(item), ctypes.sizeof(_INPUT))

    _key(_VK_CONTROL)
    _key(_VK_C)
    _key(_VK_C, _KEYEVENTF_KEYUP)
    _key(_VK_CONTROL, _KEYEVENTF_KEYUP)


def window_pid_at(x: int, y: int) -> int:
    """获取指定物理坐标处窗口的进程 id（无窗口返回 0）。"""
    if not _IS_WINDOWS:  # pragma: no cover - 平台分支
        return 0
    hwnd = _user32.WindowFromPoint(_POINT(int(x), int(y)))
    if not hwnd:
        return 0
    pid = wintypes.DWORD(0)
    _user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    return int(pid.value)


def foreground_pid() -> int:
    """获取前台窗口的进程 id（无窗口返回 0）。"""
    if not _IS_WINDOWS:  # pragma: no cover - 平台分支
        return 0
    hwnd = _user32.GetForegroundWindow()
    if not hwnd:
        return 0
    pid = wintypes.DWORD(0)
    _user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    return int(pid.value)


class ElaMouseMonitor(QObject):
    """轮询式全局鼠标监视（主线程 QTimer，无全局钩子、无额外线程）。

    信号参数中的坐标一律为 Win32 物理像素 ``(x, y)``，宿主 / 组件负责换算
    为 Qt 逻辑坐标（见 :func:`to_logical_pos`）。

    已知限制：单次按下 / 抬起间隔短于轮询间隔（默认 15ms）的极快点击可能
    被漏检；滚轮事件无法轮询，``wheelScrolled`` 仅为契约保留（真实监视不会
    发射）。

    :param parent: 父对象
    :param pollMs: 轮询间隔毫秒数
    """

    #: 左键按下
    leftPressed = pyqtSignal(object)
    #: 左键抬起（参数：按下点、抬起点）
    leftReleased = pyqtSignal(object, object)
    #: 右键 / 中键按下
    otherPressed = pyqtSignal(object)
    #: 滚轮滚动（契约保留；轮询实现不发射）
    wheelScrolled = pyqtSignal()

    def __init__(
        self,
        parent: Optional[QObject] = None,
        pollMs: int = _DEFAULT_POLL_MS,
    ) -> None:
        super().__init__(parent)
        self._down: Optional[tuple] = None
        self._left_last = False
        self._right_last = False
        self._middle_last = False
        self._timer = QTimer(self)
        self._timer.setInterval(max(1, int(pollMs)))
        self._timer.timeout.connect(self._poll)

    # -- 生命周期 ----------------------------------------------------------

    def start(self) -> bool:
        """开始轮询；失败抛 ``RuntimeError``（非 Windows）。"""
        if not _IS_WINDOWS:
            raise RuntimeError("划词助手仅支持 Windows")
        if self._timer.isActive():
            return True
        self._reset_state()
        self._timer.start()
        return True

    def stop(self) -> None:
        """停止轮询（幂等）。"""
        self._timer.stop()
        self._reset_state()

    def isRunning(self) -> bool:
        """是否正在轮询。"""
        return self._timer.isActive()

    def setPollMs(self, ms: int) -> None:
        """设置轮询间隔毫秒数。"""
        self._timer.setInterval(max(1, int(ms)))

    def pollMs(self) -> int:
        """轮询间隔毫秒数。"""
        return self._timer.interval()

    # -- 轮询 --------------------------------------------------------------

    def _reset_state(self) -> None:
        self._down = None
        self._left_last = False
        self._right_last = False
        self._middle_last = False

    def _poll(self) -> None:
        """15ms 轮询：检测按下 / 抬起边沿并转发给宿主。

        保护范围说明（重要）：这个 ``try/except`` 只能兜住 **Win32 采样调用**
        （``_cursor_pos`` / ``_key_down``）自身抛出的异常。它**兜不住**信号槽
        里宿主的异常 —— PyQt5 中槽抛异常会直接 ``abort()``（0xC0000409），
        不经过 emit 调用方，那条路只能靠 :func:`safe_connect` 在槽侧拦住。

        状态推进放在 finally，保证一次异常不会把边沿检测卡死在同一状态。
        """
        left = right = middle = False
        sampled = False
        try:
            point = self._cursor_pos()
            left = self._key_down(_VK_LBUTTON)
            right = self._key_down(_VK_RBUTTON)
            middle = self._key_down(_VK_MBUTTON)
            sampled = True

            if left and not self._left_last:
                self._down = point
                self.leftPressed.emit(point)
            elif not left and self._left_last:
                self.leftReleased.emit(self._down or point, point)
                self._down = None

            if (right and not self._right_last) or (middle and not self._middle_last):
                self.otherPressed.emit(point)
        except Exception as exc:  # noqa: BLE001 - Win32 采样异常不得逃逸
            _warn_once("划词轮询采样异常，已忽略：", exc)
        finally:
            # 只在采样成功时推进边沿状态：一次 GetCursorPos 失败就把 _left_last
            # 清零，会让下一轮把「仍按着」误判成新的按下沿，多发一次事件。
            if sampled:
                self._left_last = left
                self._right_last = right
                self._middle_last = middle

    @staticmethod
    def _key_down(vk: int) -> bool:
        return bool(_user32.GetAsyncKeyState(vk) & 0x8000)

    @staticmethod
    def _cursor_pos() -> tuple:
        point = _POINT()
        if not _user32.GetCursorPos(ctypes.byref(point)):
            return (0, 0)
        return (int(point.x), int(point.y))


__all__ = [
    "ElaMouseMonitor",
    "foreground_pid",
    "safe_connect",
    "send_copy",
    "to_logical_pos",
    "window_pid_at",
]
