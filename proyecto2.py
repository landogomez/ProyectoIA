import random


class Celda:
    def __init__(self):
        self.pozo = False
        self.wumpus = False
        self.oro = False
        self.hedor = False
        self.brisa = False
        self.brillo = False

class Mundo:
    def __init__(self, tamaño=4, prob_pozo=0.2):
        self.tamaño = tamaño
        self.prob_pozo = prob_pozo
        self.celdas = [[Celda() for _ in range(tamaño)] for _ in range(tamaño)]
        self.pos_agente = (0, 0)  # inicio fijo
        self.colocar_elementos()

    def esta_dentro(self, i, j):
        return 0 <= i < self.tamaño and 0 <= j < self.tamaño

    def colocar_elementos(self):
        # Colocar Wumpus
        w_i, w_j = random.randint(0, self.tamaño-1), random.randint(0, self.tamaño-1)
        while (w_i, w_j) == self.pos_agente:
            w_i, w_j = random.randint(0, self.tamaño-1), random.randint(0, self.tamaño-1)
        self.celdas[w_i][w_j].wumpus = True

        # Colocar Oro
        o_i, o_j = random.randint(0, self.tamaño-1), random.randint(0, self.tamaño-1)
        while (o_i, o_j) == self.pos_agente or (o_i, o_j) == (w_i, w_j):
            o_i, o_j = random.randint(0, self.tamaño-1), random.randint(0, self.tamaño-1)
        self.celdas[o_i][o_j].oro = True

        # Colocar pozos
        for i in range(self.tamaño):
            for j in range(self.tamaño):
                if (i, j) == self.pos_agente or (i, j) == (w_i, w_j) or (i, j) == (o_i, o_j):
                    continue
                if random.random() < self.prob_pozo:
                    self.celdas[i][j].pozo = True




