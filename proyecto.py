from collections import deque
import heapq 

def imprimir_tablero(estado):
    """ 
    Muestra un tablero de 3x3 a partir de una lista de 9 elementos.
    Los numeros del 1 al 8 representan las fichas y el 0 representa el espacio vacío.
    """
    for i in range(9):
        valor = estado[i] if estado[i] != 0 else "_"
        end_char = "\n" if (i+1) % 3 == 0 else " "
        print(valor, end=end_char)

def posicion_hueco(estado):
    """ Devuelve el índice del hueco (0). """
    return estado.index(0)

def posibles_movimientos(estado):
    """ """
    hueco = posicion_hueco(estado)  #Nos dice en que posición se encuentra el 0 o el hueco
    fila, col = divmod(hueco, 3)    #Se sacan las filas y columnas, el indice, para más adelante ver hacia donde se puede mover
    movimientos = []

    if fila > 0:  # Arriba
        movimientos.append(-3)
    if fila < 2:  # Abajo
        movimientos.append(+3)
    if col > 0:  # Izquierda
        movimientos.append(-1)
    if col < 2:  # Derecha
        movimientos.append(+1)

    return movimientos

def aplicar_movimiento(estado, movimiento):
    """ Aplica el movimiento y devuelve el nuevo estado (lista). """
    nuevo_estado = estado[:]                #Se crea una copia 
    hueco = posicion_hueco(estado)          #Como lo hicimos anteriormente, se obtiene la posición del hueco
    nueva_posicion = hueco + movimiento     #Calcula el índice de la ficha que se va a mover al hueco
    
    #Simplemente se hace un intercambio, esto hace que el hueco cambie de posicón
    nuevo_estado[hueco], nuevo_estado[nueva_posicion] = nuevo_estado[nueva_posicion], nuevo_estado[hueco]

    return nuevo_estado


#TODO FUNCIONES HEURÍSTICAS (A*)
def distancia_manhattan(estado, estado_objetivo):
    print("HAY QUE IMPLEMENTARLO :D")


# BFS (Búsqueda en Anchura)
def bfs(estado_inicial, estado_objetivo):
    queve = deque()
    visitados = set()
    padres = {}

    queve.append(estado_inicial)
    visitados.add(tuple(estado_inicial))
    padres[tuple(estado_inicial)] = None

    while queve:
        estado_actual = queve.popleft()

        if estado_actual == estado_objetivo:
            camino = []
            while estado_actual:
                camino.append(estado_actual)
                estado_actual = padres[tuple(estado_actual)]
            return camino[::-1]
        
        for movimiento in posibles_movimientos(estado_actual):
            vecino = aplicar_movimiento(estado_actual, movimiento)
            tupla_vecino = tuple(vecino)

            if tupla_vecino not in visitados:
                visitados.add(tupla_vecino)
                padres[tupla_vecino] = estado_actual
                queve.append(vecino)

    return None

# DFS (Búsqueda en Profundidad)
def dfs(estado_inicial, estado_objetivo):
    """
    Búsqueda no informada. Usa una pila (LIFO).
    No garantiza el camino más corto.
    """
    pila = [estado_inicial] 
    
    # Usamos tuplas porque las listas (estados) no pueden ser claves en conjuntos.
    visitados = {tuple(estado_inicial)} 
    
    # 'padres' almacena el rastro: qué estado llevó a cuál. Es clave para reconstruir el camino.
    # El estado inicial no tiene padre (es None).
    padres = {tuple(estado_inicial): None}

    while pila:
        # Extraemos el último estado añadido (LIFO). Esto define la "Profundidad"
        estado_actual = pila.pop() 
        
        if estado_actual == estado_objetivo:         #Vemos si está bien o si es la respuesta
            # Si encontramos el objetivo, iniciamos el rastreo inverso (backtracking).
            camino = []
            e = estado_actual # Empezamos el rastreo desde el objetivo.
            
            while e: # El bucle se detiene cuando 'e' llega al estado inicial, cuyo padre es None.
                camino.append(e) # Añadimos el estado al camino (en orden inverso).
                # Buscamos el estado predecesor (padre) usando la tupla como clave.
                e = padres[tuple(e)] 
            
            # Devolvemos el camino, invirtiéndolo para que vaya de Inicio a Objetivo.
            return camino[::-1]
        
        # 4. Expansión del Nodo (Generación de Vecinos)
        
        # Iteramos sobre los movimientos posibles (Arriba, Abajo, Izq, Der).
        # Usamos 'reversed' para que el primer vecino generado sea el último en salir de la pila,
        # asegurando que se explore esa rama primero y así logrando la Profundidad.
        for movimiento in reversed(posibles_movimientos(estado_actual)): 
            
            # Aplicamos el movimiento para obtener el nuevo tablero.
            vecino = aplicar_movimiento(estado_actual, movimiento)
            tupla_vecino = tuple(vecino)

            # 5. Filtrado y Registro del Nuevo Estado
            if tupla_vecino not in visitados:
                # Si el vecino es nuevo, lo registramos para no visitarlo dos veces.
                visitados.add(tupla_vecino)
                
                # Establecemos el estado actual como el "padre" del nuevo estado.
                padres[tupla_vecino] = estado_actual
                
                # Añadimos el nuevo estado a la pila para explorarlo pronto.
                pila.append(vecino)

    return None # Si la pila se vacía y no encontramos la meta, no hay solución.

