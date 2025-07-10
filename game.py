# game_v2.py

import time
import random
from sd_engine import SDEngine
from simlandia_model import model_definition # <-- IMPORT THE NEW MODEL

# --- CONSTANTS ---
EVENT_CHANCE = 0.25
TAX_ADJUSTMENT_STEP = 0.02
SPENDING_ADJUSTMENT_STEP = 0.1 # Adjust by 10% of base

# --- HELPER FUNCTIONS (display_header and display_dashboard are mostly the same) ---
def display_header():
    print("\n" + "=" * 40)
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
    print(f"  GDP per Capita:  ${engine.get_value('gdp_per_capita'):,.0f}")
    print("-" * 25)

def get_player_choice(engine):
    """A more advanced menu for multiple policy levers."""
    while True:
        print("\n[POLICY DECISIONS]")
        # Display current state of all levers
        tax = engine.get_value("tax_rate")
        infra = engine.get_value("infrastructure_spending_level")
        social = engine.get_value("social_spending_level")

        print(f"  1. Adjust Tax Rate              (current: {tax:.1%})")
        print(f"  2. Adjust Infrastructure Spending (current: {infra:.0%})")
        print(f"  3. Adjust Social Spending         (current: {social:.0%})")
        print("  4. Do nothing this year")
        
        choice = input("\nYour decision, Mr/Madam President? (1-4): ")

        if choice == '1': # Tax Menu
            print(f"\nCurrent Tax Rate: {tax:.1%}")
            sub_choice = input("  (R)aise taxes, (L)ower taxes, or (C)ancel? ").lower()
            if sub_choice == 'r':
                new_rate = min(1.0, tax + TAX_ADJUSTMENT_STEP)
                engine.set_value("tax_rate", new_rate)
                print("Tax rate has been raised.")
                return # Exit the function after a decision is made
            elif sub_choice == 'l':
                new_rate = max(0.0, tax - TAX_ADJUSTMENT_STEP)
                engine.set_value("tax_rate", new_rate)
                print("Tax rate has been lowered.")
                return
        
        elif choice == '2': # Infrastructure Menu
            print(f"\nCurrent Infrastructure Spending Level: {infra:.0%}")
            sub_choice = input("  (I)ncrease spending, (D)ecrease spending, or (C)ancel? ").lower()
            if sub_choice == 'i':
                engine.add_to_value("infrastructure_spending_level", SPENDING_ADJUSTMENT_STEP)
                print("Infrastructure spending increased.")
                return
            elif sub_choice == 'd':
                new_level = max(0.0, infra - SPENDING_ADJUSTMENT_STEP)
                engine.set_value("infrastructure_spending_level", new_level)
                print("Infrastructure spending decreased.")
                return

        elif choice == '3': # Social Spending Menu
            print(f"\nCurrent Social Spending Level: {social:.0%}")
            sub_choice = input("  (I)ncrease spending, (D)ecrease spending, or (C)ancel? ").lower()
            if sub_choice == 'i':
                engine.add_to_value("social_spending_level", SPENDING_ADJUSTMENT_STEP)
                print("Social spending increased.")
                return
            elif sub_choice == 'd':
                new_level = max(0.0, social - SPENDING_ADJUSTMENT_STEP)
                engine.set_value("social_spending_level", new_level)
                print("Social spending decreased.")
                return

        elif choice == '4':
            print("Holding steady. No policy changes this year.")
            return

        else:
            print("Invalid choice. Please enter a number from 1 to 4.")


def process_events(engine):
    """Checks for and applies random events for the year."""
    if random.random() < EVENT_CHANCE:
        event_roll = random.choice(["boom", "disaster", "scandal", "protests"])
        
        if event_roll == "boom":
            print("\n>>> EVENT: A technological breakthrough boosts investment efficiency!")
            engine.add_to_value("infra_investment_efficiency", 0.02)
        elif event_roll == "disaster":
            print("\n>>> EVENT: A natural disaster requires immediate infrastructure repair.")
            engine.add_to_value("treasury", -30e9)
            engine.add_to_value("stability", -5)
        elif event_roll == "scandal":
            print("\n>>> EVENT: A political scandal erupts, shaking public confidence!")
            engine.add_to_value("stability", -10)
        elif event_roll == "protests":
            print("\n>>> EVENT: Protests erupt over austerity! The people demand more social support.")
            engine.add_to_value("stability", -3)
            # This event could temporarily force a change in policy or add a "demand" modifier
            engine.add_modifier("stability_change", "additive_modifiers", "protest_pressure")
            engine.add_variable("protest_pressure", {"initial_value": -5, "priority":1})


# --- MAIN GAME LOOP (Unchanged except for calling the new get_player_choice) ---
def play_game():
    engine = SDEngine(model_definition)
    year = 2024
    
    display_header()
    print("You have been elected President. Your goal is to lead Simlandia to prosperity.")
    print("But beware: if national stability falls to zero, you will be overthrown!")
    
    while True:
        display_dashboard(engine, year)
        
        if engine.get_value("stability") <= 0:
            print("\n\nYour government has collapsed due to instability. The people have overthrown you.")
            print("--- GAME OVER ---")
            break
            
        get_player_choice(engine) # Use the new menu system
        process_events(engine)
        engine.update()
        
        # A little cleanup for temporary event modifiers
        if "protest_pressure" in engine.model:
            engine.remove_modifier("stability_change", "protest_pressure")
            engine.remove_variable("protest_pressure")

        year += 1
        time.sleep(1)

if __name__ == "__main__":
    play_game()
