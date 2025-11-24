from collections import deque
import random
import time

# ==========================================
# MOTOR LÓGICO (El "Cerebro" Matemático)
# Se agrega esta clase para cumplir con la IA Simbólica
# ==========================================
class MotorLogico:
    def __init__(self):
        self.clausulas = set()

    def tell(self, sentencia_fnc):
        if not isinstance(sentencia_fnc, frozenset):
            sentencia_fnc = frozenset(sentencia_fnc)
        self.clausulas.add(sentencia_fnc)

    def ask(self, query, max_pasos=500):
        """Prueba por Refutación (Resolución). Retorna True si es verdad."""
        negacion = self.negar_literal(query)
        clauses = set(self.clausulas)
        clauses.add(frozenset({negacion}))
        nuevas = set()
        pasos = 0
        while pasos < max_pasos:
            pasos += 1
            n = len(clauses)
            lista_clausulas = list(clauses)
            # Heurística simple: comparar pares
            pairs = [(lista_clausulas[i], lista_clausulas[j]) for i in range(n) for j in range(i+1, n)]
            encontro_nuevas = False
            for (ci, cj) in pairs:
                resolventes = self.pl_resolve(ci, cj)
                if frozenset() in resolventes: return True
                for res in resolventes:
                    if res not in clauses and res not in nuevas:
                        nuevas.add(res)
                        encontro_nuevas = True
            if not encontro_nuevas: return False
            clauses.update(nuevas)
        return False

    def pl_resolve(self, ci, cj):
        resolventes = set()
        for literal in ci:
            negacion = self.negar_literal(literal)
            if negacion in cj:
                nueva = set(ci | cj)
                nueva.remove(literal)
                nueva.remove(negacion)
                resolventes.add(frozenset(nueva))
        return resolventes

    def negar_literal(self, literal):
        if literal.startswith("~"): return literal[1:]
        return f"~{literal}"

# ==========================================
# ESTRUCTURAS DEL JUEGO (Estilo Visual Código 1)
# ==========================================

class Celda:
    def __init__(self):
        self.pozo = False
        self.brisa = False
        self.wumpus = False
        self.hedor = False
        self.oro = False
        self.brillo = False
        self.visitada = False # Agregado para rastreo visual

class Mundo:
    def __init__(self, tamaño=4, prob_pozo=0.2):
        self.tamaño = tamaño
        self.prob_pozo = prob_pozo
        self.celdas = [[Celda() for _ in range(tamaño)] for _ in range(tamaño)]
        self.pos_agente = (0, 0)
        self.generar_pozos()
        self.generar_brisas()
        self.colocar_wumpus()
        self.colocar_oro()
        self.validar_mundo()

    def celda_valida(self, i, j):
        adyacentes_inicio = [(0,1), (1,0), (1,1)]
        if (i,j) == self.pos_agente or (i,j) in adyacentes_inicio: return False
        celda = self.celdas[i][j]
        if celda.pozo or celda.wumpus or celda.oro: return False
        return True

    def generar_pozos(self):
        for i in range(self.tamaño):
            for j in range(self.tamaño):
                if (i, j) == self.pos_agente: continue
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
            if self.esta_dentro(x, y): self.celdas[x][y].brisa = True

    def esta_dentro(self, i, j):
        return 0 <= i < self.tamaño and 0 <= j < self.tamaño

    def colocar_wumpus(self):
        w_i, w_j = random.randint(0, self.tamaño - 1), random.randint(0, self.tamaño - 1)
        while not self.celda_valida(w_i, w_j):
            w_i, w_j = random.randint(0, self.tamaño-1), random.randint(0, self.tamaño-1)
        self.celdas[w_i][w_j].wumpus = True
        self.agregar_hedor_alrededor(w_i, w_j)

    def agregar_hedor_alrededor(self, i, j):
        adyacentes = [(i-1,j), (i+1,j), (i,j-1), (i,j+1)]
        for x, y in adyacentes:
            if self.esta_dentro(x, y): self.celdas[x][y].hedor = True

    # Se mantiene BFS para garantizar que el mapa sea justo (estilo Codigo 1)
    def bfs_ruta_segura(self, inicio, objetivo):
        queue = deque()
        queue.append((inicio, [inicio]))
        visitados = set()
        visitados.add(inicio)
        while queue:
            pos_actual, ruta = queue.popleft()
            if pos_actual == objetivo: return ruta
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
            if not self.celda_valida(o_i, o_j): continue
            self.celdas[o_i][o_j].oro = True
            self.celdas[o_i][o_j].brillo = True
            if self.bfs_ruta_segura(self.pos_agente, (o_i,o_j)):
                self.pos_oro = (o_i,o_j)
                break
            else:
                self.celdas[o_i][o_j].oro = False
                self.celdas[o_i][o_j].brillo = False

    def validar_mundo(self):
        if self.celdas[0][0].pozo or self.celdas[0][0].wumpus or self.celdas[0][0].oro:
            raise ValueError("La celda inicial no puede contener pozo, wumpus o oro.")

    def mostrar_tablero(self):
        print("\nTablero actual (debug):")
        for i in range(self.tamaño):
            fila = ""
            for j in range(self.tamaño):
                if (i, j) == self.pos_agente: fila += "A "
                elif self.celdas[i][j].wumpus: fila += "W "
                elif self.celdas[i][j].oro: fila += "O "
                elif self.celdas[i][j].pozo: fila += "P "
                elif self.celdas[i][j].hedor: fila += "H "
                elif self.celdas[i][j].brisa: fila += "B "
                else: fila += ". "
            print(fila)
        print()

