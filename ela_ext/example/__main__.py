"""
ela_ext 模块示例脚本
"""

import sys
import os
from typing import Optional

os.environ["QT_LOGGING_RULES"] = "*.debug=false;qt.qpa.fonts.warning=false"

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QHBoxLayout, QDialog
from PyQt5ElaWidgetTools import (
    eApp,
    ElaWindow,
    ElaIconType,
    ElaText,
    ElaPushButton,
)
from ela_ext import (
    fade_in,
    fade_out,
    ElaAnimatedMixin,
    shake_window,
    ElaTaskbarProgress,
)
from ela_ext.example import (
    FormComponentsPage,
    ButtonComponentsPage,
    ChartComponentsPage,
    DrawerComponentsPage,
    TooltipComponentsPage,
    AnimationPage,
    InputComponentsPage,
    BasicComponentsPage,
    NavigationComponentsPage,
    ContainerComponentsPage,
    DisplayComponentsPage,
    LayoutComponentsPage,
    DialogComponentsPage,
    MenuComponentsPage,
    ApplicationComponentsPage,
    GraphicsComponentsPage,
    AdvancedComponentsPage,
    IconBrowserPage,
    SvgIconComponentsPage,
)


class _AnimatedDemoDialog(ElaAnimatedMixin, QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("ElaAnimatedMixin 演示")
        self.resize(300, 200)
        layout = QVBoxLayout(self)
        info = ElaText(
            "通过 ElaAnimatedMixin 继承获得 fade_in() / fade_out()\n对话框自身拥有动画方法",
            self,
        )
        info.setTextPixelSize(14)
        layout.addWidget(info)
        btnLayout = QHBoxLayout()
        closeBtn = ElaPushButton("淡出并关闭", self)
        closeBtn.setFixedWidth(120)
        closeBtn.clicked.connect(lambda: self.fade_out(on_finished=self.close))
        btnLayout.addWidget(closeBtn)
        shakeBtn = ElaPushButton("抖动", self)
        shakeBtn.setFixedWidth(80)
        shakeBtn.clicked.connect(self.shake)
        btnLayout.addWidget(shakeBtn)
        btnLayout.addStretch()
        layout.addLayout(btnLayout)
        self.fade_in()

    def shake(self):
        shake_window(self)


class ExampleWindow(ElaWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ela_ext 组件示例")
        self.resize(1200, 800)

        self.setUserInfoCardTitle("组件演示")
        self.setUserInfoCardSubTitle("ela_ext@example.com")

        self.addPageNode("ela 输入组件", InputComponentsPage(self))
        self.addPageNode("ela 基础组件", BasicComponentsPage(self))
        self.addPageNode("ela 导航组件", NavigationComponentsPage(self))
        self.addPageNode("ela 容器组件", ContainerComponentsPage(self))
        self.addPageNode("ela 展示组件", DisplayComponentsPage(self))
        self.addPageNode("ela 布局组件", LayoutComponentsPage(self))
        self.addPageNode("ela 对话框组件", DialogComponentsPage(self))
        self.addPageNode("ela 菜单组件", MenuComponentsPage(self))
        self.addPageNode("ela 应用级组件", ApplicationComponentsPage(self))
        self.addPageNode("ela 图形组件", GraphicsComponentsPage(self))
        self.addPageNode("ela 高级组件", AdvancedComponentsPage(self))
        self.addPageNode("ela_ext 表单组件", FormComponentsPage(self))
        self.addPageNode("ela_ext 按钮组件", ButtonComponentsPage(self))
        self.addPageNode("ela_ext 图表组件", ChartComponentsPage(self))
        self.addPageNode("ela_ext 抽屉组件", DrawerComponentsPage(self))
        self.addPageNode("ela_ext 提示组件", TooltipComponentsPage(self))
        self.addPageNode("ela_ext 动画特效", AnimationPage(self))
        self.addPageNode("ela_ext 图标浏览器", IconBrowserPage(self))
        self.addPageNode("ela_ext SVG图标组件", SvgIconComponentsPage(self))

        self._taskbar: Optional[ElaTaskbarProgress] = None
        self._taskbar_timer: Optional[QTimer] = None
        self._taskbar_paused = False

    def closeEvent(self, event):
        if self._taskbar_timer:
            self._taskbar_timer.stop()
        if self._taskbar:
            self._taskbar.hide()
        super().closeEvent(event)

    def _startTaskbar(self):
        if self._taskbar is None:
            self._taskbar = ElaTaskbarProgress(self)
            self._taskbar.set_range(0, 100)
            self._taskbar.set_value(0)
            self._taskbar.show()

            self._taskbar_timer = QTimer(self)
            self._taskbar_timer.timeout.connect(self._advanceTaskbar)
            self._taskbar_timer.start(100)

    def _advanceTaskbar(self):
        if self._taskbar is None:
            return
        val = self._taskbar.value
        if val >= 100:
            self._taskbar_timer.stop()
            return
        self._taskbar.set_value(val + 1)

    def _pauseResumeTaskbar(self):
        if self._taskbar is None:
            return
        if self._taskbar_paused:
            self._taskbar.resume()
            self._taskbar_timer.start(100)
            self._taskbar_paused = False
        else:
            self._taskbar.pause()
            self._taskbar_timer.stop()
            self._taskbar_paused = True

    def _stopTaskbar(self):
        if self._taskbar is None:
            return
        self._taskbar_timer.stop()
        self._taskbar.stop()

    def _resetTaskbar(self):
        if self._taskbar is None:
            return
        self._taskbar_timer.stop()
        self._taskbar.reset()
        self._taskbar.set_value(0)
        self._taskbar_paused = False
        self._taskbar_timer.start(100)


if __name__ == "__main__":
    try:
        QT_VERSION_STR = "5.14.0"
    except Exception:
        QT_VERSION_STR = "6.8.3"

    if QT_VERSION_STR < "6.0.0":
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)  # ty:ignore[unresolved-attribute]
        if QT_VERSION_STR >= "5.14.0":
            QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)  # ty:ignore[unresolved-attribute]
            QApplication.setHighDpiScaleFactorRoundingPolicy(
                Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
            )

    app = QApplication(sys.argv)
    eApp.init()
    window = ExampleWindow()
    window.show()
    sys.exit(app.exec_())
