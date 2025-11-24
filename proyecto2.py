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


    def actualizar_kb_con_percepciones(self, kb):
        i, j = self.pos_agente
        celda = self.celdas[i][j]
        
        # Siempre sabemos que la casilla donde está el agente es segura
        kb.agregar_hecho(f"Seguro_{i}_{j}")
        
        if celda.brisa:
            kb.agregar_hecho(f"Brisa_{i}_{j}")
        if celda.hedor:
            kb.agregar_hecho(f"Hedor_{i}_{j}")
        if celda.brillo:
            kb.agregar_hecho(f"Brillo_{i}_{j}")

    def decidir_movimiento(self, kb):
        i, j = self.pos_agente

        # Buscar seguras sin visitar
        for x, y in kb.seguras:
            if not self.celdas[x][y].visitada:
                # Movimiento prioritario
                if abs(i-x) + abs(j-y) == 1:  # Debe ser adyacente
                    return (x,y)

        return None  # No hay movimiento seguro conocido



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
    def __init__(self, tamaño):
        self.tamaño = tamaño
        self.hechos = {}  # Ej: {'B_1_1': True}
        self.posibles_pozos = set()
        self.posibles_wumpus = set()
        self.seguras = set()
        self.confirmados_pozos = set()
        self.confirmado_wumpus = None  # Solo hay 1 wumpus
        self.percepciones = {}  # Memorias de lo que sintió en cada casilla visitada

    def agregar_hecho(self, proposicion, valor=True):
        self.hechos[proposicion] = valor
        print(f"Hecho agregado: {proposicion} = {valor}")

    def obtener_adyacentes(self, i, j):
        directions = [(i-1,j),(i+1,j),(i,j-1),(i,j+1)]
        return [(x,y) for x,y in directions if 0 <= x < self.tamaño and 0 <= y < self.tamaño]
    
    def inferir(self):
        # Regla 1: Si una casilla fue marcada segura → no puede estar en sospechosos
        for c in list(self.posibles_wumpus):
            if c in self.seguras:
                self.posibles_wumpus.remove(c)

        for c in list(self.posibles_pozos):
            if c in self.seguras:
                self.posibles_pozos.remove(c)

        # Regla 2: Casillas descartadas si contradicen percepciones sin hedor/brisa
        for i in range(self.tamaño):
            for j in range(self.tamaño):
                if (i,j) in self.seguras:
                    continue
                
                ady = self.obtener_adyacentes(i,j)
                # Si una casilla adyacente NO tenía hedor, aquí NO puede haber Wumpus
                for ax, ay in ady:
                    if not self.percepciones[(ax,ay)]["hedor"]:
                        self.posibles_wumpus.discard((i,j))
                    # Si una casilla adyacente NO tenía brisa, aquí NO puede haber pozo
                    if not self.percepciones[(ax,ay)]["brisa"]:
                        self.posibles_pozos.discard((i,j))

        # Regla 3: Si solo queda 1 sospechoso → confirmar
        if len(self.posibles_wumpus) == 1 and self.confirmado_wumpus is None:
            self.confirmado_wumpus = list(self.posibles_wumpus)[0]
            print(f"¡Wumpus confirmado en {self.confirmado_wumpus}!")


    def actualizar_conocimientos(self, i, j, brisa, hedor):
        # Guardar percepción
        self.percepciones[(i, j)] = {"brisa": brisa, "hedor": hedor}
        self.seguras.add((i, j))

        ady = self.obtener_adyacentes(i, j)

        # --- Reglas para pozos ---
        if brisa:
            # Adyacentes son sospechosos
            for c in ady:
                if c not in self.seguras:
                    self.posibles_pozos.add(c)
        else:
            # Si NO hay brisa → adyacentes libres de pozo
            for c in ady:
                if c in self.posibles_pozos:
                    self.posibles_pozos.remove(c)
                self.seguras.add(c)

        # Deducción fuerte (pozos)
        for pos in ady:
            # Si hay brisa y solo un sospechoso → confirmar pozo
            sospechosos_pozos = [c for c in ady if c in self.posibles_pozos]
            if brisa and len(sospechosos_pozos) == 1:
                pozo = sospechosos_pozos[0]
                self.confirmados_pozos.add(pozo)
                self.posibles_pozos.clear()  # Ya está confirmado
                print(f"¡Pozo confirmado en {pozo}!")

        # --- Reglas para Wumpus ---
        if hedor:
            for c in ady:
                if c not in self.seguras:
                    self.posibles_wumpus.add(c)
        else:
            for c in ady:
                if c in self.posibles_wumpus:
                    self.posibles_wumpus.remove(c)
                self.seguras.add(c)

        # Deducción fuerte (wumpus)
        sospechosos_wumpus = [c for c in self.posibles_wumpus if c in ady]
        if hedor and len(sospechosos_wumpus) == 1 and self.confirmado_wumpus is None:
            self.confirmado_wumpus = sospechosos_wumpus[0]
            print(f"¡Wumpus confirmado en {self.confirmado_wumpus}!")

        self.mostrar_estado()




    def mostrar_estado(self):
        print("\n--- KB ---")
        print("Seguras:", self.seguras)
        print("Posibles Pozos:", self.posibles_pozos)
        print("Posibles Wumpus:", self.posibles_wumpus)
        print("Wumpus Confirmado:", self.confirmado_wumpus)
        print("--------------\n")


class Agente:
    def __init__(self, mundo, kb):
        self.mundo = mundo
        self.kb = kb
        self.pos = (0, 0)
        self.vivo = True
        self.tiene_oro = False
        self.visitadas = set()

    def obtener_percepciones(self):
        i, j = self.pos
        celda = self.mundo.celdas[i][j]
        brisa = celda.brisa
        hedor = celda.hedor
        brillo = celda.brillo
        print(f"En {self.pos} → Brisa={brisa}, Hedor={hedor}, Brillo={brillo}")
        self.kb.actualizar_conocimientos(i, j, brisa, hedor)
        return brillo

    def elegir_movimiento(self):
        for casilla in self.kb.seguras:
            if casilla not in self.visitadas:
                i,j = self.pos
                x,y = casilla
                if abs(i-x) + abs(j-y) == 1:
                    return casilla
        return None

    def moverse(self, destino):
        self.visitadas.add(self.pos)
        self.pos = destino
        print(f"Movimiento a {self.pos}")
        self.mundo.pos_agente = self.pos
        celda = self.mundo.celdas[self.pos[0]][self.pos[1]]
        
        if celda.pozo or celda.wumpus:
            self.vivo = False
            print("Moriste...")
        if celda.oro:
            self.tiene_oro = True
            print("¡Encontraste el oro!")



# --- Ejecución de prueba ---
m = Mundo(tamaño=4)
kb = KB(tamaño=4)
agente = Agente(m, kb)

# Inicializar conocimiento de la casilla (0,0)
agente.obtener_percepciones()

while agente.vivo and not agente.tiene_oro:
    m.mostrar_tablero()
    destino = agente.elegir_movimiento()
    
    if not destino:
        print("No hay más movimientos seguros.")
        break
    
    agente.moverse(destino)
    if not agente.vivo:
        break
    if agente.obtener_percepciones():
        agente.tiene_oro = True
        print("Oro detectado al entrar ✨")
        break

print("\nResultado final:")
print(f"Vivo: {agente.vivo}, Oro: {agente.tiene_oro}")