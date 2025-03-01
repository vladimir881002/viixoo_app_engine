import ast
import argparse
from pathlib import Path
from typing import Dict, Optional, List
import sys

from viixoo_core.odoo_converter.converter_templates import CODE_TPL


"""
Convert Odoo models to Pydantic models. This script reads Odoo model definitions from a Python file 
and generates Pydantic models in a new Python file. The generated Pydantic models are based on the
fields defined in the Odoo models. The script can process a single Python file or an entire directory

usage: converter.py [-h] -i INPUT -o OUTPUT [--prefix PREFIX] [--suffix SUFFIX]

Convert Odoo models to Pydantic models

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        Input Python file containing Odoo models or directory containing multiple model files
  -o OUTPUT, --output OUTPUT
                        Output directory for generated Pydantic models
  --prefix PREFIX       Prefix to add to generated model files (default: none)
  --suffix SUFFIX       Suffix to add to generated model files (default: _pydantic)

"""


class OdooModelParser:
    def __init__(self):
        self.models: Dict[str, dict] = {}
        
    def parse_file(self, file_path: str) -> None:
        """Parse an Odoo model file and extract field definitions."""
        with open(file_path, 'r') as file:
            tree = ast.parse(file.read())
            
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                model_info = self._extract_model_info(node)
                if model_info:
                    self.models[model_info['name']] = model_info

    def _extract_model_info(self, node: ast.ClassDef) -> Optional[dict]:
        """Extract model information from a class definition."""
        model_info = {
            'name': node.name,
            'fields': {},
            '_name': None,
            '_inherit': None,
            '_description': None
        }
        
        # Check if it's an Odoo model
        is_odoo_model = False
        for base in node.bases:
            if isinstance(base, ast.Attribute):
                if base.attr in ('Model', 'AbstractModel', 'TransientModel'):
                    is_odoo_model = True
                    break
        
        if not is_odoo_model:
            return None

        for item in node.body:
            # Extract model attributes (_name, _inherit, _description)
            if isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        if target.id in ('_name', '_inherit', '_description', '_order'):
                            if isinstance(item.value, ast.Constant):
                                model_info[target.id] = item.value.value
            
                # Extract field definitions
                if isinstance(item.value, ast.Call) and len(item.targets) > 0:
                    field_name = item.targets[0].id
                    field_type = self._get_field_type(item.value)
                    field_args = self._get_field_args(item.value)
                    model_info['fields'][field_name] = {
                        'type': field_type,
                        'args': field_args
                    }
            
        return model_info
    
    def _get_field_type(self, node: ast.Call) -> str:
        """Extract the field type from a fields.* call."""
        if isinstance(node.func, ast.Attribute):
            if node.func.attr == 'Selection':
                # Get selection values if they are directly defined
                selection_values = self._get_selection_values(node)
                if selection_values:
                    return f"Selection:{selection_values}"
            elif node.func.attr in ('One2many', 'Many2many', 'Many2one'):
                # Get the comodel name from the first argument
                if node.args and isinstance(node.args[0], ast.Constant):
                    return f"{node.func.attr}:{node.args[0].value}"
            return node.func.attr
        return 'Unknown'
    
    def _get_field_args(self, node: ast.Call) -> dict:
        """Extract field arguments (string, required, etc.)."""
        args = {}
        # Extract positional arguments for relationship fields
        if isinstance(node.func, ast.Attribute) and node.func.attr in ('One2many', 'Many2many', 'Many2one'):
            args['comodel_name'] = node.args[0].value if node.args else None
            if len(node.args) > 1 and isinstance(node.args[1], ast.Constant):
                args['relation_field'] = node.args[1].value
            if len(node.args) > 2 and isinstance(node.args[2], ast.Constant):
                args['relation_table'] = node.args[2].value

        # Extract keyword arguments
        for kw in node.keywords:
            if isinstance(kw.value, ast.Constant):
                args[kw.arg] = kw.value.value

            elif isinstance(kw.value, ast.Name):
                # Handle method reference (e.g., default=_get_default_color)
                if kw.arg == 'default':
                    args['default_factory'] = 'None'
                    args['default_method'] = kw.value.id
                # Handle compute and method references
                elif kw.arg == 'compute':
                    args['compute_method'] = kw.value.id
                    # Check for store parameter
                    for other_kw in node.keywords:
                        if other_kw.arg == 'store':
                            if isinstance(other_kw.value, ast.Constant):
                                args['compute_store'] = other_kw.value.value
                elif kw.arg == 'depends':
                    args['compute_depends'] = kw.value.id                
                else:
                    args[kw.arg] = kw.value.id
            
            elif isinstance(kw.value, ast.List):
                # Handle depends parameter when it's a list
                if kw.arg == 'depends':
                    depends = []
                    for elt in kw.value.elts:
                        if isinstance(elt, ast.Constant):
                            depends.append(elt.value)
                    args['compute_depends'] = depends
            
            elif isinstance(kw.value, ast.Call):
                # Handle function calls as default values
                if isinstance(kw.value.func, ast.Name):
                    args[f"{kw.arg}_factory"] = kw.value.func.id
                elif isinstance(kw.value.func, ast.Attribute):
                    # Handle cases like datetime.now
                    if isinstance(kw.value.func.value, ast.Name):
                        args[f"{kw.arg}_factory"] = f"{kw.value.func.value.id}.{kw.value.func.attr}"
            elif isinstance(kw.value, ast.Lambda):
                # Handle lambda functions
                args[f"{kw.arg}_factory"] = 'None'
                args['lambda_default'] = True
        return args
    
    def _get_selection_values(self, node: ast.Call) -> Optional[str]:
        """Extract selection values from a Selection field definition."""
        if node.args:
            first_arg = node.args[0]
            if isinstance(first_arg, ast.List) or isinstance(first_arg, ast.Tuple):
                # Handle direct list/tuple of selection values
                values = []
                for elt in first_arg.elts:
                    if isinstance(elt, ast.Tuple) and len(elt.elts) == 2:
                        key = elt.elts[0]
                        value = elt.elts[1]
                        if isinstance(key, ast.Constant) and isinstance(value, ast.Constant):
                            values.append((key.value, value.value))
                return str(values)
            elif isinstance(first_arg, ast.Name) or isinstance(first_arg, ast.Attribute):
                # Handle function reference for selection values
                return "dynamic"
        return None


