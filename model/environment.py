import networkx as nx
import random


def build_household_network(households, p_connect=0.1):
    """
    Creates an undirected social network among households (e.g., friends, neighbors).
    Each household receives a .neighbors list.
    """
    G = nx.erdos_renyi_graph(len(households), p_connect)
    for i, household in enumerate(households):
        household.neighbors = [households[j] for j in G.neighbors(i)]
    return G


def build_government_firm_graph(firms, government):
    graph = nx.DiGraph()
    for i, firm in enumerate(firms):
        graph.add_edge(government, firm, influence=random.uniform(0.5, 1.5))
        firm.node_id = f"Firm_{i}"
        firm.policy_graph = graph
    government.policy_graph = graph
    return graph



def build_market_matching(households, firms, p_match=0.3):
    """
    Connects households to firms based on probability.
    This can represent consumer preference, access, or market relationships.
    """
    G = nx.DiGraph()
    for i, hh in enumerate(households):
        for j, firm in enumerate(firms):
            if random.random() < p_match:
                G.add_edge(f"Household_{i}", f"Firm_{j}")
    return G


def assign_regional_clusters(households, num_regions=5):
    """
    Assigns households to regional clusters for geographic stratification.
    Each household receives a `region` attribute.
    """
    for i, hh in enumerate(households):
        hh.region = random.randint(1, num_regions)
    return {r: [hh for hh in households if hh.region == r] for r in range(1, num_regions + 1)}


def build_trade_network(households, max_links=3):
    """
    Builds a limited trade network among households, simulating informal economic activity.
    """
    G = nx.Graph()
    for i in range(len(households)):
        G.add_node(f"HH_{i}")
        links = random.sample([j for j in range(len(households)) if j != i], 
                                k=min(max_links, len(households) - 1))
        for j in links:
            G.add_edge(f"HH_{i}", f"HH_{j}")
    return G


def define_shock_zones(households, num_zones=2):
    """
    Tags random regions as 'shock zones' for simulating disasters or conflict.
    Each household may get a `shock_zone = True` flag.
    """
    shock_zone_ids = random.sample(range(len(households)), num_zones)
    for i, hh in enumerate(households):
        hh.shock_zone = i in shock_zone_ids
    return shock_zone_ids


def simulate_info_spread(graph, source_idx=0, spread_prob=0.3, max_depth=3):
    """
    Simulates rumor or information spread using BFS on household social graph.
    Marks `hh.informed = True` for those reached.
    """
    visited = set()
    queue = [(source_idx, 0)]

    while queue:
        current, depth = queue.pop(0)
        if current in visited or depth > max_depth:
            continue
        visited.add(current)
        graph.nodes[current]['informed'] = True
        for neighbor in graph.neighbors(current):
            if random.random() < spread_prob:
                queue.append((neighbor, depth + 1))

    return visited
