from collections import deque
import random
import time

# Explicación: Este es el núcleo de la IA. No sabe nada de pozos o wumpus,
class MotorLogico:
    def __init__(self):
        # Almacena todo el conocimiento como un conjunto de reglas matemáticas.
        # Usamos 'set' para evitar reglas duplicadas automáticamente.
        self.clausulas = set()

    def tell(self, sentencia_fnc):
        """Recibe: Una cláusula (ej: "Hay pozo en 1,1 O hay pozo en 1,2")"""
        if not isinstance(sentencia_fnc, frozenset): # Usamos 'frozenset' porque los sets normales no pueden guardarse dentro de otros sets.
            sentencia_fnc = frozenset(sentencia_fnc)
        self.clausulas.add(sentencia_fnc)

    def ask(self, query, max_pasos=500):
        """Si quiero saber si "Es seguro", asumo temporalmente que "NO es seguro" """
        # Negamos la hipótesis (Asumimos lo contrario a lo que queremos probar)
        negacion = self.negar_literal(query)
        clauses = set(self.clausulas)
        clauses.add(frozenset({negacion}))
        
        nuevas = set()
        pasos = 0
        
        # Bucle de resolución: Intentamos chocar reglas contra reglas hasta hallar una contradicción
        while pasos < max_pasos:
            pasos += 1
            n = len(clauses)
            lista_clausulas = list(clauses)
            
            # Comparamos todas las reglas contra todas (fuerza bruta heurística)
            pairs = [(lista_clausulas[i], lista_clausulas[j]) for i in range(n) for j in range(i+1, n)]
            
            encontro_nuevas = False
            for (ci, cj) in pairs:
                # Intentamos fusionar dos reglas (Resolver)
                resolventes = self.pl_resolve(ci, cj)
                
                # Si obtenemos un set vacío, encontramos una CONTRADICCIÓN (Ej: A y no A).
                # Esto significa que nuestra hipótesis negada era falsa, por tanto la query es VERDAD.
                if frozenset() in resolventes: return True
                
                for res in resolventes:
                    if res not in clauses and res not in nuevas:
                        nuevas.add(res)
                        encontro_nuevas = True
            
            # Si no encontramos nada nuevo, no podemos probarlo.
            if not encontro_nuevas: return False
            clauses.update(nuevas)
        
        return False # Se acabó el tiempo/pasos

    def pl_resolve(self, ci, cj):
        """
        La regla matemática de Resolución:
        Si tenemos (A o B) y (No B o C) -> Los 'B' se cancelan -> Queda (A o C).
        """
        resolventes = set()
        for literal in ci:
            negacion = self.negar_literal(literal)
            # Buscamos si el opuesto exacto existe en la otra cláusula
            if negacion in cj:
                nueva = set(ci | cj) # Unimos todo
                nueva.remove(literal) # Quitamos el positivo
                nueva.remove(negacion) # Quitamos el negativo
                resolventes.add(frozenset(nueva))
        return resolventes

    def negar_literal(self, literal):
        # Convierte "A" en "~A" y viceversa
        if literal.startswith("~"): return literal[1:]
        return f"~{literal}"


# MODULO 2
class Celda:
    def __init__(self):
        self.pozo = False
        self.brisa = False
        self.wumpus = False
        self.hedor = False
        self.oro = False
        self.brillo = False
        self.visitada = False # Nos ayuda a pintar el mapa o decidir movimientos

