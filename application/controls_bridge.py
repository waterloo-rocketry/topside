from PySide2.QtCore import Qt, QObject, Signal, Slot, Property
from PySide2.QtWidgets import QFileDialog

class ControlsBridge(QObject):
    component_state_sig = Signal()
    number_of_component_sig = Signal()
    components_sig = Signal()

    def __init__(self, plumb):
        QObject.__init__(self)

        self.plumbing_bridge = plumb
        self.plumbing_eng = self.plumbing_bridge.engine
        self.toggleable_components = []
        self._isOpen = []
    
    def set_component_states(self, index, state):
        if state == 'open':
            self._isOpen[index] = True
            self.plumbing_eng.set_component_state(self.toggleable_components[index], 'open')
        elif state == 'closed':
            self._isOpen[index] = False
            self.plumbing_eng.set_component_state(self.toggleable_components[index], 'closed')
        self.component_state_sig.emit()

    @Slot()
    def refresh(self):
        self.plumbing_eng = self.plumbing_bridge.engine
        self.toggleable_components = self.plumbing_eng.list_toggles()
        self._isOpen = [False] * len(self.toggleable_components)
        for i in range(len(self.toggleable_components)):
            if self.plumbing_eng.current_state(self.toggleable_components[i]) == 'open' or self.plumbing_eng.current_state(self.toggleable_components[i]) == 'closed':
                self.set_component_states(i, self.plumbing_eng.current_state(self.toggleable_components[i]))
            else:
                print('invalid state')
        self.number_of_component_sig.emit()
        self.components_sig.emit()

    def get_component_states(self):
        return self._isOpen

    isOpen = Property(list, get_component_states, set_component_states, notify=component_state_sig)

    @Property(int, notify=number_of_component_sig)
    def numOfComponents(self):
        return len(self.toggleable_components)

    @Property(list, notify=components_sig)
    def components(self):
        return self.toggleable_components

    @Slot(int)
    def toggle_on(self, index):
        self.set_component_states(index, 'open')    

    @Slot(int)
    def toggle_off(self, index):
        self.set_component_states(index, 'closed')    