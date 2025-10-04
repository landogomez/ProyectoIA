from collections import deque



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
    """ 
    Devuelve la posición del hueco (0) en el estado dado.
    
    """
    return estado.index(0)

def posibles_movimientos(estado):

    hueco = posicion_hueco(estado)
    fila, col = divmod(hueco, 3)
    movimientos = []

    if fila > 0:  # Puede mover hacia arriba
        movimientos.append(-3)

    if fila < 2:  # Puede mover hacia abajo
        movimientos.append(+3)

    if col > 0:  # Puede mover hacia la izquierda
        movimientos.append(-1)

    if col < 2:  # Puede mover hacia la derecha
        movimientos.append(+1)

    return movimientos

def aplicar_movimiento(estado, movimiento):
    """
    Aplica un movimiento al estado dado y devuelve el nuevo estado.
    
    """
    nuevo_estado = estado[:]
    hueco = posicion_hueco(estado)
    nueva_posicion = hueco + movimiento

    # swap
    nuevo_estado[hueco], nuevo_estado[nueva_posicion] = nuevo_estado[nueva_posicion], nuevo_estado[hueco]

    return nuevo_estado



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

def main():
    estado_objetivo = [1, 2, 3, 4, 5, 6, 7, 8, 0]
    estado_prueba1 = [1, 2, 3, 4, 0, 5, 6, 7, 8]

    imprimir_tablero(estado_prueba1)
    print("Posición del hueco en la lista:", posicion_hueco(estado_prueba1))
    camino = bfs(estado_prueba1, estado_objetivo)

    print(f"Se encontraron {len(camino)-1} movimientos:")
    for paso in camino:
        print("-----")
        imprimir_tablero(paso)

if __name__ == "__main__":
    main()