# game.py

import time
import random
from sd_engine import SDEngine_Eventful
from simlandia_model import model_definition

# --- HELPER FUNCTIONS ---
def display_header():
    print("=" * 40)
    print("      THE REPUBLIC OF SIMLANDIA")
    print("=" * 40)

def display_dashboard(engine, year):
    pop = engine.get_value("population")
    gdp = engine.get_value("gdp")
    treasury = engine.get_value("treasury")
    stability = engine.get_value("stability")
    unemployment = engine.get_value("unemployment_rate")
    
    print(f"\n---== YEAR {year} REPORT ==---")
    print(f"  Population:      {pop:,.0f}")
    print(f"  Stability:       {stability:.1f}%")
    print(f"  Unemployment:    {unemployment:.2%}")
    print(f"  Treasury:        ${treasury/1e9:,.2f} B")
    print(f"  GDP:             ${gdp/1e9:,.2f} B")
    print("-" * 25)

def get_player_choice(engine):
    # FIX 1: Display with one decimal place for clarity
    current_tax_rate = engine.get_value("tax_rate")
    print(f"Current Income Tax Rate: {current_tax_rate:.1%}") # Changed from .0% to .1%
    print("\n[POLICY DECISION]")
    print("  1. Raise Taxes by 2%")
    print("  2. Keep Taxes the same")
    print("  3. Lower Taxes by 2%")
    
    while True:
        choice = input("Your decision, Mr/Madam President? (1/2/3): ")
        if choice in ['1', '2', '3']:
            return int(choice)
        print("Invalid choice. Please enter 1, 2, or 3.")

def process_events(engine):
    """Checks for and applies random events for the year."""
    # Every year, there's a small chance of a random event.
    if random.random() < 0.25: # 25% chance of an event
        # Pick one of the possible events
        event_roll = random.choice(["boom", "disaster", "scandal"])
        
        if event_roll == "boom":
            print("\n>>> EVENT: A global economic boom boosts our GDP per capita!")
            engine.add_to_value("gdp_per_capita", 5000)
            
        elif event_roll == "disaster":
            print("\n>>> EVENT: A natural disaster has struck! The treasury will pay for repairs.")
            engine.add_to_value("treasury", -20e9) # -20 Billion
            engine.add_to_value("stability", -5) # People are unhappy
            
        elif event_roll == "scandal":
            print("\n>>> EVENT: A political scandal erupts, shaking public confidence!")
            engine.add_to_value("stability", -10)

# --- MAIN GAME LOOP ---
def play_game():
    engine = SDEngine_Eventful(model_definition)
    year = 2024
    
    display_header()
    print("You have been elected President. Your goal is to lead Simlandia to prosperity.")
    print("But beware: if national stability falls to zero, you will be overthrown!")
    
    while True:
        display_dashboard(engine, year)
        
        # 1. Check for lose condition
        if engine.get_value("stability") <= 0:
            print("\n\nYour government has collapsed due to instability. The people have overthrown you.")
            print("--- GAME OVER ---")
            break
            
        # 2. Player makes a policy choice
        choice = get_player_choice(engine)
        if choice == 1:
            # Raise taxes
            current_rate = engine.get_value("tax_rate")
            new_rate = min(1.0, current_rate + 0.02)
            engine.set_value("tax_rate", new_rate)
            print("Taxes have been raised.")
        # THE FIX: Add an explicit case for doing nothing.
        elif choice == 2:
            print("Tax rate remains unchanged.")
            pass
        elif choice == 3:
            # Lower taxes
            current_rate = engine.get_value("tax_rate")
            new_rate = max(0.0, current_rate - 0.02)
            engine.set_value("tax_rate", new_rate)
            print("Taxes have been lowered.")
        
        # 3. Process random events
        process_events(engine)
        
        # 4. Run the simulation for one year
        engine.update()
        
        if False: 
            engine.dump_variables()
        
        # 5. Advance to the next year
        year += 1
        time.sleep(1) # Pause for dramatic effect

if __name__ == "__main__":
    play_game()
