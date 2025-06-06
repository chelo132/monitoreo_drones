import customtkinter as ctk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import animation
from mpl_toolkits.mplot3d import Axes3D
import os
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

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
        a = min(a, 6)
        b = min(b, 6)
        orientacion = 'horizontal' if digitos[7] % 2 == 0 else 'vertical'
        grupo_tipo = "IMPAR"
    else:  # Grupo par
        a = digitos[5] + digitos[6]
        b = digitos[7] + digitos[2]
        a = min(a, 6)
        b = min(b, 6)

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
    refresh_rut_list()

def obtener_ecuacion_elipse(h, k, a, b, orientacion):
    if orientacion == 'horizontal':
        eq = f"((x - {h})² / {a**2}) + ((y - {k})² / {b**2}) = 1"
    else:
        eq = f"((x - {h})² / {b**2}) + ((y - {k})² / {a**2}) = 1"
    return eq

def renderizar_latex(enunciado, parent_frame, ancho=6.5, alto=1, fontsize=14):
    fig = Figure(figsize=(ancho, alto), dpi=100, facecolor='none')
    ax = fig.add_subplot(111)
    ax.set_facecolor("none")  # Sin fondo en el área del gráfico
    ax.axis("off")

    ax.text(0.5, 0.5, f"${enunciado}$", fontsize=fontsize, ha='center', va='center', color='white')

    canvas = FigureCanvasTkAgg(fig, master=parent_frame)
    canvas.draw()
    widget = canvas.get_tk_widget()
    widget.config(bg="#1a1a1a", highlightthickness=0)  # Combina con el fondo oscuro
    widget.pack(pady=5)


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
    ruts_en_colision = set()

    for i in range(len(ruts_validos)):
        for j in range(i + 1, len(ruts_validos)):
            p1 = generar_parametros(ruts_validos[i])
            p2 = generar_parametros(ruts_validos[j])
            if elipses_colisionan(p1, p2):
                colisiones.append((ruts_validos[i], ruts_validos[j]))
                ruts_en_colision.add(ruts_validos[i])
                ruts_en_colision.add(ruts_validos[j])



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

    for idx, rut in enumerate(ruts_validos):
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

        # 🎨 Elegimos el color según colisión
        if rut in ruts_en_colision:
            # Matiz si termina en número impar
            alpha = 0.8 if int(rut[-1]) % 2 == 0 else 0.5
            color = (1, 0, 0, alpha)  # rojo con transparencia
        else:
            color = "limegreen"

        # 📉 Dibujamos trayectoria 2D
        ax1.plot(x, y, color=color, alpha=1.0, linewidth=2, linestyle='-')
        ax1.scatter(h, k, color=color)
        punto2d, = ax1.plot([], [], 'o', color=color, markersize=5)
        puntos_2d.append((punto2d, x, y))

        # 📈 Dibujamos trayectoria 3D
        ax2.plot3D(x, y, z, color=color, alpha=1.0, linewidth=2)
        ax2.scatter(h, k, 0, color=color)
        punto3d, = ax2.plot([], [], [], 'o', color=color, markersize=5)
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

def mostrar_ventana_creditos():
    ventana = ctk.CTkToplevel()
    ventana.title("Créditos del Proyecto")
    ventana.geometry("400x300")
    ventana.resizable(False, False)

    ctk.CTkLabel(ventana, text=" Proyecto: Modelado de Trayectorias de Drones", font=("Arial", 16, "bold")).pack(pady=10)

    ctk.CTkLabel(ventana, text="Integrantes:", font=("Arial", 14, "bold")).pack()
    ctk.CTkLabel(ventana, text=" Marcelo Matamala\n• Catalina Vergara\n• Francisco Benavides\n• José Sáez", font=("Arial", 13)).pack(pady=5)

    ctk.CTkLabel(ventana, text=" Profesor: Gabriel Sandoval", font=("Arial", 13)).pack(pady=5)
    ctk.CTkLabel(ventana, text=" Asignatura: MAT1186 - Introducción al Cálculo", font=("Arial", 13)).pack(pady=5)

    ctk.CTkButton(ventana, text="Cerrar", command=ventana.destroy).pack(pady=10)


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
    ecuacion = obtener_ecuacion_elipse(h, k, a, b, orientacion)
    label_ecuacion.configure(text=f"Ecuación canónica:\n{ecuacion}")


    animar_elipse_2d_3d_embebida(h, k, a, b, orientacion, frame_animacion)
    mostrar_ventana_ecuaciones(rut, h, k, a, b, orientacion)

