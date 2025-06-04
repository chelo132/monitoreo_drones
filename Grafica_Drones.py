import customtkinter as ctk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import animation
from mpl_toolkits.mplot3d import Axes3D
import os


ctk.set_appearance_mode("dark")  # Solo modo oscuro
ruts_multiples = []


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

def agregar_rut():
    rut = entry_rut.get()
    if len([c for c in rut if c.isdigit()]) < 8:
        resultado.configure(text="⚠️ RUT inválido (mínimo 8 dígitos numéricos)")
        return
    ruts_multiples.append(rut)
    resultado.configure(text=f"✅ RUT agregado: {rut}")


def animar_multiples_trayectorias(master_frame):
    global canvas, ani

    if canvas:
        canvas.get_tk_widget().destroy()
        canvas = None
        ani = None

    if not ruts_multiples:
        resultado.configure(text="⚠️ No hay RUTs en la lista")
        return

    ruts_validos = [rut for rut in ruts_multiples if generar_parametros(rut)]

    if not ruts_validos:
        resultado.configure(text="⚠️ No hay RUTs válidos en la lista")
        return
    
    colormap = plt.get_cmap('viridis')
    colores = colormap(np.linspace(0, 1, len(ruts_validos))) #hay un error que no afecta al programa debe ser un bug del propio mat asi que de ahi lo veo xD

    # Detectar colisiones entre pares de elipses
    colisiones = []
    for i in range(len(ruts_validos)):
        for j in range(i + 1, len(ruts_validos)):
            p1 = generar_parametros(ruts_validos[i])
            p2 = generar_parametros(ruts_validos[j])
            if elipses_colisionan(p1, p2):
                colisiones.append((ruts_validos[i], ruts_validos[j]))

    if colisiones:
        mensaje = "⚠️ Colisión detectada entre:\n" + "\n".join(
            [f"→ {a} y {b}" for a, b in colisiones]
        )
        resultado.configure(text=mensaje)
    else:
        resultado.configure(text="✅ Sin colisiones detectadas entre trayectorias.")


    fig = plt.figure(figsize=(10, 5))
    ax1 = fig.add_subplot(1, 2, 1)
    ax2 = fig.add_subplot(1, 2, 2, projection='3d')

    puntos_2d = []
    puntos_3d = []


    todas_x, todas_y, todas_z = [], [], []

    for idx, rut in enumerate(ruts_multiples):
        params = generar_parametros(rut)
        if not params:
            continue
        h, k, a, b, orientacion, _, _ = params
        t = np.linspace(0, 2 * np.pi, 300)

        if orientacion == 'horizontal':
            x = h + a * np.cos(t)
            y = k + b * np.sin(t)
        else:
            x = h + b * np.cos(t)
            y = k + a * np.sin(t)

        z = np.sin(t + idx) * 2

        ax1.plot(x, y, color=colores[idx], alpha=0.5)
        ax1.scatter(h, k, color=colores[idx])
        punto2d, = ax1.plot([], [], 'o', color=colores[idx], markersize=5)
        puntos_2d.append((punto2d, x, y))

        ax2.plot3D(x, y, z, color=colores[idx], alpha=0.5)
        ax2.scatter(h, k, 0, color=colores[idx])
        punto3d, = ax2.plot([], [], [], 'o', color=colores[idx], markersize=5)
        puntos_3d.append((punto3d, x, y, z))

        todas_x.extend(x)
        todas_y.extend(y)
        todas_z.extend(z)

    ax1.set_title("Múltiples Trayectorias 2D")
    ax1.set_aspect("equal")
    ax1.grid(True)
    ax1.set_xlim(min(todas_x) - 1, max(todas_x) + 1)
    ax1.set_ylim(min(todas_y) - 1, max(todas_y) + 1)

    ax2.set_title("Múltiples Trayectorias 3D")
    ax2.set_xlim(min(todas_x) - 1, max(todas_x) + 1)
    ax2.set_ylim(min(todas_y) - 1, max(todas_y) + 1)
    ax2.set_zlim(min(todas_z) - 1, max(todas_z) + 1)

    def update(i):
        for punto, x, y in puntos_2d:
            punto.set_data([x[i]], [y[i]])
        for punto, x, y, z in puntos_3d:
            punto.set_data([x[i]], [y[i]])
            punto.set_3d_properties([z[i]])
        return [p[0] for p in puntos_2d + puntos_3d]

    canvas = FigureCanvasTkAgg(fig, master=master_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(pady=10, fill='both', expand=True)

    ani = animation.FuncAnimation(fig, update, frames=300, interval=20, blit=True)


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


def elipses_colisionan(params1, params2):
    h1, k1, a1, b1, orient1, *_ = params1
    h2, k2, a2, b2, orient2, *_ = params2

    # Distancia entre centros
    distancia = np.sqrt((h2 - h1) ** 2 + (k2 - k1) ** 2)

    # Radio de seguridad depende de la orientación
    if orient1 == 'horizontal' and orient2 == 'horizontal':
        radio_seguridad = a1 + a2
    elif orient1 == 'vertical' and orient2 == 'vertical':
        radio_seguridad = b1 + b2
    else:
        # Si son diferentes, usar una combinación de ambos
        radio_seguridad = max(a1, b1) + max(a2, b2)

    return distancia < radio_seguridad


def cerrar_programa():
    global ani
    try:
        if ani:
            ani.event_source.stop()  # Detiene la animación
    except:
        pass
    root.destroy()
    os._exit(0)


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

boton_agregar_rut = ctk.CTkButton(master=frame, text="Agregar RUT a la Lista", command=agregar_rut,
                                  fg_color="#1c7c54", hover_color="#239b66", text_color="#ffffff")
boton_agregar_rut.pack(pady=5)

boton_simular_multiples = ctk.CTkButton(master=frame, text="Simular Múltiples Trayectorias",
                                        command=lambda: animar_multiples_trayectorias(frame_animacion),
                                        fg_color="#aa3e98", hover_color="#c758b1", text_color="#ffffff")
boton_simular_multiples.pack(pady=5)


frame_animacion = ctk.CTkFrame(master=frame, fg_color="#121212", corner_radius=10, border_width=2, border_color="#0d6f8f")
frame_animacion.pack(pady=10, fill="both", expand=True)

root.protocol("WM_DELETE_WINDOW", cerrar_programa)

canvas = None
ani = None

root.mainloop()
