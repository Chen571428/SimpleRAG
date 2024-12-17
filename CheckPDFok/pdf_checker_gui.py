import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, 
                            QHBoxLayout, QWidget, QLineEdit, QLabel, QFileDialog)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
import qdarktheme
from check_if_pdf_isok import process_pdfs
import logging

class PdfProcessThread(QThread):
    """处理PDF的后台线程"""
    finished = pyqtSignal()
    progress_update = pyqtSignal(str)

    def __init__(self, source_dir, good_dir, bad_dir):
        super().__init__()
        self.source_dir = source_dir
        self.good_dir = good_dir
        self.bad_dir = bad_dir

    def run(self):
        # 重定向日志到GUI
        logging.getLogger().handlers = []
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger()
        
        class GuiHandler(logging.Handler):
            def __init__(self, signal):
                super().__init__()
                self.signal = signal

            def emit(self, record):
                msg = self.format(record)
                self.signal.emit(msg)

        logger.addHandler(GuiHandler(self.progress_update))

        # 运行处理
        process_pdfs(self.source_dir, self.good_dir, self.bad_dir)
        self.finished.emit()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF 完整性检查工具")
        self.setMinimumSize(600, 400)
        self.setup_ui()

    def setup_ui(self):
        # 创建主窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        # 源目录选择
        source_layout = QHBoxLayout()
        self.source_edit = QLineEdit()
        self.source_edit.setPlaceholderText("选择源PDF文件目录")
        source_btn = QPushButton("浏览...")
        source_btn.clicked.connect(lambda: self.browse_folder(self.source_edit))
        source_layout.addWidget(QLabel("源目录:"))
        source_layout.addWidget(self.source_edit)
        source_layout.addWidget(source_btn)

        # 正常PDF目录选择
        good_layout = QHBoxLayout()
        self.good_edit = QLineEdit()
        self.good_edit.setPlaceholderText("选择正常PDF存放目录")
        good_btn = QPushButton("浏览...")
        good_btn.clicked.connect(lambda: self.browse_folder(self.good_edit))
        good_layout.addWidget(QLabel("正常PDF:"))
        good_layout.addWidget(self.good_edit)
        good_layout.addWidget(good_btn)

        # 损坏PDF目录选择
        bad_layout = QHBoxLayout()
        self.bad_edit = QLineEdit()
        self.bad_edit.setPlaceholderText("选择损坏PDF存放目录")
        bad_btn = QPushButton("浏览...")
        bad_btn.clicked.connect(lambda: self.browse_folder(self.bad_edit))
        bad_layout.addWidget(QLabel("损坏PDF:"))
        bad_layout.addWidget(self.bad_edit)
        bad_layout.addWidget(bad_btn)

        # 开始按钮
        self.start_btn = QPushButton("开始处理")
        self.start_btn.setFixedHeight(40)
        self.start_btn.clicked.connect(self.start_processing)

        # 日志显示区域
        self.log_area = QLineEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setPlaceholderText("处理日志将显示在这里...")

        # 添加所有控件到主布局
        layout.addLayout(source_layout)
        layout.addLayout(good_layout)
        layout.addLayout(bad_layout)
        layout.addWidget(self.start_btn)
        layout.addWidget(self.log_area)

        # 设置样式
        self.apply_styles()

    def apply_styles(self):
        # 应用 Fluent 样式
        qdarktheme.load_stylesheet("dark")
        
        style = """
        QPushButton {
            background-color: #0078D4;
            color: white;
            border: none;
            padding: 5px 15px;
            border-radius: 4px;
        }
        QPushButton:hover {
            background-color: #106EBE;
        }
        QPushButton:pressed {
            background-color: #005A9E;
        }
        QLineEdit {
            padding: 5px;
            border: 1px solid #D1D1D1;
            border-radius: 4px;
        }
        """
        self.setStyleSheet(style)

    def browse_folder(self, line_edit):
        folder = QFileDialog.getExistingDirectory(self, "选择目录")
        if folder:
            line_edit.setText(folder)

    def start_processing(self):
        source_dir = self.source_edit.text()
        good_dir = self.good_edit.text()
        bad_dir = self.bad_edit.text()

        if not all([source_dir, good_dir, bad_dir]):
            self.log_area.setText("请选择所有必需的目录！")
            return

        self.start_btn.setEnabled(False)
        self.start_btn.setText("处理中...")

        # 创建并启动处理线程
        self.thread = PdfProcessThread(source_dir, good_dir, bad_dir)
        self.thread.progress_update.connect(self.update_log)
        self.thread.finished.connect(self.processing_finished)
        self.thread.start()

    def update_log(self, message):
        self.log_area.setText(message)

    def processing_finished(self):
        self.start_btn.setEnabled(True)
        self.start_btn.setText("开始处理")
        self.log_area.setText("处理完成！")

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 