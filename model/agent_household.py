from agentpy import Agent
import random

class Household(Agent):

    def setup(self):
        self.num_members = 4                          # Total household members
        self.earners = [True, True]                   # Initially 2 earners
        self.wealth = 10000                            # Initial wealth
        self.cost_of_living = random.uniform(200, 500)  # Daily expense per member
        self.neighbors = []                           # Assigned in setup
        self.income = 0                               # Earned from firms each step

    def update_employment(self):
        """Update employment status based on model rate and peer influence."""
        neighbor_ratio = self._get_neighbor_employment_ratio()

        for i in range(len(self.earners)):
            prob = self.model.employment_rate * (0.8 + 0.2 * neighbor_ratio)
            self.earners[i] = random.random() < min(1.0, prob)

        # 10% chance a new household member becomes employable
        if random.random() < 0.1 and len(self.earners) < self.num_members:
            self.earners.append(random.random() < self.model.employment_rate)

    def _get_neighbor_employment_ratio(self):
        """Average employment rate among neighbors."""
        if not self.neighbors:
            return 1.0

        ratios = []
        for neighbor in self.neighbors:
            employed = neighbor.earners.count(True)
            total = len(neighbor.earners)
            if total > 0:
                ratios.append(employed / total)

        return sum(ratios) / len(ratios) if ratios else 1.0

    def compute_expenses(self, employed_count):
        """Adjust expenses based on employment coverage."""
        base = self.cost_of_living * self.num_members
        if employed_count == 0:
            return base * 0.6
        elif employed_count == 1:
            return base * 0.85
        else:
            return base

    def update_unrest(self, employed_count):
        """Adjust unrest levels based on employment sufficiency."""
        if employed_count == 0:
            self.model.unrest += 2
        elif employed_count == 1:
            self.model.unrest += 1
        elif employed_count == 2:
            self.model.unrest = max(0, self.model.unrest - 5)
        else:
            self.model.unrest = max(0, self.model.unrest - 8)

    def step(self):
        self.update_employment()
        employed_count = self.earners.count(True)

        # Income earned last round
        earned = self.income
        self.income = 0  # Reset after use

        expenses = self.compute_expenses(employed_count)
        self.update_unrest(employed_count)

        self.wealth = max(0, self.wealth + earned - expenses)

        # Avoid divide-by-zero in demand
        if len(self.earners) > 0:
            participation_ratio = employed_count / len(self.earners)
        else:
            participation_ratio = 0.0

        # Demand is driven by income and willingness to spend
        demand = min(self.wealth, 50) * participation_ratio
        self.model.total_demand += demand
