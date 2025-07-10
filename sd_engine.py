# sd_engine.py

import operator
from functools import reduce

class SDEngine_Eventful:
    def __init__(self, model_definition):
        self.model = model_definition['variables']
        self.values = {}
        self._sorted_variables = []
        self._initialize_state()

    def _initialize_state(self):
        """Initializes all values and creates the single sorted list."""
        for name, definition in self.model.items():
            self.values[name] = definition.get('initial_value', 0)
        self._resort_variables()

    def _resort_variables(self):
        """Re-sorts the single master list of variables."""
        priority_list = [(v.get('priority', 0), k) for k, v in self.model.items()]
        priority_list.sort()
        self._sorted_variables = [name for priority, name in priority_list]

    def update(self):
        """Advance the simulation using the new base_value rule."""
        old_values = self.values.copy()
        
        for name in self._sorted_variables:
            definition = self.model.get(name, {})
            current_priority = definition.get('priority', 0)
            
            # --- THE NEW UNIFIED CALCULATION ---
            base_var = definition.get('base_value')
            
            # THE NEW RULE: If no base_value is specified, default to the variable's own previous value.
            base_value = self._get_mod_val(base_var, current_priority, old_values) if base_var else old_values.get(name, 0)

            add = sum(self._get_mod_val(m, current_priority, old_values) for m in definition.get('additive_modifiers', []))
            sub = sum(self._get_mod_val(m, current_priority, old_values) for m in definition.get('subtractive_modifiers', []))
            mul = reduce(operator.mul, [self._get_mod_val(m, current_priority, old_values, 1) for m in definition.get('multiplicative_modifiers', [])], 1)
            
            self.values[name] = (base_value + add - sub) * mul

    def _get_mod_val(self, modifier, current_priority, old_values, default=0):
        # This logic remains the same and is still crucial
        if isinstance(modifier, (int, float)): return modifier
        if isinstance(modifier, str):
            if modifier not in self.model: return default
            modifier_priority = self.model[modifier].get('priority', 99)
            if modifier_priority < current_priority: return self.values.get(modifier, default)
            else: return old_values.get(modifier, default)
        return default

    # All other methods (get_value, set_value, add_variable, etc.) are unchanged.
    # add_variable and remove_variable must still call _resort_variables().
    def get_value(self, name): return self.values.get(name)
    def set_value(self, name, value): self.values[name] = value
    def add_to_value(self, name, amount): self.values[name] = self.values.get(name, 0) + amount
    def multiply_value(self, name, factor): self.values[name] = self.values.get(name, 0) * factor
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
    def add_modifier(self, target_variable, modifier_type, modifier):
        target_def = self.model.get(target_variable)
        if modifier_type not in target_def: target_def[modifier_type] = []
        target_def[modifier_type].append(modifier)
    def remove_modifier(self, target_variable, modifier):
        target_def = self.model.get(target_variable)
        for mod_type in ['additive_modifiers', 'subtractive_modifiers', 'multiplicative_modifiers']:
            if mod_type in target_def:
                target_def[mod_type] = [m for m in target_def[mod_type] if m != modifier]

    def dump_variables(self):
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
