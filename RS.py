from brian2 import *
import matplotlib.pyplot as plt

# ---- force NO compiled cache ----
prefs.codegen.target = "numpy"

start_scope()

# timestep
defaultclock.dt = 0.01*ms

# simulation length
duration = 1000*ms
dt = defaultclock.dt

# ---- stimulus: DC=10 after 100 ms ----
I_values = zeros(int(duration/dt))
I_values[int(600*ms/dt):] = 10
I_t = TimedArray(I_values, dt=dt)

# ---- Izhikevich resonator equations ----
eqs = '''
dv/dt = (0.04*v**2 + 5*v + 140 - u + I_t(t)) / ms : 1
du/dt = a*(b*v - u) / ms : 1
a : 1
b : 1
c : 1
d : 1
'''

G = NeuronGroup(
    1,
    eqs,
    threshold='v >= 30',
    reset='v = c; u += d',
    method='euler'
)

# ---- resonator parameters (paper values) ----
G.v = -60
G.a = 0.1
G.b = 0.26
G.c = -65
G.d = 2
G.u = G.b * G.v

print("dt:", defaultclock.dt)
print("c,d:", G.c[:], G.d[:])

M = StateMonitor(G, 'v', record=True)

run(duration)

plt.figure(figsize=(8, 4))
plt.plot(M.t/ms, M.v[0])
plt.xlabel("Time (ms)")
plt.ylabel("v")
plt.title("Izhikevich resonator test")
plt.show()