def obtener_ecuaciones_elipse(h, k, a, b, orientacion):
    if orientacion == 'horizontal':
        canonica = (
            f"\\frac{{(x - {h})^2}}{{{a**2}}} + \\frac{{(y - {k})^2}}{{{b**2}}} = 1"
        )
        A = 1 / a**2
        C = 1 / b**2
    else:
        canonica = (
            f"\\frac{{(x - {h})^2}}{{{b**2}}} + \\frac{{(y - {k})^2}}{{{a**2}}} = 1"
        )
        A = 1 / b**2
        C = 1 / a**2

    D = -2 * A * h
    E = -2 * C * k
    F = A * h**2 + C * k**2 - 1

    general = (
        f"{A:.4f}x^2 + {C:.4f}y^2 + ({D:.4f})x + ({E:.4f})y + ({F:.4f}) = 0"
    )

    return canonica, general


def mostrar_ventana_ecuaciones(rut, h, k, a, b, orientacion):
    canonica, general = obtener_ecuaciones_elipse(h, k, a, b, orientacion)

    ventana = ctk.CTkToplevel()
    ventana.title("Ecuaciones de la Elipse")
    ventana.geometry("750x400")
    ventana.resizable(False, False)

    ctk.CTkLabel(ventana, text="📐 Ecuaciones de la Elipse", font=("Arial", 16, "bold")).pack(pady=5)
    ctk.CTkLabel(ventana, text=f"🔢 RUT: {rut}", font=("Arial", 13)).pack(pady=5)

    # ---------- Mostrar ecuación canónica con fracciones ----------
    ctk.CTkLabel(ventana, text="🟦 Ecuación Canónica:", font=("Arial", 14, "bold")).pack()
    renderizar_latex(canonica, ventana)

    # ---------- Mostrar ecuación general (formato LaTeX) ----------
    ctk.CTkLabel(ventana, text="🟥 Ecuación General:", font=("Arial", 14, "bold")).pack()
    renderizar_latex(general, ventana)

    ctk.CTkButton(ventana, text="Cerrar", command=ventana.destroy).pack(pady=10)


def elipses_colisionan(p1, p2, steps=300):
    if not p1 or not p2:
        return False

    h1, k1, a1, b1, orient1, *_ = p1
    h2, k2, a2, b2, orient2, *_ = p2

    t = np.linspace(0, 2 * np.pi, steps)

    if orient1 == "horizontal":
        x1 = h1 + a1 * np.cos(t)
        y1 = k1 + b1 * np.sin(t)
    else:
        x1 = h1 + b1 * np.cos(t)
        y1 = k1 + a1 * np.sin(t)

    if orient2 == "horizontal":
        x2 = h2 + a2 * np.cos(t)
        y2 = k2 + b2 * np.sin(t)
    else:
        x2 = h2 + b2 * np.cos(t)
        y2 = k2 + a2 * np.sin(t)

    # Comparar distancia entre todos los puntos
    for i in range(steps):
        distancias = np.sqrt((x2 - x1[i]) ** 2 + (y2 - y1[i]) ** 2)
        if np.any(distancias < 0.5):  # Umbral mínimo de contacto
            return True

    return False

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
root.geometry("900x800")

frame = ctk.CTkFrame(master=root, corner_radius=10, border_width=2)
frame.pack(pady=10, padx=10, fill="both", expand=True)

container_frame = ctk.CTkFrame(master=frame, corner_radius=10, border_width=0)
container_frame.pack(pady=10, padx=10, fill="x", expand=False)

left_frame = ctk.CTkFrame(master=container_frame, corner_radius=10, border_width=2, border_color="#0d6f8f")
left_frame.pack(side="left", fill="y", expand=False, padx=(0, 10))

titulo = ctk.CTkLabel(master=left_frame, text="Modelador de Trayectorias de Drones", font=("Arial", 24), text_color="#d0f0fd")
titulo.pack(pady=10)

entry_rut = ctk.CTkEntry(
    master=left_frame,
    placeholder_text="Ingresa RUT (ej: 12.345.678-9)",
    width=400,
    height=45,
    font=("Arial", 18),
    fg_color="#121212",
    border_color="#0d6f8f",
    text_color="#d0f0fd",
    placeholder_text_color="#7ab8c6"
)
entry_rut.pack(pady=10, padx=10)

boton_generar = ctk.CTkButton(master=left_frame, text="Generar y Animar Trayectoria", command=procesar,
                              fg_color="#0d6f8f", hover_color="#1282a2", text_color="#d0f0fd")
boton_generar.pack(pady=10)

resultado = ctk.CTkLabel(master=left_frame, text="", font=("Arial", 14), text_color="#d0f0fd")
resultado.pack(pady=5)

label_ecuacion = ctk.CTkLabel(master=left_frame, text="", font=("Arial", 14), text_color="#d0f0fd", wraplength=800, justify="center")
label_ecuacion.pack(pady=5)

boton_creditos = ctk.CTkButton(master=left_frame, text="Créditos del Proyecto",
                               command=mostrar_ventana_creditos,
                               fg_color="#444", hover_color="#666", text_color="#fff")
boton_creditos.pack(pady=10)



