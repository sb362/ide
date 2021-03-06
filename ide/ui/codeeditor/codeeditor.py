from PySide2.QtCore import QRect
from PySide2.QtGui import QFont, QResizeEvent, QTextFormat
from PySide2.QtWidgets import QTextEdit, QPlainTextEdit

from .linenumberarea import LineNumberArea
from ..colours import OuterSpace
from ..documents import CodeDocument


class CodeEditor(QPlainTextEdit):
	def __init__(self, parent=None):
		super().__init__(parent)

		self._document = CodeDocument()

		self.setFont(QFont("Source Code Pro", 12))
		self.setLineWrapMode(QPlainTextEdit.NoWrap)
		self.setIndentationWidth(4)

		self.lineNumberArea = LineNumberArea(self)

		self.blockCountChanged.connect(lambda: self.setViewportMargins(self.lineNumberArea.numberWidth(), 0, 0, 0))
		self.updateRequest.connect(self.updateLineNumberArea)
		self.cursorPositionChanged.connect(self.highlightCurrentLine)

		self.highlightCurrentLine()
		self.setViewportMargins(self.lineNumberArea.numberWidth(), 0, 0, 0)

	def document(self):
		return self._document

	def setDocument(self, document: CodeDocument):
		self._document = document
		super().setDocument(document.document())
		super().setPlainText(document.document().toPlainText())

	def setIndentationWidth(self, n_spaces: int):
		self.setTabStopDistance(self.fontMetrics().horizontalAdvance(" ") * n_spaces)

	def highlightCurrentLine(self):
		selections = []

		if not self.isReadOnly():
			selection = QTextEdit.ExtraSelection()

			selection.format.setBackground(OuterSpace.lighter(160))
			selection.format.setProperty(QTextFormat.FullWidthSelection, True)
			selection.cursor = self.textCursor()
			selection.cursor.clearSelection()

			selections.append(selection)

		self.setExtraSelections(selections)

	def resizeEvent(self, event: QResizeEvent):
		super().resizeEvent(event)

		# todo: move this into LineNumberArea
		cr = self.contentsRect()
		self.lineNumberArea.setGeometry(cr.left(), cr.top(), self.lineNumberArea.numberWidth(), cr.height())

	def updateLineNumberArea(self, rect: QRect, dy: int = 0):
		# todo: move this into LineNumberArea
		if dy:
			self.lineNumberArea.scroll(0, dy)
		else:
			self.lineNumberArea.update(0, rect.y(), self.lineNumberArea.width(), rect.height())

		if rect.contains(self.viewport().rect()):
			self.setViewportMargins(self.lineNumberArea.numberWidth(), 0, 0, 0)
