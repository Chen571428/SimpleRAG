import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, 
                             QHBoxLayout, QWidget, QLineEdit, QLabel, QFileDialog,
                             QTextEdit, QCheckBox, QComboBox)
from PyQt6.QtCore import Qt, QTimer
import qdarktheme
import subprocess
import logging
from pathlib import Path

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OneStepPreForRAG GUI")
        self.setMinimumSize(800, 600)
        self.setup_ui()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_log)
        self.timer.setInterval(100)  # 100ms 检查间隔

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # 输入目录选择
        input_layout = QHBoxLayout()
        self.input_edit = QLineEdit()
        self.input_edit.setPlaceholderText("选择PDF文件输入目录")
        input_btn = QPushButton("浏览...")
        input_btn.clicked.connect(lambda: self.browse_folder(self.input_edit))
        input_layout.addWidget(QLabel("输入目录:"))
        input_layout.addWidget(self.input_edit)
        input_layout.addWidget(input_btn)

        # 输出目录选择
        output_layout = QHBoxLayout()
        self.output_edit = QLineEdit()
        self.output_edit.setPlaceholderText("选择输出文件目录")
        output_btn = QPushButton("浏览...")
        output_btn.clicked.connect(lambda: self.browse_folder(self.output_edit))
        output_layout.addWidget(QLabel("输出目录:"))
        output_layout.addWidget(self.output_edit)
        output_layout.addWidget(output_btn)

        # 步骤选择
        steps_layout = QHBoxLayout()
        self.steps_checkboxes = []
        steps = ["PDF to MD", "Split MD", "Process Images"]
        for step in steps:
            checkbox = QCheckBox(step)
            self.steps_checkboxes.append(checkbox)
            steps_layout.addWidget(checkbox)

        # 上传器选择
        uploader_layout = QHBoxLayout()
        self.uploader_combo = QComboBox()
        self.uploader_combo.addItems(["picgo", "alioss"])
        uploader_layout.addWidget(QLabel("上传器:"))
        uploader_layout.addWidget(self.uploader_combo)

        # QPS限制
        qps_layout = QHBoxLayout()
        self.qps_edit = QLineEdit()
        self.qps_edit.setPlaceholderText("QPS限制 (0为无限制)")
        qps_layout.addWidget(QLabel("QPS限制:"))
        qps_layout.addWidget(self.qps_edit)

        # 开始按钮
        self.start_btn = QPushButton("开始处理")
        self.start_btn.setFixedHeight(40)
        self.start_btn.clicked.connect(self.start_processing)

        # 日志显示区域
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setPlaceholderText("处理日志将显示在这里...")

        # 添加所有控件到主布局
        layout.addLayout(input_layout)
        layout.addLayout(output_layout)
        layout.addLayout(steps_layout)
        layout.addLayout(uploader_layout)
        layout.addLayout(qps_layout)
        layout.addWidget(self.start_btn)
        layout.addWidget(self.log_area)

        # 设置样式
        self.apply_styles()

    def apply_styles(self):
        # 应用Material Design风格
        self.setStyleSheet(qdarktheme.load_stylesheet("light"))
        
        style = """
        QPushButton {
            background-color: #6200EE;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #7722FF;
        }
        QPushButton:pressed {
            background-color: #3700B3;
        }
        QLineEdit {
            padding: 8px;
            border: 2px solid #E0E0E0;
            border-radius: 4px;
            background-color: white;
        }
        QLineEdit:focus {
            border-color: #6200EE;
        }
        QTextEdit {
            border: 2px solid #E0E0E0;
            border-radius: 4px;
            padding: 8px;
            background-color: white;
        }
        QCheckBox {
            spacing: 8px;
        }
        QCheckBox::indicator {
            width: 18px;
            height: 18px;
        }
        """
        self.setStyleSheet(style)

    def browse_folder(self, line_edit):
        folder = QFileDialog.getExistingDirectory(self, "选择目录")
        if folder:
            line_edit.setText(folder)

    def start_processing(self):
        input_dir = self.input_edit.text()
        output_dir = self.output_edit.text()
        steps = [i+1 for i, checkbox in enumerate(self.steps_checkboxes) if checkbox.isChecked()]
        uploader = self.uploader_combo.currentText()
        qps = int(self.qps_edit.text()) if self.qps_edit.text() else 0

        if not input_dir or not output_dir:
            self.log_area.append("请选择输入和输出目录！")
            return

        self.start_btn.setEnabled(False)
        self.log_area.clear()

        # 创建并启动处理进程
        self.process = subprocess.Popen(
            [
                "conda", "run", "--no-capture-output", "-n", "pdf2md",
                "python", "../main.py",
                "--input_dir", input_dir,
                "--output_dir", output_dir,
                "--steps", " ".join(map(str, steps)),
                "--uploader", uploader,
                "--qps", str(qps)
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        self.timer.start()

    def update_log(self):
        if self.process.poll() is not None:
            self.timer.stop()
            self.start_btn.setEnabled(True)
            self.log_area.append("处理完成！")
            return

        output = self.process.stdout.readline()
        if output:
            self.log_area.append(output.strip())

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
