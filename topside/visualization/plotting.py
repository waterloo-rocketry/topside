import numpy as np
import matplotlib.pyplot as plt

import topside as top


def plot_graph(g, pos):
    fig, ax = plt.subplots()

    for node in g.nodes:
        pt = pos[node]
        ax.plot(pt[0], pt[1], '.', color='teal', markersize=25, zorder=10)
        ax.text(pt[0]+0.5, pt[1]+0.5, str(node), zorder=15)

    for edge in g.edges:
        p1 = pos[edge[0]]
        p2 = pos[edge[1]]
        ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color='darkgrey', zorder=1)

    pts = np.transpose(list(pos.values()))
    xmin = min(pts[0])
    xmax = max(pts[0])
    ymin = min(pts[1])
    ymax = max(pts[1])

    ax.set_xlim(xmin-5, xmax+5)
    ax.set_ylim(ymin-5, ymax+5)

    ax.grid()
    ax.set_aspect('equal')

    return fig, ax


def layout_and_plot_plumbing_engine(engine):
    t = top.terminal_graph(engine)
    pos = top.layout_plumbing_engine(engine)

    return plot_graph(t, pos)
