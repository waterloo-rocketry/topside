import topside as top


class Parser:
    def __init__(self, files):
        self.package = top.Package(files)

        self.components = []
        self.mapping = {}
        self.initial_pressure = {}
        self.initial_states = {}

    def parse_components(self):
        # for entry in self.package.components.values():
        pass
