import copy
import os
import warnings

import yaml

import topside as top
from topside.pdl import exceptions, utils

# imports is a dict of {package name: path to file}, used to locate files to load
# on requested import.

# TODO: make importing more efficent by having a YAML file storing the self.importable_files dict
# and updating whenever a Package is instantiated

# TODO; Make the importing code more unit testable


class Package:
    """Package represents a collection of files that make a coherent plumbing system."""

    def __init__(self, files):
        """
        Initialize a Package from one or more Files.

        A Package should have all the components of a complete plumbing engine system; from
        here no additional information will make it into the PlumbingEngine. Once instantiated,
        a Package's PDL is cleaned and ready to use.

        Parameters
        ----------

        files: iterable
            files is an iterable (usually a list) of one or more Files whose contents should go
            into the Package.
        """
        self.importable_files = dict()

        imports_folder = os.listdir(utils.imports_path)

        for imported_file in imports_folder:

            path = os.path.join(utils.imports_path, imported_file)
            try:
                name = yaml.safe_load(open(path, 'r'))['name']

                if (name in self.importable_files):
                    self.importable_files[name].add(path)
                else:
                    self.importable_files[name] = {path}
            except (KeyError):
                warnings.warn(path + " does not describe a pdl file")

        if len(list(files)) < 1:
            raise exceptions.BadInputError("cannot instantiate a Package with no Files")
        self.imports = []

        # dicts of {namespace: [entries]}, where entry is a PDL object. Organized like this to
        # reduce dict nesting; since this is a one time process it should be easy to keep
        # them synced.
        self.typedefs = {}
        self.component_dict = {}
        self.graph_dict = {}

        for file in files:
            # TODO(wendi): unused import detection
            self.imports.extend(copy.deepcopy(file.imports))

        for imp in set(self.imports):
            if imp not in self.importable_files:
                raise exceptions.BadInputError(f"invalid import: {imp}")
            for path in self.importable_files[imp]:
                files.append(top.File(path))

        # consolidate entry information from files
        for file in files:
            name = file.namespace
            if name not in self.typedefs:
                self.typedefs[name] = {}
                self.component_dict[name] = []
                self.graph_dict[name] = []
            self.typedefs[name].update(copy.deepcopy(file.typedefs))
            self.component_dict[name].extend(copy.deepcopy(file.components))
            self.graph_dict[name].extend(copy.deepcopy(file.graphs))

        self.clean()

    def clean(self):
        """Change user-friendly PDL shortcuts into the verbose PDL standard."""

        # preprocess typedefs
        for namespace in self.typedefs:
            for idx, component in enumerate(self.component_dict[namespace]):
                if 'type' in component:
                    self.component_dict[namespace][idx] = self.fill_typedef(namespace, component)

        # clean PDL shortcuts
        for namespace, entries in self.component_dict.items():
            for idx, component in enumerate(entries):
                # deal with single state shortcuts
                if 'states' not in component:
                    self.component_dict[namespace][idx] = unpack_single_state(component)

                # unpack single teq direction shortcuts
                self.component_dict[namespace][idx] = unpack_teq(component)

        self.rename()

        default_states = self.get_default_states()

        for namespace, entries in self.graph_dict.items():
            for entry in entries:
                self.fill_blank_states(entry, default_states)

    def rename(self):
        """Prepend any conflicting component names with namespace to disambiguate."""

        # record of {component name: namespace}
        names = set()

        # record of which components were repeated (and need prepending)
        repeats = {}
        for namespace, entries in self.component_dict.items():
            for entry in entries:
                name = entry['name']
                if name in names:
                    repeats[name] = True
                else:
                    names.add(name)

        for namespace, entries in self.component_dict.items():
            for idx, entry in enumerate(entries):
                name = entry['name']
                if name in repeats:
                    self.component_dict[namespace][idx]['name'] = namespace + '.' + name

    def fill_typedef(self, namespace, component):
        """Fill in typedef template for components invoking a typedef."""
        name = component['type']
        component_name = component['name']

        if name.count('.') > 1:
            raise NotImplementedError(f"nested imports (in {name}) not supported yet")

        # handle imported components
        if '.' in name:
            # NOTE: we might eventually want to consider how well this will play with nested imports
            fields = name.split('.')
            namespace = fields[0]
            name = fields[-1]
        if name not in self.typedefs[namespace]:
            raise exceptions.BadInputError(f"invalid component type: {name}")

        params = component['params']
        body = yaml.dump(self.typedefs[namespace][name])

        for var, value in params.items():
            body = body.replace(var, str(value))

        ret = yaml.safe_load(body)
        ret.pop('params')
        ret['name'] = component_name
        return ret

    def fill_blank_states(self, graph, default_states):
        """Fill in states field with default states if left blank."""
        if 'states' not in graph:
            graph['states'] = {}

        # set of components in this graph
        components = set()
        for node in graph['nodes'].values():
            for component in node['components']:
                components.add(component[0])

        for component in components:
            if component in graph['states']:
                continue

            if component not in default_states:
                raise exceptions.BadInputError(
                    f"missing component {component}: either a nonexistent or a"
                    "multi-state component")

            graph['states'][component] = default_states[component]

    def get_default_states(self):
        """Return a dict of {component_name: default state name} for one-state components"""
        # dict of {component:(namespace, index)} used to locate the component in self.component_dict
        places = {}
        for namespace in self.component_dict:
            for idx, component in enumerate(self.component_dict[namespace]):
                places[component['name']] = (namespace, idx)

        default_states = {}
        for component in self.components():
            namespace, idx = places[component['name']]
            component_states = self.component_dict[namespace][idx]['states']
            if len(component_states) == 1:
                default_states[component["name"]] = list(component_states.keys())[0]

        return default_states

    def components(self):
        """Return list of all component objects"""
        components = []
        for component_list in self.component_dict.values():
            components.extend(component_list)
        return components

    def graphs(self):
        """Return a list of all graph objects"""
        graphs = []
        for graph_list in self.graph_dict.values():
            graphs.extend(graph_list)
        return graphs


def unpack_teq(component):
    """Replace single-direction teq shortcut with verbose teq."""
    ret = component
    for state, edges in component['states'].items():
        for edge, teq in edges.items():
            if isinstance(teq, dict):
                continue
            long_teq = {}
            long_teq['fwd'] = teq
            long_teq['back'] = teq
            ret['states'][state][edge] = long_teq
    return ret


def unpack_single_state(component):
    """Replace single-state shortcut with verbose states entry."""
    ret = component
    states = {'default': {}}
    for edge, specs in component['edges'].items():
        states['default'][edge] = specs['teq']
        ret['edges'][edge].pop('teq')
    ret['states'] = states
    return ret