# ==========================================
# BASE DE CONOCIMIENTO (Modificada para usar MOTOR LÓGICO)
# ==========================================
class KB:
    def __init__(self, tamaño):
        self.tamaño = tamaño
        # INTEGRAMOS EL MOTOR LÓGICO AQUÍ
        self.motor = MotorLogico()
        
        # Listas visuales (para mantener el print igual al código 1)
        self.seguras = set()
        self.posibles_pozos = set()
        self.posibles_wumpus = set()
        self.confirmado_wumpus = None
        
        # Axiomas iniciales
        self.motor.tell(frozenset({'~P_0_0'}))
        self.motor.tell(frozenset({'~W_0_0'}))
        self.seguras.add((0,0))

    def obtener_adyacentes(self, i, j):
        directions = [(i-1,j),(i+1,j),(i,j-1),(i,j+1)]
        return [(x,y) for x,y in directions if 0 <= x < self.tamaño and 0 <= y < self.tamaño]

    def actualizar_conocimientos(self, i, j, brisa, hedor):
        # 1. TRADUCCIÓN: Convertir percepciones a Fórmulas Lógicas (FNC)
        self.seguras.add((i, j))
        ady = self.obtener_adyacentes(i, j)

        # Reglas Lógicas para Pozos
        if not brisa:
            for nx, ny in ady:
                self.motor.tell(frozenset({f"~P_{nx}_{ny}"})) # Sabemos que NO hay pozo
        else:
            clausula = set()
            for nx, ny in ady:
                clausula.add(f"P_{nx}_{ny}") # Al menos uno es pozo
            self.motor.tell(frozenset(clausula))

        # Reglas Lógicas para Wumpus
        if not hedor:
            for nx, ny in ady:
                self.motor.tell(frozenset({f"~W_{nx}_{ny}"})) # Sabemos que NO hay Wumpus
        else:
            clausula = set()
            for nx, ny in ady:
                clausula.add(f"W_{nx}_{ny}") # Al menos uno es Wumpus
            self.motor.tell(frozenset(clausula))

        # 2. INFERENCIA Y ACTUALIZACIÓN DE LISTAS VISUALES
        # Aquí consultamos al Motor para llenar las listas que se imprimen en pantalla
        self.actualizar_listas_visuales(ady)
        self.mostrar_estado()

    def actualizar_listas_visuales(self, adyacentes_relevantes):
        # Recorremos adyacentes para ver qué deduce el motor sobre ellos
        for nx, ny in adyacentes_relevantes:
            if (nx, ny) in self.seguras: continue

            # Preguntar al motor: ¿Es seguro (no pozo y no wumpus)?
            no_pozo = self.motor.ask(f"~P_{nx}_{ny}")
            no_wumpus = self.motor.ask(f"~W_{nx}_{ny}")

            if no_pozo and no_wumpus:
                self.seguras.add((nx, ny))
                # Limpiar listas de sospechosos si estaban ahí
                if (nx, ny) in self.posibles_pozos: self.posibles_pozos.remove((nx, ny))
                if (nx, ny) in self.posibles_wumpus: self.posibles_wumpus.remove((nx, ny))
            else:
                # Si no es seguro, actualizamos sospechas visuales
                if not no_pozo: self.posibles_pozos.add((nx, ny))
                if not no_wumpus: self.posibles_wumpus.add((nx, ny))

    def mostrar_estado(self):
        # Formato exacto del Código 1
        print("\n--- KB ---")
        print("Seguras:", list(self.seguras)) # Convertimos a list para print limpio
        print("Posibles Pozos:", list(self.posibles_pozos))
        print("Posibles Wumpus:", list(self.posibles_wumpus))
        print("Wumpus Confirmado:", self.confirmado_wumpus)
        print("--------------\n")


