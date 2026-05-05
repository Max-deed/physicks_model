import tkinter as tk
from tkinter import ttk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import math

class Model:
    def __init__(self):
        self.t = 0
        self.dt = 0.05

    def step(self):
        self.t += self.dt

    def get_state(self):
        # Временная имитация энергий
        Ek = 5 * abs(math.sin(self.t))
        Ep = 5 * abs(math.cos(self.t))

        return {
            "t": self.t,
            "Ek": Ek,
            "Ep": Ep
        }

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Energy graphicks")

        self.model = Model()
        self.running = False

        self.t_values = []
        self.ek_values = []
        self.ep_values = []

        self.creat_widgets()
        self.update_loop()

    def creat_widgets(self):
        control_frame = ttk.Frame(self.root)
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        self.start_button = ttk.Button(
            control_frame,
            text="Start",
            command=self.start
        )
        self.start_button.pack(side=tk.LEFT, padx=5)


        self.stop_button = ttk.Button(
            control_frame, 
            text="Stop",
            command=self.pause
        )
        self.stop_button.pack(side=tk.LEFT, padx=5)

        self.reset_button = ttk.Button(
            control_frame,
            text="Reset",
            command=self.reset
        )
        self.reset_button.pack(side=tk.LEFT, padx=5)

        self.fig, self.ax = plt.subplots(figsize=(7, 4))

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def start(self):
        self.running = True

    def pause(self):
        self.running = False

    def reset(self):
        self.running = False

        self.model = Model()

        self.t_values.clear()
        self.ek_values.clear()
        self.ep_values.clear()

        self.draw_plot()

    def update_loop(self):
        if self.running:
            self.model.step()
            state = self.model.get_state()

            self.t_values.append(state["t"])
            self.ek_values.append(state["Ek"])
            self.ep_values.append(state["Ep"])

            self.draw_plot()

        self.root.after(50, self.update_loop)

    def draw_plot(self):
        self.ax.clear()

        self.ax.plot(
            self.t_values,
            self.ek_values,
            label="Kinetic energy"
        )

        self.ax.plot(
            self.t_values,
            self.ep_values,
            label="Potential energy"
        )

        self.ax.set_title("Energy graphics")
        self.ax.set_xlabel("t, s")
        self.ax.set_ylabel("E, J")
        self.ax.legend()
        self.ax.grid(True)

        self.canvas.draw()

root = tk.Tk()
app = App(root)
root.mainloop()
