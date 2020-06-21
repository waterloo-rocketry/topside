import yaml

import topside.pdl.exceptions as exceptions


def check_fields(fields, entry):
    for field in fields:
        if field not in entry or entry[field] is None:
            raise exceptions.BadInputError(f"field {field} required and not found")


class File:
    """Represents a single PDL file."""

    def __init__(self, path, input_type="f"):
        if input_type == "f":
            file = open(path, "r")
        elif input_type == "s":
            file = path
        else:
            raise exceptions.BadInputError(f"invalid input type {input_type}")

        pdl = yaml.safe_load(file)

        self.type_checks = {
            "typedef": self.validate_typedef,
            "component": self.validate_component,
            "graph": self.validate_graph,
        }
        self.namespace = pdl['name']
        self.imports = pdl['import']
        self.body = pdl['body']
        self.typedefs = {}

    def validate(self):
        for entry in self.body:
            e_type = list(entry.keys())[0]
            if e_type not in self.type_checks:
                raise exceptions.BadInputError(f"invalid input type {e_type}")

            body = entry[e_type]
            self.type_checks[e_type](body)

    def validate_typedef(self, entry):
        check_fields(["params", "name", "edges", "states"], entry)
        name = entry["name"]
        self.typedefs[name] = entry["params"]

    def validate_component(self, entry):
        if "type" in entry:
            self.validate_type_entry(entry)
            return

        check_fields(["name", "edges"], entry)

        if "states" not in entry:
            for edge in entry["edges"]:
                edge_value = entry["edges"][edge]
                if "nodes" not in edge_value or "teq" not in edge_value or len(edge_value) != 2:
                    raise exceptions.BadInputError(
                        f"invalid single-state component syntax in {entry}")

    # This setup doesn't allow for hoisting (ie defining a typedef after a component that
    # references it)
    def validate_type_entry(self, entry):
        check_fields(["name", "type", "params"], entry)
        def_type = entry["type"]
        if def_type not in self.typedefs:
            raise exceptions.BadInputError(f"typedef {def_type} not found; hoisting not allowed")

        params = self.typedefs[def_type]
        if len(params) != len(entry):
            raise exceptions.BadInputError(f"not all params ({params}) present in component "
                                           "declaration")

        for param in params:
            if param not in entry["params"]:
                raise exceptions.BadInputError(f"param {param} not found")

    def validate_graph(self, entry):
        check_fields(["name", "nodes", "states"], entry)
        for node_name in entry["nodes"]:
            node = entry["nodes"][node_name]
            if len(node) < 1 or "components" not in node:
                raise exceptions.BadInputError(f"invalid entry for {node_name}: {node}")


f = File("topside/pdl/example.yaml")
f.validate()
