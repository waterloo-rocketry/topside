import os

pdl_path = os.path.dirname(__file__)
example_path = os.path.join(pdl_path, "example.yaml")
default_path = os.path.join(pdl_path, "imports")
default_paths = [default_path]

imports_alt_folder = os.path.join("tests", "imports_alt")
alt_path = os.path.join(pdl_path, imports_alt_folder)
