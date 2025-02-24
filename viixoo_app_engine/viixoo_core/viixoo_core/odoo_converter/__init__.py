"""
This module contains the OdooConverter class which is used to convert Odoo models to Viixoo models.

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
  -m: The name of the model to be converted. (TODO: Add support for m parameter)

How to use this module:
1. Using command line:
    -Run converter.py with the following arguments:
        python converter.py -i './odoo/addons/base/models/res_partner.py' -o './converted_models'
"""

from . import converter
