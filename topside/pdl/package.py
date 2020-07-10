import copy
import yaml

import topside as top
import topside.pdl.exceptions as exceptions

# imports is a dict of {package name: path to file}, used to locate files to load
# on requested import.

# TODO(wendi): make imports more dynamic, so that users can add importable files
# outside a predefined library. Likely involves a function that traipses through the
# imports folder for new files and stores them in this dict whenever new Packages are instantiated.
IMPORTS = {
    'stdlib': './topside/pdl/imports/stdlib.yaml'
}


class Package:
    """Package represents a collection of files that make a coherent plumbing system."""

    def __init__(self, files):
        """
        Initialize a Package from one or more Files.

        A Package should have all the components of a complete plumbing engine system; from
        here no additional information will make it into the PlumbingEngine. Once instantiated,
        a Package's PDL is cleaned and ready to use.

        Parameters
        ==========

        files: list
            files is the list of one or more Files whose contents should go into the Package.
        """

        if len(files) < 1:
            raise exceptions.BadInputError("cannot instantiate a Package with no Files")
        self.imports = []

        # dicts of {namespace: [entries]}, where entry is a PDL object. Organized like this to
        # reduce dict nesting; since this is a one time process it should be easy to keep
        # them synced.
        self.typedefs = {}
        self.components = {}
        self.graphs = {}

        for file in files:
            # TODO(wendi): unused import detection
            self.imports.extend(copy.deepcopy(file.imports))

        for imp in set(self.imports):
            if imp not in IMPORTS:
                raise exceptions.BadInputError(f"invalid import: {imp}")
            files.append(top.File(IMPORTS[imp]))

        # consolidate entry information from files
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
        """Change user-friendly PDL shortcuts into the verbose PDL standard."""

        # preprocess typedefs
        for namespace in self.typedefs:
            for idx, component in enumerate(self.components[namespace]):
                if 'type' in component:
                    self.components[namespace][idx] = self.fill_typedef(namespace, component)

        # clean PDL shortcuts
        for namespace in self.components:
            for idx, component in enumerate(self.components[namespace]):
                # deal with single state shortcuts
                if 'states' not in component:
                    self.components[namespace][idx] = unpack_single_state(component)

                # unpack single teq direction shortcuts
                self.components[namespace][idx] = unpack_teq(component)

        # prepend any conflicting names with namespace to disambiguate
        names = {}
        repeats = {}
        for namespace, entries in self.components.items():
            for entry in entries:
                name = entry['name']
                if name in names:
                    repeats[name] = True
                else:
                    names[name] = namespace

        for namespace, entries in self.components.items():
            for idx, entry in enumerate(entries):
                name = entry['name']
                if name in repeats:
                    self.components[namespace][idx]['name'] = namespace + '.' + name


    def fill_typedef(self, namespace, component):
        """Fill in typedef template for components invoking a typedef."""
        name = component['type']
        if name.count('.') > 1:
            raise NotImplementedError(f"nested imports (in {name}) not supported yet")
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
        return ret


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
