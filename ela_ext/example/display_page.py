"""
[ela_ext] 展示组件演示页面
"""

import os
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QWidget
from PyQt5.QtGui import QFont, QImage, QPixmap
from PyQt5.QtCore import Qt
from PyQt5ElaWidgetTools import (
    ElaText,
    ElaProgressBar,
    ElaProgressRing,
    ElaProgressRingType,
    ElaImageCard,
    ElaInteractiveCard,
    ElaPopularCard,
    ElaPromotionCard,
    ElaReminderCard,
    ElaAcrylicUrlCard,
    ElaKeyBinder,
)
from .base_page import ExamplePage


RESOURCE_PATH = os.path.join(os.path.dirname(__file__), "resource", "images")


def _res(filename):
    return os.path.join(RESOURCE_PATH, filename)


class DisplayComponentsPage(ExamplePage):
    """ela 展示组件演示页面"""

    PAGE_TITLE = "ela 展示组件"

    def __init__(self, parent=None):
        super().__init__(parent)

    def _addDemoContent(self, main_layout):
        self._demoProgressBar(main_layout)
        self._demoProgressRing(main_layout)
        self._demoImageCard(main_layout)
        self._demoInteractiveCard(main_layout)
        self._demoPopularCard(main_layout)
        self._demoPromotionCard(main_layout)
        self._demoReminderCard(main_layout)
        self._demoAcrylicUrlCard(main_layout)
        self._demoKeyBinder(main_layout)

    def _createSectionHeader(self, title):
        section = ElaText(title, self)
        section.setTextPixelSize(18)
        font = QFont()
        font.setPixelSize(18)
        font.setBold(True)
        section.setFont(font)
        return section

    def _demoProgressBar(self, parent_layout):
        parent_layout.addWidget(
            self._createSectionHeader("01. ElaProgressBar - 进度条")
        )
        parent_layout.addSpacing(10)

        info = ElaText("水平进度条，显示当前操作进度", self)
        info.setTextPixelSize(14)
        parent_layout.addWidget(info)
        parent_layout.addSpacing(10)

        progress_bar = ElaProgressBar(self)
        progress_bar.setRange(0, 100)
        progress_bar.setValue(65)
        progress_bar.setFixedWidth(400)
        parent_layout.addWidget(progress_bar)
        parent_layout.addSpacing(30)

    def _demoProgressRing(self, parent_layout):
        parent_layout.addWidget(
            self._createSectionHeader("02. ElaProgressRing - 环形进度")
        )
        parent_layout.addSpacing(10)

        info = ElaText("环形进度指示器，适用于等待状态", self)
        info.setTextPixelSize(14)
        parent_layout.addWidget(info)
        parent_layout.addSpacing(10)

        ring_container = QWidget(self)
        ring_layout = QHBoxLayout(ring_container)

        ring1 = ElaProgressRing(self)
        ring1.setValue(75)
        ring1.setIsDisplayValue(True)
        ring1.setValueDisplayMode(ElaProgressRingType.ValueDisplayMode.Percent)
        ring1.setFixedSize(100, 100)
        ring_layout.addWidget(ring1)

        ring2 = ElaProgressRing(self)
        ring2.setValue(50)
        ring2.setIsDisplayValue(True)
        ring2.setValueDisplayMode(ElaProgressRingType.ValueDisplayMode.Actual)
        ring2.setFixedSize(80, 80)
        ring_layout.addWidget(ring2)

        ring3 = ElaProgressRing(self)
        ring3.setIsBusying(True)
        ring3.setFixedSize(60, 60)
        ring_layout.addWidget(ring3)

        parent_layout.addWidget(ring_container)
        parent_layout.addSpacing(30)

    def _demoImageCard(self, parent_layout):
        parent_layout.addWidget(
            self._createSectionHeader("03. ElaImageCard - 图片卡片")
        )
        parent_layout.addSpacing(10)

        info = ElaText("带图片的卡片组件", self)
        info.setTextPixelSize(14)
        parent_layout.addWidget(info)
        parent_layout.addSpacing(10)

        card = ElaImageCard(self)
        card.setFixedSize(240, 180)
        card.setBorderRadius(8)
        pixmap = QPixmap(_res("miku.png"))
        if not pixmap.isNull():
            card.setCardImage(QImage(pixmap.toImage()))
        parent_layout.addWidget(card)
        parent_layout.addSpacing(30)

    def _demoInteractiveCard(self, parent_layout):
        parent_layout.addWidget(
            self._createSectionHeader("04. ElaInteractiveCard - 交互卡片")
        )
        parent_layout.addSpacing(10)

        info = ElaText("可交互的卡片组件，支持点击", self)
        info.setTextPixelSize(14)
        parent_layout.addWidget(info)
        parent_layout.addSpacing(10)

        card = ElaInteractiveCard(self)
        card.setTitle("热门文章")
        card.setSubTitle("点击查看详情")
        card.setBorderRadius(8)
        pixmap = QPixmap(_res("beach.png"))
        if not pixmap.isNull():
            card.setCardPixmap(pixmap)
        card.setCardPixmapSize(240, 120)
        card.setFixedSize(260, 200)
        parent_layout.addWidget(card)
        parent_layout.addSpacing(30)

    def _demoPopularCard(self, parent_layout):
        parent_layout.addWidget(
            self._createSectionHeader("05. ElaPopularCard - 热门卡片")
        )
        parent_layout.addSpacing(10)

        info = ElaText("展示热门内容的卡片组件", self)
        info.setTextPixelSize(14)
        parent_layout.addWidget(info)
        parent_layout.addSpacing(10)

        card = ElaPopularCard(self)
        card.setTitle("STYX HELIX")
        card.setSubTitle("阅读量: 10,000+")
        card.setInteractiveTips("查看详情")
        card.setCardButtonText("立即阅读")
        card.setBorderRadius(8)
        pixmap = QPixmap(_res("classroom.png"))
        if not pixmap.isNull():
            card.setCardPixmap(pixmap)
        card.setFixedSize(260, 220)
        parent_layout.addWidget(card)
        parent_layout.addSpacing(30)

    def _demoPromotionCard(self, parent_layout):
        parent_layout.addWidget(
            self._createSectionHeader("06. ElaPromotionCard - 推广卡片")
        )
        parent_layout.addSpacing(10)

        info = ElaText("推广促销类卡片组件", self)
        info.setTextPixelSize(14)
        parent_layout.addWidget(info)
        parent_layout.addSpacing(10)

        card = ElaPromotionCard(self)
        card.setTitle("STYX HELIX")
        card.setSubTitle("Never close your eyes")
        card.setCardTitle("MiKu")
        card.setPromotionTitle("SONG~")
        card.setBorderRadius(10)
        pixmap = QPixmap(_res("dream.png"))
        if not pixmap.isNull():
            card.setCardPixmap(pixmap)
        card.setHorizontalCardPixmapRatio(0.5)
        card.setFixedSize(340, 180)
        parent_layout.addWidget(card)
        parent_layout.addSpacing(30)

    def _demoReminderCard(self, parent_layout):
        parent_layout.addWidget(
            self._createSectionHeader("07. ElaReminderCard - 提醒卡片")
        )
        parent_layout.addSpacing(10)

        info = ElaText("提醒通知类卡片组件", self)
        info.setTextPixelSize(14)
        parent_layout.addWidget(info)
        parent_layout.addSpacing(10)

        card = ElaReminderCard(self)
        card.setTitle("会议提醒")
        card.setSubTitle("下午3点有一场会议")
        card.setBorderRadius(8)
        pixmap = QPixmap(_res("Cirno.jpg"))
        if not pixmap.isNull():
            card.setCardPixmap(pixmap)
        card.setFixedSize(320, 100)
        parent_layout.addWidget(card)
        parent_layout.addSpacing(30)

    def _demoAcrylicUrlCard(self, parent_layout):
        parent_layout.addWidget(
            self._createSectionHeader("08. ElaAcrylicUrlCard - 亚克力URL卡片")
        )
        parent_layout.addSpacing(10)

        info = ElaText("带亚克力效果的URL链接卡片", self)
        info.setTextPixelSize(14)
        parent_layout.addWidget(info)
        parent_layout.addSpacing(10)

        card = ElaAcrylicUrlCard(self)
        card.setTitle("访问网站")
        card.setSubTitle("点击打开链接")
        card.setUrl("https://example.com")
        card.setBorderRadius(8)
        pixmap = QPixmap(_res("Moon.jpg"))
        if not pixmap.isNull():
            card.setCardPixmap(pixmap)
        card.setFixedSize(320, 120)
        parent_layout.addWidget(card)
        parent_layout.addSpacing(30)

    def _demoKeyBinder(self, parent_layout):
        parent_layout.addWidget(
            self._createSectionHeader("09. ElaKeyBinder - 快捷键提示")
        )
        parent_layout.addSpacing(10)

        info = ElaText("显示快捷键绑定的标签组件", self)
        info.setTextPixelSize(14)
        parent_layout.addWidget(info)
        parent_layout.addSpacing(10)

        binder_container = QWidget(self)
        binder_layout = QHBoxLayout(binder_container)

        binder1 = ElaKeyBinder(self)
        binder1.setBinderKeyText("Ctrl + S")
        binder1.setBorderRadius(4)
        binder_layout.addWidget(binder1)

        binder2 = ElaKeyBinder(self)
        binder2.setBinderKeyText("Ctrl + C")
        binder2.setBorderRadius(4)
        binder_layout.addWidget(binder2)

        binder3 = ElaKeyBinder(self)
        binder3.setBinderKeyText("Ctrl + V")
        binder3.setBorderRadius(4)
        binder_layout.addWidget(binder3)

        parent_layout.addWidget(binder_container)
        parent_layout.addSpacing(20)
