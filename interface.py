import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import math


class Model:
    def __init__(self, m=1.0, h0=5.0, mu=0.1):
        self.m = m
        self.h0 = h0
        self.mu = mu

        self.g = 9.81
        self.t = 0
        self.dt = 0.05

        self.E_initial = self.m * self.g * self.h0

    def step(self):
        self.t += self.dt

    def get_state(self):
        # Временная имитация движения/энергий
        # Потом это заменится на данные от физической модели

        damping = math.exp(-self.mu * self.t)

        Ek = self.E_initial * abs(math.sin(self.t)) * damping
        Ep = self.E_initial * abs(math.cos(self.t)) * damping

        A_kinetic = Ek
        A_friction = self.E_initial * (1 - damping)

        A_useful = self.E_initial - A_friction - A_kinetic

        if A_useful < 0:
            A_useful = 0

        return {
            "t": self.t,
            "Ek": Ek,
            "Ep": Ep,
            "A_total": self.E_initial,
            "A_useful": A_useful,
            "A_friction": A_friction,
            "A_kinetic": A_kinetic
        }


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Physics Model Interface")

        self.model = Model()
        self.running = False

        self.t_values = []
        self.ek_values = []
        self.ep_values = []

        self.current_work_state = {
            "A_useful": 0,
            "A_friction": 0,
            "A_kinetic": 0
        }

        self.create_widgets()
        self.update_loop()

    def create_widgets(self):
        control_frame = ttk.Frame(self.root)
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        ttk.Label(control_frame, text="Mass m, kg:").pack(side=tk.LEFT, padx=5)
        self.mass_entry = ttk.Entry(control_frame, width=8)
        self.mass_entry.insert(0, "1.0")
        self.mass_entry.pack(side=tk.LEFT, padx=5)

        ttk.Label(control_frame, text="Height h0, m:").pack(side=tk.LEFT, padx=5)
        self.height_entry = ttk.Entry(control_frame, width=8)
        self.height_entry.insert(0, "5.0")
        self.height_entry.pack(side=tk.LEFT, padx=5)

        ttk.Label(control_frame, text="Friction μ:").pack(side=tk.LEFT, padx=5)
        self.mu_entry = ttk.Entry(control_frame, width=8)
        self.mu_entry.insert(0, "0.1")
        self.mu_entry.pack(side=tk.LEFT, padx=5)

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

        self.fig, (self.energy_ax, self.work_ax) = plt.subplots(
            1,
            2,
            figsize=(11, 4)
        )

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.line_ek, = self.energy_ax.plot([], [], label="Kinetic energy")
        self.line_ep, = self.energy_ax.plot([], [], label="Potential energy")

    def read_params(self):
        try:
            m = float(self.mass_entry.get())
            h0 = float(self.height_entry.get())
            mu = float(self.mu_entry.get())

            if m <= 0:
                raise ValueError("Mass must be greater than 0")

            if h0 <= 0:
                raise ValueError("Height must be greater than 0")

            if mu < 0:
                raise ValueError("Friction coefficient must be >= 0")

            return m, h0, mu

        except ValueError as error:
            messagebox.showerror("Input error", str(error))
            return None

    def start(self):
        params = self.read_params()

        if params is None:
            return

        if len(self.t_values) == 0:
            m, h0, mu = params
            self.model = Model(m, h0, mu)

        self.running = True

    def pause(self):
        self.running = False

    def reset(self):
        self.running = False

        params = self.read_params()

        if params is None:
            return

        m, h0, mu = params
        self.model = Model(m, h0, mu)

        self.t_values.clear()
        self.ek_values.clear()
        self.ep_values.clear()

        self.current_work_state = {
            "A_useful": 0,
            "A_friction": 0,
            "A_kinetic": 0
        }

        self.draw_plots()

    def update_loop(self):
        if self.running:
            self.model.step()
            state = self.model.get_state()

            self.t_values.append(state["t"])
            self.ek_values.append(state["Ek"])
            self.ep_values.append(state["Ep"])

            self.current_work_state = {
                "A_useful": state["A_useful"],
                "A_friction": state["A_friction"],
                "A_kinetic": state["A_kinetic"]
            }

            self.draw_plots()

        self.root.after(30, self.update_loop)

    def draw_plots(self):
        self.line_ek.set_data(self.t_values, self.ek_values)
        self.line_ep.set_data(self.t_values, self.ep_values)

        self.energy_ax.relim()
        self.energy_ax.autoscale_view()

        self.energy_ax.set_title("Energy over time")
        self.energy_ax.set_xlabel("t, s")
        self.energy_ax.set_ylabel("E, J", rotation=0, labelpad=30)
        self.energy_ax.legend()
        self.energy_ax.grid(True)

        self.work_ax.clear()

        labels = ["Useful", "Friction", "Kinetic"]
        values = [
            self.current_work_state["A_useful"],
            self.current_work_state["A_friction"],
            self.current_work_state["A_kinetic"]
        ]

        self.work_ax.bar(labels, values)

        self.work_ax.set_title("Work distribution")
        self.work_ax.set_ylabel("A, J", rotation=0, labelpad=30)
        self.work_ax.grid(True, axis="y")

        self.fig.subplots_adjust(wspace=0.4)

        self.canvas.draw()


root = tk.Tk()
app = App(root)
root.mainloop()