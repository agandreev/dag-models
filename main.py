import logging

from simulation_components.agents.malicious_agent import MaliciousAgent
from simulation_components.agents.parasite_chain_attacker import ParasiteChainAttacker
from simulations.byteball_simulation import Byteball, Byteball_attack, DOUBLE
from simulations.ghost_simulation import GhostSimulation
from simulations.nano_simulation import Nano
from simulations.spectre_simulation import Spectre
from simulations.tangle_simulation import TangleSimulation
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx
import sys

# if __name__ == '__main__':
#     arguments = sys.argv[1:]
#     # arguments = arguments[0].split()
#
#     transaction_quantity = int(arguments[0])
#     agent_quantity = int(arguments[1])
#     transaction_rate = int(arguments[2])
#     network_agents_delay = int(arguments[3])
#     network_delay = int(arguments[4])
#     alpha = float(arguments[5])
#     tip_selection = arguments[6]
#     walkers_quantity = int(arguments[7])
#     walkers_choice = arguments[8]
#     start_choice = arguments[9]
#     attacker_type = arguments[10]
#
#     # try:
#     #     if attacker_type == "None":
#     #         simulation = TangleSimulation(transaction_quantity, agent_quantity,
#     #                                       transaction_rate, network_agents_delay,
#     #                                       network_delay, alpha,
#     #                                       tip_selection, walkers_quantity,
#     #                                       walkers_choice, start_choice)
#     #     else:
#     #         attackers_transactions_quantity = int(arguments[11])
#     #         attackers_start_time = int(arguments[12])
#     #         attackers_rate = int(arguments[13])
#     #         if attacker_type == "Parasite":
#     #             simulation = TangleSimulation(transaction_quantity, agent_quantity,
#     #                                           transaction_rate, network_agents_delay,
#     #                                           network_delay, alpha,
#     #                                           tip_selection, walkers_quantity,
#     #                                           walkers_choice, start_choice,
#     #                                           attacker_type,
#     #                                           attackers_transactions_quantity=attackers_transactions_quantity,
#     #                                           attackers_start_time=attackers_start_time,
#     #                                           attackers_rate=attackers_rate,
#     #                                           attackers_confirmation_delay=int(arguments[14]),
#     #                                           attackers_references=int(arguments[15]))
#     #         if attacker_type == "Outpace":
#     #             simulation = TangleSimulation(transaction_quantity, agent_quantity,
#     #                                           transaction_rate, network_agents_delay,
#     #                                           network_delay, alpha,
#     #                                           tip_selection, walkers_quantity,
#     #                                           walkers_choice, start_choice,
#     #                                           attacker_type,
#     #                                           attackers_transactions_quantity=attackers_transactions_quantity,
#     #                                           attackers_start_time=attackers_start_time,
#     #                                           attackers_rate=attackers_rate,
#     #                                           attackers_confirmation_delay=int(arguments[14]))
#     #         if attacker_type == "Split":
#     #             simulation = TangleSimulation(transaction_quantity, agent_quantity,
#     #                                           transaction_rate, network_delay,
#     #                                           network_agents_delay, alpha,
#     #                                           tip_selection, walkers_quantity,
#     #                                           walkers_choice, start_choice,
#     #                                           attacker_type,
#     #                                           attackers_transactions_quantity=attackers_transactions_quantity,
#     #                                           attackers_start_time=attackers_start_time,
#     #                                           attackers_rate=attackers_rate,
#     #                                           attackers_splits=int(arguments[14]))
#     #
#     #     simulation.setup()
#     #     simulation.run()
#     # except Exception as ex:
#     #     print(ex.args)
#     #     exit()
#
#     # simulation = GhostSimulation(transaction_quantity,
#     #                              agent_quantity,
#     #                              transaction_rate,
#     #                              network_delay,
#     #                              1)
#
#     # simulation = Spectre(transaction_quantity,
#     #                      agent_quantity,
#     #                      transaction_rate,
#     #                      network_delay,
#     #                      1,
#     #                      2)
#
#     simulation = Byteball(transaction_quantity,
#                          agent_quantity,
#                          transaction_rate,
#                          network_delay,
#                          1,
#                          2,
#                          None)
#
#     # simulation = Nano(transaction_quantity,
#     #                   agent_quantity,
#     #                   transaction_rate,
#     #                   network_delay,
#     #                   2,
#     #                   0.8,
#     #                   3,
#     #                   0.8,
#     #                   4,
#     #                   2,
#     #                   1)
#
#     simulation.setup()
#     simulation.run()
#
#     plt.figure(figsize=(9, 6))
#
#     pos = nx.get_node_attributes(simulation.dag.tangle, 'pos')
#
#     colors = [simulation.dag.tangle._node[transaction]['node_color']
#               for transaction in simulation.dag.transactions]
#     node_size = len(list(simulation.dag.tangle.nodes)) * [150]
#     nx.draw_networkx(simulation.dag.tangle,
#                      pos,
#                      with_labels=True,
#                      node_color=colors,
#                      alpha=1,
#                      node_size=node_size,
#                      font_size=6,
#                      edge_color=simulation.edge_colors)
#
#     patches = list()
#     # todo: add r_transaction
#     patches.append(mpatches.Patch(color="black", label="Genesis"))
#     names, colors = simulation.get_agents_legend()
#     for i in range(len(names)):
#         patches.append(mpatches.Patch(color=colors[i], label=names[i]))
#     plt.title("DAG based simulation")
#     plt.xlabel("Time")
#     plt.ylabel("Agents")
#     plt.legend(handles=patches)
#     plt.savefig("graph.png")
#     # plt.show()
#
#     # votes = simulation._voting()
#     # print(len(votes))
#     # minus = 0
#     # plus = 0
#     # for vote in votes:
#     #     for v in votes[vote]:
#     #         if votes[vote][v] == -1:
#     #             minus += 1
#     #         if votes[vote][v] == 1:
#     #             plus += 1
#     # print(f"-1: {minus}")
#     # print(f"1: {plus}")


