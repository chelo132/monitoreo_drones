import customtkinter as ctk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import animation
from mpl_toolkits.mplot3d import Axes3D

ctk.set_appearance_mode("dark")  # Solo modo oscuro

# ---------- Lógica para calcular los parámetros de la elipse ----------
def generar_parametros(rut):
    digitos = [int(c) for c in rut if c.isdigit()]
    if len(digitos) < 8:
        return None  # RUT inválido

    h, k = digitos[0], digitos[1]
    grupo_val = digitos[7]  # Usamos d8

    if grupo_val % 2 == 1:  # Grupo impar
        a = digitos[2] + digitos[3]
        b = digitos[4] + digitos[5]
        orientacion = 'horizontal' if digitos[7] % 2 == 0 else 'vertical'
        grupo_tipo = "IMPAR"
    else:  # Grupo par
        a = digitos[5] + digitos[6]
        b = digitos[7] + digitos[2]
        orientacion = 'horizontal' if digitos[3] % 2 == 0 else 'vertical'
        grupo_tipo = "PAR"

    return h, k, a, b, orientacion, grupo_tipo, grupo_val

canvas = None
ani = None

def animar_elipse_2d_3d_embebida(h, k, a, b, orientacion, master_frame):
    global canvas, ani

    if canvas:
        canvas.get_tk_widget().destroy()
        canvas = None
        ani = None

    fig = plt.figure(figsize=(10, 5))

    t = np.linspace(0, 2 * np.pi, 300)
    if orientacion == 'horizontal':
        x = h + a * np.cos(t)
        y = k + b * np.sin(t)
    else:
        x = h + b * np.cos(t)
        y = k + a * np.sin(t)

    ax1 = fig.add_subplot(1, 2, 1)
    ax1.plot(x, y, 'b-', alpha=0.3)
    ax1.set_aspect('equal')
    ax1.set_title("Animación 2D")
    ax1.grid(True)
    ax1.set_xlim(min(x) - 1, max(x) + 1)
    ax1.set_ylim(min(y) - 1, max(y) + 1)
    ax1.scatter(h, k, color='red')
    ax1.text(h, k - 0.15, f'Centro ({h},{k})', ha='center', va='top', fontsize=9, color='red')

    point_2d, = ax1.plot([], [], 'ro', markersize=8)

    ax2 = fig.add_subplot(1, 2, 2, projection='3d')
    z = np.sin(t) * 2
    ax2.plot3D(x, y, z, 'b-', alpha=0.3)
    ax2.set_title("Animación 3D")
    ax2.scatter(h, k, 0, color='red')
    ax2.set_xlim(min(x) - 1, max(x) + 1)
    ax2.set_ylim(min(y) - 1, max(y) + 1)
    ax2.set_zlim(min(z) - 1, max(z) + 1)

    point_3d, = ax2.plot([], [], [], 'ro', markersize=8)

    def update(i):
        point_2d.set_data([x[i]], [y[i]])
        point_3d.set_data([x[i]], [y[i]])
        point_3d.set_3d_properties([z[i]])
        return point_2d, point_3d

    canvas = FigureCanvasTkAgg(fig, master=master_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(pady=10, fill='both', expand=True)

    ani = animation.FuncAnimation(fig, update, frames=len(t), interval=20, blit=True)

def procesar():
    rut = entry_rut.get()
    params = generar_parametros(rut)
    if not params:
        resultado.configure(text="⚠️ RUT inválido (mínimo 8 dígitos numéricos)")
        return

    h, k, a, b, orientacion, grupo_tipo, grupo_valor = params
    resultado.configure(
        text=f"Grupo {grupo_tipo} (d8 = {grupo_valor}) | Centro: ({h},{k}), a = {a}, b = {b}, orientación {orientacion}"
    )

    animar_elipse_2d_3d_embebida(h, k, a, b, orientacion, frame_animacion)

root = ctk.CTk()
root.title("Simulador de Trayectorias de Drones")
root.geometry("900x700")

frame = ctk.CTkFrame(master=root, fg_color="#121212", corner_radius=10, border_width=2, border_color="#0d6f8f")
frame.pack(pady=10, padx=10, fill="both", expand=True)

titulo = ctk.CTkLabel(master=frame, text="Modelador de Trayectorias de Drones", font=("Arial", 24), text_color="#d0f0fd")
titulo.pack(pady=10)

entry_rut = ctk.CTkEntry(
    master=frame,
    placeholder_text="Ingresa RUT (ej: 12.345.678-9)",
    width=400,
    height=45,
    font=("Arial", 18),
    fg_color="#121212",
    border_color="#0d6f8f",
    text_color="#d0f0fd",
    placeholder_text_color="#7ab8c6"
)
entry_rut.pack(pady=10)

boton_generar = ctk.CTkButton(master=frame, text="Generar y Animar Trayectoria", command=procesar,
                              fg_color="#0d6f8f", hover_color="#1282a2", text_color="#d0f0fd")
boton_generar.pack(pady=10)

resultado = ctk.CTkLabel(master=frame, text="", font=("Arial", 14), text_color="#d0f0fd")
resultado.pack(pady=5)

frame_animacion = ctk.CTkFrame(master=frame, fg_color="#121212", corner_radius=10, border_width=2, border_color="#0d6f8f")
frame_animacion.pack(pady=10, fill="both", expand=True)

canvas = None
ani = None

root.mainloop()
