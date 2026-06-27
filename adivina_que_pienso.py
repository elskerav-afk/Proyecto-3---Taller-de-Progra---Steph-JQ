

import customtkinter as ctk
import tkinter.filedialog as filedialog
import tkinter.messagebox as messagebox
import json
import os


# Cada nodo puede ser una pregunta o una respuesta final
class Nodo:
    def __init__(self, contenido, es_pregunta=True):
        self.contenido = contenido
        self.es_pregunta = es_pregunta
        self.rama_si = None
        self.rama_no = None

    def es_hoja(self):
        return self.rama_si is None and self.rama_no is None

    # Convierte el nodo y sus hijos a diccionario para guardarlo en JSON
    def a_diccionario(self):
        return {
            'contenido': self.contenido,
            'es_pregunta': self.es_pregunta,
            'rama_si': self.rama_si.a_diccionario() if self.rama_si else None,
            'rama_no': self.rama_no.a_diccionario() if self.rama_no else None
        }

    @staticmethod
    def desde_diccionario(datos):
        if datos is None:
            return None
        nodo = Nodo(datos['contenido'], datos['es_pregunta'])
        nodo.rama_si = Nodo.desde_diccionario(datos.get('rama_si'))
        nodo.rama_no = Nodo.desde_diccionario(datos.get('rama_no'))
        return nodo


# El árbol guarda la lógica del juego y el nodo donde está el jugador
class ArbolDecision:
    def __init__(self):
        self.raiz = Nodo("Es un animal?", es_pregunta=True)
        self.raiz.rama_si = Nodo("Perro", es_pregunta=False)
        self.raiz.rama_no = Nodo("Computadora", es_pregunta=False)
        self.nodo_actual = self.raiz

    def reiniciar(self):
        self.nodo_actual = self.raiz

    def responder_si(self):
        if self.nodo_actual.rama_si:
            self.nodo_actual = self.nodo_actual.rama_si

    def responder_no(self):
        if self.nodo_actual.rama_no:
            self.nodo_actual = self.nodo_actual.rama_no

    # Cuando el árbol falla, expande la hoja actual en una nueva pregunta
    def agregar_aprendizaje(self, respuesta_correcta, pregunta_nueva, es_si_para_correcta):
        respuesta_anterior = Nodo(self.nodo_actual.contenido, es_pregunta=False)
        respuesta_correcta_node = Nodo(respuesta_correcta, es_pregunta=False)

        if es_si_para_correcta:
            self.nodo_actual.rama_si = respuesta_correcta_node
            self.nodo_actual.rama_no = respuesta_anterior
        else:
            self.nodo_actual.rama_si = respuesta_anterior
            self.nodo_actual.rama_no = respuesta_correcta_node

        self.nodo_actual.contenido = pregunta_nueva
        self.nodo_actual.es_pregunta = True

    def a_diccionario(self):
        return self.raiz.a_diccionario() if self.raiz else None

    def desde_diccionario(self, datos):
        self.raiz = Nodo.desde_diccionario(datos)
        self.nodo_actual = self.raiz


# Guarda y carga el árbol como archivo JSON
class GestorArchivos:
    @staticmethod
    def guardar(arbol, ruta_archivo):
        try:
            datos = arbol.a_diccionario()
            with open(ruta_archivo, 'w', encoding='utf-8') as f:
                json.dump(datos, f, ensure_ascii=False, indent=2)
            return True, "Archivo guardado correctamente"
        except Exception as e:
            return False, f"Error al guardar: {str(e)}"

    @staticmethod
    def cargar(ruta_archivo):
        try:
            if not os.path.exists(ruta_archivo):
                return None, "El archivo no existe"
            with open(ruta_archivo, 'r', encoding='utf-8') as f:
                datos = json.load(f)
            arbol = ArbolDecision()
            arbol.desde_diccionario(datos)
            return arbol, "Archivo cargado correctamente"
        except json.JSONDecodeError:
            return None, "El archivo tiene formato incorrecto"
        except Exception as e:
            return None, f"Error al cargar: {str(e)}"


