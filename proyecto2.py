from collections import deque
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

    def celda_valida(self, i, j):
        # Definir celdas adyacentes a la inicial
        adyacentes_inicio = [(0,1), (1,0), (1,1)]
        
        # Evitar la celda inicial, sus adyacentes, y casillas ocupadas por Wumpus, pozo u oro
        if (i,j) == self.pos_agente or (i,j) in adyacentes_inicio:
            return False
        celda = self.celdas[i][j]
        if celda.pozo or celda.wumpus or celda.oro:
            return False
        return True



    def generar_pozos(self):
        for i in range(self.tamaño):
            for j in range(self.tamaño):
                # Evitamos poner pozo en la posición inicial del agente
                if (i, j) == self.pos_agente:
                    continue
                if self.celda_valida(i,j) and random.random() < self.prob_pozo:
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
        while not self.celda_valida(w_i, w_j):
            w_i, w_j = random.randint(0, self.tamaño-1), random.randint(0, self.tamaño-1)
        self.celdas[w_i][w_j].wumpus = True

        # Generar hedores evitando (0,0)
        self.agregar_hedor_alrededor(w_i, w_j)

    def agregar_hedor_alrededor(self, i, j):
        adyacentes = [(i-1,j), (i+1,j), (i,j-1), (i,j+1)]
        for x, y in adyacentes:
            if self.esta_dentro(x, y):
                self.celdas[x][y].hedor = True

    def generar_mundo_seguro(self):
        # Intentamos colocar pozos aleatorios
        for i in range(self.tamaño):
            for j in range(self.tamaño):
                if (i, j) == self.pos_agente or (i, j) == self.pos_oro:
                    continue
                if random.random() < self.prob_pozo:
                    # Colocamos temporalmente
                    self.celdas[i][j].pozo = True
                    if not self.bfs_ruta_segura(self.pos_agente, self.pos_oro):
                        # Si bloquea la ruta, lo quitamos
                        self.celdas[i][j].pozo = False

    def bfs_ruta_segura(self, inicio, objetivo):
        queue = deque()
        queue.append((inicio, [inicio]))
        visitados = set()
        visitados.add(inicio)

        while queue:
            pos_actual, ruta = queue.popleft()
            if pos_actual == objetivo:
                return ruta

            i, j = pos_actual
            vecinos = [(i-1,j), (i+1,j), (i,j-1), (i,j+1)]
            for x, y in vecinos:
                if self.esta_dentro(x, y) and (x, y) not in visitados:
                    celda = self.celdas[x][y]
                    if not celda.pozo and not celda.wumpus:
                        queue.append(((x,y), ruta + [(x,y)]))
                        visitados.add((x,y))
        return None

    
    def colocar_oro(self):
        while True:
            o_i, o_j = random.randint(0, self.tamaño-1), random.randint(0, self.tamaño-1)
            
            # Validar celda antes de colocar
            if not self.celda_valida(o_i, o_j):
                continue
            
            # Probar ruta segura
            self.celdas[o_i][o_j].oro = True
            self.celdas[o_i][o_j].brillo = True
            
            if self.bfs_ruta_segura(self.pos_agente, (o_i,o_j)):
                self.pos_oro = (o_i,o_j)
                break
            else:
                # Si no hay ruta, quitar oro y seguir buscando
                self.celdas[o_i][o_j].oro = False
                self.celdas[o_i][o_j].brillo = False


    

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
                elif self.celdas[i][j].oro:
                    fila += "O "
                elif self.celdas[i][j].pozo:
                    fila += "P "
                elif self.celdas[i][j].hedor:
                    fila += "H "
                elif self.celdas[i][j].brisa:
                    fila += "B "
                
                
                else:
                    fila += ". "
            print(fila)
        print()
    
    def mostrar_informacion_celda(self, kb):
        i, j = self.pos_agente
        celda = self.celdas[i][j]

        # Registrar hechos en la KB
        if celda.pozo:
            kb.agregar_hecho(f"Pozo_{i}_{j}")
        if celda.wumpus:
            kb.agregar_hecho(f"Wumpus_{i}_{j}")
        if celda.oro:
            kb.agregar_hecho(f"Oro_{i}_{j}")
        if celda.brisa:
            kb.agregar_hecho(f"Brisa_{i}_{j}")
        if celda.hedor:
            kb.agregar_hecho(f"Hedor_{i}_{j}")
        if not (celda.pozo or celda.wumpus or celda.oro):
            kb.agregar_hecho(f"Seguro_{i}_{j}")

        # Mostrar información al usuario
        print(f"\nTe encuentras en {self.pos_agente}")
        if celda.pozo:
            print("¡Caíste en un pozo!  Fin del juego.")
        if celda.wumpus:
            print("¡El Wumpus te comió! Fin del juego.")
        if celda.oro:
            print("¡Encontraste el oro! ")
        if celda.brisa:
            print("Sientes una brisa... ")
        if celda.hedor:
            print("Sientes un hedor terrible...")
        if not (celda.brisa or celda.hedor or celda.oro):
            print("La celda parece segura.")

    def mover_agente(self, direccion, kb):
        i, j = self.pos_agente
        if direccion == "arriba":
            nueva_pos = (i - 1, j)
        elif direccion == "abajo":
            nueva_pos = (i + 1, j)
        elif direccion == "izquierda":
            nueva_pos = (i, j - 1)
        elif direccion == "derecha":
            nueva_pos = (i, j + 1)
        else:
            print("Dirección inválida")
            return

        if self.esta_dentro(*nueva_pos):
            self.pos_agente = nueva_pos
            self.mostrar_informacion_celda(kb)
        else:
            print("No puedes salir del mapa")

class KB:
    def __init__(self):
        self.reglas = []
        self.hechos = set()
        self.conclusiones = set()

    def agregar_hecho(self, proposicion):
        self.hechos.add(proposicion)
        print(f"Hecho agregado: {proposicion}")

    def agregar_regla(self, regla):
        self.reglas.append(regla)
        print(f"Regla agregada: {regla}")

    def mostrar_estado(self):
        print("\n--- KB ---")
        print("Hechos observados:", self.hechos)
        print("Reglas del dominio:", self.reglas)
        print("Conclusiones inferidas:", self.conclusiones)
        print("-----------\n")



# --- Ejecución de prueba ---
m = Mundo()
m.mostrar_tablero()
