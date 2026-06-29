

import customtkinter as ctk
import tkinter.filedialog as filedialog
import tkinter.messagebox as messagebox
import json
import os
from pathlib import Path


# Cada nodo es una pregunta (tiene hijos) o una respuesta final (no tiene hijos)
class Nodo:
    
    def __init__(self, contenido, es_pregunta=True):
        self.contenido = contenido      # texto de la pregunta o respuesta
        self.es_pregunta = es_pregunta  # False si es una respuesta final
        self.rama_si = None             # nodo que se sigue cuando el usuario dice sí
        self.rama_no = None             # nodo que se sigue cuando el usuario dice no
    
    def es_hoja(self):
        # si no tiene hijos, es una respuesta final (el árbol va a adivinar)
        return self.rama_si is None and self.rama_no is None
    
    # convierte el nodo a diccionario para poder guardarlo como JSON
    def a_diccionario(self):
        return {
            'contenido': self.contenido,
            'es_pregunta': self.es_pregunta,
            'rama_si': self.rama_si.a_diccionario() if self.rama_si else None,
            'rama_no': self.rama_no.a_diccionario() if self.rama_no else None
        }
    
    @staticmethod
    def desde_diccionario(datos):
        # reconstruye el árbol de nodos desde un diccionario cargado del JSON
        if datos is None:
            return None
        nodo = Nodo(datos['contenido'], datos['es_pregunta'])
        nodo.rama_si = Nodo.desde_diccionario(datos.get('rama_si'))
        nodo.rama_no = Nodo.desde_diccionario(datos.get('rama_no'))
        return nodo


# Maneja el árbol completo y guarda en qué nodo está el jugador en cada momento
class ArbolDecision:
    
    def __init__(self):
        # árbol inicial con una sola pregunta y dos respuestas de ejemplo
        self.raiz = Nodo("Es un animal?", es_pregunta=True)
        self.raiz.rama_si = Nodo("Perro", es_pregunta=False)
        self.raiz.rama_no = Nodo("Computadora", es_pregunta=False)
        self.nodo_actual = self.raiz
    
    def reiniciar(self):
        # vuelve al inicio del árbol para empezar una nueva partida
        self.nodo_actual = self.raiz
    
    def responder_si(self):
        if self.nodo_actual.rama_si:
            self.nodo_actual = self.nodo_actual.rama_si
    
    def responder_no(self):
        if self.nodo_actual.rama_no:
            self.nodo_actual = self.nodo_actual.rama_no
    
    def agregar_aprendizaje(self, respuesta_correcta, pregunta_nueva, es_si_para_correcta):
        # cuando el árbol falla, convierte la hoja incorrecta en una nueva pregunta
        # con dos hijos: la respuesta correcta y la que ya tenía antes
        respuesta_anterior = Nodo(self.nodo_actual.contenido, es_pregunta=False)
        
        pregunta_node = Nodo(pregunta_nueva, es_pregunta=True)
        respuesta_correcta_node = Nodo(respuesta_correcta, es_pregunta=False)
        
        # conecta las ramas según lo que respondió el usuario
        if es_si_para_correcta:
            pregunta_node.rama_si = respuesta_correcta_node
            pregunta_node.rama_no = respuesta_anterior
        else:
            pregunta_node.rama_si = respuesta_anterior
            pregunta_node.rama_no = respuesta_correcta_node
        
        # modifica el nodo actual en lugar de reemplazarlo para no perder referencias
        self.nodo_actual.contenido = pregunta_nueva
        self.nodo_actual.es_pregunta = True
        self.nodo_actual.rama_si = pregunta_node.rama_si
        self.nodo_actual.rama_no = pregunta_node.rama_no
    
    def a_diccionario(self):
        return self.raiz.a_diccionario() if self.raiz else None
    
    def desde_diccionario(self, datos):
        self.raiz = Nodo.desde_diccionario(datos)
        self.nodo_actual = self.raiz


# Guarda y carga el árbol en disco como archivo JSON
class GestorArchivos:
    
    @staticmethod
    def guardar(arbol, ruta_archivo):
        try:
            datos = arbol.a_diccionario()
            with open(ruta_archivo, 'w', encoding='utf-8') as f:
                # indent=2 para que el JSON sea legible si alguien lo abre
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
            
            # reconstruye el árbol desde los datos del archivo
            arbol = ArbolDecision()
            arbol.desde_diccionario(datos)
            return arbol, "Archivo cargado correctamente"
        except json.JSONDecodeError:
            return None, "El archivo tiene formato incorrecto"
        except Exception as e:
            return None, f"Error al cargar: {str(e)}"


# Pantalla de bienvenida con las tres opciones principales
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
                 "Si fallamos, nos enseñaras qué es! El árbol crece con cada juego.",
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


