import logging
from PySide6.QtWidgets import QWidget, QTextEdit, QVBoxLayout, QPushButton, QSizePolicy
from PySide6.QtGui import QFont, QTextCharFormat, QColor


class LogWindow(QWidget, logging.Handler):
  def __init__(self):
    QWidget.__init__(self)
    logging.Handler.__init__(self)

    self.setWindowTitle('Log')
    self.setMaximumWidth(700)
    self.setMinimumWidth(650)
    self.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)

    self.logTextEdit = QTextEdit(self)
    self.logTextEdit.setFont(QFont('Ubuntu Sans', 11))
    self.logTextEdit.setReadOnly(True)

    self.clearButton = QPushButton('Clear')
    self.clearButton.clicked.connect(self.logTextEdit.clear)
    self.clearButton.setMaximumWidth(100)

    _layout = QVBoxLayout()
    _layout.addWidget(self.logTextEdit)
    _layout.addWidget(self.clearButton)
    self.setLayout(_layout)

    self.setFormatter(logging.Formatter('%(asctime)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
    logging.getLogger().addHandler(self)
    logging.getLogger().setLevel(logging.DEBUG)

  def emit(self, record):
    _msg = self.format(record)
    _cursor = self.logTextEdit.textCursor()
    fmt = QTextCharFormat()

    if record.levelno >= logging.ERROR:
      fmt.setForeground(QColor("red"))
    elif record.levelno >= logging.WARNING:
      fmt.setForeground(QColor("orange"))

    _cursor.insertText(_msg + '\n', fmt)
    self.logTextEdit.setTextCursor(_cursor)





