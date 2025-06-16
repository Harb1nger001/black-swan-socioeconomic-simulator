from agentpy import Model, AgentList
import random

from model.agent_household import Household
from model.agent_firm import Firm
from model.agent_government import Government
from model.shocks import ShockManager
from model.environment import (
    build_household_network,
    build_government_firm_graph,
    build_market_matching,
    assign_regional_clusters,
    build_trade_network,
    define_shock_zones,
    simulate_info_spread
)

class CollapseModel(Model):

    def setup(self):
        self.unrest = 0
        self.step_count = 0

        # === Simulation Parameters ===
        self.num_households = self.p['num_households']
        self.num_firms = self.p.get('num_firms', 10)
        self.inflation_rate = self.p['init_inflation_rate']
        self.employment_rate = self.p['init_employment_rate']

        # === Agent Initialization ===
        self.households = AgentList(self, self.num_households, Household)
        self.firms = AgentList(self, self.num_firms, Firm)
        self.government = Government(self)

        # === Make Households Accessible to Firms ===
        self.households.model = self
        self.firms.model = self

        # === Environment & Networks ===
        self.household_graph = build_household_network(self.households, p_connect=0.1)
        self.policy_graph = build_government_firm_graph(self.firms, self.government)
        self.market_graph = build_market_matching(self.households, self.firms)
        self.regions = assign_regional_clusters(self.households, num_regions=4)
        self.trade_network = build_trade_network(self.households)
        self.shock_zones = define_shock_zones(self.households)

        # === Attach Regional & Trade Data ===
        for household in self.households:
            household.region = self.regions.get(household, None)
            household.trading_partners = list(self.trade_network.neighbors(household)) \
                if household in self.trade_network else []

        for firm in self.firms:
            firm.policy_graph = self.policy_graph

        self.shock_manager = ShockManager(self)

        # === Macroeconomic Tracking ===
        self.total_demand = 0
        self.total_income = 0
        self.income_distribution = []
        self.previous_gdp = None
        self.gdp_growth = 0.0

    def update_macroeconomics(self):
        # === Inflation Dynamics ===
        inflation_trend = random.uniform(-0.005, 0.01)
        if self.employment_rate < 0.8:
            inflation_trend += 0.005
        self.inflation_rate = max(0.0, round(self.inflation_rate + inflation_trend, 3))

        # === Employment Adjustment ===
        unrest_ratio = self.unrest / self.num_households
        if unrest_ratio > 0.25:
            self.employment_rate -= random.uniform(0.01, 0.03)
        else:
            self.employment_rate += random.uniform(-0.01, 0.01)

        self.employment_rate = round(min(1.0, max(0.6, self.employment_rate)), 3)

        # === Natural Dissipation of Unrest ===
        self.unrest = max(0, self.unrest - int(self.num_households * 0.01))

    def compute_gini(self):
        values = sorted(self.income_distribution)
        n = len(values)
        if n == 0 or sum(values) == 0:
            return 0.0
        cumulative = sum((i + 1) * val for i, val in enumerate(values))
        return round((2 * cumulative) / (n * sum(values)) - (n + 1) / n, 3)

    def step(self):
        # === Reset Trackers ===
        self.total_demand = 0
        self.total_income = 0
        self.income_distribution = []

        # === Step Agents ===
        self.households.step()
        self.firms.step()
        self.government.step()
        self.shock_manager.maybe_trigger_shock(self.t)

        # === Macroeconomic Updates ===
        self.step_count += 1
        if self.step_count % 90 == 0:
            self.update_macroeconomics()

        # === GDP Tracking ===
        firm_profits = sum(f.profit for f in self.firms)
        gdp = self.total_income + firm_profits

        if self.previous_gdp and self.previous_gdp != 0:
            self.gdp_growth = round(((gdp - self.previous_gdp) / self.previous_gdp) * 100, 2)
        else:
            self.gdp_growth = 0.0

        self.previous_gdp = gdp

        # === Aggregates ===
        gini = self.compute_gini()
        avg_profit = firm_profits / self.num_firms if self.num_firms > 0 else 0

        # === Record Metrics ===
        self.record('Unrest', self.unrest)
        self.record('Inflation', self.inflation_rate)
        self.record('EmploymentRate', self.employment_rate)
        self.record('AvgFirmProfit', round(avg_profit, 2))
        self.record('FirmProfitTotal', round(firm_profits, 2))
        self.record('TotalDemand', self.total_demand)
        self.record('GDP', gdp)
        self.record('GDPGrowthRate', self.gdp_growth)
        self.record('GiniCoefficient', gini)

    def end(self):
        # === Final Report ===
        self.report("Unrest", self.unrest)
        self.report("Inflation", self.inflation_rate)
        self.report("EmploymentRate", self.employment_rate)

        avg_profit = sum(f.profit for f in self.firms) / self.num_firms if self.num_firms > 0 else 0
        self.report("AvgFirmProfit", round(avg_profit, 2))
        self.report("FirmProfitTotal", round(sum(f.profit for f in self.firms), 2))
        self.report("TotalDemand", self.total_demand)
        self.report("GDPGrowthRate", self.output.get('GDPGrowthRate', [0])[-1])
        self.report("GiniCoefficient", self.output.get('GiniCoefficient', [0])[-1])
        self.report("GDP", self.output.get('GDP', [0])[-1])
