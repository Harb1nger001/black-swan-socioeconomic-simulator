from agentpy import Agent
import random


class Government(Agent):

    def setup(self):
        # Fiscal state
        self.budget = 100_000

        # Policy levers
        self.tax_rate_firm = 0.15
        self.tax_rate_household = 0.10
        self.minimum_wage = 70
        self.interest_rate = 0.03

        # Optional graph structures for policy networks
        self.outflow_graph = None  # Can be injected from the model

    def collect_taxes(self):
        """Collect taxes from profitable firms and all households."""
        for firm in self.model.firms:
            if firm.profit > 0:
                tax = firm.profit * self.tax_rate_firm
                firm.profit -= tax
                self.budget += tax

        for household in self.model.households:
            tax = household.wealth * self.tax_rate_household
            household.wealth -= tax
            self.budget += tax

    def provide_subsidies(self):
        """Support low-wealth households and struggling firms."""
        for household in self.model.households:
            if household.wealth < 300:
                household.wealth += 50
                self.budget -= 50

        for firm in self.model.firms:
            if firm.loss_streak >= 2:
                firm.profit += 100
                self.budget -= 100

    def adjust_monetary_policy(self):
        """Adjust interest rates and minimum wage based on inflation."""
        inflation = self.model.inflation_rate

        if inflation > 0.5:
            self.interest_rate += 0.01
            self.minimum_wage += 5
        elif inflation < 0.1:
            self.interest_rate = max(0.01, self.interest_rate - 0.005)

    def deploy_stimulus(self):
        """Inject stimulus when profits or employment drop."""
        avg_profit = sum(f.profit for f in self.model.firms) / len(self.model.firms)
        if avg_profit < 0 or self.model.employment_rate < 0.75:
            amount = 100
            total = amount * len(self.model.households)
            self.budget -= total

            for household in self.model.households:
                household.wealth += amount

    def stabilize_society(self):
        """Reduce unrest if budget permits."""
        if self.budget > 10_000 and self.model.unrest > 0:
            reduction = int(self.model.unrest * 0.1)
            self.model.unrest = max(0, self.model.unrest - reduction)
            self.budget -= reduction * 10

    def simulate_negative_effects(self):
        """Simulate corruption, policy failure, or random shocks."""
        # Corruption drains budget
        if random.random() < 0.05:
            loss = random.randint(500, 2000)
            self.budget = max(0, self.budget - loss)

        # Emergency tax hike if nearly bankrupt
        if self.budget < 2000:
            self.tax_rate_firm += 0.02
            self.tax_rate_household += 0.01
            self.model.unrest += random.randint(5, 15)

        # Random policy shock
        if random.random() < 0.03:
            affected = random.choice(['firm', 'household'])
            if affected == 'firm':
                for firm in self.model.firms:
                    firm.profit -= 50
            else:
                for household in self.model.households:
                    household.wealth = max(0, household.wealth - 50)
            self.model.unrest += 5

    def step(self):
        """Execute all policy functions in order."""
        self.collect_taxes()
        self.provide_subsidies()
        self.adjust_monetary_policy()
        self.deploy_stimulus()
        self.stabilize_society()
        self.simulate_negative_effects()
