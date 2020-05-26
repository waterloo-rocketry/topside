class Immediate:
    def update(self, state):
        pass

    def satisfied(self):
        return True


class WaitUntil:
    def __init__(self, t):
        self.target_t = t
        self.current_t = None

    def update(self, state):
        self.current_t = state['time']

    def satisfied(self):
        if self.current_t is None:
            return False
        return self.current_t >= self.target_t


class Comparison:
    def __init__(self, node, pressure, comp_fn=None):
        self.node = node
        self.reference_pressure = pressure
        self.current_pressure = None
        self.comp_fn = comp_fn

    def compare(self, current_pressure, reference_pressure):
        if self.comp_fn is None:
            raise NotImplementedError('Comparison base class requires a custom comparison function')
        return self.comp_fn(self.current_pressure, self.reference_pressure)

    def update(self, state):
        self.current_pressure = state['pressures'][self.node]

    def satisfied(self):
        if self.current_pressure is None:
            return False
        return self.compare(self.current_pressure, self.reference_pressure)


class Equal(Comparison):
    def __init__(self, node, pressure, eps=0):
        self.eps = eps
        Comparison.__init__(self, node, pressure)

    def compare(self, current_pressure, reference_pressure):
        return abs(current_pressure - reference_pressure) <= self.eps


class Less(Comparison):
    def compare(self, current_pressure, reference_pressure):
        return current_pressure < reference_pressure


class Greater(Comparison):
    def compare(self, current_pressure, reference_pressure):
        return current_pressure > reference_pressure


class LessEqual(Comparison):
    def compare(self, current_pressure, reference_pressure):
        return current_pressure <= reference_pressure


class GreaterEqual(Comparison):
    def compare(self, current_pressure, reference_pressure):
        return current_pressure >= reference_pressure