class PydanticModelGenerator:
    def __init__(self):
        self.type_mapping = {
            'Binary': ('bytes', None),           
            'Boolean': ('bool', None),
            'Char': ('str', None),
            'Date': ('date', 'from datetime import date'),
            'Datetime': ('datetime', 'from datetime import datetime'),
            'Float': ('float', None),
            'Html': ('str', None),
            'Integer': ('int', None),            
            'Monetary': ('Decimal', 'from decimal import Decimal'),
            'Text': ('str', None)
        }
        # Track used types across all models
        self.used_types = set()
        self.has_enums = False
        self.has_lists = False
        self.has_optionals = False
        self.has_forward_refs = False
        self.has_any = False
        self.used_factories = set()

    def generate_model_file(self, models: Dict[str, dict], output_path: str) -> None:
        """Generate a Python file with Pydantic models."""
        # Reset type tracking for new file generation
        self.used_types.clear()
        self.has_enums = False
        self.has_lists = False
        self.has_optionals = False
        self.has_forward_refs = False
        self.has_any = False

        # First pass to collect all model names for forward references
        model_names = {model_info['_name']: name 
                      for name, model_info in models.items() 
                      if model_info['_name']}
        
        model_code = []

        # Check if we need forward refs
        need_forward_refs = self._check_need_forward_refs(models)
        if need_forward_refs:
            self.has_forward_refs = True
            forward_refs = []
            for model_name in models.keys():
                forward_refs.append(f"{model_name}Model = ForwardRef('{model_name}Model')\n")
            model_code.extend(forward_refs)
            model_code.append('')

        # Generate model classes
        for model_name, model_info in models.items():
            model_code.append(self._generate_model_class(
                model_name, 
                model_info,
                model_names
            ))

        # Generate imports based on used types
        imports = self._generate_imports(models=models)
        
        # Write the file
        with open(output_path, 'w') as f:
            # Write imports
            f.write('\n'.join(sorted(imports)))
            f.write('\n\n')
            # Write models
            f.write(''.join(model_code))            
            # Add update_forward_refs() calls if needed
            if need_forward_refs:
                f.write('\n\n# Update forward references\n')
                for model_name in models.keys():
                    f.write(f"{model_name}Model.update_forward_refs()\n")

    def _check_need_forward_refs(self, models: Dict[str, dict]) -> bool:
        """Check if we need forward refs by looking for circular dependencies."""
        model_refs = {name: set() for name in models.keys()}
        
        for model_name, model_info in models.items():
            for field_info in model_info['fields'].values():
                field_type = field_info['type']
                if ':' in field_type:
                    _, comodel = field_type.split(':')
                    for other_name, other_info in models.items():
                        if other_info['_name'] == comodel:
                            model_refs[model_name].add(other_name)
        
        # Check for circular dependencies
        for model_name in models:
            visited = set()
            if self._has_circular_ref(model_name, model_refs, visited):
                return True
        return False

    def _has_circular_ref(self, model_name: str, model_refs: Dict[str, set], 
                         visited: set) -> bool:
        """Helper function to detect circular dependencies."""
        if model_name in visited:
            return True
        visited.add(model_name)
        for ref in model_refs[model_name]:
            if self._has_circular_ref(ref, model_refs, visited.copy()):
                return True
        return False

    def _generate_imports(self, models) -> List[str]:
        """Generate import statements based on used types."""
        imports = set()
        
        # Always import BaseModel and Field from pydantic
        imports.add('from pydantic import Field')
        
        # Add imports based on used types
        type_imports = set()
        for type_name in self.used_types:
            for odoo_type, (_, import_stmt) in self.type_mapping.items():
                if import_stmt and type_name == self.type_mapping[odoo_type][0]:
                    type_imports.add(import_stmt)
        
        imports.update(type_imports)

        # Add factory imports
        for factory in self.used_factories:
            if '.' in factory:
                module, func = factory.split('.')
                if module == 'datetime' or f"{module}".replace('Model', '') in models:
                    # datetime already imported if needed
                    continue
                imports.add(f'from {module} import {func}')
        
        # Add typing imports
        typing_imports = []
        if self.has_optionals:
            typing_imports.append('Optional')
        if self.has_lists:
            typing_imports.append('List')
        if self.has_any:
            typing_imports.append('Any')
        if self.has_forward_refs:
            typing_imports.append('ForwardRef')
            
        if typing_imports:
            imports.add(f'from typing import {", ".join(sorted(typing_imports))}')
            
        # Add enum import if needed
        if self.has_enums:
            imports.add('from enum import Enum')
        
        # Add PostgresModel import
        imports.add('from viixoo_core.models.postgres import PostgresModel')
        # Add separator between imports and model code
        return sorted(imports)
    
    def _generate_compute_method(self, field_name: str, method_name: str, 
                               python_type: str, is_stored: bool,
                               field_args: dict) -> str:
        """Generate a compute method using the template if available."""
        
        # Get depends fields if any
        depends = field_args.get('compute_depends', [])
        depends_doc = f"\n        Depends on: {', '.join(depends)}" if depends else ""
        
        if is_stored:
            return CODE_TPL.get_compute_store_property(
                field_name=field_name,
                method_name=method_name,
                python_type=python_type,
                depends_doc=depends_doc,
                field_args=field_args
            )
        else:
            return CODE_TPL.get_compute_property(
                field_name=field_name,
                method_name=method_name,
                python_type=python_type,
                depends_doc=depends_doc
            )
    
    def _generate_model_class(self, model_name, model_info: dict, model_names: Dict[str, str]) -> str:
        """Generate a single Pydantic model class."""
        lines = [f"\n\n\nclass {model_name}Model(PostgresModel):"]
        # Track enums for this model
        model_enums, default_methods, compute_methods  = [], [], []
        line_brake = False
        computed_fields = set()

        if model_info.get('_description'):
            lines.append(f'    """{model_info["_description"]}"""')
            lines.append(f'    __description__ = "{model_info["_description"]}"')
            line_brake = True
        
        if model_info.get('_name'):
            lines.append(f'    __tablename__ = "{model_info["_name"].replace(".", "_")}"')
            line_brake = True
        
        if model_info.get('_order'):
            lines.append(f'    __order__ = "{model_info["_order"]}"')
            line_brake = True

        if line_brake:
            lines.append('\n')
        
        for field_name, field_info in model_info['fields'].items():
            field_type = field_info['type']
            field_args = field_info['args']

            # Handle default method
            if 'default_method' in field_args:
                method_name = field_args['default_method']
                default_method = CODE_TPL.get_default_method(
                    field_name=field_name,
                    method_name=method_name,
                    return_type=self.type_mapping.get(field_type, ('Any', None))[0]
                )
                default_methods.append(default_method)
                field_args['default_factory'] = f'{model_name}Model.{method_name}'
            
            # Handle Selection fields
            if field_type.startswith('Selection:'):
                selection_values = field_type.split(':', 1)[1]
                if selection_values == "dynamic":
                    # For dynamic selections, use str type
                    python_type = 'str'
                    self.used_types.add('str')
                else:
                    # Create an Enum for static selections
                    try:
                        values = eval(selection_values)
                        enum_name = f"{model_name}_{field_name}_enum"
                        enum_def = [f"\n\nclass {enum_name}(str, Enum):"]
                        for key, value in values:
                            # Clean the enum member name
                            member_name = (
                                str(key)
                                .upper()
                                .replace('-', '_')
                                .replace(' ', '_')
                                .replace('.', '_')
                            )
                            enum_def.append(f'    {member_name} = "{key}"  # {value}')
                        
                        model_enums.append('\n'.join(enum_def))
                        python_type = enum_name
                        self.has_enums = True
                    except (SyntaxError, ValueError):
                        # Fallback to str if there's an issue with the selection values
                        python_type = 'str'
                        self.used_types.add('str')
            
            # Handle relationship fields
            elif ':' in field_type:  # Relationship field
                field_type, comodel = field_type.split(':')
                if field_type in ('One2many', 'Many2many'):
                    related_model = model_names.get(comodel, 'Any')
                    if related_model == 'Any':
                        self.has_any = True
                    if related_model != 'Any':
                        related_model += 'Model'
                    python_type = f'List[{related_model}]'
                    self.has_lists = True
                    field_args['default_factory'] = 'list'
                elif field_type == 'Many2one':
                    related_model = model_names.get(comodel, 'Any')
                    if related_model == 'Any':
                        self.has_any = True
                    if related_model != 'Any':
                        related_model += 'Model'
                    python_type = f'Optional[{related_model}]'
                    self.has_optionals = True
            else:
                mapped_type = self.type_mapping.get(field_type, ('Any', None))
                python_type = mapped_type[0]
                if python_type == 'Any':
                    self.has_any = True
                else:
                    self.used_types.add(python_type)

            # Handle compute fields
            if 'compute' in field_args:
                method_name = field_args['compute']
                is_stored = field_args.get('store', False)
                
                if is_stored:
                    computed_fields.add(field_name)
                    compute_methods.append(
                        self._generate_compute_method(
                            field_name, method_name, python_type, 
                            is_stored, field_args
                        )
                    )                    
                    # Add private field for storage
                    field_def = f"    _{field_name}: {python_type}"
                    if 'string' in field_args:
                        field_def += f' = Field(description="{field_args["string"]}")'
                    lines.append(field_def)
                else:
                    compute_methods.append(
                        self._generate_compute_method(
                            field_name, method_name, python_type, 
                            is_stored, field_args
                        )
                    )
                continue
            
            # Handle optional fields
            required = not field_args.get('required', False)
            if required and 'List[' not in python_type:
                python_type = f'Optional[{python_type}]'
                self.has_optionals = True
            
            # Prepare field arguments
            field_params = []
            if 'string' in field_args:
                field_params.append(f'description="{field_args["string"]}"')

            # Handle default factory functions
            for arg_name, arg_value in field_args.items():
                if arg_name.endswith('_factory'):
                    base_name = arg_name.replace('_factory', '')
                    if '.' in arg_value:
                        self.used_factories.add(arg_value)
                    field_params.append(f'{base_name}_factory={arg_value}')
            
            # Generate field definition
            field_def = f'    {field_name}: {python_type}'
            if field_params:
                field_def += f' = Field({", ".join(field_params)})'
            
            lines.append(field_def)

        # Add default methods after field definitions
        if default_methods:
            lines.extend([''] + default_methods)

        # Add Config class if we have computed fields
        if computed_fields:
            config_lines = [
                "",
                "    class Config:",
                "        underscore_attrs_are_private = True"
            ]
            lines.extend(config_lines)
        
        # Add compute methods after field definitions
        if compute_methods:
            lines.extend([''] + compute_methods)
        
        if len(lines) == 1:
            lines.append('    pass')

        # Add enums before the model class if any were created
        if model_enums:
            return ''.join(model_enums + ['\n'.join(lines)])
            
        return '\n'.join(lines)
    