import tkinter
from typing import List


def load_byteball_form():
    global DAG
    DAG = BYTEBALL

    clear(components)
    clear(attack_components)

    _create_entry_row(1, "Transaction quantity:", components, t_quantity)
    _create_entry_row(2, "Agent quantity:", components, a_quantity)
    _create_entry_row(3, "Transaction rate:", components, t_rate)
    _create_entry_row(4, "Network delay:", components, n_delay)
    _create_entry_row(5, "Witness quantity:", components, w_quantity)
    _create_entry_row(6, "Validation quantity:", components, v_quantity)
    _create_dropmenu_row(7, "Attack type:", ["None", "Double-spend"], components, a_type)


def load_tangle_form():
    clear(components)
    clear(attack_components)

    global DAG
    DAG = TANGLE
    label = tk.Label(app, text=TANGLE, width=20, font=("bold", 10))
    label.grid(row=1)
    components.append(label)


def load_nano_form():
    clear(components)
    clear(attack_components)


def clear(components: List):
    for component in components:
        component.destroy()
    components.clear()


def _create_entry_row(row: int, text: str, components: List, var):
    label = tk.Label(app, text=text, width=20, font=("bold", 10))
    label.grid(row=row, column=0, sticky="NW")
    entry = tk.Entry(app, textvariable=var)
    entry.grid(row=row, column=1, sticky="NW")
    components.extend([label, entry])


def _create_dropmenu_row(row: int, text: str, options: List[str], components: List, var):
    label = tk.Label(app, text=text, width=20, font=("bold", 10))
    label.grid(row=row, column=0, sticky="NW")
    var.set(options[0])
    option_menu = tk.OptionMenu(app, var, *options, command=lambda *x: _add_attack_rows(row + 1, var.get()))
    option_menu.grid(row=row, column=1, sticky="NW")
    components.extend([label, option_menu])


