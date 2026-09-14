"""
[pyqt5_ela_pro] ElaBlueprintCanvas 节点图编辑器页面

类 UE5 Blueprint / ComfyUI 的节点图编辑器：右键空白创建节点、拖引脚
连线、拖节点 / 框选 / Ctrl 多选、Delete 删除、滚轮缩放、右键节点菜单。
附带「执行模拟」演示 running/done/error 状态与路径流动动画，以及
JSON 保存 / 加载。
"""

import json
import os

from PyQt5.QtCore import QPointF, QTimer
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5ElaWidgetTools import (
    ElaPushButton,
    ElaSpinBox,
    ElaMessageBar,
    ElaMessageBarType,
)

from pyqt5_ela_pro import (
    ElaBlueprintCanvas,
    ElaBlueprintGraph,
    register_node_type,
)
from pyqt5_ela_pro.blueprint import register_pin_type
from .base_page import ExamplePage

DEMO_OWNER = "blueprint-demo"
_DEMO_JSON = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "blueprint_demo.json"
)


def _ensure_demo_types():
    """注册演示节点类型（幂等：同定义重复注册被静默忽略）。"""
    register_pin_type("image", "#C080D0")

    def build_resize_body(node, container):
        spin = ElaSpinBox()
        spin.setRange(16, 8192)
        spin.setValue(int(node.properties.get("width", 512)))
        spin.valueChanged.connect(
            lambda v: node.properties.__setitem__("width", int(v))
        )
        container.layout().addWidget(spin)

    def build_blur_body(node, container):
        spin = ElaSpinBox()
        spin.setRange(0, 64)
        spin.setValue(int(node.properties.get("radius", 4)))
        spin.valueChanged.connect(
            lambda v: node.properties.__setitem__("radius", int(v))
        )
        container.layout().addWidget(spin)

    register_node_type(
        "load_image",
        "载入图像",
        "输入",
        outputs=[{"id": "img", "name": "图像", "data_type": "image"}],
        accent="primary",
        description="从磁盘载入一张图像",
        owner=DEMO_OWNER,
    )
    register_node_type(
        "noise",
        "添加噪点",
        "处理",
        inputs=[{"id": "img", "name": "图像", "data_type": "image", "multi": True}],
        outputs=[{"id": "img", "name": "图像", "data_type": "image"}],
        accent="warning",
        description="为图像叠加高斯噪声",
        owner=DEMO_OWNER,
    )
    register_node_type(
        "resize",
        "调整尺寸",
        "处理",
        inputs=[{"id": "img", "name": "图像", "data_type": "image"}],
        outputs=[{"id": "img", "name": "图像", "data_type": "image"}],
        accent="warning",
        body_builder=build_resize_body,
        description="按指定宽度缩放图像",
        owner=DEMO_OWNER,
    )
    register_node_type(
        "blur",
        "高斯模糊",
        "处理",
        inputs=[{"id": "img", "name": "图像", "data_type": "image"}],
        outputs=[{"id": "img", "name": "图像", "data_type": "image"}],
        accent="warning",
        body_builder=build_blur_body,
        description="按半径对图像做高斯模糊",
        owner=DEMO_OWNER,
    )
    register_node_type(
        "save_image",
        "保存图像",
        "输出",
        inputs=[{"id": "img", "name": "图像", "data_type": "image", "multi": True}],
        accent="danger",
        description="把结果写入磁盘",
        owner=DEMO_OWNER,
    )