# Costo Uniforme (UCS)
def costo_uniforme(estado_inicial, estado_objetivo):
    """
    Búsqueda de Costo Uniforme (UCS). Idéntico a A* con h(n)=0.
    Garantiza la solución de menor costo (mínimo número de movimientos).
    """
    # 1. Inicialización de Estructuras Clave
    
    # 'cola_prioridad' usará un min-heap (heapq) para siempre sacar el estado con menor costo.
    cola_prioridad = []
    
    # 'g_score' guarda el costo (g_n) actual más bajo conocido desde el inicio a cada estado.
    g_score = {tuple(estado_inicial): 0}
    
    # 'padres' sigue siendo esencial para reconstruir el camino.
    padres = {tuple(estado_inicial): None}
    
    # Añadimos el estado inicial a la cola con su prioridad (costo = 0).
    # Formato: (costo, estado)
    heapq.heappush(cola_prioridad, (0, estado_inicial))

    # 2. Ciclo Principal de Exploración
    while cola_prioridad:
        # Extraemos el estado con la menor prioridad (el menor costo g_actual).
        g_actual, estado_actual = heapq.heappop(cola_prioridad)
        tupla_actual = tuple(estado_actual)

        # 3. Verificación de la Solución
        if estado_actual == estado_objetivo:
            # La reconstrucción del camino es idéntica a la de DFS/BFS, 
            # usando el diccionario 'padres'.
            camino = []
            e = estado_actual
            while e:
                camino.append(e)
                e = padres[tuple(e)]
            return camino[::-1]

        # 4. Expansión del Nodo (Generación de Vecinos)
        for movimiento in posibles_movimientos(estado_actual):
            vecino = aplicar_movimiento(estado_actual, movimiento)
            tupla_vecino = tuple(vecino)
            
            # Calculamos el costo para llegar a este nuevo estado:
            # Costo actual + 1 (ya que cada movimiento en el 8-Puzzle cuesta 1).
            g_tentativo = g_actual + 1 

            # 5. Evaluación y Actualización
            # Si el vecino no ha sido visitado O si encontramos un camino más barato para llegar a él:
            if tupla_vecino not in g_score or g_tentativo < g_score[tupla_vecino]:
                
                # ¡Este es el camino más corto conocido hasta ahora! Actualizamos el registro de costos.
                g_score[tupla_vecino] = g_tentativo
                
                # Actualizamos el rastro de padres para este camino más corto.
                padres[tupla_vecino] = estado_actual
                
                # Añadimos el vecino a la cola de prioridad con su nuevo costo como prioridad.
                heapq.heappush(cola_prioridad, (g_tentativo, vecino))

    return None


#TODO A* (A-Star)
def a_star(estado_inicial, estado_objetivo):
    print("HAY QUE IMPLEMENTARLO :D")

def main():
    estado_objetivo = [1, 2, 3, 4, 5, 6, 7, 8, 0]  
    estado_complejo = [8, 6, 7, 2, 5, 4, 3, 0, 1] 

    estado_inicial = estado_complejo 
    
    print("\n--- 8-Puzzle Solucionador ---")
    print("Estado Inicial:")
    imprimir_tablero(estado_inicial)
    
    print("\nSelecciona el algoritmo a utilizar")
    print("1: BFS (Búsqueda en Anchura)")
    print("2: DFS (Búsqueda en Profundidad)")
    print("3: Costo Uniforme (UCS)")
    print("4: A* (A-Star)")
    opcion = input("\nIntroduce el número de la opción (1-4): ")

    solver = None
    algoritmo_nombre = ""
    
    if opcion == '1':
        solver = bfs
        algoritmo_nombre = "BFS"
    elif opcion == '2':
        solver = dfs
        algoritmo_nombre = "DFS"
    elif opcion == '3':
        solver = costo_uniforme
        algoritmo_nombre = "Costo Uniforme (UCS)"
    elif opcion == '4':
        solver = a_star
        algoritmo_nombre = "A*"
    else:
        print("Opción no válida. Terminando programa.")
        return
    
    # Ejecuta el algoritmo seleccionado
    camino = solver(estado_inicial, estado_objetivo)
    
    # Muestra cada paso del camino
    for i, paso in enumerate(camino):
    #   print(f"--- Paso {i} ---") -> por si queremos poner cada paso
        print("------")
        imprimir_tablero(paso)
    print(f"\n¡Solución encontrada en {len(camino)-1} movimientos!")

if __name__ == "__main__":
    main()