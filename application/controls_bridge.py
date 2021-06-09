from PySide2.QtCore import Qt, QObject, Signal, Slot, Property
from PySide2.QtWidgets import QFileDialog


class ControlsBridge(QObject):
    component_state_sig = Signal()

    def __init__(self, plumb):
        QObject.__init__(self)

        self.plumbing_eng = plumb.engine
        self.toggleable_components = self.plumbing_eng.list_toggles()
        self._isOpen = [False] * len(self.toggleable_components)

        for i in range(len(self.toggleable_components)):
            if self.toggleable_components[i] in self.plumbing_eng.initial_state:
                if self.plumbing_eng.initial_state[self.toggleable_components[i]] == 'open':
                    self._isOpen[i] = True
                elif self.plumbing_eng.initial_state[self.toggleable_components[i]] == 'closed':
                    self._isOpen[i] = False
                else:
                    print('unknown state')
            else:
                print('component not in initial states')
    
    def set_component_states(self, index):
        self._isOpen[index] = not self._isOpen[index]
        if self._isOpen[index]:
            self.plumbing_eng.set_component_state(self.toggleable_components[index], 'open')
        else:
            self.plumbing_eng.set_component_state(self.toggleable_components[index], 'closed')
        self.component_state_sig.emit()

    def get_component_states(self):
        return self._isOpen

    isOpen = Property(list, get_component_states, set_component_states, notify=component_state_sig)

    @Property(int)
    def numOfComponents(self):
        return len(self.toggleable_components)

    @Property(list)
    def components(self):
        return self.toggleable_components

    @Slot(int)
    def toggle_state(self, index):
        self.set_component_states(index)    