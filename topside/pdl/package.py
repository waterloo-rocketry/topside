import copy
import yaml

import topside as top
import topside.pdl.exceptions as exceptions

# imports is a dict of package name: path to file, used to locate files to read in
# on requested import.
# TODO(wendi): make imports more dynamic, so that users can add importable files
# outside a predefined library. Likely involves a function that traipses through the
# imports folder for new files and stores them in this dict whenever new Packages are instantiated.
IMPORTS = {
    "stdlib": "./topside/pdl/imports/stdlib.yaml"
}


class Package:
    """Package represents a collection of files that make a coherent plumbing system."""

    def __init__(self, files):
        self.imports = []

        # dicts of namespace: entry. Organized ilke this to reduce dict nesting;
        # since this is a one time process it should be easy to keep them synced.
        self.typedefs = {}
        self.components = {}
        self.graphs = {}

        for file in files:
            self.imports.extend(copy.deepcopy(file.imports))

        for imp in self.imports:
            if imp not in IMPORTS:
                raise exceptions.BadInputError(f"invalid import: {imp}")
            files.append(top.File(IMPORTS[imp]))

        for file in files:
            name = file.namespace
            if name not in self.typedefs:
                self.typedefs[name] = {}
                self.components[name] = []
                self.graphs[name] = []
            self.typedefs[name].update(copy.deepcopy(file.typedefs))
            self.components[name].extend(copy.deepcopy(file.components))
            self.graphs[name].extend(copy.deepcopy(file.graphs))

        self.clean()

    def clean(self):
        # preprocessing for typedefs
        for namespace in self.typedefs:
            for idx, component in enumerate(self.components[namespace]):
                if "type" in component:
                    self.components[namespace][idx] = self.fill_typedef(namespace, component)

        # cleaning PDL shortcuts
        for namespace in self.components:
            for idx, component in enumerate(self.components[namespace]):
                # deal with single state shortcuts
                if "states" not in component:
                    self.components[namespace][idx] = unpack_single_state(component)

                # unpack single teq direction shortcuts
                self.components[namespace][idx] = unpack_teq(component)

    def fill_typedef(self, namespace, component):
        name = component["type"]
        if "." in name:
            # rough implementation, needs more robustness in the future
            fields = name.split(".")
            namespace = fields[0]
            name = fields[-1]
        if name not in self.typedefs[namespace]:
            raise exceptions.BadInputError(f"invalid component type: {name}")
        params = component["params"]
        body = yaml.dump(self.typedefs[namespace][name])

        for var, value in params.items():
            body = body.replace(var, str(value))

        ret = yaml.safe_load(body)
        ret.pop("params")
        print(yaml.dump(ret))
        return ret


def unpack_teq(component):
    ret = component
    for state, edges in component["states"].items():
        for edge, teq in edges.items():
            if isinstance(teq, dict):
                continue
            long_teq = {}
            long_teq["fwd"] = teq
            long_teq["back"] = teq
            ret["states"][state][edge] = long_teq
    return ret


def unpack_single_state(component):
    ret = component
    states = {"default": {}}
    for edge, specs in component["edges"].items():
        states["default"][edge] = specs["teq"]
        ret["edges"][edge].pop("teq")
    ret["states"] = states
    return ret
