

def imprimir_tablero(estado):
    """ 
    Muestra un tablero de 3x3 a partir de una lista de 9 elementos.
    Los numeros del 1 al 8 representan las fichas y el 0 representa el espacio vacío.
    
    """
    for i in range(9):
        valor = estado[i] if estado[i] != 0 else "_"
        end_char = "\n" if (i+1) % 3 == 0 else " "
        print(valor, end=end_char)



def main():
    estado_prueba1 = [2, 8, 3, 1, 6, 4, 7, 0, 5]

    imprimir_tablero(estado_prueba1)

if __name__ == "__main__":
    main()