# Pantalla de bienvenida con opciones para iniciar o cargar un árbol
class PantallaInicial(ctk.CTkFrame):
    def __init__(self, parent, callback_iniciar, callback_cargar):
        super().__init__(parent, fg_color="#f5f5f5")
        self.callback_iniciar = callback_iniciar
        self.callback_cargar = callback_cargar

        titulo = ctk.CTkLabel(
            self,
            text="Adivina en qué estoy pensando",
            font=("Helvetica", 48, "bold"),
            text_color="#2d5016"
        )
        titulo.pack(pady=(60, 20))

        subtitulo = ctk.CTkLabel(
            self,
            text="Un juego que aprende cada vez que juegas",
            font=("Helvetica", 18),
            text_color="#5a9e3f"
        )
        subtitulo.pack(pady=(0, 40))

        instrucciones = ctk.CTkLabel(
            self,
            text="Piensa en algo y responde sí o no a nuestras preguntas.\n"
                 "Si fallamos, nos enseñas qué es! El árbol crece con cada juego.",
            font=("Helvetica", 14),
            text_color="#3a3a3a",
            justify="center"
        )
        instrucciones.pack(pady=(0, 50))

        frame_botones = ctk.CTkFrame(self, fg_color="transparent")
        frame_botones.pack(pady=30)

        btn_iniciar = ctk.CTkButton(
            frame_botones,
            text="Iniciar Juego",
            command=callback_iniciar,
            font=("Helvetica", 16, "bold"),
            fg_color="#2d5016",
            hover_color="#1f3a0f",
            height=50,
            width=280,
            corner_radius=10
        )
        btn_iniciar.pack(pady=10)

        btn_cargar = ctk.CTkButton(
            frame_botones,
            text="Cargar árbol desde archivo",
            command=callback_cargar,
            font=("Helvetica", 14),
            fg_color="#5a9e3f",
            hover_color="#4a8830",
            height=45,
            width=280,
            corner_radius=10
        )
        btn_cargar.pack(pady=10)

        btn_salir = ctk.CTkButton(
            frame_botones,
            text="Salir",
            command=parent.quit,
            font=("Helvetica", 14),
            fg_color="#a0a0a0",
            hover_color="#808080",
            height=45,
            width=280,
            corner_radius=10
        )
        btn_salir.pack(pady=10)


