import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, 
                            QHBoxLayout, QWidget, QLineEdit, QLabel, QFileDialog,
                            QCheckBox, QTextEdit, QProgressBar)
from PyQt6.QtCore import Qt, QTimer
import qdarktheme
import subprocess
import logging
from datetime import datetime
from pathlib import Path
from multiprocessing import Process, Queue, Event
import queue
import platform

class PdfConverter:
    """PDF转换处理类"""
    def __init__(self, input_dir, output_dir, force_ocr, message_queue, stop_event):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.force_ocr = force_ocr
        self.message_queue = message_queue
        self.stop_event = stop_event
        self.setup_logging()

    def setup_logging(self):
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = log_dir / f"pdf2md_conversion_{timestamp}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file, encoding='utf-8'),
            ]
        )
        self.logger = logging.getLogger(__name__)

    def log_message(self, message, level=logging.INFO):
        """记录日志并发送到队列"""
        self.logger.log(level, message)
        self.message_queue.put(message)

    def convert(self):
        input_dir = os.path.abspath(self.input_dir)
        output_dir = os.path.abspath(self.output_dir)
        
        self.log_message(f"开始转换任务")
        self.log_message(f"输入目录: {input_dir}")
        self.log_message(f"输出目录: {output_dir}")
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            self.log_message(f"创建输出目录: {output_dir}")

        pdf_files = [f for f in os.listdir(input_dir) if f.lower().endswith('.pdf')]
        
        if not pdf_files:
            self.log_message(f"未找到PDF文件", logging.WARNING)
            return

        self.log_message(f"找到 {len(pdf_files)} 个PDF文件待转换")
        
        # 创建 startupinfo 对象来隐藏窗口
        if platform.system() == 'Windows':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
        else:
            startupinfo = None

        for filename in pdf_files:
            if self.stop_event.is_set():
                self.log_message("转换过程被用户终止", logging.WARNING)
                break
                
            input_path = os.path.join(input_dir, filename)
            self.log_message(f"正在处理: {filename}")
            
            try:
                command = [
                    'marker_single',
                    input_path,
                    '--output_dir', output_dir,
                    '--output_format', 'markdown'
                ]
                
                if self.force_ocr:
                    command.append('--force_ocr')
                
                process = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1,
                    universal_newlines=True,
                    startupinfo=startupinfo  # 添加 startupinfo 参数
                )

                while True:
                    output = process.stdout.readline()
                    if output == '' and process.poll() is not None:
                        break
                    if output:
                        self.log_message(output.strip())

                stderr_output = process.stderr.read()
                if stderr_output:
                    self.log_message(f"错误输出: {stderr_output}", logging.ERROR)

                if self.stop_event.is_set():
                    process.terminate()
                    break
                    
                if process.returncode == 0:
                    self.log_message(f"成功转换 {filename}")
                else:
                    self.log_message(f"转换 {filename} 失败", logging.ERROR)
                
            except Exception as e:
                self.log_message(f"处理错误 {filename}: {str(e)}", logging.ERROR)

        self.log_message("转换任务结束")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF to Markdown Converter")
        self.setMinimumSize(800, 600)
        self.setup_ui()
        self.converter_process = None
        self.message_queue = None
        self.stop_event = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_messages)
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
        self.output_edit.setPlaceholderText("选择Markdown文件输出目录")
        output_btn = QPushButton("浏览...")
        output_btn.clicked.connect(lambda: self.browse_folder(self.output_edit))
        output_layout.addWidget(QLabel("输出目录:"))
        output_layout.addWidget(self.output_edit)
        output_layout.addWidget(output_btn)

        # OCR选项
        self.force_ocr_checkbox = QCheckBox("强制使用OCR")
        self.force_ocr_checkbox.setToolTip("启��此选项将强制对所有页面进行OCR处理")

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)

        # 按钮布局
        button_layout = QHBoxLayout()
        
        # 开始按钮
        self.start_btn = QPushButton("开始转换")
        self.start_btn.setFixedHeight(40)
        self.start_btn.clicked.connect(self.start_conversion)
        
        # 终止按钮
        self.stop_btn = QPushButton("终止转换")
        self.stop_btn.setFixedHeight(40)
        self.stop_btn.clicked.connect(self.stop_conversion)
        self.stop_btn.setEnabled(False)  # 初始状态下禁用
        
        button_layout.addWidget(self.start_btn)
        button_layout.addWidget(self.stop_btn)

        # 日志显示区域
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setPlaceholderText("转换日志将显示在这里...")

        # 添加所有控件到主布局
        layout.addLayout(input_layout)
        layout.addLayout(output_layout)
        layout.addWidget(self.force_ocr_checkbox)
        layout.addWidget(self.progress_bar)
        layout.addLayout(button_layout)
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
        QProgressBar {
            border: none;
            background-color: #E0E0E0;
            height: 4px;
            border-radius: 2px;
        }
        QProgressBar::chunk {
            background-color: #6200EE;
            border-radius: 2px;
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

        # 添加终止按钮的样式
        additional_style = """
        QPushButton#stop_btn {
            background-color: #DC3545;
        }
        QPushButton#stop_btn:hover {
            background-color: #C82333;
        }
        QPushButton#stop_btn:pressed {
            background-color: #BD2130;
        }
        """
        self.stop_btn.setObjectName("stop_btn")  # 设置对象名以应用特定样式
        self.setStyleSheet(self.styleSheet() + additional_style)

    def browse_folder(self, line_edit):
        folder = QFileDialog.getExistingDirectory(self, "选择目录")
        if folder:
            line_edit.setText(folder)

    def start_conversion(self):
        input_dir = self.input_edit.text()
        output_dir = self.output_edit.text()

        if not input_dir or not output_dir:
            self.log_area.append("请选择输入和输出目录！")
            return

        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.progress_bar.setMaximum(0)
        self.log_area.clear()

        # 创建消息队列和停止事件
        self.message_queue = Queue()
        self.stop_event = Event()

        # 创建并启动转换进程
        self.converter_process = Process(
            target=PdfConverter(
                input_dir,
                output_dir,
                self.force_ocr_checkbox.isChecked(),
                self.message_queue,
                self.stop_event
            ).convert
        )
        self.converter_process.start()
        
        # 启动消息检查定时器
        self.timer.start()

    def stop_conversion(self):
        if self.converter_process and self.converter_process.is_alive():
            self.stop_event.set()
            self.log_area.append("\n正在终止转换过程...")
            self.stop_btn.setEnabled(False)

    def check_messages(self):
        """检查消息队列并更新UI"""
        try:
            while True:  # 处理队列中的所有消息
                message = self.message_queue.get_nowait()
                self.log_area.append(message)
                self.log_area.verticalScrollBar().setValue(
                    self.log_area.verticalScrollBar().maximum()
                )
        except queue.Empty:
            pass

        # 检查进程是否结束
        if self.converter_process and not self.converter_process.is_alive():
            self.conversion_finished()

    def conversion_finished(self):
        self.timer.stop()
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(100)
        self.log_area.append("\n转换完成！")

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 