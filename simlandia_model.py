# simlandia_model.py

model_definition = {
  "variables": {
    # --- PARAMETERS (No base_value, no modifiers, no priority) ---
    "tax_rate": { "initial_value": 0.25 },
    "gdp_per_capita": { "initial_value": 40000 },
    "base_birth_rate": { "initial_value": 0.02 },
    "base_death_rate": { "initial_value": 0.01 },
    "base_spending": { "initial_value": 50e9 },
    "min_unemployment": { "initial_value": 0.02 },
    "stability_target": { "initial_value": 80 },

    # --- PRIORITY 1: Converters ---
    "gdp": { "priority": 1, "base_value": "population", "multiplicative_modifiers": ["gdp_per_capita"]},
    "tax_revenue": { "priority": 1, "base_value": "gdp", "multiplicative_modifiers": ["tax_rate"]},
    "unemployment_from_taxes": { "priority": 1, "base_value": "tax_rate", "multiplicative_modifiers": [0.5] },
    "unemployment_from_stability": { "priority": 1, "base_value": "stability", "multiplicative_modifiers": [-0.0005] },
    "unemployment_rate": { "priority": 1, "base_value": "min_unemployment", "additive_modifiers": ["unemployment_from_taxes", "unemployment_from_stability"]},
    "stability_pressure_from_unemployment": { "priority": 1, "base_value": "unemployment_rate", "multiplicative_modifiers": [-200]},

    # --- PRIORITY 2: Flows ---
    "births": { "priority": 2, "base_value": "population", "multiplicative_modifiers": ["base_birth_rate"]},
    "deaths": { "priority": 2, "base_value": "population", "multiplicative_modifiers": ["base_death_rate"]},
    "treasury_change": { "priority": 2, "base_value": "tax_revenue", "subtractive_modifiers": ["base_spending"]},
    "stability_change": { "priority": 2, "base_value": "stability_target", "subtractive_modifiers": ["stability"], "additive_modifiers": ["stability_pressure_from_unemployment"], "multiplicative_modifiers": [0.2]},

    # --- PRIORITY 3: Stocks (No base_value) ---
    "population": { "priority": 3, "initial_value": 10_000_000, "additive_modifiers": ["births"], "subtractive_modifiers": ["deaths"]},
    "treasury": { "priority": 3, "initial_value": 200e9, "additive_modifiers": ["treasury_change"]},
    "stability": { "priority": 3, "initial_value": 75, "additive_modifiers": ["stability_change"]},
  }
}