class BlueprintPage(ExamplePage):
    """ElaBlueprintCanvas：UE5 风格节点图编辑器"""

    PAGE_TITLE = "ElaBlueprintCanvas 节点图编辑器"

    def __init__(self, parent=None):
        super().__init__(parent)

    def _addDemoContent(self, main_layout):
        _ensure_demo_types()
        self._canvas = ElaBlueprintCanvas(ElaBlueprintGraph(), owner=DEMO_OWNER)
        self._canvas.setMinimumHeight(440)
        self._demo_scene()
        self._canvas.fit_view()

        self._addInfoText(
            "操作：右键空白创建节点 · 拖引脚连线（磁吸高亮）· 拖节点 / 框选 / Ctrl 多选 · "
            "Delete 删除 · 滚轮缩放 · 右键节点打开菜单",
            main_layout,
        )
        main_layout.addWidget(self._canvas, 1)
        self._buildControls(main_layout)

    # ── 控制栏 ─────────────────────────────────────────────────────────

    def _buildControls(self, main_layout):
        row = QHBoxLayout()
        row.setSpacing(8)
        run_btn = ElaPushButton("执行模拟", self)
        run_btn.clicked.connect(self._run_simulation)
        reset_btn = ElaPushButton("重置状态", self)
        reset_btn.clicked.connect(lambda: self._canvas.execution().reset())
        fit_btn = ElaPushButton("适应视图", self)
        fit_btn.clicked.connect(self._canvas.fit_view)
        save_btn = ElaPushButton("保存 JSON", self)
        save_btn.clicked.connect(self._save_json)
        load_btn = ElaPushButton("加载 JSON", self)
        load_btn.clicked.connect(self._load_json)
        clear_btn = ElaPushButton("清空画布", self)
        clear_btn.clicked.connect(self._canvas.graph.clear)
        for btn in (run_btn, reset_btn, fit_btn, save_btn, load_btn, clear_btn):
            row.addWidget(btn)
        row.addStretch()
        main_layout.addLayout(row)

    # ── 演示场景 ────────────────────────────────────────────────────────

    def _demo_scene(self):
        n1 = self._canvas.add_node_at("load_image", QPointF(40, 60))
        n2 = self._canvas.add_node_at("noise", QPointF(280, 20))
        n3 = self._canvas.add_node_at("resize", QPointF(280, 170))
        n4 = self._canvas.add_node_at("blur", QPointF(520, 90))
        n5 = self._canvas.add_node_at("save_image", QPointF(780, 120))
        g = self._canvas.graph
        g.add_edge(n1.id, "img", n2.id, "img")
        g.add_edge(n1.id, "img", n3.id, "img")
        g.add_edge(n2.id, "img", n4.id, "img")
        g.add_edge(n3.id, "img", n4.id, "img")
        g.add_edge(n4.id, "img", n5.id, "img")

    # ── 执行模拟（QTimer 顺序推进，纯 UI 状态）──────────────────────────

    def _run_simulation(self):
        self._canvas.execution().reset()
        graph = self._canvas.graph
        nodes = graph.nodes()
        if not nodes:
            return
        # 按创建序简单模拟一条执行链
        chain = [n.id for n in nodes if graph.edges_of(n.id)]
        chain += [n.id for n in nodes if not graph.edges_of(n.id)]
        chain = list(dict.fromkeys(chain))  # 去重保序
        self._canvas.execution().set_path(chain)
        self._sim_chain = chain
        self._sim_index = 0
        timer = QTimer(self)
        timer.setSingleShot(True)
        timer.timeout.connect(lambda: self._sim_step(timer))
        timer.start(200)

    def _sim_step(self, timer):
        chain = self._sim_chain
        if self._sim_index >= len(chain):
            return
        nid = chain[self._sim_index]
        self._sim_index += 1
        if self._sim_index % 4 == 0:
            # 每 4 步失败一次演示 error 状态
            node = self._canvas.graph.node(nid)
            self._canvas.execution().fail(nid, f"模拟失败：{node.title}")
        else:
            self._canvas.execution().start(nid)
            self._canvas.execution().finish(nid, 20 + self._sim_index * 17)
        if self._sim_index < len(chain):
            timer.start(200)

    # ── JSON 保存 / 加载 ────────────────────────────────────────────────

    def _save_json(self):
        try:
            with open(_DEMO_JSON, "w", encoding="utf-8") as f:
                json.dump(self._canvas.to_dict(), f, ensure_ascii=False, indent=2)
        except OSError as exc:
            ElaMessageBar.error(
                ElaMessageBarType.PositionPolicy.TopRight,
                "",
                f"保存失败：{exc}",
                2000,
                self.window(),
            )
            return
        ElaMessageBar.success(
            ElaMessageBarType.PositionPolicy.TopRight,
            "",
            f"已保存到 {_DEMO_JSON}",
            2000,
            self.window(),
        )

    def _load_json(self):
        try:
            with open(_DEMO_JSON, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError) as exc:
            ElaMessageBar.error(
                ElaMessageBarType.PositionPolicy.TopRight,
                "",
                f"加载失败：{exc}",
                2000,
                self.window(),
            )
            return
        self._canvas.from_dict(data)
        self._canvas.fit_view()
        ElaMessageBar.success(
            ElaMessageBarType.PositionPolicy.TopRight,
            "",
            "已恢复画布",
            2000,
            self.window(),
        )
