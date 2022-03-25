import logging

from simulation_components.agents.malicious_agent import MaliciousAgent
from simulation_components.agents.parasite_chain_attacker import ParasiteChainAttacker
from simulations.byteball_simulation import Byteball
from simulations.ghost_simulation import GhostSimulation
from simulations.nano_simulation import Nano
from simulations.spectre_simulation import Spectre
from simulations.tangle_simulation import TangleSimulation
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx
import sys

if __name__ == '__main__':
    arguments = sys.argv[1:]
    # arguments = arguments[0].split()

    transaction_quantity = int(arguments[0])
    agent_quantity = int(arguments[1])
    transaction_rate = int(arguments[2])
    network_agents_delay = int(arguments[3])
    network_delay = int(arguments[4])
    alpha = float(arguments[5])
    tip_selection = arguments[6]
    walkers_quantity = int(arguments[7])
    walkers_choice = arguments[8]
    start_choice = arguments[9]
    attacker_type = arguments[10]

    # try:
    #     if attacker_type == "None":
    #         simulation = TangleSimulation(transaction_quantity, agent_quantity,
    #                                       transaction_rate, network_agents_delay,
    #                                       network_delay, alpha,
    #                                       tip_selection, walkers_quantity,
    #                                       walkers_choice, start_choice)
    #     else:
    #         attackers_transactions_quantity = int(arguments[11])
    #         attackers_start_time = int(arguments[12])
    #         attackers_rate = int(arguments[13])
    #         if attacker_type == "Parasite":
    #             simulation = TangleSimulation(transaction_quantity, agent_quantity,
    #                                           transaction_rate, network_agents_delay,
    #                                           network_delay, alpha,
    #                                           tip_selection, walkers_quantity,
    #                                           walkers_choice, start_choice,
    #                                           attacker_type,
    #                                           attackers_transactions_quantity=attackers_transactions_quantity,
    #                                           attackers_start_time=attackers_start_time,
    #                                           attackers_rate=attackers_rate,
    #                                           attackers_confirmation_delay=int(arguments[14]),
    #                                           attackers_references=int(arguments[15]))
    #         if attacker_type == "Outpace":
    #             simulation = TangleSimulation(transaction_quantity, agent_quantity,
    #                                           transaction_rate, network_agents_delay,
    #                                           network_delay, alpha,
    #                                           tip_selection, walkers_quantity,
    #                                           walkers_choice, start_choice,
    #                                           attacker_type,
    #                                           attackers_transactions_quantity=attackers_transactions_quantity,
    #                                           attackers_start_time=attackers_start_time,
    #                                           attackers_rate=attackers_rate,
    #                                           attackers_confirmation_delay=int(arguments[14]))
    #         if attacker_type == "Split":
    #             simulation = TangleSimulation(transaction_quantity, agent_quantity,
    #                                           transaction_rate, network_delay,
    #                                           network_agents_delay, alpha,
    #                                           tip_selection, walkers_quantity,
    #                                           walkers_choice, start_choice,
    #                                           attacker_type,
    #                                           attackers_transactions_quantity=attackers_transactions_quantity,
    #                                           attackers_start_time=attackers_start_time,
    #                                           attackers_rate=attackers_rate,
    #                                           attackers_splits=int(arguments[14]))
    #
    #     simulation.setup()
    #     simulation.run()
    # except Exception as ex:
    #     print(ex.args)
    #     exit()

    # simulation = GhostSimulation(transaction_quantity,
    #                              agent_quantity,
    #                              transaction_rate,
    #                              network_delay,
    #                              1)

    # simulation = Spectre(transaction_quantity,
    #                      agent_quantity,
    #                      transaction_rate,
    #                      network_delay,
    #                      1,
    #                      2)

    # simulation = Byteball(transaction_quantity,
    #                      agent_quantity,
    #                      transaction_rate,
    #                      network_delay,
    #                      2,
    #                      2)

    simulation = Nano(transaction_quantity,
                      agent_quantity,
                      transaction_rate,
                      network_delay,
                      2,
                      0.8,
                      3,
                      0.8,
                      4,
                      2,
                      1)

    simulation.setup()
    simulation.run()

    plt.figure(figsize=(9, 6))

    pos = nx.get_node_attributes(simulation.dag.tangle, 'pos')

    colors = [simulation.dag.tangle._node[transaction]['node_color']
              for transaction in simulation.dag.transactions]
    node_size = len(list(simulation.dag.tangle.nodes)) * [150]
    nx.draw_networkx(simulation.dag.tangle,
                     pos,
                     with_labels=True,
                     node_color=colors,
                     alpha=1,
                     node_size=node_size,
                     font_size=6)

    patches = list()
    # todo: add r_transaction
    patches.append(mpatches.Patch(color="black", label="Genesis"))
    names, colors = simulation.get_agents_legend()
    for i in range(len(names)):
        patches.append(mpatches.Patch(color=colors[i], label=names[i]))
    plt.title("DAG based simulation")
    plt.xlabel("Time")
    plt.ylabel("Agents")
    plt.legend(handles=patches)
    plt.savefig("graph.png")
    # plt.show()

    # votes = simulation._voting()
    # print(len(votes))
    # minus = 0
    # plus = 0
    # for vote in votes:
    #     for v in votes[vote]:
    #         if votes[vote][v] == -1:
    #             minus += 1
    #         if votes[vote][v] == 1:
    #             plus += 1
    # print(f"-1: {minus}")
    # print(f"1: {plus}")