# ==========================================
# AGENTE (Lógica Híbrida)
# ==========================================
class Agente:
    def __init__(self, mundo, kb):
        self.mundo = mundo
        self.kb = kb
        self.pos = (0, 0)
        self.vivo = True
        self.tiene_oro = False
        self.visitadas = set()
        self.visitadas.add((0,0))
        self.estancamiento = 0 # Para evitar bucles infinitos

    def obtener_percepciones(self):
        i, j = self.pos
        celda = self.mundo.celdas[i][j]
        celda.visitada = True
        brisa = celda.brisa
        hedor = celda.hedor
        brillo = celda.brillo
        print(f"En {self.pos} → Brisa={brisa}, Hedor={hedor}, Brillo={brillo}")
        self.kb.actualizar_conocimientos(i, j, brisa, hedor)
        return brillo

    def elegir_movimiento(self):
        i, j = self.pos
        vecinos = self.kb.obtener_adyacentes(i, j)
        
        # 1. Buscar movimiento seguro NO visitado (Prioridad Lógica)
        candidatos_seguros = []
        for nx, ny in vecinos:
            # Usamos la lista 'seguras' que la KB llenó consultando al Motor Lógico
            if (nx, ny) in self.kb.seguras and (nx, ny) not in self.visitadas:
                candidatos_seguros.append((nx, ny))
        
        if candidatos_seguros:
            self.estancamiento = 0
            return random.choice(candidatos_seguros)
        
        # 2. Si no hay nuevos, Backtracking seguro
        self.estancamiento += 1
        print(f"(Razonando... no veo casillas nuevas seguras. Intento {self.estancamiento}/5)")
        visitadas_seguras = [v for v in vecinos if v in self.visitadas]
        
        if self.estancamiento < 5 and visitadas_seguras:
             return random.choice(visitadas_seguras)
        
        # 3. MODO ARRIESGADO (Si se atasca, adivina)
        if self.estancamiento >= 5:
            print(">>> AGENTE ATASCADO: ¡Tomando un riesgo calculado! <<<")
            riesgosos = [v for v in vecinos if v not in self.visitadas]
            if riesgosos:
                self.estancamiento = 0
                return random.choice(riesgosos)
        
        return None

    def moverse(self, destino):
        self.visitadas.add(self.pos)
        self.pos = destino
        print(f"Movimiento a {self.pos}")
        self.mundo.pos_agente = self.pos
        celda = self.mundo.celdas[self.pos[0]][self.pos[1]]
        
        if celda.pozo:
            self.vivo = False
            print("Moriste... (Caíste en un pozo)")
        elif celda.wumpus:
            self.vivo = False
            print("Moriste... (Te comió el Wumpus)")
        
        if celda.oro:
            self.tiene_oro = True
            print("¡Encontraste el oro!")


# ==========================================
# EJECUCIÓN PRINCIPAL (Idéntica al Código 1)
# ==========================================
m = Mundo(tamaño=4)
kb = KB(tamaño=4)
agente = Agente(m, kb)

# Inicializar conocimiento de la casilla (0,0)
print(f"\nTe encuentras en {agente.pos}")
agente.obtener_percepciones()

while agente.vivo and not agente.tiene_oro:
    m.mostrar_tablero()
    destino = agente.elegir_movimiento()
    
    if not destino:
        print("No hay más movimientos posibles.")
        break
    
    # Pequeña pausa para dar efecto de "pensar"
    # time.sleep(0.5) 
    agente.moverse(destino)
    
    if not agente.vivo:
        break
    if agente.obtener_percepciones():
        agente.tiene_oro = True
        print("Oro detectado al entrar ✨")
        break

print("\nResultado final:")
print(f"Vivo: {agente.vivo}, Oro: {agente.tiene_oro}")