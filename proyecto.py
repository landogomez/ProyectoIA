

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

def main():
    estado_prueba1 = [1, 2, 3, 4, 0, 5, 6, 7, 8]

    imprimir_tablero(estado_prueba1)
    print("Posición del hueco en la lista:", posicion_hueco(estado_prueba1))
    movs = posibles_movimientos(estado_prueba1)
    print("Movimientos posibles:", movs)
    print("Tableros resultantes de aplicar cada movimiento:")
    for d in movs:
        nuevo_estado = aplicar_movimiento(estado_prueba1, d)
        imprimir_tablero(nuevo_estado)
        print("-----")

if __name__ == "__main__":
    main()