import random
import time

# ==========================================
# 1. MOTOR LÓGICO (CEREBRO)
# ==========================================
class MotorLogico:
    def __init__(self):
        self.clausulas = set()

    def tell(self, sentencia_fnc):
        if not isinstance(sentencia_fnc, frozenset):
            sentencia_fnc = frozenset(sentencia_fnc)
        self.clausulas.add(sentencia_fnc)

    def ask(self, query, max_pasos=500):
        """Intenta probar query por refutación (Resolución)."""
        negacion = self.negar_literal(query)
        clauses = set(self.clausulas)
        clauses.add(frozenset({negacion}))
        
        nuevas = set()
        pasos = 0

        while pasos < max_pasos:
            pasos += 1
            n = len(clauses)
            lista_clausulas = list(clauses)
            pairs = [(lista_clausulas[i], lista_clausulas[j]) for i in range(n) for j in range(i+1, n)]
            
            encontro_nuevas = False
            for (ci, cj) in pairs:
                resolventes = self.pl_resolve(ci, cj)
                if frozenset() in resolventes:
                    return True # Contradicción -> Es Verdad
                for res in resolventes:
                    if res not in clauses and res not in nuevas:
                        nuevas.add(res)
                        encontro_nuevas = True
            if not encontro_nuevas:
                return False
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
# 2. REPRESENTACIÓN DEL MUNDO
# ==========================================
class Celda:
    def __init__(self):
        self.pozo = False
        self.wumpus = False
        self.oro = False
        self.brisa = False
        self.hedor = False
        self.brillo = False

class Mundo:
    def __init__(self, tamano=4, prob_pozo=0.2):
        self.tamano = tamano
        self.celdas = [[Celda() for _ in range(tamano)] for _ in range(tamano)]
        self.pos_agente = (0, 0)
        self.juego_activo = True
        self.gano = False
        self.mensaje_fin = ""
        
        self._generar_mapa(prob_pozo)
        self._calcular_percepciones()

    def _generar_mapa(self, prob_pozo):
        celdas_libres = [(x, y) for x in range(self.tamano) for y in range(self.tamano) if (x,y) != (0,0)]
        
        for x, y in celdas_libres:
            if random.random() < prob_pozo:
                self.celdas[x][y].pozo = True

        if celdas_libres:
            wx, wy = random.choice(celdas_libres)
            self.celdas[wx][wy].wumpus = True

        if celdas_libres:
            ox, oy = random.choice(celdas_libres)
            self.celdas[ox][oy].oro = True

    def _calcular_percepciones(self):
        for x in range(self.tamano):
            for y in range(self.tamano):
                celda = self.celdas[x][y]
                if celda.pozo:
                    for nx, ny in self.adyacentes(x, y):
                        self.celdas[nx][ny].brisa = True
                if celda.wumpus:
                    for nx, ny in self.adyacentes(x, y):
                        self.celdas[nx][ny].hedor = True
                if celda.oro:
                    celda.brillo = True

    def adyacentes(self, x, y):
        dirs = [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]
        return [(nx, ny) for nx, ny in dirs if 0 <= nx < self.tamano and 0 <= ny < self.tamano]

    def obtener_percepcion(self, pos):
        x, y = pos
        c = self.celdas[x][y]
        return {"brisa": c.brisa, "hedor": c.hedor, "brillo": c.brillo, "pos": pos}

    def realizar_accion(self, accion):
        if not self.juego_activo: return
        x, y = self.pos_agente
        
        if accion == "TOMAR":
            if self.celdas[x][y].oro:
                self.gano = True
                self.juego_activo = False
                print(">>> ¡Encontraste el oro! <<<")
            else:
                print("No hay oro aquí.")
        
        elif accion in ["ARRIBA", "ABAJO", "IZQUIERDA", "DERECHA"]:
            dx, dy = 0, 0
            if accion == "ARRIBA": dx = -1
            elif accion == "ABAJO": dx = 1
            elif accion == "IZQUIERDA": dy = -1
            elif accion == "DERECHA": dy = 1
            
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.tamano and 0 <= ny < self.tamano:
                self.pos_agente = (nx, ny)
                print(f"Movimiento a {self.pos_agente}") # Estilo solicitado
                
                c = self.celdas[nx][ny]
                if c.pozo:
                    self.juego_activo = False
                    self.mensaje_fin = "Moriste... (Caíste en pozo)"
                    print("Moriste...")
                elif c.wumpus:
                    self.juego_activo = False
                    self.mensaje_fin = "Moriste... (Wumpus)"
                    print("Moriste...")
            else:
                print("¡GOLPE! (Pared)")

    def mostrar_tablero(self):
        # Estilo visual solicitado en la imagen
        print("\nTablero actual (debug):")
        for x in range(self.tamano):
            fila = ""
            for y in range(self.tamano):
                if (x, y) == self.pos_agente:
                    fila += "A "
                elif self.celdas[x][y].wumpus:
                    fila += "W "
                elif self.celdas[x][y].pozo:
                    fila += "P "
                elif self.celdas[x][y].oro:
                    fila += "O "
                elif self.celdas[x][y].hedor:
                    fila += "H "
                elif self.celdas[x][y].brisa:
                    fila += "B "
                else:
                    fila += ". "
            print(fila)
        print()

