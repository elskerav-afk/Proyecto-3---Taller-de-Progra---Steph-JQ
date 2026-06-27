

# Cada nodo puede ser una pregunta o una respuesta final
class Nodo:
    def __init__(self, contenido, es_pregunta=True):
        self.contenido = contenido
        self.es_pregunta = es_pregunta
        self.rama_si = None
        self.rama_no = None

    def es_hoja(self):
        return self.rama_si is None and self.rama_no is None


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


# Prueba básica en consola
if __name__ == "__main__":
    arbol = ArbolDecision()
    print(arbol.raiz.contenido)
    arbol.responder_si()
    print(arbol.nodo_actual.contenido)