class Mundo:
    def __init__(self, tamaño=4, prob_pozo=0.2):
        self.tamaño = tamaño
        self.prob_pozo = prob_pozo
        self.celdas = [[Celda() for _ in range(tamaño)] for _ in range(tamaño)]
        self.pos_agente = (0, 0)
        
        # Generación procedimental del mapa
        self.generar_pozos()
        self.generar_brisas()
        self.colocar_wumpus()
        self.colocar_oro()
        self.validar_mundo() # Asegura que el inicio sea seguro

    def celda_valida(self, i, j):
        # Regla: No poner monstruos ni pozos en el inicio (0,0) ni sus vecinos inmediatos
        adyacentes_inicio = [(0,1), (1,0), (1,1)]
        if (i,j) == self.pos_agente or (i,j) in adyacentes_inicio: return False
        celda = self.celdas[i][j]
        # Regla: Una celda no puede tener dos objetos físicos a la vez (simplificación)
        if celda.pozo or celda.wumpus or celda.oro: return False
        return True

    def generar_pozos(self):
        for i in range(self.tamaño):
            for j in range(self.tamaño):
                if (i, j) == self.pos_agente: continue
                # Coloca pozos basado en probabilidad aleatoria
                if self.celda_valida(i,j) and random.random() < self.prob_pozo:
                    self.celdas[i][j].pozo = True

    def generar_brisas(self):
        # Física del juego: Si hay pozo, las 4 celdas vecinas tienen brisa
        for i in range(self.tamaño):
            for j in range(self.tamaño):
                if self.celdas[i][j].pozo:
                    self.agregar_brisas_alrededor(i, j)

    def agregar_brisas_alrededor(self, i, j):
        adyacentes = [(i-1,j), (i+1,j), (i,j-1), (i,j+1)]
        for x, y in adyacentes:
            if self.esta_dentro(x, y): self.celdas[x][y].brisa = True

    def esta_dentro(self, i, j):
        # Evita errores de índice fuera de la matriz
        return 0 <= i < self.tamaño and 0 <= j < self.tamaño

    def colocar_wumpus(self):
        w_i, w_j = random.randint(0, self.tamaño - 1), random.randint(0, self.tamaño - 1)
        while not self.celda_valida(w_i, w_j):
            w_i, w_j = random.randint(0, self.tamaño-1), random.randint(0, self.tamaño-1)
        self.celdas[w_i][w_j].wumpus = True
        self.agregar_hedor_alrededor(w_i, w_j)

    def agregar_hedor_alrededor(self, i, j):
        # Física del juego: El Wumpus emite hedor en cruz
        adyacentes = [(i-1,j), (i+1,j), (i,j-1), (i,j+1)]
        for x, y in adyacentes:
            if self.esta_dentro(x, y): self.celdas[x][y].hedor = True

    def bfs_ruta_segura(self, inicio, objetivo):
        """
        Algoritmo Búsqueda en Anchura (BFS).
        Sirve para verificar que el Oro sea alcanzable. 
        Si el oro queda encerrado por pozos, el mapa se descarta y se regenera.
        """
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
        # Intenta colocar oro hasta que encuentra una posición accesible
        while True:
            o_i, o_j = random.randint(0, self.tamaño-1), random.randint(0, self.tamaño-1)
            if not self.celda_valida(o_i, o_j): continue
            self.celdas[o_i][o_j].oro = True
            self.celdas[o_i][o_j].brillo = True
            
            # Verificación de solubilidad del mapa
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
        # Imprime la matriz en consola para depuración (Modo Dios)
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

# MÓDULO 3: EL PUENTE (Traductor KB)
class KB:
    def __init__(self, tamaño):
        self.tamaño = tamaño
        # Aquí vive la instancia del Motor Lógico
        self.motor = MotorLogico()
        
        # Listas visuales para mostrar al usuario qué sospecha el agente
        self.seguras = set()
        self.posibles_pozos = set()
        self.posibles_wumpus = set()
        self.confirmado_wumpus = None
        
        # AXIOMAS INICIALES: Hechos que sabemos antes de empezar
        # ~P_0_0 significa "NO hay Pozo en 0,0"
        self.motor.tell(frozenset({'~P_0_0'}))
        self.motor.tell(frozenset({'~W_0_0'}))
        self.seguras.add((0,0))

    def obtener_adyacentes(self, i, j):
        directions = [(i-1,j),(i+1,j),(i,j-1),(i,j+1)]
        return [(x,y) for x,y in directions if 0 <= x < self.tamaño and 0 <= y < self.tamaño]

    def actualizar_conocimientos(self, i, j, brisa, hedor):
        # 1. TRADUCCIÓN: Convertir sensaciones físicas a fórmulas lógicas
        self.seguras.add((i, j))
        ady = self.obtener_adyacentes(i, j)

        # --- LÓGICA DE POZOS ---
        if not brisa:
            # Si NO hay brisa, es matemáticamente imposible que haya pozos alrededor.
            # Agregamos hechos negativos: ~P_x_y para todos los vecinos.
            for nx, ny in ady:
                self.motor.tell(frozenset({f"~P_{nx}_{ny}"})) 
        else:
            # Si HAY brisa, al menos uno de los vecinos tiene un pozo.
            # Agregamos una cláusula disyuntiva: P_vecino1 v P_vecino2 v ...
            clausula = set()
            for nx, ny in ady:
                clausula.add(f"P_{nx}_{ny}") 
            self.motor.tell(frozenset(clausula))

        # --- LÓGICA DE WUMPUS --- 
        if not hedor:
            for nx, ny in ady:
                self.motor.tell(frozenset({f"~W_{nx}_{ny}"})) 
        else:
            clausula = set()
            for nx, ny in ady:
                clausula.add(f"W_{nx}_{ny}") 
            self.motor.tell(frozenset(clausula))

        # 2. CONSULTA Y VISUALIZACIÓN
        # Una vez alimentado el cerebro, le preguntamos qué opina de los vecinos
        self.actualizar_listas_visuales(ady)
        self.mostrar_estado()

    def actualizar_listas_visuales(self, adyacentes_relevantes):
        """
        Esta función actualiza lo que se imprime en pantalla ("Posibles Pozos", etc.)
        consultando al Motor Lógico sobre la seguridad de cada casilla vecina.
        """
        for nx, ny in adyacentes_relevantes:
            if (nx, ny) in self.seguras: continue

            # ASK: Preguntamos si es imposible que haya pozo Y wumpus
            no_pozo = self.motor.ask(f"~P_{nx}_{ny}")
            no_wumpus = self.motor.ask(f"~W_{nx}_{ny}")

            if no_pozo and no_wumpus:
                # Si el motor prueba que no hay nada, es SEGURA
                self.seguras.add((nx, ny))
                if (nx, ny) in self.posibles_pozos: self.posibles_pozos.remove((nx, ny))
                if (nx, ny) in self.posibles_wumpus: self.posibles_wumpus.remove((nx, ny))
            else:
                # Si el motor no puede probar que no hay peligro, mantenemos la sospecha
                if not no_pozo: self.posibles_pozos.add((nx, ny))
                if not no_wumpus: self.posibles_wumpus.add((nx, ny))

    def mostrar_estado(self):
        print("\n--- KB (Conocimiento) ---")
        print("Seguras:", list(self.seguras))
        print("Posibles Pozos:", list(self.posibles_pozos))
        print("Posibles Wumpus:", list(self.posibles_wumpus))
        print("Wumpus Confirmado:", self.confirmado_wumpus)
        print("-------------------------\n")


