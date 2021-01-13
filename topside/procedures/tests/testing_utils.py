import topside as top


class NeverSatisfied(top.Condition):
    def reinitialize(self, state):
        pass

    def update(self, state):
        pass

    def satisfied(self):
        return False
