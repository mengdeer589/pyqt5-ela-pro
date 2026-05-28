from __future__ import annotations

from PyQt5.QtCore import Qt

from pyqt5_ela_pro.ela_upload_area import ElaUploadArea


class TestElaUploadAreaInit:
    def test_initialization_with_defaults(self):
        area = ElaUploadArea()
        assert area._title == "拖拽文件到此处"
        assert area._sub_title == "或点击选择文件"
        assert area._border_radius == 8
        assert area._accepted_suffixes == []
        assert area._max_file_count == 0
        assert area._max_file_size == 0
        assert area._is_multiple is True
        assert area._is_drag_over is False
        assert area._is_hover is False
        assert area._is_pressed is False
        assert area._file_paths == []
        area.deleteLater()

    def test_minimum_size(self):
        area = ElaUploadArea()
        assert area.minimumWidth() == 260
        assert area.minimumHeight() == 160
        area.deleteLater()

    def test_accepts_drops(self):
        area = ElaUploadArea()
        assert area.acceptDrops() is True
        area.deleteLater()

    def test_mouse_tracking_enabled(self):
        area = ElaUploadArea()
        assert area.hasMouseTracking() is True
        area.deleteLater()

    def test_hand_cursor(self):
        area = ElaUploadArea()
        assert area.cursor().shape() == Qt.CursorShape.PointingHandCursor
        area.deleteLater()


class TestElaUploadAreaSignals:
    def test_has_files_selected_signal(self):
        area = ElaUploadArea()
        assert hasattr(area, "filesSelected")
        area.deleteLater()

    def test_has_file_added_signal(self):
        area = ElaUploadArea()
        assert hasattr(area, "fileAdded")
        area.deleteLater()

    def test_has_file_removed_signal(self):
        area = ElaUploadArea()
        assert hasattr(area, "fileRemoved")
        area.deleteLater()

    def test_has_file_rejected_signal(self):
        area = ElaUploadArea()
        assert hasattr(area, "fileRejected")
        area.deleteLater()


class TestElaUploadAreaTitle:
    def test_title_default(self):
        area = ElaUploadArea()
        assert area.title() == "拖拽文件到此处"
        area.deleteLater()

    def test_set_title(self):
        area = ElaUploadArea()
        area.setTitle("上传文件")
        assert area.title() == "上传文件"
        area.deleteLater()

    def test_set_title_empty(self):
        area = ElaUploadArea()
        area.setTitle("")
        assert area.title() == ""
        area.deleteLater()


class TestElaUploadAreaSubTitle:
    def test_sub_title_default(self):
        area = ElaUploadArea()
        assert area.subTitle() == "或点击选择文件"
        area.deleteLater()

    def test_set_sub_title(self):
        area = ElaUploadArea()
        area.setSubTitle("点击上传")
        assert area.subTitle() == "点击上传"
        area.deleteLater()


class TestElaUploadAreaBorderRadius:
    def test_border_radius_default(self):
        area = ElaUploadArea()
        assert area.borderRadius() == 8
        area.deleteLater()

    def test_set_border_radius(self):
        area = ElaUploadArea()
        area.setBorderRadius(16)
        assert area.borderRadius() == 16
        area.deleteLater()


class TestElaUploadAreaAcceptedSuffixes:
    def test_accepted_suffixes_default(self):
        area = ElaUploadArea()
        assert area.acceptedSuffixes() == []
        area.deleteLater()

    def test_set_accepted_suffixes(self):
        area = ElaUploadArea()
        area.setAcceptedSuffixes([".txt", ".py"])
        assert area.acceptedSuffixes() == [".txt", ".py"]
        area.deleteLater()


class TestElaUploadAreaMaxFileCount:
    def test_max_file_count_default(self):
        area = ElaUploadArea()
        assert area.maxFileCount() == 0
        area.deleteLater()

    def test_set_max_file_count(self):
        area = ElaUploadArea()
        area.setMaxFileCount(5)
        assert area.maxFileCount() == 5
        area.deleteLater()


class TestElaUploadAreaMaxFileSize:
    def test_max_file_size_default(self):
        area = ElaUploadArea()
        assert area.maxFileSize() == 0
        area.deleteLater()

    def test_set_max_file_size(self):
        area = ElaUploadArea()
        area.setMaxFileSize(1024)
        assert area.maxFileSize() == 1024
        area.deleteLater()


class TestElaUploadAreaMultiple:
    def test_is_multiple_default(self):
        area = ElaUploadArea()
        assert area.isMultiple() is True
        area.deleteLater()

    def test_set_multiple(self):
        area = ElaUploadArea()
        area.setMultiple(False)
        assert area.isMultiple() is False
        area.deleteLater()


class TestElaUploadAreaDialogTitle:
    def test_dialog_title_default(self):
        area = ElaUploadArea()
        assert area.dialogTitle() == ""
        area.deleteLater()

    def test_set_dialog_title(self):
        area = ElaUploadArea()
        area.setDialogTitle("选择文件")
        assert area.dialogTitle() == "选择文件"
        area.deleteLater()


