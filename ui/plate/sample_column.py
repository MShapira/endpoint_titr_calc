from functools import partial

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QInputDialog, QMenu

from immuno_calculator import Sample as SampleData


class SampleColumn(QWidget):
    def __init__(self, parent, data: SampleData = None, dummy_name: str = ''):
        super().__init__(parent)

        self.data = data
        self.selected = False
        self.selected_value_index = None

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignTop)

        # add group name
        self.group_name = QLabel(self, text='')
        self.layout.addWidget(self.group_name)

        # add sample name
        sample_name = dummy_name if data is None else data.name
        self.name_context_menu = QMenu(parent)
        self.name_context_menu__rename = QAction('Rename')
        self.name_context_menu__rename.triggered.connect(self.rename)
        self.name_context_menu.addAction(self.name_context_menu__rename)
        self.name_context_menu__group = QAction('Group')
        self.name_context_menu__group.triggered.connect(parent.parent().group_samples)
        self.name_context_menu.addAction(self.name_context_menu__group)
        self.name_context_menu__remove_from_group = QAction('Remove from groups')
        self.name_context_menu__remove_from_group.triggered.connect(parent.parent().remove_from_corresponding_groups)
        self.name_context_menu.addAction(self.name_context_menu__remove_from_group)
        self.name = QLabel(self, text=sample_name)
        self.layout.addWidget(self.name)

        self.value_context_menu = QMenu(parent)
        self.value_context_menu__mark_negative_control = QAction('Mark as negative control')
        self.value_context_menu__mark_negative_control.triggered.connect(self.mark_negative_control)
        self.value_context_menu.addAction(self.value_context_menu__mark_negative_control)

        # add values
        self.values = list()
        if self.data is None:
            # data is invalid, show dummy values
            for i in range(8):
                value = QLabel(self, text='')
                self.values.append(value)
                self.layout.addWidget(self.values[-1])
        else:
            # data is valid, show correct values
            for value_data in self.data.ydata:
                value = QLabel(self, text=f'{value_data}')
                self.values.append(value)
                self.layout.addWidget(self.values[-1])

        self.setLayout(self.layout)

        self.group_stylesheet = ''

    def mousePressEvent(self, event):
        widget = self.childAt(event.pos())

        # shift + left click on sample name to select/deselect sample
        if widget == self.name and event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
            self.selected = not self.selected
            self.update_selected_style()

    def mouseDoubleClickEvent(self, event):
        widget = self.childAt(event.pos())

        # show a sample rename pop-up if clicking on the name
        if widget == self.name:
            self.rename()

    def rename(self):
        dialog = QInputDialog(self)
        old_name = self.name.text()
        new_name, changed = dialog.getText(self, 'Set sample name', 'New name: ',
                                           echo=QLineEdit.EchoMode.Normal, text=old_name)
        if changed:
            self.data.name = new_name
            self.name.setText(new_name)

    def remove_from_group(self):
        # inform the sample group that this sample no longer belongs to it
        self.data.group.remove_sample(self.data)
        # update stylesheet
        self.group_stylesheet = ''
        self.update_selected_style()
        # update group title
        self.group_name.setText('')

    def mark_negative_control(self):
        if self.data.group is not None:
            negative_control_index = self.selected_value_index
            if negative_control_index not in self.data.group.negative_control_indices:
                self.data.group.negative_control_indices.append(negative_control_index)
            self.parent().parent().parent().parent().update_negative_controls()

    def contextMenuEvent(self, event):
        widget = self.childAt(event.pos())
        if widget == self.name:
            # disable `Group` menu entry if sample is not selected
            self.name_context_menu__group.setEnabled(self.selected)

            # disable `Remove from groups` menu entry if sample does not belong to any group
            self.name_context_menu__remove_from_group.setEnabled(self.data.group is not None and self.selected)

            self.name_context_menu.popup(event.globalPos())
        else:
            # it's possible that user requests a context menu for some of the values
            for index in range(len(self.values)):
                value = self.values[index]
                if widget == value:
                    self.selected_value_index = index
                    self.value_context_menu.popup(event.globalPos())

    def update_group_name(self, name: str):
        self.group_name.setText(name)

    def update_selected_style(self):
        if self.selected:
            self.setStyleSheet('background-color:blue;color:white')
        else:
            self.setStyleSheet(self.group_stylesheet)

    def update_negative_controls(self):
        if self.data.group is not None:
            for index in range(len(self.values)):
                if index in self.data.group.negative_control_indices:
                    self.values[index].setStyleSheet('font-weight: bold')
                else:
                    self.values[index].setStyleSheet('')
        else:
            for value in self.values:
                value.setStyleSheet('')