class Agente:
    def __init__(self, mundo, kb):
        self.mundo = mundo
        self.kb = kb
        self.pos = (0, 0)
        self.vivo = True
        self.tiene_oro = False
        self.visitadas = set()
        self.visitadas.add((0,0))
        self.estancamiento = 0 # Contador para detectar si estamos dando vueltas

    def obtener_percepciones(self):
        # Interactúa con el mundo y pasa los datos a la KB
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
        
        # ESTRATEGIA 1: Exploración Segura
        # Buscar una casilla que la KB marque como SEGURA y que NO hayamos visitado.
        candidatos_seguros = []
        for nx, ny in vecinos:
            if (nx, ny) in self.kb.seguras and (nx, ny) not in self.visitadas:
                candidatos_seguros.append((nx, ny))
        
        if candidatos_seguros:
            self.estancamiento = 0
            return random.choice(candidatos_seguros)
        
        # ESTRATEGIA 2: Backtracking (Retroceder)
        # Si no hay nuevas seguras, volvemos a una vieja segura para buscar otro camino.
        self.estancamiento += 1
        print(f"(Razonando... no veo casillas nuevas seguras. Intento {self.estancamiento}/5)")
        visitadas_seguras = [v for v in vecinos if v in self.visitadas]
        
        if self.estancamiento < 5 and visitadas_seguras:
             return random.choice(visitadas_seguras)
        
        # ESTRATEGIA 3: Modo Valiente (Probabilístico)
        # Si llevamos mucho tiempo atascados (estancamiento >= 5), nos arriesgamos.
        # Elegimos una casilla no visitada aunque sea peligrosa.
        if self.estancamiento >= 5:
            print(">>> AGENTE ATASCADO: ¡Tomando un riesgo calculado! <<<")
            riesgosos = [v for v in vecinos if v not in self.visitadas]
            if riesgosos:
                self.estancamiento = 0
                return random.choice(riesgosos)
        
        return None

    def moverse(self, destino):
        # Ejecuta el movimiento físico y verifica si vive o muere
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


# 1. Crear el entorno
m = Mundo(tamaño=4)
# 2. Crear la mente (KB + Motor Lógico)
kb = KB(tamaño=4)
# 3. Crear el agente (Cuerpo)
agente = Agente(m, kb)

# Inicializar
print(f"\nTe encuentras en {agente.pos}")
agente.obtener_percepciones()

# Bucle del juego
while agente.vivo and not agente.tiene_oro:
    m.mostrar_tablero()
    destino = agente.elegir_movimiento()
    
    if not destino:
        print("No hay más movimientos posibles.")
        break
    
    # Pausa opcional para ver paso a paso
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