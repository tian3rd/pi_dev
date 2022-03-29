#!/usr/bin/python
# -*- coding: utf-8 -*-

import tkinter as tk
import matplotlib.pyplot as plt
import numpy as np
import control.matlab as ml
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# plot function


def plot_bode():
    # get the data
    r1 = float(r1_entry.get().strip())
    r2 = float(r2_entry.get().strip())
    c4 = float(c4_entry.get().strip())
    c5 = float(c5_entry.get().strip())

    # because we use kΩ and nF as default unit, here we need to convert the multiplication to standard unit
    r1c4 = r1 * c4 / 1000000
    r2c5 = r2 * c5 / 1000000
    r1c5 = r1 * c5 / 1000000

    num = np.array([r1c4 * r2c5, r1c4 + r2c5 + r1c5, 1])
    den = np.polymul(np.array([r1c4, 1]), np.array([r2c5, 1]))

    # transfer function
    G = ml.tf(num, den)

    # pole and zero
    poles = ml.pole(G) / (2 * np.pi)
    zeros = ml.zero(G) / (2 * np.pi)
    print(str(poles) + str(zeros))
    pole_value.set(f'{-poles[0]:.1f} Hz; {-poles[1]:.1f} Hz')
    zero_value.set(f'{-zeros[0]:.1f} Hz; {-zeros[1]:.1f} Hz')

    # bode plot
    plt.close()
    plt.cla()
    plt.clf()
    fig = plt.figure(figsize=(10, 8), dpi=100)
    # fig.add_subplot(111)
    ml.bode(G, Hz=True)
    plot = FigureCanvasTkAgg(fig, window)
    plot.get_tk_widget().grid(row=0, column=2, columnspan=8, rowspan=8)

# ------- GUI setup -------


window = tk.Tk()
window.title("Bode Plot")
window.config(padx=20, pady=20, height=500, width=1000)

# labels
r1_label = tk.Label(window, text="R1(kΩ): ")
r2_label = tk.Label(window, text="R2(kΩ): ")
c4_label = tk.Label(window, text="C4(nF): ")
c5_label = tk.Label(window, text="C5(nF): ")
pole_label = tk.Label(window, text="Poles: ")
pole_value, zero_value = tk.StringVar(), tk.StringVar()
pole_values = tk.Label(window, textvariable=pole_value)
zero_label = tk.Label(window, text="Zeros: ")
zero_values = tk.Label(window, textvariable=zero_value)

# entry boxes
r1_entry = tk.Entry(window, width=10)
r1_entry.insert(0, "15.0")
r2_entry = tk.Entry(window, width=10)
r2_entry.insert(0, "1.58")
c4_entry = tk.Entry(window, width=10)
c4_entry.insert(0, "0.1")
c5_entry = tk.Entry(window, width=10)
c5_entry.insert(0, "10000")

# buttons
plot_btn = tk.Button(window, text='plot bode', command=plot_bode)

# positions
r1_label.grid(row=0, column=0)
r1_entry.grid(row=0, column=1)
r2_label.grid(row=1, column=0)
r2_entry.grid(row=1, column=1)
c4_label.grid(row=2, column=0)
c4_entry.grid(row=2, column=1)
c5_label.grid(row=3, column=0)
c5_entry.grid(row=3, column=1)
plot_btn.grid(row=4, column=1)
pole_label.grid(row=5, column=0)
pole_values.grid(row=5, column=1)
zero_label.grid(row=6, column=0)
zero_values.grid(row=6, column=1)

window.mainloop()
