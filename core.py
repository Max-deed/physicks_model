import math

class Model:
    def __init__(self, m=1.0, h0=5.0, mu=0.1):
        self.m = m
        self.h0 = h0
        self.mu = mu

        self.g = 9.81
        self.dt = 0.1
        self.a = 0.3  #коэффициент параболы
        self.x0 = math.sqrt(h0 / self.a)

        self.x = self.x0
        self.vx = 0.0 #горизонтальная скорость
        self.t = 0.0
        #self.E_initial = self.m * self.g * self.h0
        self.Ep = 0.0
        self.Ek = 0.0
        self.E_mech = 0.0
        self.E_initial = None
        self.E_friction = 0.0
        self.is_stuck = True

        self.update_energies()

    def get_y(self, x):
        return self.a * x**2

    def get_slope(self, x): # y(x) = a*x^2 => y'(x) = 2ax, считает tg угла наклона
        return 2 * self.a * x

    def get_full_speed(self, x, vx):
        slope = self.get_slope(x)
        return abs(vx) * math.sqrt(1 + slope**2)

    def get_normal_force(self,x): # N = mg*cos(a), a - угол наклона
        slope = self.get_slope(x)
        angle = math.atan(slope)
        return self.m * self.g * math.cos(angle)

    def update_energies(self):
        y = self.get_y(self.x)

        self.Ep = self.m * self.g * y

        v_full = self.get_full_speed(self.x, self.vx)
        self.Ek = (self.m * v_full**2)/2

        self.E_mech = self.Ep + self.Ek #текущая полная механическая энергия

        # запоминаем начальную энергию при первом вызове
        if self.E_initial is None:
            self.E_initial = self.E_mech

        # считаем энергию, потерянную на трение
        self.E_friction = self.E_initial - self.E_mech

    def compute_acceleration(self, x, vx):
        '''ВОЗВРАЩАЕТ
        a_x - ускорение по горизонтали
        should_stop - должно ли тело остановиться'''
        slope = self.get_slope(x)
        angle = math.atan(slope)

        F_mg = -self.m * self.g * math.sin(angle)
        N = self.m * self.g * math.cos(angle)
        F_friction_max = self.mu * N

        cos_angle = math.cos(angle)
        if abs(cos_angle) < 0.000001:
            cos_angle = 0.000001
        v_along = vx / cos_angle #скорость вдоль траектории
        speed_threshold = 0.001 #ограничение скорости

        if abs(v_along) < speed_threshold:
            # ТЕЛО ПОКОИТСЯ
            if abs(F_mg) <= F_friction_max:
                # трение способно удержать шар на месте
                return 0.0, True
            else:
                # гравитация срывает с места шар и он продолжает двигаться
                F_friction = -math.copysign(F_friction_max, F_mg)
                F_total = F_mg + F_friction
                a_along = F_total / self.m      #из F = ma
                return a_along * cos_angle, False
        else:
            # ТЕЛО ДВИЖЕТСЯ
            F_friction = -math.copysign(F_friction_max, v_along)
            F_total = F_mg + F_friction
            a_along = F_total / self.m
            return a_along * cos_angle, False


    def step(self): # обновление системы во времени на dt при помощи метода Эйлера-Кромера
        if self.is_stuck:
            # тело застряло, делаем проверки
            a_x, should_stop = self.compute_acceleration(self.x, 0.0)
            if should_stop:
                self.t += self.dt
                return
            else:
                self.is_stuck = False
                self.vx = a_x * self.dt
                self.x += self.vx
                self.t += self.dt
                self.update_energies()
                return

        x_old = self.x
        vx_old = self.vx

        a_x, should_stop = self.compute_acceleration(x_old, vx_old)

        vx_new = vx_old + a_x * self.dt     # V = V0 + at
        x_new = x_old + vx_new * self.dt    # X = X0 + Vt

        if vx_old * vx_new < 0:     #проверка на смену знака
            if abs(a_x) > 0.00001:
                t_stop = -vx_old / a_x
                t_stop = max(0.0, min(t_stop, self.dt))
                x_stop = x_old + vx_old*t_stop + (a_x * t_stop**2)/2
            else:
                x_stop = x_old

            self.x = x_stop
            self.vx = 0.0

            # проверка, удержится ли в этой точке тело благодаря трению
            a_test, is_stuck_test = self.compute_acceleration(x_stop, 0.0)
            self.is_stuck = is_stuck_test
        else:
            # обычный шаг
            self.x = x_new
            self.vx = vx_new

        self.t += self.dt
        self.update_energies()

    def get_state(self):

        return {
            "t": self.t,
            "x": self.x,
            "y": self.get_y(self.x),
            "v": self.get_full_speed(self.x, self.vx),
            "Ek": self.Ek,
            "Ep": self.Ep,
            "A_total": self.E_initial,
            "A_useful": self.Ep,
            "A_friction": self.E_friction,
            "A_kinetic": self.Ek
        }
