"""
Office 文档预览组件。

通过 QAxWidget（ActiveX）嵌入 MS Office 或 WPS 文档查看器，
支持 Word、Excel、PowerPoint 三种格式。

仅 Windows 平台有效。
"""

from __future__ import annotations

from typing import Optional

from PyQt5.QAxContainer import QAxWidget
from PyQt5.QtGui import QCloseEvent, QResizeEvent
from PyQt5.QtWidgets import QMessageBox, QSizePolicy, QWidget

from .widget_base import ElaThemeWidget

_MS_WORD_PROGIDS = ["Word.Application"]
_WPS_WORD_PROGIDS = ["KWps.Application", "WPS.Application"]

_MS_EXCEL_PROGIDS = ["Excel.Application"]
_WPS_EXCEL_PROGIDS = ["KET.Application", "ET.Application"]

_MS_PPT_PROGIDS = ["PowerPoint.Application"]
_WPS_PPT_PROGIDS = ["WPP.Application"]

_BACKEND_PROGIDS = {
    "office": {
        "word": _MS_WORD_PROGIDS,
        "excel": _MS_EXCEL_PROGIDS,
        "ppt": _MS_PPT_PROGIDS,
    },
    "wps": {
        "word": _WPS_WORD_PROGIDS,
        "excel": _WPS_EXCEL_PROGIDS,
        "ppt": _WPS_PPT_PROGIDS,
    },
}


class ElaOfficeViewerMixin:
    """Office 预览组件混入类，提供通用 load/close 逻辑。

    子类必须设置 _appName 类属性。
    """

    _appName: str = ""

    def __init__(self, backend: str = "office", **kwargs):
        super().__init__(**kwargs)
        self._backend = backend
        self._loaded = False
        self._axWidget = QAxWidget(self)
        self._axWidget.resize(self.size())
        self._axWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def loadFile(self, path: str) -> bool:
        """加载 Office 文档。

        :param path: 文档路径
        :return: 加载成功返回 True，失败返回 False
        """
        self.close()

        progids = _BACKEND_PROGIDS.get(self._backend, {}).get(self._appName, [])

        # 1) 尝试直接用文档路径创建控件（COM 自动解析 handler）
        try:
            self._axWidget.setControl(path)
            self._axWidget.dynamicCall("SetVisible(bool)", False)
            self._axWidget.setProperty("DisplayAlerts", False)
            self._loaded = True
            return True
        except Exception:
            pass

        # 2) 回退：先创建应用实例再 Open
        for progid in progids:
            try:
                self._axWidget.setControl(progid)
                self._axWidget.dynamicCall("SetVisible(bool)", False)
                self._axWidget.setProperty("DisplayAlerts", False)
                self._axWidget.dynamicCall("Open(const QString&)", path)
                self._loaded = True
                return True
            except Exception:
                continue

        QMessageBox.critical(
            self,
            "错误",
            f"未找到可用的 {self._appName} 程序（{self._backend}）。\n"
            f"请确认已安装 MS Office 或 WPS。",
        )
        return False

    def close(self) -> None:
        """关闭当前文档并清理资源。"""
        if not self._loaded:
            return
        try:
            self._axWidget.dynamicCall("Quit()")
        except Exception:
            pass
        try:
            self._axWidget.close()
            self._axWidget.clear()
        except Exception:
            import traceback
            traceback.print_exc()
        self._loaded = False

    @property
    def is_loaded(self) -> bool:
        """当前是否已加载文档。"""
        return self._loaded

    def closeEvent(self, event: QCloseEvent) -> None:
        self.close()
        super().closeEvent(event)

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        self._axWidget.resize(self.size())


class ElaWordViewer(ElaOfficeViewerMixin, ElaThemeWidget):
    """Word 文档预览组件。

    支持 ``.doc``、``.docx`` 格式。

    :param parent: 父控件
    :param backend: 渲染后端，``"office"``（默认）或 ``"wps"``
    """

    _appName = "word"

    def __init__(self, parent: Optional[QWidget] = None, backend: str = "office"):
        super().__init__(parent=parent, backend=backend)


class ElaExcelViewer(ElaOfficeViewerMixin, ElaThemeWidget):
    """Excel 文档预览组件。

    支持 ``.xls``、``.xlsx`` 格式。

    :param parent: 父控件
    :param backend: 渲染后端，``"office"``（默认）或 ``"wps"``
    """

    _appName = "excel"

    def __init__(self, parent: Optional[QWidget] = None, backend: str = "office"):
        super().__init__(parent=parent, backend=backend)


class ElaPowerPointViewer(ElaOfficeViewerMixin, ElaThemeWidget):
    """PowerPoint 文档预览组件。

    支持 ``.ppt``、``.pptx`` 格式。

    :param parent: 父控件
    :param backend: 渲染后端，``"office"``（默认）或 ``"wps"``
    """

    _appName = "ppt"

    def __init__(self, parent: Optional[QWidget] = None, backend: str = "office"):
        super().__init__(parent=parent, backend=backend)