class TestElaUploadAreaMimeFilter:
    def test_mime_filter_default(self):
        area = ElaUploadArea()
        assert area.acceptedMimeFilter() == ""
        area.deleteLater()

    def test_set_mime_filter(self):
        area = ElaUploadArea()
        area.setAcceptedMimeFilter("Text (*.txt)")
        assert area.acceptedMimeFilter() == "Text (*.txt)"
        area.deleteLater()


class TestElaUploadAreaSelectedFiles:
    def test_selected_files_default_empty(self):
        area = ElaUploadArea()
        assert area.selectedFiles() == []
        area.deleteLater()

    def test_clear_files(self):
        area = ElaUploadArea()
        area._file_paths = ["a.txt", "b.py"]
        area.clearFiles()
        assert area.selectedFiles() == []
        area.deleteLater()


class TestElaUploadAreaValidateFile:
    def test_validate_file_nonexistent(self):
        area = ElaUploadArea()
        ok, reason = area._validateFile("Z:\\nonexistent_file.xyz")
        assert ok is False
        assert reason == "文件不存在"
        area.deleteLater()

    def test_validate_file_suffix_rejected(self):
        area = ElaUploadArea()
        area.setAcceptedSuffixes([".txt"])
        ok, reason = area._validateFile("C:\\Windows\\System32\\drivers\\etc\\hosts")
        assert ok is False
        assert "不支持的文件类型" in reason
        area.deleteLater()

    def test_validate_file_duplicate(self):
        area = ElaUploadArea()
        area._file_paths = ["C:\\test.txt"]
        ok, reason = area._validateFile("C:\\test.txt")
        assert ok is False
        assert len(reason) > 0
        area.deleteLater()


class TestElaUploadAreaAddFiles:
    def test_add_file_emits_file_added(self):
        area = ElaUploadArea()
        area._validateFile = lambda p: (True, "")
        received = []
        area.fileAdded.connect(lambda p: received.append(p))
        area._addFiles(["C:\\test.txt"])
        assert "C:\\test.txt" in received
        area.deleteLater()

    def test_add_file_emits_files_selected(self):
        area = ElaUploadArea()
        area._validateFile = lambda p: (True, "")
        received = []
        area.filesSelected.connect(lambda p: received.append(p))
        area._addFiles(["C:\\test.txt"])
        assert any("C:\\test.txt" in files for files in received)
        area.deleteLater()

    def test_add_rejected_file_emits_file_rejected(self):
        area = ElaUploadArea()
        area._validateFile = lambda p: (False, "不支持")
        received = []
        area.fileRejected.connect(lambda p, r: received.append((p, r)))
        area._addFiles(["C:\\bad.exe"])
        assert len(received) == 1
        assert received[0] == ("C:\\bad.exe", "不支持")
        area.deleteLater()


class TestElaUploadAreaRemoveFile:
    def test_remove_file_emits_file_removed(self):
        area = ElaUploadArea()
        area._file_paths = ["a.txt", "b.py"]
        received = []
        area.fileRemoved.connect(lambda p: received.append(p))
        area._removeFile(0)
        assert "a.txt" in received
        area.deleteLater()

    def test_remove_file_updates_list(self):
        area = ElaUploadArea()
        area._file_paths = ["a.txt", "b.py"]
        area._removeFile(0)
        assert area._file_paths == ["b.py"]
        area.deleteLater()

    def test_remove_invalid_index(self):
        area = ElaUploadArea()
        area._file_paths = ["a.txt"]
        area._removeFile(5)
        assert area._file_paths == ["a.txt"]
        area.deleteLater()


class TestElaUploadAreaDragEvents:
    def test_drag_enter_sets_drag_over(self):
        area = ElaUploadArea()
        from PyQt5.QtCore import QMimeData
        from PyQt5.QtGui import QDragEnterEvent
        mime = QMimeData()
        mime.setUrls([])
        area.dragEnterEvent(QDragEnterEvent(area.rect().topLeft(), Qt.DropAction.CopyAction, mime, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier))
        assert area._is_drag_over is True
        area.deleteLater()

    def test_drag_leave_clears_drag_over(self):
        area = ElaUploadArea()
        from PyQt5.QtGui import QDragLeaveEvent
        area._is_drag_over = True
        area.dragLeaveEvent(QDragLeaveEvent())
        assert area._is_drag_over is False
        area.deleteLater()


class TestElaUploadAreaEnterLeave:
    def test_enter_event_sets_hover(self):
        area = ElaUploadArea()
        from PyQt5.QtCore import QEvent
        area.enterEvent(QEvent(QEvent.Type.Enter))
        assert area._is_hover is True
        area.deleteLater()

    def test_leave_event_clears_hover(self):
        area = ElaUploadArea()
        from PyQt5.QtCore import QEvent
        area._is_hover = True
        area.leaveEvent(QEvent(QEvent.Type.Leave))
        assert area._is_hover is False
        area.deleteLater()


class TestElaUploadAreaTheme:
    def test_on_theme_changed_updates_mode(self):
        area = ElaUploadArea()
        from PyQt5ElaWidgetTools import ElaThemeType
        area._onThemeChanged(ElaThemeType.ThemeMode.Dark)
        assert area._theme_mode == ElaThemeType.ThemeMode.Dark
        area.deleteLater()


class TestElaUploadAreaDeleteLater:
    def test_delete_later_cleans_up(self):
        area = ElaUploadArea()
        area.deleteLater()
