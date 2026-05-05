import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import math
import numpy as np


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
        self.root.geometry("1300x650")

        self.model = Model()
        self.running = False
        self.was_started = False

        self.t_values = []
        self.ek_values = []
        self.ep_values = []

        self.current_work_state = {
            "A_useful": 0,
            "A_friction": 0,
            "A_kinetic": 0
        }

        self.create_widgets()
        self.draw_plots()
        self.update_loop()

    def create_widgets(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        control_frame = ttk.Frame(main_frame)
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

        self.start_button = ttk.Button(control_frame, text="Start", command=self.start)
        self.start_button.pack(side=tk.LEFT, padx=5)

        self.stop_button = ttk.Button(control_frame, text="Stop", command=self.pause)
        self.stop_button.pack(side=tk.LEFT, padx=5)

        self.reset_button = ttk.Button(control_frame, text="Reset", command=self.reset)
        self.reset_button.pack(side=tk.LEFT, padx=5)

        self.info_label = ttk.Label(
            main_frame,
            text="t = 0.00 s | Ek = 0.00 J | Ep = 0.00 J | Useful = 0.00 J | Friction = 0.00 J | Kinetic work = 0.00 J"
        )
        self.info_label.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        self.fig, (self.motion_ax, self.energy_ax, self.work_ax) = plt.subplots(
            1, 3, figsize=(15, 5)
        )

        self.fig.subplots_adjust(wspace=0.45)

        self.canvas = FigureCanvasTkAgg(self.fig, master=main_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

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

        if not self.was_started:
            m, h0, mu = params
            self.model = Model(m, h0, mu)
            self.was_started = True

        self.running = True

    def pause(self):
        self.running = False

    def reset(self):
        self.running = False
        self.was_started = False

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

        self.info_label.config(
            text="t = 0.00 s | Ek = 0.00 J | Ep = 0.00 J | Useful = 0.00 J | Friction = 0.00 J | Kinetic work = 0.00 J"
        )

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

            self.info_label.config(
                text=(
                    f"t = {state['t']:.2f} s | "
                    f"Ek = {state['Ek']:.2f} J | "
                    f"Ep = {state['Ep']:.2f} J | "
                    f"Useful = {state['A_useful']:.2f} J | "
                    f"Friction = {state['A_friction']:.2f} J | "
                    f"Kinetic work = {state['A_kinetic']:.2f} J"
                )
            )

            self.draw_plots()

        self.root.after(30, self.update_loop)

    def draw_motion_visualization(self):
        self.motion_ax.clear()

        a = 0.3
        h0 = self.model.h0
        mu = self.model.mu

        # Стартовая координата из условия y = a*x^2 => x = sqrt(h0/a)
        x_start = math.sqrt(h0 / a)

        # Делаем запас по x, чтобы шарик не упирался в край
        x_limit = x_start * 1.15

        # Минимальный размер графика, чтобы при маленьких h0 всё не сжималось
        x_limit = max(x_limit, 2.0)

        # Парабола строится под текущую высоту h0
        x_values = np.linspace(-x_limit, x_limit, 500)
        y_values = a * x_values ** 2

        self.motion_ax.plot(x_values, y_values, label="Parabolic track")

        # Шарик стартует на высоте h0
        if len(self.t_values) > 0:
            t = self.t_values[-1]

            damping = math.exp(-mu * self.model.t)

            x_ball = x_start * math.cos(t) * damping
            y_ball = a * x_ball ** 2
        else:
            x_ball = x_start
            y_ball = h0

        self.motion_ax.scatter(x_ball, y_ball, s=90, label="Ball")

        # Стрелка силы тяжести масштабируется от высоты
        arrow_length = max(h0 * 0.12, 0.4)

        self.motion_ax.arrow(
            x_ball,
            y_ball,
            0,
            -arrow_length,
            head_width=x_limit * 0.035,
            head_length=arrow_length * 0.25,
            length_includes_head=True
        )

        y_limit = max(h0 * 1.2, 2.0)

        self.motion_ax.set_title("Motion visualization")
        self.motion_ax.set_xlabel("x, m")
        self.motion_ax.set_ylabel("y, m", rotation=0, labelpad=20)

        self.motion_ax.set_xlim(-x_limit, x_limit)
        self.motion_ax.set_ylim(-y_limit * 0.08, y_limit)

        self.motion_ax.grid(True)
        self.motion_ax.legend()

    def draw_energy_plot(self):
        self.energy_ax.clear()

        self.energy_ax.plot(
            self.t_values,
            self.ek_values,
            label="Kinetic energy"
        )

        self.energy_ax.plot(
            self.t_values,
            self.ep_values,
            label="Potential energy"
        )

        self.energy_ax.set_title("Energy over time")
        self.energy_ax.set_xlabel("t, s")
        self.energy_ax.set_ylabel("E, J", rotation=0, labelpad=25)
        self.energy_ax.legend()
        self.energy_ax.grid(True)

    def draw_work_distribution(self):
        self.work_ax.clear()

        labels = ["Useful", "Friction", "Kinetic"]

        values = [
            self.current_work_state["A_useful"],
            self.current_work_state["A_friction"],
            self.current_work_state["A_kinetic"]
        ]

        bars = self.work_ax.bar(labels, values)

        for bar, value in zip(bars, values):
            self.work_ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height(),
                f"{value:.2f}",
                ha="center",
                va="bottom",
                fontsize=9
            )

        max_value = max(values) if max(values) > 0 else self.model.E_initial
        self.work_ax.set_ylim(0, max_value * 1.25)

        self.work_ax.set_title("Work distribution")
        self.work_ax.set_ylabel("A, J", rotation=0, labelpad=25)
        self.work_ax.grid(True, axis="y")

    def draw_plots(self):
        self.draw_motion_visualization()
        self.draw_energy_plot()
        self.draw_work_distribution()

        self.fig.subplots_adjust(wspace=0.45)
        self.canvas.draw()


root = tk.Tk()
app = App(root)
root.mainloop()