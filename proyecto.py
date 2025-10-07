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
    visitados = {tuple(estado_inicial)}         #Son los estados que ya han sido explorados
    padres = {tuple(estado_inicial): None}

    while pila:
        estado_actual = pila.pop()      #Aqui se extrae el último estado que se añadio a la pila
        
        if estado_actual == estado_objetivo:
            camino = []
            e = estado_actual
            while e:
                camino.append(e)
                e = padres[tuple(e)]
            return camino[::-1]
        
        # Nota: Los vecinos se añaden en orden inverso para que el primero
        # generado sea el último en salir (profundidad).
        for movimiento in reversed(posibles_movimientos(estado_actual)): 
            vecino = aplicar_movimiento(estado_actual, movimiento)
            tupla_vecino = tuple(vecino)

            if tupla_vecino not in visitados:
                visitados.add(tupla_vecino)
                padres[tupla_vecino] = estado_actual
                pila.append(vecino)

    return None

# Costo Uniforme (UCS)
def costo_uniforme(estado_inicial, estado_objetivo):
    """
    Búsqueda de Costo Uniforme (UCS). Idéntico a A* con h(n)=0.
    Garantiza la solución de menor costo (mínimo número de movimientos).
    """
    # Cola de prioridad
    cola_prioridad = []
    # g_score: Almacena el costo real (g_n) para llegar a un estado
    g_score = {tuple(estado_inicial): 0}
    padres = {tuple(estado_inicial): None}
    
    # El costo inicial es 0
    heapq.heappush(cola_prioridad, (0, estado_inicial))

    while cola_prioridad:
        g_actual, estado_actual = heapq.heappop(cola_prioridad)
        tupla_actual = tuple(estado_actual)

        if estado_actual == estado_objetivo:
            # Reconstrucción del camino
            camino = []
            e = estado_actual
            while e:
                camino.append(e)
                e = padres[tuple(e)]
            return camino[::-1]

        for movimiento in posibles_movimientos(estado_actual):
            vecino = aplicar_movimiento(estado_actual, movimiento)
            tupla_vecino = tuple(vecino)
            
            g_tentativo = g_actual + 1 # Cada movimiento cuesta 1

            # Si encontramos un camino más corto a este estado
            if tupla_vecino not in g_score or g_tentativo < g_score[tupla_vecino]:
                
                g_score[tupla_vecino] = g_tentativo
                padres[tupla_vecino] = estado_actual
                
                # Añade a la cola de prioridad, solo usando g_tentativo como prioridad
                heapq.heappush(cola_prioridad, (g_tentativo, vecino))

    return None

#---------------------------------------------------------------------------------
#//////////////////////////A* con Heuristica Manhattan////////////////////////////
#---------------------------------------------------------------------------------

def a_star(estado_inicial, estado_objetivo):
    
    cola_prioridad = []
    
    g_score = {tuple(estado_inicial): 0}
    
    h_inicial = distancia_manhattan(estado_inicial, estado_objetivo)
    f_score = {tuple(estado_inicial): h_inicial}
    
    padres = {tuple(estado_inicial): None}
    
    conjunto_cerrado = set()
    
    heapq.heappush(cola_prioridad, (h_inicial, estado_inicial))

    while cola_prioridad:
        f_actual, estado_actual = heapq.heappop(cola_prioridad)
        tupla_actual = tuple(estado_actual)
        
        if tupla_actual in conjunto_cerrado:
            continue

        conjunto_cerrado.add(tupla_actual)

        if estado_actual == estado_objetivo:
            camino = []
            e = estado_actual
            while e:
                camino.append(e)
                e = padres[tuple(e)]
            return camino[::-1]

        for movimiento in posibles_movimientos(estado_actual):
            vecino = aplicar_movimiento(estado_actual, movimiento)
            tupla_vecino = tuple(vecino)
            
            if tupla_vecino in conjunto_cerrado:
                continue
            
            g_tentativo = g_score[tupla_actual] + 1 
            
            if tupla_vecino not in g_score or g_tentativo < g_score[tupla_vecino]:
                
                g_score[tupla_vecino] = g_tentativo
                h_vecino = distancia_manhattan(vecino, estado_objetivo)
                f_score[tupla_vecino] = g_tentativo + h_vecino
                
                
                padres[tupla_vecino] = estado_actual
                
                heapq.heappush(cola_prioridad, (f_score[tupla_vecino], vecino))

    return None 

def distancia_manhattan(estado, estado_objetivo):
    
    distancia = 0
    
    for i in range(9):
        if estado[i] != 0:  
            fila_actual, col_actual = divmod(i, 3)
            
            valor = estado[i]
            posicion_objetivo = estado_objetivo.index(valor)
            fila_objetivo, col_objetivo = divmod(posicion_objetivo, 3)
            
            distancia += abs(fila_actual - fila_objetivo) + abs(col_actual - col_objetivo)
    
    return distancia

#---------------------------------------------------------------------------------
#---------------------------------------------------------------------------------

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