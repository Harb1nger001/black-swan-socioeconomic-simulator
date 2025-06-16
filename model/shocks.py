import random

class ShockManager:

    def __init__(self, model):
        self.model = model
        self.last_shock_step = -100  # to prevent back-to-back shocks

    def maybe_trigger_shock(self, step):
        if step - self.last_shock_step < 100:
            return  # Cooldown period between shocks

        if random.random() < 0.0002:  
            shock_type = random.choice([
                self.financial_crisis,
                self.political_instability,
                self.pandemic_outbreak,
                self.natural_disaster,
                self.technology_crash
            ])
            shock_type()
            self.last_shock_step = step

    def financial_crisis(self):
        print("[Shock] 💥 Financial Crisis Triggered")
        for firm in self.model.firms:
            firm.profit *= 0.3
            firm.production_capacity = int(firm.production_capacity * 0.7)
        self.model.inflation_rate += 0.05
        self.model.unrest += 20

    def political_instability(self):
        print("[Shock] 🔥 Political Instability Erupts")
        self.model.unrest += 40
        self.model.government.tax_rate_firm += 0.05
        self.model.government.tax_rate_household += 0.03

    def pandemic_outbreak(self):
        print("[Shock] 🦠 Pandemic Strikes")
        for firm in self.model.firms:
            firm.num_employees = int(firm.num_employees * 0.5)
        self.model.unrest += 25
        self.model.inflation_rate += 0.03

    def natural_disaster(self):
        print("[Shock] 🌪️ Natural Disaster Hits")
        for hh in self.model.households:
            hh.wealth = max(0, hh.wealth - random.randint(50, 150))
        for firm in self.model.firms:
            firm.inventory = max(0, firm.inventory - random.randint(50, 100))
        self.model.unrest += 30

    def technology_crash(self):
        print("[Shock] ⚡ Tech Infrastructure Collapse")
        self.model.government.interest_rate += 0.02
        for firm in self.model.firms:
            firm.production_capacity = int(firm.production_capacity * 0.6)
        self.model.inflation_rate += 0.04
        self.model.unrest += 15
        
    def trigger_shock_by_name(self, shock_name):
        shock_map = {
            'financial_crisis': self.financial_crisis,
            'political_instability': self.political_instability,
            'pandemic_outbreak': self.pandemic_outbreak,
            'natural_disaster': self.natural_disaster,
            'technology_crash': self.technology_crash
        }

        shock_fn = shock_map.get(shock_name)
        if shock_fn:
            print(f"[Manual Trigger] 🚨 {shock_name.replace('_', ' ').title()} activated")
            shock_fn()
            self.last_shock_step = self.model.t  # Prevent repeat triggers if desired
        else:
            print(f"[Warning] Unknown shock: {shock_name}")
