# Árbol de Decisión Interactivo

Un juego educativo en Python que implementa un árbol binario de decisión que **aprende** con cada partida.

## Requisitos

- **Python 3.8+**
- Librerías requeridas:
  ```bash
  pip install customtkinter
  ```

## Instalación

1. **Instalar CustomTkinter:**
   ```bash
   pip install customtkinter
   ```

2. **Copiar todos los archivos a tu directorio de trabajo**

## Cómo Ejecutar

```bash
python arbol_decision.py
```

La interfaz gráfica se abrirá automáticamente.

## Archivos Incluidos

### Código Fuente
- **arbol_decision.py**: Aplicación completa con interfaz gráfica, lógica del árbol y persistencia

### Archivos de Ejemplo (Árboles Pre-cargados)
Estos archivos contienen árboles de decisión pre-entrenados con 10+ respuestas cada uno. Puedes cargarlos desde la pantalla inicial:

1. **arbol_animales.json** - Árbol para adivinar animales
   - Perro, Gato, Delfín, León, Águila, Pingüino, Araña, Serpiente, etc.

2. **arbol_comidas.json** - Árbol para adivinar comidas
   - Manzana, Fresa, Plátano, Pizza, Pastel, Ensalada, etc.

3. **arbol_deportes.json** - Árbol para adivinar deportes
   - Fútbol, Baloncesto, Voleibol, Natación, Esquí, Judo, etc.

4. **arbol_profesiones.json** - Árbol para adivinar profesiones
   - Pediatra, Médico, Ingeniero, Actor, Profesor, Abogado, etc.

5. **arbol_objetos.json** - Árbol para adivinar objetos
   - Lápiz, Cuchillo, Cuchara, Cama, Auto, Refrigerador, etc.

### Documentación
- **Documento_Diseño_OOP.docx**: Documento detallado con la arquitectura OOP del proyecto

## Cómo Jugar

1. **Pantalla de Inicio**: Elige entre:
   - Iniciar con el árbol por defecto
   - Cargar un árbol desde archivo (cualquiera de los .json incluidos)

2. **Durante el Juego**:
   - La aplicación hará preguntas de Sí/No
   - Responde honestamente
   - El sistema intentará adivinarlo

3. **Si Adivina Correctamente**:
   - ¡Felicidades! Puedes jugar otra partida

4. **Si Falla**:
   - Dile cuál era la respuesta correcta
   - Dame una pregunta que la diferencie
   - Indica si la respuesta correcta sería Sí o No
   - ¡El árbol aprenderá para la próxima!

## Arquitectura OOP

El proyecto utiliza estas clases principales:

### **Nodo**
Representa un nodo del árbol binario. Puede ser una pregunta o una respuesta.
- `contenido`: La pregunta o respuesta
- `es_pregunta`: True si es pregunta, False si es respuesta
- `rama_si`, `rama_no`: Referencias a nodos hijos
- Métodos: `es_hoja()`, `a_diccionario()`, `desde_diccionario()`

### **ArbolDecision**
Gestiona el árbol completo y el flujo del juego.
- Proporciona métodos para navegar: `responder_si()`, `responder_no()`
- Implementa aprendizaje: `agregar_aprendizaje()`
- Maneja serialización: `a_diccionario()`, `desde_diccionario()`

### **GestorArchivos**
Clase estática que maneja persistencia.
- `guardar(arbol, ruta)`: Guarda el árbol en JSON
- `cargar(ruta)`: Carga un árbol desde JSON

### **Clases de Interfaz** (CustomTkinter)
- `PantallaInicial`: Pantalla de bienvenida
- `PantallaJuego`: Lógica principal del juego
- `VentanaAprendizaje`: Formulario para enseñanza
- `AplicacionPrincipal`: Controlador de la aplicación

## Diseño Visual

La interfaz utiliza **CustomTkinter** para un diseño moderno y atractivo:
- Colores: Verde bosque (#2d5016), verde claro (#5a9e3f)
- Tipografía: Helvetica limpia y legible
- Componentes: Botones estilizados, campos de texto, radio buttons
- Experiencia: Intuitiva y responsiva

## Guardado Automático

El árbol se guarda automáticamente en `arbol_decision.json` cada vez que:
- El sistema aprende una nueva pregunta y respuesta
- El árbol crece con nuevo conocimiento

## Ejemplo de Aprendizaje

**Árbol Inicial:**
```
¿Es un animal?
├─ Sí → Perro
└─ No → Computadora
```

**Después de una sesión (usuario responde Sí pero no es Perro):**
```
¿Es un animal?
├─ Sí → ¿Maúlla?
│       ├─ Sí → Gato
│       └─ No → Perro
└─ No → Computadora
```

## Características

✅ Árbol binario de decisión totalmente funcional
✅ Interfaz gráfica moderna con CustomTkinter
✅ Sistema de aprendizaje automático
✅ Persistencia en archivos JSON
✅ 5 árboles de ejemplo pre-cargados
✅ Manejo robusto de errores
✅ Comentarios en código español
✅ Separación clara de responsabilidades (OOP)

## Notas de Desarrollo

- El código está completamente comentado en español
- Sigue principios SOLID de programación OOP
- Las responsabilidades están claras:
  - Lógica del árbol: clases `Nodo` y `ArbolDecision`
  - Persistencia: clase `GestorArchivos`
  - Interfaz: clases heredadas de `CTkFrame`
- No hay lógica de GUI en los botones; todo está organizado en métodos
- El archivo por defecto se guarda como `arbol_decision.json`

## Troubleshooting

**Error: "No module named customtkinter"**
```bash
pip install customtkinter
```

**Los botones no responden**
- Asegúrate de que CustomTkinter está instalado correctamente
- Reinicia la aplicación

**No se pueden cargar archivos JSON**
- Verifica que el archivo esté en formato JSON válido
- Comprueba que el path es correcto

## Licencia

Este proyecto fue desarrollado como tarea programada del curso Taller de Programación III.

## Contacto

Para dudas sobre el proyecto, consulta el documento `Documento_Diseño_OOP.docx` que contiene información detallada de la arquitectura.

---

**¡Diviértete jugando!**