boton_agregar_rut = ctk.CTkButton(master=left_frame, text="Agregar RUT a la Lista", command=agregar_rut,
                                  fg_color="#1c7c54", hover_color="#239b66", text_color="#ffffff")
boton_agregar_rut.pack(pady=5)

boton_simular_multiples = ctk.CTkButton(master=left_frame, text="Simular Múltiples Trayectorias",
                                        command=lambda: animar_multiples_trayectorias(frame_animacion),
                                        fg_color="#aa3e98", hover_color="#c758b1", text_color="#ffffff")

boton_simular_multiples.pack(pady=5)

right_frame = ctk.CTkFrame(master=container_frame, corner_radius=10, border_width=2, border_color="#0d6f8f")
right_frame = ctk.CTkFrame(master=container_frame, corner_radius=10, border_width=2, border_color="#0d6f8f")
right_frame.pack(side="left", fill="both", expand=True)

ctk.CTkLabel(master=right_frame, text="RUTs Agregados", font=("Arial", 18), text_color="#d0f0fd").pack(pady=10)

selected_rut_index = None

def refresh_rut_list():
    for widget in rut_list_container.winfo_children():
        widget.destroy()
    for idx, rut in enumerate(ruts_multiples):
        def on_click(event, index=idx):
            global selected_rut_index
            selected_rut_index = index
            refresh_rut_list()
        label_color = "#0d6f8f" if idx == selected_rut_index else "#1a1a1a"
        label_fg = "white" if idx == selected_rut_index else "#d0f0fd"
        rut_label = ctk.CTkLabel(rut_list_container, text=rut, fg_color=label_color, text_color=label_fg, corner_radius=5, height=30)
        rut_label.pack(fill="x", pady=2, padx=5)
        rut_label.bind("<Button-1>", on_click)

rut_list_container = ctk.CTkScrollableFrame(master=right_frame, width=300, height=300, fg_color="#121212", corner_radius=10, border_width=2, border_color="#0d6f8f")
rut_list_container.pack(padx=10, pady=10, fill="both", expand=True)

refresh_rut_list()

def eliminar_rut_seleccionado():
    global selected_rut_index
    if selected_rut_index is not None and 0 <= selected_rut_index < len(ruts_multiples):
        del ruts_multiples[selected_rut_index]
        selected_rut_index = None
        refresh_rut_list()
        resultado.configure(text="✅ RUT eliminado de la lista")
    else:
        resultado.configure(text="⚠️ No hay RUT seleccionado para eliminar")

boton_eliminar_rut = ctk.CTkButton(master=right_frame, text="Eliminar RUT seleccionado", command=eliminar_rut_seleccionado,
                                   fg_color="#a83232", hover_color="#d04040", text_color="#fff")
boton_eliminar_rut.pack(pady=5)

def editar_rut_seleccionado():
    global selected_rut_index
    if selected_rut_index is None or not (0 <= selected_rut_index < len(ruts_multiples)):
        resultado.configure(text="⚠️ No hay RUT seleccionado para editar")
        return

    def guardar_edicion():
        nuevo_rut = entry_editar.get()
        if len([c for c in nuevo_rut if c.isdigit()]) < 8:
            resultado.configure(text="⚠️ RUT inválido (mínimo 8 dígitos numéricos)")
            return
        ruts_multiples[selected_rut_index] = nuevo_rut
        resultado.configure(text=f"✅ RUT editado: {nuevo_rut}")
        refresh_rut_list()
        ventana_editar.destroy()

    ventana_editar = ctk.CTkToplevel()
    ventana_editar.title("Editar RUT")
    ventana_editar.geometry("400x150")
    ventana_editar.resizable(False, False)

    ctk.CTkLabel(ventana_editar, text="Editar RUT seleccionado:", font=("Arial", 14)).pack(pady=10)
    entry_editar = ctk.CTkEntry(ventana_editar, width=300, height=30, font=("Arial", 14))
    entry_editar.pack(pady=5)
    entry_editar.insert(0, ruts_multiples[selected_rut_index])

    boton_guardar = ctk.CTkButton(ventana_editar, text="Guardar", command=guardar_edicion,
                                  fg_color="#0d6f8f", hover_color="#1282a2", text_color="#d0f0fd")
    boton_guardar.pack(pady=10)

boton_editar_rut = ctk.CTkButton(master=right_frame, text="Editar RUT seleccionado", command=editar_rut_seleccionado,
                                 fg_color="#0d6f8f", hover_color="#1282a2", text_color="#fff")
boton_editar_rut.pack(pady=5)


frame_animacion = ctk.CTkFrame(master=frame, corner_radius=10, border_width=2, border_color="#0d6f8f")
frame_animacion.pack(pady=5,padx=10, fill="both", expand=True)

root.protocol("WM_DELETE_WINDOW", cerrar_programa)

canvas = None
ani = None

root.mainloop()
