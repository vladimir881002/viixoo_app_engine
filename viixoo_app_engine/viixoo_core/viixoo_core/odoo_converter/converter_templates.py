"""
    This file contains templates for the converter. 
    It is used to generate the code for the converter.
"""

# Do NOT modify string indentation. It is used to generate the code correctly.

class CODE_TPL:
    @classmethod
    def get_compute_store_property(cls, field_name: str, method_name:str, python_type: str,
                              depends_doc: str, field_args: list) -> str:
        """
            Generates a default property for a field
            
            param field_name: The name of the field
            param return_type: The return type of the property
            
            return: The generated default property code template as a string
        """
        # Get depends fields if any
        depends = field_args.get('compute_depends', [])
        depends_doc = f"\n        Depends on: {', '.join(depends)}" if depends else ""
        
        template = f"""
    @property
    def {field_name}(self) -> {python_type}:
        '''
        Computed field from Odoo method: {method_name}{depends_doc}
        '''
        pass

    @{field_name}.setter
    def {field_name}(self, value: {python_type}) -> None:
        self._{field_name} = value"""

        return template        
            
    @classmethod
    def get_compute_property(cls, field_name: str, method_name:str, python_type: str,
                              depends_doc: str) -> str:
        template = f"""
    @property
    def {field_name}(self) -> {python_type}:
        '''
        Computed field from Odoo method: {method_name}{depends_doc}
        '''
        pass"""
        return template

    @classmethod
    def get_default_method(cls, method_name: str, field_name: str, return_type: str) -> str:
        """
        Generates a default method for a field
        
        param method_name: The name of the method
        param field_name: The name of the field
        param return_type: The return type of the method
        
        return: The generated default method code template as a string
        """
        default_method = f"""
    @classmethod
    def {method_name}(cls) -> {return_type}:
        '''
        TODO: Implement this default method
        This is a placeholder for the original Odoo method: {method_name}
        '''
        # Original Odoo method name: {method_name}
        # use as default for field {field_name}
        return None  # Replace with actual default value
        """
        return default_method
