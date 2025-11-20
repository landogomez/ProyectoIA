import random

class Celda:
    def __init__(self):
        self.pozo = False
        self.brisa = False
        self.wumpus = False
        self.hedor = False
        self.oro = False
        self.brillo = False

class Mundo:
    def __init__(self, tamaño=4, prob_pozo=0.2):
        self.tamaño = tamaño
        self.prob_pozo = prob_pozo
        self.celdas = [[Celda() for _ in range(tamaño)] for _ in range(tamaño)]
        self.pos_agente = (0, 0)  # Arriba izquierda por ahora
        self.generar_pozos()
        self.generar_brisas()
        self.colocar_wumpus()
        self.colocar_oro()
        self.validar_mundo()


    def generar_pozos(self):
        for i in range(self.tamaño):
            for j in range(self.tamaño):
                # Evitamos poner pozo en la posición inicial del agente
                if (i, j) == self.pos_agente:
                    continue
                if random.random() < self.prob_pozo:
                    self.celdas[i][j].pozo = True

    def generar_brisas(self):
        for i in range(self.tamaño):
            for j in range(self.tamaño):
                if self.celdas[i][j].pozo:
                    self.agregar_brisas_alrededor(i, j)

    def agregar_brisas_alrededor(self, i, j):
        adyacentes = [(i-1,j), (i+1,j), (i,j-1), (i,j+1)]
        for x, y in adyacentes:
            if self.esta_dentro(x, y):
                self.celdas[x][y].brisa = True


    def esta_dentro(self, i, j):
        return 0 <= i < self.tamaño and 0 <= j < self.tamaño


    def colocar_wumpus(self):
        w_i, w_j = random.randint(0, self.tamaño - 1), random.randint(0, self.tamaño - 1)

        # Evitar inicio y pozos
        while (w_i, w_j) == self.pos_agente or self.celdas[w_i][w_j].pozo:
            w_i, w_j = random.randint(0, self.tamaño - 1), random.randint(0, self.tamaño - 1)

        self.celdas[w_i][w_j].wumpus = True

        # Generar hedores evitando (0,0)
        self.agregar_hedor_alrededor(w_i, w_j)

    def agregar_hedor_alrededor(self, i, j):
        adyacentes = [(i-1,j), (i+1,j), (i,j-1), (i,j+1)]
        for x, y in adyacentes:
            if self.esta_dentro(x, y):
                self.celdas[x][y].hedor = True

    
    def colocar_oro(self):
        o_i, o_j = random.randint(0, self.tamaño - 1), random.randint(0, self.tamaño - 1)

        # Evitar inicio, pozos y wumpus
        while (o_i, o_j) == self.pos_agente or self.celdas[o_i][o_j].pozo or self.celdas[o_i][o_j].wumpus:
            o_i, o_j = random.randint(0, self.tamaño - 1), random.randint(0, self.tamaño - 1)

        self.celdas[o_i][o_j].oro = True
        self.celdas[o_i][o_j].brillo = True

    def validar_mundo(self):
        # Asegurarse de que la celda inicial no tenga pozo, wumpus, ni oro
        if self.celdas[0][0].pozo or self.celdas[0][0].wumpus or self.celdas[0][0].oro:
            raise ValueError("La celda inicial no puede contener pozo, wumpus o oro.")

    def mostrar_tablero(self):
        print("\nTablero actual (debug):")
        for i in range(self.tamaño):
            fila = ""
            for j in range(self.tamaño):
                if (i, j) == self.pos_agente:
                    fila += "A "
                elif self.celdas[i][j].wumpus:
                    fila += "W "
                elif self.celdas[i][j].pozo:
                    fila += "P "
                elif self.celdas[i][j].hedor:
                    fila += "H "
                elif self.celdas[i][j].brisa:
                    fila += "B "
                elif self.celdas[i][j].oro:
                    fila += "O "
                
                else:
                    fila += ". "
            print(fila)
        print()


# --- Ejecución de prueba ---
m = Mundo()
m.mostrar_tablero()