# Pantalla principal del juego donde se hacen y responden las preguntas
class PantallaJuego(ctk.CTkFrame):
    
    def __init__(self, parent, arbol, archivo_actual, callback_volver):
        super().__init__(parent, fg_color="#f5f5f5")
        self.arbol = arbol
        self.archivo_actual = archivo_actual  # donde se guardará el árbol al aprender algo nuevo
        self.callback_volver = callback_volver
        self.arbol.reiniciar()  # siempre empieza desde la raíz
        
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
        
        # label donde se muestra la pregunta actual o la suposición del árbol
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
        
        # los botones cambian de texto y función según el estado del juego
        self.btn_si = ctk.CTkButton(
            frame_respuestas,
            text="Sí",
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
            fg_color="#d74c3c",
            hover_color="#c0392b",
            height=60,
            width=200,
            corner_radius=15
        )
        self.btn_no.pack(side="left", padx=20)
        
        self.label_mensaje = ctk.CTkLabel(
            frame_main,
            text="",
            font=("Helvetica", 14),
            text_color="#3a3a3a",
            wraplength=600
        )
        self.label_mensaje.pack(pady=(40, 0))
        
        self.mostrar_pregunta()
    
    def mostrar_pregunta(self):
        self.label_mensaje.configure(text="")
        
        if self.arbol.nodo_actual.es_pregunta:
            self.label_pregunta.configure(text=self.arbol.nodo_actual.contenido)
            self.btn_si.configure(state="normal")
            self.btn_no.configure(state="normal")
        else:
            # llegamos a una hoja: el árbol hace su suposición
            self.intentar_adivinar()
    
    def responder_si(self):
        self.arbol.responder_si()
        self.mostrar_pregunta()
    
    def responder_no(self):
        self.arbol.responder_no()
        self.mostrar_pregunta()
    
    def intentar_adivinar(self):
        # desactiva los botones mientras el usuario confirma si acertó o no
        self.btn_si.configure(state="disabled")
        self.btn_no.configure(state="disabled")
        
        respuesta = self.arbol.nodo_actual.contenido
        self.label_pregunta.configure(text=f"Estabas pensando en: {respuesta}?")
        self.label_mensaje.configure(text="")
        
        # reasigna los botones para manejar la confirmación
        self.btn_si.configure(text="Sí, acertaste!", command=self.adivino_correcto)
        self.btn_no.configure(text="No, intenta otra vez", command=self.adivino_incorrecto)
        self.btn_si.configure(state="normal")
        self.btn_no.configure(state="normal")
    
    def adivino_correcto(self):
        self.label_pregunta.configure(text="Lo adiviné!")
        self.label_mensaje.configure(text="Eres genial. ¿Quieres jugar otra vez?")
        self.btn_si.configure(text="Jugar de Nuevo", command=self.nueva_partida)
        self.btn_no.configure(text="Volver al Inicio", command=self.volver_inicio)
    
    def adivino_incorrecto(self):
        # bloquea los botones y abre la ventana para que el usuario enseñe al árbol
        self.btn_si.configure(state="disabled")
        self.btn_no.configure(state="disabled")
        
        ventana_aprendizaje = VentanaAprendizaje(
            self.master,
            self.arbol.nodo_actual.contenido,
            self.completar_aprendizaje
        )
    
    def completar_aprendizaje(self, respuesta_correcta, pregunta_nueva, es_si):
        self.arbol.agregar_aprendizaje(respuesta_correcta, pregunta_nueva, es_si)
        
        # guarda en el archivo actual, o crea uno nuevo si no hay ninguno cargado
        if self.archivo_actual:
            archivo_guardado = self.archivo_actual
        else:
            archivo_guardado = "arbol_decision.json"
        
        exito, mensaje = GestorArchivos.guardar(self.arbol, archivo_guardado)
        
        self.label_pregunta.configure(text="Aprendi algo nuevo!")
        self.label_mensaje.configure(
            text=f"Ahora sé que {respuesta_correcta} y {self.arbol.nodo_actual.contenido}.\n¿Otra partida?"
        )
        
        # reactiva los botones con las opciones para continuar
        self.btn_si.configure(
            text="Jugar de Nuevo",
            command=self.nueva_partida,
            state="normal"
        )
        self.btn_no.configure(
            text="Volver al Inicio",
            command=self.volver_inicio,
            state="normal"
        )
    
    def nueva_partida(self):
        # reinicia el árbol y devuelve los botones a su estado original
        self.arbol.reiniciar()
        self.btn_si.configure(text="Si", command=self.responder_si)
        self.btn_no.configure(text="No", command=self.responder_no)
        self.mostrar_pregunta()
    
    def volver_inicio(self):
        self.callback_volver()


