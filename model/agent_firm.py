from agentpy import Agent
import random

class Firm(Agent):

    def setup(self):
        self.num_employees = random.randint(50, 150)
        self.production_capacity = 1000
        self.inventory = 0
        self.base_wage = random.uniform(60, 100)
        self.profit = 0
        self.loss_streak = 0
        self.bankrupt = False

    # === Cost Pressure Calculation ===
    def assess_cost_pressure(self):
        inflation_penalty = self.model.inflation_rate * 20
        unrest_penalty = (self.model.unrest / max(1, self.model.num_households)) * 30
        return inflation_penalty + unrest_penalty

    def expected_demand_factor(self):
        return max(0.5, self.model.employment_rate)

    # === Bankruptcy Check ===
    def check_bankruptcy(self):
        if self.loss_streak >= 3 and self.profit < -1000:
            self.bankrupt = True
            self.num_employees = 0
            self.inventory = 0
            self.production_capacity = int(self.production_capacity * 0.5)
            self.model.unrest += 3
            self.model.government.budget += 200
        elif self.bankrupt and self.profit > 0:
            self.bankrupt = False

    # === Labor Adjustments ===
    def adjust_employment(self):
        if self.loss_streak >= 3 or self.profit < -500:
            self.num_employees = max(1, self.num_employees - 1)
            self.loss_streak = 0
        elif self.profit > 200:
            self.num_employees += 1

    # === Production ===
    def produce(self):
        efficiency = max(0.6, 1.0 - self.model.inflation_rate)
        output = int(min(self.production_capacity, self.num_employees * 8 * efficiency))
        self.inventory += output

    # === Sales ===
    def sell_goods(self):
        price_per_unit = 60 + self.model.inflation_rate * 10
        expected_factor = self.expected_demand_factor()

        # Estimate demand for this firm
        average_household_demand = (self.model.total_demand / max(1, len(self.model.firms)))
        demand = min(self.inventory, int(average_household_demand * expected_factor))

        revenue = demand * price_per_unit
        self.profit += revenue
        self.inventory -= demand
        self.model.total_demand += demand  # Booked demand

    # === Wage Payment ===
    def pay_wages(self):
        wage = self.base_wage * (1 + self.model.inflation_rate * 0.5)
        wage_bill = self.num_employees * wage
        self.profit -= wage_bill

        # Distribute income across random households
        employed_households = random.sample(
            self.model.households,
            min(self.num_employees, len(self.model.households))
        )

        for household in employed_households:
            household.income += wage
            self.model.total_income += wage
            self.model.income_distribution.append(wage)

    # === Government Policy Boost ===
    def check_policy_influence(self):
        g = getattr(self.model, 'policy_graph', None)
        if g and g.has_edge(self.model.government, self):
            influence = g.get_edge_data(self.model.government, self).get('influence', 1.0)
            self.profit += 20 * influence
            self.production_capacity += int(2 * influence)

    # === Firm Expansion ===
    def expand_if_profitable(self):
        if self.profit > 500:
            self.production_capacity += 10
            self.base_wage *= 1.02

    # === Main Step Function ===
    def step(self):
        self.profit = 0  # Reset profit at each step

        if self.bankrupt:
            return

        self.check_policy_influence()
        self.produce()
        self.sell_goods()
        self.pay_wages()
        self.adjust_employment()
        self.expand_if_profitable()

        self.loss_streak = self.loss_streak + 1 if self.profit < 0 else 0
        self.check_bankruptcy()
