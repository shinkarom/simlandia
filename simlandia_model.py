# simlandia_model_unified.py

model_definition = {
  "variables": {
    # --- PARAMETERS (No base_value, no modifiers) ---
    "tax_rate": { "initial_value": 0.25 },
    "infrastructure_spending_level": { "initial_value": 1.0 },
    "social_spending_level": { "initial_value": 1.0 },
    "base_infra_spending": { "initial_value": 25e9 },
    "base_social_spending": { "initial_value": 60e9 },
    "base_admin_cost": { "initial_value": 40e9 },
    "infra_investment_efficiency": { "initial_value": 0.05 },
    "social_spending_stability_factor": { "initial_value": 15 },
    "base_birth_rate": { "initial_value": 0.02 },
    "base_death_rate": { "initial_value": 0.01 },
    "min_unemployment": { "initial_value": 0.02 },
    "stability_target": { "initial_value": 80 },

    # --- STOCKS (Accumulators) ---
    # Stocks now use `base_value: name` to signify they accumulate.
    "population":     { "priority": 3, "initial_value": 10_000_000 },
    "treasury":       { "priority": 3, "initial_value": 200e9 },
    "stability":      { "priority": 3, "initial_value": 75 },
    "gdp_per_capita": { "priority": 3, "initial_value": 40000 },

    # --- CONVERTERS & FLOWS ---
    "gdp": { 
        "priority": 1, 
        "base_value": "population", # Start with population...
        "modifiers": [
            {"type": "multiply", "source": "gdp_per_capita"} # ...and multiply by GDP per capita.
        ]
    },
    "tax_revenue": { 
        "priority": 1, 
        "base_value": "gdp",
        "modifiers": [
            {"type": "multiply", "source": "tax_rate"}
        ]
    },
    "total_spending": {
        "priority": 1,
        "base_value": "base_admin_cost", # Start with fixed costs...
        "modifiers": [
            # ...then add the variable spending components.
            {"type": "add", "source": "base_infra_spending", "scale": "infrastructure_spending_level"},
            {"type": "add", "source": "base_social_spending", "scale": "social_spending_level"}
        ]
    },
    "unemployment_rate": {
        "priority": 1,
        "base_value": "min_unemployment",
        "modifiers": [
            {"type": "add", "source": "tax_rate", "scale": 0.5},
            {"type": "subtract", "source": "stability", "scale": 0.0005}
        ]
    },
    
    # Flows now modify the stocks directly.
    "population": {
        "priority": 3,
        "initial_value": 10_000_000,
        "base_value": "population", # Crucial: start with your own previous value
        "modifiers": [
            {"type": "add", "source": "population", "scale": "base_birth_rate"},
            {"type": "subtract", "source": "population", "scale": "base_death_rate"}
        ]
    },
    "treasury": {
        "priority": 3,
        "initial_value": 200e9,
        "base_value": "treasury",
        "modifiers": [
            {"type": "add", "source": "tax_revenue"},
            {"type": "subtract", "source": "total_spending"}
        ]
    },
    "stability": {
        "priority": 3,
        "initial_value": 75,
        "base_value": "stability",
        "modifiers": [
            # This shows the power of the new system.
            # It models: stability moves 20% closer to a modified target.
            {"type": "add", "source": "stability_target", "scale": 0.2},
            {"type": "subtract", "source": "stability", "scale": 0.2},
            {"type": "add", "source": "unemployment_rate", "scale": -40}, # -200 * 0.2
            {"type": "add", "source": "social_spending_level", "scale": 3}, # 15 * 0.2
            {"type": "subtract", "source": 1, "scale": 3} # (level-1)*factor = level*factor - factor
        ]
    },
    "gdp_per_capita": {
        "priority": 3,
        "initial_value": 40000,
        "base_value": "gdp_per_capita",
        "modifiers": [
            # The 'source' can also be a constant value if needed
            {"type": "add", "source": "base_infra_spending", "scale": "infra_investment_efficiency"}
            # A more complex model could divide by population here
        ]
    }
  }
}