# Ventana emergente que aparece cuando el árbol falla su suposición
class VentanaAprendizaje(ctk.CTkToplevel):
    
    def __init__(self, parent, respuesta_incorrecta, callback):
        super().__init__(parent)
        self.title("Enseñar al árbol")
        self.geometry("600x500")
        self.resizable(False, False)
        self.configure(fg_color="#f5f5f5")
        self.callback = callback
        self.respuesta_incorrecta = respuesta_incorrecta
        
        # hace que esta ventana bloquee la principal hasta que se cierre
        self.transient(parent)
        self.grab_set()
        
        titulo = ctk.CTkLabel(
            self,
            text="Enseñame la Respuesta Correcta",
            font=("Helvetica", 20, "bold"),
            text_color="#2d5016"
        )
        titulo.pack(pady=20)
        
        explicacion = ctk.CTkLabel(
            self,
            text=f"Pensabas en algo diferente a '{respuesta_incorrecta}'.\n¿Qué era?",
            font=("Helvetica", 12),
            text_color="#3a3a3a",
            justify="center"
        )
        explicacion.pack(pady=10)
        
        # campo 1: la respuesta correcta
        ctk.CTkLabel(self, text="¿Qué respuesta era?", font=("Helvetica", 12, "bold"), text_color="#2d5016").pack(pady=(20, 5))
        self.entrada_respuesta = ctk.CTkEntry(
            self,
            placeholder_text="Ejemplo: Gato, Casa, Libro...",
            font=("Helvetica", 12),
            height=40
        )
        self.entrada_respuesta.pack(padx=20, pady=5, fill="x")
        
        # campo 2: una pregunta que distingue la respuesta correcta de la incorrecta
        ctk.CTkLabel(self, text="Que pregunta diferencia tu respuesta?", font=("Helvetica", 12, "bold"), text_color="#2d5016").pack(pady=(20, 5))
        self.entrada_pregunta = ctk.CTkEntry(
            self,
            placeholder_text="Ejemplo: Maulla?",
            font=("Helvetica", 12),
            height=40
        )
        self.entrada_pregunta.pack(padx=20, pady=5, fill="x")
        
        # campo 3: en qué rama va la respuesta correcta
        ctk.CTkLabel(self, text="Para tu pregunta, la respuesta es sí o no?", font=("Helvetica", 12, "bold"), text_color="#2d5016").pack(pady=(20, 10))
        
        frame_si_no = ctk.CTkFrame(self, fg_color="transparent")
        frame_si_no.pack(pady=10)
        
        self.var_si_no = ctk.StringVar(value="si")
        
        radio_si = ctk.CTkRadioButton(
            frame_si_no,
            text="Si",
            variable=self.var_si_no,
            value="si",
            font=("Helvetica", 12)
        )
        radio_si.pack(side="left", padx=20)
        
        radio_no = ctk.CTkRadioButton(
            frame_si_no,
            text="No",
            variable=self.var_si_no,
            value="no",
            font=("Helvetica", 12)
        )
        radio_no.pack(side="left", padx=20)
        
        frame_botones = ctk.CTkFrame(self, fg_color="transparent")
        frame_botones.pack(pady=30)
        
        btn_guardar = ctk.CTkButton(
            frame_botones,
            text="Guardar y Aprender",
            command=self.guardar_aprendizaje,
            font=("Helvetica", 14, "bold"),
            fg_color="#5a9e3f",
            hover_color="#4a8830",
            height=40,
            width=250
        )
        btn_guardar.pack(side="left", padx=10)
        
        btn_cancelar = ctk.CTkButton(
            frame_botones,
            text="Cancelar",
            command=self.destroy,
            font=("Helvetica", 12),
            fg_color="#a0a0a0",
            hover_color="#808080",
            height=40,
            width=120
        )
        btn_cancelar.pack(side="left", padx=10)
    
    def guardar_aprendizaje(self):
        respuesta = self.entrada_respuesta.get().strip()
        pregunta = self.entrada_pregunta.get().strip()
        
        # valida que los dos campos estén llenos antes de continuar
        if not respuesta or not pregunta:
            messagebox.showerror("Error", "Todos los campos son obligatorios")
            return
        
        # convierte "si"/"no" a booleano para pasarlo al árbol
        es_si = self.var_si_no.get() == "si"
        self.callback(respuesta, pregunta, es_si)
        self.destroy()


# Ventana raíz: inicializa la app y controla la navegación entre pantallas
class AplicacionPrincipal(ctk.CTk):
    
    def __init__(self):
        super().__init__()
        self.title("Árbol de Decision Interactivo")
        self.geometry("900x700")
        self.configure(fg_color="#f5f5f5")
        
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("green")
        
        self.arbol = ArbolDecision()
        self.archivo_cargado = None  # guarda la ruta del JSON si el usuario cargó uno
        
        self.container = ctk.CTkFrame(self, fg_color="#f5f5f5")
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        
        self.frames = {}
        self.mostrar_pantalla(PantallaInicial)
    
    def mostrar_pantalla(self, clase_pantalla):
        # destruye los widgets de la pantalla anterior antes de mostrar la nueva
        for widget in self.container.winfo_children():
            widget.destroy()
        
        if clase_pantalla == PantallaInicial:
            frame = clase_pantalla(
                self.container,
                self.iniciar_juego,
                self.cargar_archivo
            )
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
            title="Cargar árbol de decision",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if ruta:
            arbol_cargado, mensaje = GestorArchivos.cargar(ruta)
            
            if arbol_cargado:
                # reemplaza el árbol en memoria con el que se cargó
                self.arbol = arbol_cargado
                self.archivo_cargado = ruta
                messagebox.showinfo("Éxito", mensaje)
                self.iniciar_juego()
            else:
                messagebox.showerror("Error", mensaje)


if __name__ == "__main__":
    app = AplicacionPrincipal()
    app.mainloop()
