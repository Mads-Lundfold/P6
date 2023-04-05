import networkx as nx
import matplotlib.pyplot as plt
import json
import pandas as pd


def patterns_to_graph(patterns_path: str):

    edges = list()

    with open(patterns_path) as f:
        patterns = json.load(f)
    
    patterns_df = pd.DataFrame(patterns)

    for pattern in patterns_df['name_node']:
        edges.append(pattern.split(','))

    return edges


def visualize_patterns():
    options = {
        'node_color': 'green',
        'node_size': 40,
        'font_size': 8,
        'width': 1,
        'arrowstyle': '-|>',
        'arrowsize': 50,
    }   

    graph = nx.Graph()
    edges = patterns_to_graph('C:/Users/Mads/Bachelor/P6/data_analysis/TPM/TPM/output/2014/Experiment_minsup0.05_minconf_0.6/level2.json')
    graph.add_edges_from(edges)
    nx.draw_networkx(graph, **options)
    plt.show()


visualize_patterns()