def _add_attack_rows(row: int, item: str):
    print(item)
    clear(attack_components)
    if item == "None":
        return
    if item == "Double-spend":
        _create_entry_row(row, "Start time:", attack_components, s_time)
        _create_entry_row(row + 1, "Attack rate:", attack_components, a_rate)


def _int_var() -> 'tk.StringVar':
    s = tk.StringVar()
    s.trace("w", lambda *x: _check_int(s))
    return s


def _float_var() -> 'tk.StringVar':
    s = tk.StringVar()
    s.trace("w", lambda *x: _check_float(s))
    return s


def _str_var() -> 'tk.StringVar':
    return tk.StringVar()


def _check_int(s: 'tk.StringVar'):
    if not s.get().isdigit():
        s.set("")


def _check_float(s: 'tk.StringVar'):
    try:
        float(s.get())
    except ValueError:
        s.set("")


def _run():
    if DAG == BYTEBALL:
        _run_byteball()


def _run_byteball():
    if not (_check_fields(t_quantity) and _check_fields(a_quantity) and _check_fields(t_rate)
            and _check_fields(n_delay) and _check_fields(w_quantity) \
            and _check_fields(v_quantity) and _check_fields(a_type)):
        return

    attack = None
    if str(a_type) != "None":
        attack = None

    simulation = Byteball(int(t_quantity.get()), int(a_quantity.get()), int(t_rate.get()),
                          float(n_delay.get()), int(w_quantity.get()), int(v_quantity.get()), attack)
    print(int(t_quantity.get()), int(a_quantity.get()), int(t_rate.get()),
                          float(n_delay.get()), int(w_quantity.get()), int(v_quantity.get()), attack)

    simulation.setup()
    simulation.run()

    plt.figure(figsize=(9, 6))

    pos = nx.get_node_attributes(simulation.dag.tangle, 'pos')

    print(simulation.dag.tangle._node)
    colors = [simulation.dag.tangle._node[transaction]['node_color']
              for transaction in simulation.dag.transactions]
    node_size = len(list(simulation.dag.tangle.nodes)) * [150]
    nx.draw_networkx(simulation.dag.tangle,
                     pos,
                     with_labels=True,
                     node_color=colors,
                     alpha=1,
                     node_size=node_size,
                     font_size=6,
                     edge_color=simulation.edge_colors)

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

    # image = Image.open("graph.png")
    # test = ImageTk.PhotoImage(image)
    #
    # global img
    # img = tkinter.Label(app, image=test)
    # img.image = test
    #
    # img.grid(row=0, column=2, columnspan=2, rowspan=10, padx=5, pady=5)
    print("here")


def _check_fields(field) -> bool:
    if len(field.get()) == 0:
        tkinter.messagebox.showinfo(title="Warning", message="All fields should be filled!")
        return False
    return True


import tkinter as tk
import tkinter.messagebox
from PIL import Image, ImageTk

DAG = ""
TANGLE = "Tangle"
BYTEBALL = "Byteball"

components = list()
attack_components = list()

app = tk.Tk()
app.geometry('300x200')
app.title("Basic Menu Bar")

t_quantity = _int_var()
a_quantity = _int_var()
t_rate = _int_var()
n_delay = _float_var()
w_quantity = _int_var()
v_quantity = _int_var()
a_type = _str_var()

s_time = _float_var()
a_rate = _float_var()

menubar = tk.Menu(app)

filemenu = tk.Menu(menubar)
filemenu.add_command(label="Tangle", command=load_tangle_form)
filemenu.add_command(label="Byteball", command=load_byteball_form)
filemenu.add_command(label="Nano", command=load_nano_form)

menubar.add_cascade(label="Select model", menu=filemenu)
tk.Button(app, text="Run", command=lambda: _run()).grid(row=0, sticky="NW")

app.config(menu=menubar)

img = None

app.mainloop()