def setup_parser() -> argparse.ArgumentParser:
    """Set up command line argument parser."""
    parser = argparse.ArgumentParser(
        description='Convert Odoo models to Pydantic models',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '-i', '--input',
        required=True,
        help='Input Python file containing Odoo models or directory containing multiple model files'
    )
    
    parser.add_argument(
        '-o', '--output',
        required=True,
        help='Output directory for generated Pydantic models'
    )
    
    parser.add_argument(
        '--prefix',
        default='',
        help='Prefix to add to generated model files (default: none)'
    )
    
    parser.add_argument(
        '--suffix',
        default='_pydantic',
        help='Suffix to add to generated model files (default: _pydantic)'
    )
    
    return parser

def process_file(input_path: Path, output_dir: Path, prefix: str, suffix: str) -> None:
    """Process a single input file and generate corresponding Pydantic model file."""
    try:
        # Generate output filename
        output_filename = f"{prefix}{input_path.stem}{suffix}.py"
        output_path = output_dir / output_filename
        
        # Parse and convert
        parser = OdooModelParser()
        parser.parse_file(str(input_path))
        
        if not parser.models:
            print(f"No Odoo models found in {input_path}")
            return
        
        # Create output directory if it doesn't exist
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate Pydantic models
        generator = PydanticModelGenerator()
        generator.generate_model_file(parser.models, str(output_path))
        
        print(f"Successfully converted {input_path} -> {output_path}")
        
    except Exception as e:
        print(f"Error processing {input_path}: {str(e)}", file=sys.stderr)

def main():
    """Main entry point for the converter."""
    parser = setup_parser()
    args = parser.parse_args()
    
    # Convert paths to Path objects
    input_path = Path(args.input)
    output_path = Path(args.output)
    
    if not input_path.exists():
        print(f"Error: Input path '{input_path}' does not exist", file=sys.stderr)
        sys.exit(1)
    
    # Handle single file
    if input_path.is_file():
        if not input_path.suffix == '.py':
            print("Error: Input file must be a Python file (.py)", file=sys.stderr)
            sys.exit(1)
        process_file(input_path, output_path, args.prefix, args.suffix)
    
    # Handle directory
    elif input_path.is_dir():
        python_files = list(input_path.glob('**/*.py'))
        if not python_files:
            print(f"No Python files found in {input_path}", file=sys.stderr)
            sys.exit(1)
        
        for py_file in python_files:
            # Skip __init__.py files
            if py_file.name == '__init__.py':
                continue
            process_file(py_file, output_path, args.prefix, args.suffix)
    
    else:
        print(f"Error: Input path '{input_path}' is neither a file nor a directory", 
              file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
