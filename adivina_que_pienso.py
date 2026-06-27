

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


if __name__ == "__main__":
    arbol = ArbolDecision()
    # Probar que el aprendizaje funciona
    arbol.responder_si()
    arbol.agregar_aprendizaje("Gato", "Maulle?", True)
    GestorArchivos.guardar(arbol, "prueba.json")
    print("Árbol guardado")
