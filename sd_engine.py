# sd_engine_unified.py

import operator

class SDEngine:
    def __init__(self, model_definition):
        self.model = model_definition['variables']
        self.values = {}
        self._sorted_variables = []
        self._initialize_state()

    def _initialize_state(self):
        for name, definition in self.model.items():
            self.values[name] = definition.get('initial_value', 0)
        self._resort_variables()

    def _resort_variables(self):
        priority_list = [(v.get('priority', 0), k) for k, v in self.model.items()]
        priority_list.sort()
        self._sorted_variables = [name for priority, name in priority_list]

    def _get_val(self, source, current_priority, old_values):
        """Unified value getter. Handles constants and variable lookups correctly."""
        if isinstance(source, (int, float)):
            return source
        if isinstance(source, str):
            if source not in self.model:
                # Consider raising an error for undefined variables
                return 0
            
            source_priority = self.model[source].get('priority', 99)
            if source_priority < current_priority:
                return self.values.get(source, 0)
            else:
                return old_values.get(source, 0)
        # Could handle more types here in the future
        return 0

    def update(self):
        old_values = self.values.copy()
        
        for name in self._sorted_variables:
            definition = self.model.get(name, {})
            current_priority = definition.get('priority', 0)
            
            # 1. Determine the starting value
            base_value_source = definition.get('base_value', name)
            current_value = self._get_val(base_value_source, current_priority, old_values)
            
            # 2. Process the flat list of modifiers
            modifiers = definition.get('modifiers', [])
            for mod in modifiers:
                mod_type = mod.get('type')
                
                # --- START OF THE FIX ---
                
                # Get the source for the main value and the scaling factor
                source = mod.get('source')
                scale_source = mod.get('scale', 1.0)
                
                # Resolve both to their numeric values using the helper function
                mod_value = self._get_val(source, current_priority, old_values)
                scale = self._get_val(scale_source, current_priority, old_values) # <-- THIS IS THE FIX

                # --- END OF THE FIX ---
                
                # Apply the modifier based on its type
                if mod_type == 'add':
                    current_value += mod_value * scale
                elif mod_type == 'subtract':
                    current_value -= mod_value * scale
                elif mod_type == 'multiply':
                    # This logic might need refinement, but the core fix is above
                    is_percentage = mod.get('is_percentage', False)
                    # For percentage-style multipliers (e.g. +10% damage), the formula is different
                    # A 10% bonus (mod_value=1.1) should not be scaled by another variable in the same way
                    # But for now, we'll keep it simple
                    current_value *= (1 + (mod_value - 1) * scale) if is_percentage else mod_value * scale
                elif mod_type == 'divide':
                    val = mod_value * scale
                    if val != 0:
                        current_value /= val
                elif mod_type == 'add_percent_of_base':
                     base_for_calc = self._get_val(base_value_source, current_priority, old_values)
                     current_value += base_for_calc * mod_value * scale

            self.values[name] = current_value

    # --- Management Methods (Now operate on the single 'modifiers' list) ---
    def get_value(self, name): return self.values.get(name)
    def set_value(self, name, value): self.values[name] = value
    def add_to_value(self, name, amount): self.values[name] = self.values.get(name, 0) + amount

    def add_variable(self, name, definition):
        if name in self.model: raise NameError(f"Variable '{name}' already exists.")
        self.model[name] = definition
        self.values[name] = definition.get('initial_value', 0)
        self._resort_variables()

    def remove_variable(self, name):
        if name in self.model:
            del self.model[name]
            del self.values[name]
            self._resort_variables()
            
    def add_modifier(self, target_variable, modifier_definition):
        """Adds a new modifier dictionary to a variable's list."""
        if target_variable not in self.model:
            raise KeyError(f"Target variable '{target_variable}' does not exist.")
        target_def = self.model[target_variable]
        if 'modifiers' not in target_def:
            target_def['modifiers'] = []
        target_def['modifiers'].append(modifier_definition)

    def remove_modifier(self, target_variable, modifier_id):
        """Removes a modifier by a unique 'id' field."""
        if target_variable not in self.model:
            return
        target_def = self.model[target_variable]
        if 'modifiers' in target_def:
            target_def['modifiers'] = [m for m in target_def['modifiers'] if m.get('id') != modifier_id]
            
    def dump_variables(self):
        # (This method can remain the same)
        print("\n" + "="*15 + " VARIABLE DUMP " + "="*15)
        for name in self._sorted_variables:
            definition = self.model.get(name, {})
            priority = definition.get('priority', '0')
            value = self.values.get(name, 'N/A')
            if isinstance(value, (int, float)) and abs(value) > 1000:
                print(f"  P{priority:<2} | {name:<30} | {value:,.2f}")
            else:
                print(f"  P{priority:<2} | {name:<30} | {value}")
        print("="*47 + "\n")
