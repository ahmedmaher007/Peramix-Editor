import sys
import os
import subprocess
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QAction, QFileDialog, QVBoxLayout, QPushButton, QWidget, QTabWidget, QTreeWidget,
    QTreeWidgetItem, QSplitter, QComboBox, QTextEdit, QMenuBar
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from PyQt5.Qsci import QsciScintilla, QsciLexerPython, QsciLexerCPP, QsciLexerJavaScript

class MultiLangEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('PeramixEditor')
        self.setGeometry(100, 100, 1200, 800)
        self.setWindowIcon(QIcon('icon.png'))

        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        
        file_tree = QTreeWidget()
        file_tree.setHeaderLabel("Files")
        self.text_edit = QsciScintilla()
        self.set_lexer('Python')  # Default language

        self.language_selector = QComboBox()
        self.language_selector.addItems(['Python', 'C++', 'JavaScript'])
        self.language_selector.currentTextChanged.connect(self.change_language)

        self.run_button = QPushButton("Run Code")
        self.run_button.clicked.connect(self.run_code)

        terminal_output_tab = QTabWidget()
        self.terminal = QTextEdit()
        self.terminal.setPlaceholderText("Terminal")
        self.terminal.setReadOnly(True)
        terminal_output_tab.addTab(self.terminal, "Terminal")
        
        self.output = QTextEdit()
        self.output.setPlaceholderText("Output")
        self.output.setReadOnly(True)
        terminal_output_tab.addTab(self.output, "Output")

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(file_tree)
        splitter.addWidget(self.text_edit)
        splitter.setSizes([200, 800])

        vertical_splitter = QSplitter(Qt.Vertical)
        vertical_splitter.addWidget(splitter)
        vertical_splitter.addWidget(terminal_output_tab)
        vertical_splitter.setSizes([600, 200])

        code_layout = QVBoxLayout()
        code_layout.addWidget(self.language_selector)
        code_layout.addWidget(self.run_button)
        code_layout.addWidget(vertical_splitter)

        main_layout.addLayout(code_layout)
        self.setCentralWidget(central_widget)
        self.create_menu()
        self.apply_styles()
        
        self.file_tree = file_tree

    def create_menu(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu('File')
        open_file = QAction('Open File', self)
        open_file.triggered.connect(self.open_file)
        file_menu.addAction(open_file)

        extensions_menu = menubar.addMenu('Extensions')
        install_extension = QAction('Install Extension', self)
        install_extension.triggered.connect(self.install_extension)
        extensions_menu.addAction(install_extension)

    def set_lexer(self, language):
        if language == 'Python':
            lexer = QsciLexerPython()
        elif language == 'C++':
            lexer = QsciLexerCPP()
        elif language == 'JavaScript':
            lexer = QsciLexerJavaScript()
        else:
            lexer = None
        if lexer:
            self.text_edit.setLexer(lexer)

    def change_language(self):
        language = self.language_selector.currentText()
        self.set_lexer(language)

    def open_file(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Open File", "", "All Files (*)", options=options)
        if file_name:
            with open(file_name, 'r') as file:
                self.text_edit.setText(file.read())

    def run_code(self):
        language = self.language_selector.currentText()
        code = self.text_edit.text()

        if language == 'Python':
            command = [sys.executable, '-c', code]
        elif language == 'JavaScript':
            command = ['node', '-e', code]
        elif language == 'C++':
            self.run_cpp_code(code)
            return
        else:
            self.terminal.append("Running code for this language is not supported yet.")
            return

        try:
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            stdout, stderr = process.communicate()
            self.terminal.append(f"$ {' '.join(command)}")
            self.terminal.append(stdout + stderr)
            self.output.setText(stdout + stderr)
        except Exception as e:
            self.terminal.append(str(e))

    def run_cpp_code(self, code):
        temp_file = os.path.join(os.getcwd(), 'temp_code.cpp')
        with open(temp_file, 'w') as f:
            f.write(code)

        executable = temp_file.replace('.cpp', '.exe')
        compile_command = ['g++', temp_file, '-o', executable]
        compile_process = subprocess.run(compile_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if compile_process.returncode != 0:
            self.terminal.append("Compilation failed:\n" + compile_process.stderr)
            return


        try:
            process = subprocess.Popen([executable], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            stdout, stderr = process.communicate()
            self.terminal.append(stdout)
            self.output.setText(stdout)
            if stderr:
                self.terminal.append(stderr)
        finally:
            os.remove(temp_file)
            if os.path.exists(executable):
                os.remove(executable)

    def install_extension(self):

        options = QFileDialog.Options()
        extension_file, _ = QFileDialog.getOpenFileName(self, "Install Extension", "", "Python Files (*.py);;All Files (*)", options=options)
        if extension_file:
            try:
                exec(open(extension_file).read())  # Executes the extension file (caution!)
                self.terminal.append(f"Extension {extension_file} installed successfully.")
            except Exception as e:
                self.terminal.append(f"Error installing extension: {e}")

    def apply_styles(self):
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: #00101F;
                color: #FFF;
            }}
            QTreeWidget {{
                background-color: #0D2135;
                color: #FFF;
            }}
            QsciScintilla {{
                background-color: #0D2135;
                color: #FFF;
                font-family: Consolas;
                font-size: 12px;
            }}
            QTabWidget::pane {{
                border: 1px solid #3A3A3A;
            }}
            QTabBar::tab {{
                background: #0D2135;
                color: #FFF;
                padding: 10px;
            }}
            QTabBar::tab:selected {{
                background: #007ACC;
            }}
            QPlainTextEdit, QTextEdit {{
                background-color: #0D2135;
                color: #FFF;
                font-family: Consolas;
                font-size: 12px;
            }}
            QPushButton {{
                background-color: #007ACC;
                color: #FFF;
                padding: 5px 10px;
                border: none;
            }}
            QPushButton:hover {{
                background-color: #005A8C;
            }}
        """)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MultiLangEditor()
    window.show()
    sys.exit(app.exec_())
