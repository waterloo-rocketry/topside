import yaml

import topside.pdl.exceptions as exceptions


def check_fields(fields, entry):
    """ Check that all fields in field are in entry."""
    if entry is None:
        raise exceptions.BadInputError("empty entry")
    for field in fields:
        if field not in entry:
            raise exceptions.BadInputError(f"field {field} required and not found")
        if entry[field] is None:
            raise exceptions.BadInputError(f"field {field} required not to be empty")


class File:
    """ Represents a single PDL file."""

    def __init__(self, path, input_type="f"):
        """
        Initialize a File object from a file's worth of PDL.

        The PDL file should contain exactly three fields:
          - name: the namespace that the file's contents belong in,
          - imports: a list of imports that the file's contents use,
          - body: the body of PDL.

        Parameters
        ==========

        path: string
            path should contain either the path to the file containing PDL,
            or a string that contains a valid PDL file by itself (mostly for
            testing purpoeses).

        input_type: char
            input_type indicates whether the argument provided to "path" is
            a file (f) path or a string (s).

        Instantiating a File automatically validates its contents; a successful
        initialization produces a ready-to-use File.

        Fields
        ======

        imports: list
            list of imports (by name) that are relevant to this file.

        typedefs: dict
            dict of {typedef name: typedef body}, used to access typedef
            definitions by name.

        components: list
            list of PDL component bodies, stored as objects.

        graphs: list
            list of PDL graph bodies, stored as objects.
        """
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
        self.components = []
        self.graphs = []
        self.validate()

    def validate(self):
        """ Validate the PDL contents of the File."""

        for entry in self.body:
            e_type = list(entry.keys())[0]
            if e_type not in self.type_checks:
                raise exceptions.BadInputError(f"invalid input type {e_type}")

            body = entry[e_type]
            self.type_checks[e_type](body)

    def validate_typedef(self, entry):
        """ Validate typedef entries specifically."""

        check_fields(["params", "name", "edges", "states"], entry)
        name = entry["name"]
        self.typedefs[name] = entry

    def validate_component(self, entry):
        """ Validate component entries specifically."""

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

        self.components.append(entry)

    # This setup doesn't allow for hoisting (i.e. defining a typedef after a component that
    # references it).
    def validate_type_entry(self, entry):
        """ Validate typedef implementation components specifically."""
        check_fields(["name", "type", "params"], entry)
        def_type = entry["type"]
        # a "." indicates it's an import, which will be checked later.
        if "." in def_type:
            self.components.append(entry)
            return
        if def_type not in self.typedefs:
            raise exceptions.BadInputError(f"typedef {def_type} not found; hoisting not allowed")

        params = self.typedefs[def_type]["params"]
        if len(params) != len(entry):
            raise exceptions.BadInputError(f"not all params ({params}) present in component "
                                           "declaration")

        for param in params:
            if param not in entry["params"]:
                raise exceptions.BadInputError(f"param {param} not found")

        self.components.append(entry)

    def validate_graph(self, entry):
        """ Validate graph entries specifically."""
        check_fields(["name", "nodes", "states"], entry)
        for node_name in entry["nodes"]:
            node = entry["nodes"][node_name]
            if len(node) < 1 or "components" not in node:
                raise exceptions.BadInputError(f"invalid entry for {node_name}: {node}")

        self.graphs.append(entry)
