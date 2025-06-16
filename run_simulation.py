import sys
import os
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), "model"))
from base_model import CollapseModel

def run_simulation(params, live=False, update_callback=None):
    model = CollapseModel(params)

    if live:
        model.setup()
        model_data = []

        for step in range(params['steps']):
            model.step()
            step_data = {
                "Step": step,
                "Unrest": model.unrest,
                "Inflation": model.inflation_rate,
                "EmploymentRate": model.employment_rate,
                "AvgFirmProfit": sum(f.profit for f in model.firms) / model.num_firms,
                "TotalDemand": model.total_demand,
                "GDPGrowthRate": model.gdp_growth,
                "GiniCoefficient": model.compute_gini(),
            }
            model_data.append(step_data)

            if update_callback:
                update_callback(step, step_data)

        df = pd.DataFrame(model_data)
    else:
        results = model.run(steps=params['steps']).variables
        df = pd.DataFrame(results['CollapseModel'])

    return model, df