# ==========================================
# 3. AGENTE LÓGICO (VISUALIZACIÓN ANTIGUA)
# ==========================================
class AgenteLogico:
    def __init__(self, mundo):
        self.mundo = mundo
        self.motor = MotorLogico()
        self.visitadas = set()
        self.seguras = set() # Para mostrar en el KB
        
        # Listas para simular la visualización del KB antiguo
        self.posibles_pozos = set() 
        self.posibles_wumpus = set()
        self.wumpus_confirmado = None

        self.kb_inicial()

    def kb_inicial(self):
        self.motor.tell(frozenset({'~P_0_0'}))
        self.motor.tell(frozenset({'~W_0_0'}))
        self.seguras.add((0,0))

    def mostrar_kb_status(self):
        # Reproducimos el formato exacto de tu imagen
        print("--- KB ---")
        # Convertimos a lista y ordenamos para que se vea ordenado al imprimir
        print(f"Seguras: {self.seguras}")
        print(f"Posibles Pozos: {self.posibles_pozos}")
        print(f"Posibles Wumpus: {self.posibles_wumpus}")
        print(f"Wumpus Confirmado: {self.wumpus_confirmado}")
        print("------------------")

    def jugar(self):
        max_turnos = 25
        turno = 0
        estancamiento = 0
        
        # Bucle principal
        while self.mundo.juego_activo and turno < max_turnos:
            turno += 1
            
            # 1. MOSTRAR ESTADO (Estilo Visual Solicitado)
            self.mostrar_kb_status()
            self.mundo.mostrar_tablero()
            
            # 2. PERCIBIR
            percepcion = self.mundo.obtener_percepcion(self.mundo.pos_agente)
            
            if percepcion["brillo"]:
                self.mundo.realizar_accion("TOMAR")
                break
            
            # 3. ACTUALIZAR KB (Lógica Nueva)
            self.actualizar_conocimiento(percepcion)
            
            # 4. DECIDIR (Lógica Nueva)
            x, y = self.mundo.pos_agente
            vecinos = self.mundo.adyacentes(x, y)
            movimientos_seguros = []
            
            for nx, ny in vecinos:
                if (nx, ny) in self.visitadas:
                    continue 
                
                # INFERENCIA LÓGICA
                safe_pozo = self.motor.ask(f"~P_{nx}_{ny}")
                safe_wumpus = self.motor.ask(f"~W_{nx}_{ny}")
                
                if safe_pozo and safe_wumpus:
                    movimientos_seguros.append((nx, ny))
                    self.seguras.add((nx, ny))
                    # Limpieza visual de sospechosos si ya es segura
                    if (nx,ny) in self.posibles_pozos: self.posibles_pozos.remove((nx,ny))
                    if (nx,ny) in self.posibles_wumpus: self.posibles_wumpus.remove((nx,ny))

            mejor_movimiento = None
            if movimientos_seguros:
                mejor_movimiento = random.choice(movimientos_seguros)
                estancamiento = 0
            else:
                # Backtracking
                estancamiento += 1
                visitadas = [v for v in vecinos if v in self.visitadas]
                if visitadas:
                    mejor_movimiento = random.choice(visitadas)
            
            # MODO VALIENTE (Si se atasca)
            if estancamiento >= 5:
                posibles_arriesgadas = [n for n in vecinos if n not in self.visitadas]
                if posibles_arriesgadas:
                    mejor_movimiento = random.choice(posibles_arriesgadas)
                    estancamiento = 0

            # 5. EJECUTAR
            if mejor_movimiento:
                self.visitadas.add((x,y))
                self.seguras.add((x,y))
                
                # Calcular dirección para mover
                mx, my = mejor_movimiento
                direccion = ""
                if mx < x: direccion = "ARRIBA"
                elif mx > x: direccion = "ABAJO"
                elif my < y: direccion = "IZQUIERDA"
                elif my > y: direccion = "DERECHA"
                
                self.mundo.realizar_accion(direccion)
            else:
                print("No hay movimientos posibles.")
                break
        
        print("\nResultado final:")
        print(f"Vivo: {not 'Moriste' in self.mundo.mensaje_fin}, Oro: {self.mundo.gano}")


    def actualizar_conocimiento(self, p):
        """Traduce percepciones a Lógica y actualiza listas visuales"""
        x, y = p["pos"]
        vecinos = self.mundo.adyacentes(x, y)
        
        # --- POZOS ---
        if not p["brisa"]:
            for nx, ny in vecinos:
                self.motor.tell(frozenset({f"~P_{nx}_{ny}"}))
                # Visual: Si sabemos que no hay pozo, removemos de sospechosos
                if (nx, ny) in self.posibles_pozos:
                    self.posibles_pozos.remove((nx, ny))
        else:
            clausula = set()
            for nx, ny in vecinos:
                clausula.add(f"P_{nx}_{ny}")
                # Visual: Agregamos a sospechosos si no sabemos que es segura
                if (nx, ny) not in self.seguras:
                    self.posibles_pozos.add((nx, ny))
            self.motor.tell(frozenset(clausula))

        # --- WUMPUS ---
        if not p["hedor"]:
            for nx, ny in vecinos:
                self.motor.tell(frozenset({f"~W_{nx}_{ny}"}))
                if (nx, ny) in self.posibles_wumpus:
                    self.posibles_wumpus.remove((nx, ny))
        else:
            clausula = set()
            for nx, ny in vecinos:
                clausula.add(f"W_{nx}_{ny}")
                if (nx, ny) not in self.seguras:
                    self.posibles_wumpus.add((nx, ny))
            self.motor.tell(frozenset(clausula))


if __name__ == "__main__":
    m = Mundo(tamano=4)
    agente = AgenteLogico(m)
    agente.jugar()