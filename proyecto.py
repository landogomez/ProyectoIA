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
    visitados = {tuple(estado_inicial)}             # Usamos tuplas porque las listas (estados) no pueden ser claves en conjuntos
    
    # Es clave para reconstruir el camino ya que almacena el rastro, el camino que lo llevó ahi
    # El estado inicial no tiene padre (es None)
    padres = {tuple(estado_inicial): None}

    while pila:
        estado_actual = pila.pop()                  # Extraemos el último estado añadido (LIFO). Esto define la "Profundidad"
        
        if estado_actual == estado_objetivo:        #Vemos si está bien o si es la respuesta
            camino = []                             # iniciamos el backtracking
            e = estado_actual                       # Empezamos el rastreo desde el objetivo
            
            while e:                                # El bucle se detiene cuando 'e' llega al estado inicial, cuyo padre es None
                camino.append(e)                    # Añadimos el estado al camino (en orden inverso)
                e = padres[tuple(e)]                # Buscamos el estado predecesor (padre) usando la tupla como clave
 
            return camino[::-1]
        
        # Iteramos sobre los movimientos posibles (Arriba, Abajo, Izq, Der)
        # Usamos 'reversed' para que el primer vecino sea el último en salir, asi se explora esa rama primero y logramos rofundidad
        for movimiento in reversed(posibles_movimientos(estado_actual)): 
            
            vecino = aplicar_movimiento(estado_actual, movimiento)          # Aplicamos el movimiento para obtener el nuevo tablero
            tupla_vecino = tuple(vecino)

            # Filtrado y Registro del Nuevo Estado
            if tupla_vecino not in visitados:
                visitados.add(tupla_vecino)             # Si el vecino es nuevo, lo registramos para no visitarlo dos veces
                padres[tupla_vecino] = estado_actual    # Establecemos el estado actual como el "padre" del nuevo estado
                
                pila.append(vecino)

    return None         # Si la pila se vacía entonces no hay solución

# Costo Uniforme (UCS)
def costo_uniforme(estado_inicial, estado_objetivo):
    """
    Búsqueda de Costo Uniforme (UCS). Idéntico a A* con h(n)=0.
    Garantiza la solución de menor costo (mínimo número de movimientos).
    """  
    cola_prioridad = []                         # 'cola_prioridad' usará un min-heap (heapq) para siempre sacar el estado con menor costo
    
    g_score = {tuple(estado_inicial): 0}        # 'g_score' guarda el costo (g_n) actual más bajo conocido desde el inicio a cada estado
    
    padres = {tuple(estado_inicial): None}      # Es igual para reconstruir el camino
    
    # Añadimos el estado inicial a la cola con su prioridad (costo = 0), (costo, estado)
    heapq.heappush(cola_prioridad, (0, estado_inicial))

    # Exploración
    while cola_prioridad:
        # Extraemos el estado con la menor prioridad (el menor costo g_actual)
        g_actual, estado_actual = heapq.heappop(cola_prioridad)
        tupla_actual = tuple(estado_actual)

        # Vemos si es la solución
        if estado_actual == estado_objetivo:
            # La reconstrucción del camino es idéntica a la de DFS o BFS
            camino = []
            e = estado_actual
            while e:
                camino.append(e)
                e = padres[tuple(e)]
            return camino[::-1]

        # Vemos o generamos los vecinos
        for movimiento in posibles_movimientos(estado_actual):
            vecino = aplicar_movimiento(estado_actual, movimiento)
            tupla_vecino = tuple(vecino)
            
            # Calculamos el costo para llegar a este nuevo estado: costo actual + 1 (cada paso cuesta 11)
            g_tentativo = g_actual + 1 

            # Si el vecino no ha sido visitado O si encontramos un camino más barato para llegar a él
            if tupla_vecino not in g_score or g_tentativo < g_score[tupla_vecino]:
                
                g_score[tupla_vecino] = g_tentativo         #Actualizamos el registro de costos ya que este es el camino más corto
                
                padres[tupla_vecino] = estado_actual        # Actualizamos el rastro de padres para este camino más corto.
                
                # Añadimos el vecino a la cola de prioridad con su nuevo costo como prioridad
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