# Pantalla donde ocurre el juego: muestra preguntas y recibe respuestas
class PantallaJuego(ctk.CTkFrame):
    def __init__(self, parent, arbol, archivo_actual, callback_volver):
        super().__init__(parent, fg_color="#f5f5f5")
        self.arbol = arbol
        self.archivo_actual = archivo_actual
        self.callback_volver = callback_volver
        self.arbol.reiniciar()

        frame_superior = ctk.CTkFrame(self, fg_color="transparent")
        frame_superior.pack(pady=10, padx=10, fill="x")

        btn_volver = ctk.CTkButton(
            frame_superior,
            text="Volver al inicio",
            command=self.volver_inicio,
            font=("Helvetica", 12),
            fg_color="#a0a0a0",
            hover_color="#808080",
            width=150,
            height=35
        )
        btn_volver.pack(side="left")

        frame_main = ctk.CTkFrame(self, fg_color="transparent")
        frame_main.pack(expand=True, fill="both", padx=40, pady=40)

        self.label_pregunta = ctk.CTkLabel(
            frame_main,
            text="",
            font=("Helvetica", 28, "bold"),
            text_color="#2d5016",
            wraplength=600,
            justify="center"
        )
        self.label_pregunta.pack(pady=(40, 60))

        frame_respuestas = ctk.CTkFrame(frame_main, fg_color="transparent")
        frame_respuestas.pack(pady=30)

        self.btn_si = ctk.CTkButton(
            frame_respuestas,
            text="Si",
            command=self.responder_si,
            font=("Helvetica", 18, "bold"),
            fg_color="#5a9e3f",
            hover_color="#4a8830",
            height=60,
            width=200,
            corner_radius=15
        )
        self.btn_si.pack(side="left", padx=20)

        self.btn_no = ctk.CTkButton(
            frame_respuestas,
            text="No",
            command=self.responder_no,
            font=("Helvetica", 18, "bold"),
            fg_color="#c0392b",
            hover_color="#a93226",
            height=60,
            width=200,
            corner_radius=15
        )
        self.btn_no.pack(side="left", padx=20)

        self.label_mensaje = ctk.CTkLabel(
            frame_main,
            text="",
            font=("Helvetica", 14),
            text_color="#5a5a5a",
            wraplength=600,
            justify="center"
        )
        self.label_mensaje.pack(pady=20)

        self.mostrar_pregunta()

    def mostrar_pregunta(self):
        nodo = self.arbol.nodo_actual
        if nodo.es_pregunta:
            self.label_pregunta.configure(text=nodo.contenido)
            self.label_mensaje.configure(text="")
        else:
            # Llegamos a una hoja: el árbol hace su suposición
            self.label_pregunta.configure(text=f"Es un(a) {nodo.contenido}?")
            self.label_mensaje.configure(text="Confirma si acerté o no.")
            self.btn_si.configure(text="Sí, acertaste!", command=self.adivino_correcto)
            self.btn_no.configure(text="No, intenta otra vez", command=self.adivino_incorrecto)

    def responder_si(self):
        self.arbol.responder_si()
        self.mostrar_pregunta()

    def responder_no(self):
        self.arbol.responder_no()
        self.mostrar_pregunta()

    def adivino_correcto(self):
        self.label_pregunta.configure(text="Lo adiviné!")
        self.label_mensaje.configure(text="¿Quieres jugar otra vez?")
        self.btn_si.configure(text="Jugar de Nuevo", command=self.nueva_partida)
        self.btn_no.configure(text="Volver al Inicio", command=self.volver_inicio)

    def adivino_incorrecto(self):
        # TODO: abrir ventana para que el usuario enseñe al árbol
        messagebox.showinfo("TO DO", "Pendiente")

    def nueva_partida(self):
        self.arbol.reiniciar()
        self.btn_si.configure(text="Sí", command=self.responder_si)
        self.btn_no.configure(text="No", command=self.responder_no)
        self.mostrar_pregunta()

    def volver_inicio(self):
        self.callback_volver()


# Ventana principal: coordina las pantallas y el estado global
class AplicacionPrincipal(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Árbol de decisión interactivo")
        self.geometry("900x700")
        self.configure(fg_color="#f5f5f5")

        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("green")

        self.arbol = ArbolDecision()
        self.archivo_cargado = None

        self.container = ctk.CTkFrame(self, fg_color="#f5f5f5")
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.mostrar_pantalla(PantallaInicial)

    def mostrar_pantalla(self, clase_pantalla):
        # Elimina los widgets anteriores antes de mostrar la nueva pantalla
        for widget in self.container.winfo_children():
            widget.destroy()

        if clase_pantalla == PantallaInicial:
            frame = clase_pantalla(self.container, self.iniciar_juego, self.cargar_archivo)
        elif clase_pantalla == PantallaJuego:
            frame = clase_pantalla(
                self.container,
                self.arbol,
                self.archivo_cargado,
                lambda: self.mostrar_pantalla(PantallaInicial)
            )

        frame.pack(fill="both", expand=True)

    def iniciar_juego(self):
        self.mostrar_pantalla(PantallaJuego)

    def cargar_archivo(self):
        ruta = filedialog.askopenfilename(
            title="Cargar árbol de decisión",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if ruta:
            arbol_cargado, mensaje = GestorArchivos.cargar(ruta)
            if arbol_cargado:
                self.arbol = arbol_cargado
                self.archivo_cargado = ruta
                messagebox.showinfo("Éxito", mensaje)
                self.iniciar_juego()
            else:
                messagebox.showerror("Error", mensaje)


if __name__ == "__main__":
    app = AplicacionPrincipal()
    app.mainloop()
