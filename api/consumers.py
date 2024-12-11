import json
from channels.generic.websocket import AsyncWebsocketConsumer

class TriquiConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        self.inicializar_juego()
        await self.send(json.dumps({
            'action': 'juego_iniciado',
            'tablero': self.tablero,
            'turno': 'Jugador 1' if self.juegaJugador1 else 'Jugador 2'
        }))

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data['action']

        if action == 'hacer_jugada':
            await self.hacer_jugada(data)
        elif action == 'iniciar_juego':
            await self.iniciar_juego(data)

    async def hacer_jugada(self, data):
        casilla = data['casilla']
        if self.celda_disponible(casilla):
            if self.juegaJugador1:
                self.tablero = self.jugar(casilla, self.figuraJugador1)
                self.listaJugadasJ1.append(casilla)
                if len(self.listaJugadasJ1) > 3:
                    primera_jugada = self.listaJugadasJ1.pop(0)
                    self.remover_jugada(primera_jugada)
            else:
                self.tablero = self.jugar(casilla, self.figuraJugador2)
                self.listaJugadasJ2.append(casilla)
                if len(self.listaJugadasJ2) > 3:
                    primera_jugada = self.listaJugadasJ2.pop(0)
                    self.remover_jugada(primera_jugada)

            self.juegaJugador1 = not self.juegaJugador1

            if self.es_fin_del_juego(self.tablero):
                await self.send(json.dumps({
                    'action': 'fin_juego',
                    'tablero': self.tablero,
                    'mensaje': "Fin del juego"
                }))
            else:
                await self.send(json.dumps({
                    'action': 'actualizar_tablero',
                    'tablero': self.tablero,
                    'turno': 'Jugador 1' if self.juegaJugador1 else 'Jugador 2'
                }))
                if not self.juegaJugador1 and not self.modoNormal:
                    await self.jugada_maquina()
        else:
            await self.send(json.dumps({
                'action': 'error',
                'mensaje': 'Celda ocupada o inválida'
            }))

    async def jugada_maquina(self):
        mejor_jugada = self.obtener_mejor_jugada()
        if mejor_jugada is not None:
            self.tablero = self.jugar(mejor_jugada, self.figuraJugador2)
            self.listaJugadasJ2.append(mejor_jugada)
            if len(self.listaJugadasJ2) > 3:
                primera_jugada = self.listaJugadasJ2.pop(0)
                self.remover_jugada(primera_jugada)

            self.juegaJugador1 = not self.juegaJugador1

            if self.es_fin_del_juego(self.tablero):
                await self.send(json.dumps({
                    'action': 'fin_juego',
                    'tablero': self.tablero,
                    'mensaje': "La máquina ha ganado"
                }))
            else:
                await self.send(json.dumps({
                    'action': 'actualizar_tablero',
                    'tablero': self.tablero,
                    'turno': 'Jugador 1' if self.juegaJugador1 else 'Jugador 2'
                }))

    async def iniciar_juego(self, data):
        self.modoNormal = data.get('modoNormal', True)
        self.figuraJugador1 = data.get('figuraJugador1', 'X')
        self.figuraJugador2 = 'O' if self.figuraJugador1 == 'X' else 'X'
        self.juegaJugador1 = data.get('juegaPrimero', False)
        self.listaJugadasJ1 = []
        self.listaJugadasJ2 = []
        self.tablero = [[" ", " ", " "] for _ in range(3)]
        self.dificultad = max(1, min(int(data.get('dificultad', 1)), 10))

        if not self.juegaJugador1 and not self.modoNormal:
            await self.jugada_maquina()

        await self.send(json.dumps({
            'action': 'juego_iniciado',
            'tablero': self.tablero,
            'turno': 'Jugador 1' if self.juegaJugador1 else 'Jugador 2'
        }))

    def inicializar_juego(self):
        self.tablero = [[" ", " ", " "] for _ in range(3)]
        self.figuraJugador1 = 'X'
        self.figuraJugador2 = 'O'
        self.juegaJugador1 = True
        self.listaJugadasJ1 = []
        self.listaJugadasJ2 = []
        self.dificultad = 1

    def celda_disponible(self, celda):
        columna = ord(celda[0]) - ord('a')
        fila = int(celda[1]) - 1
        return self.tablero[fila][columna] == ' '

    def jugar(self, casilla, figura):
        columna = ord(casilla[0]) - ord('a')
        fila = int(casilla[1]) - 1
        self.tablero[fila][columna] = figura
        return self.tablero

    def remover_jugada(self, casilla):
        columna = ord(casilla[0]) - ord('a')
        fila = int(casilla[1]) - 1
        self.tablero[fila][columna] = ' '

    def es_fin_del_juego(self, estado):
        for x in range(3):
            if estado[x][0] == estado[x][1] == estado[x][2] != ' ':
                return True
            if estado[0][x] == estado[1][x] == estado[2][x] != ' ':
                return True
        if estado[0][0] == estado[1][1] == estado[2][2] != ' ':
            return True
        if estado[0][2] == estado[1][1] == estado[2][0] != ' ':
            return True
        return not any(' ' in row for row in estado)

    def obtener_casillas_libres(self):
        return [(chr(y + ord('a')) + str(x + 1)) for x in range(3) for y in range(3) if self.tablero[x][y] == ' ']

    def obtener_mejor_jugada(self):
        mejor_valor = float("-inf")
        mejor_movimiento = None
        for casilla in self.obtener_casillas_libres():
            fila, columna = int(casilla[1]) - 1, ord(casilla[0]) - ord('a')
            self.tablero[fila][columna] = self.figuraJugador2
            valor = self.minimax(self.tablero, 0, False, self.dificultad)
            self.tablero[fila][columna] = ' '
            if valor > mejor_valor:
                mejor_valor = valor
                mejor_movimiento = casilla
        return mejor_movimiento

    def minimax(self, estado, profundidad, es_maximizador, profundidad_max):
        if profundidad >= profundidad_max or self.es_fin_del_juego(estado):
            return self.utilidad(estado)
        if es_maximizador:
            mejor_valor = float("-inf")
            for casilla in self.obtener_casillas_libres():
                fila, columna = int(casilla[1]) - 1, ord(casilla[0]) - ord('a')
                estado[fila][columna] = self.figuraJugador2
                valor = self.minimax(estado, profundidad + 1, False, profundidad_max)
                estado[fila][columna] = ' '
                mejor_valor = max(mejor_valor, valor)
            return mejor_valor
        else:
            mejor_valor = float("inf")
            for casilla in self.obtener_casillas_libres():
                fila, columna = int(casilla[1]) - 1, ord(casilla[0]) - ord('a')
                estado[fila][columna] = self.figuraJugador1
                valor = self.minimax(estado, profundidad + 1, True, profundidad_max)
                estado[fila][columna] = ' '
                mejor_valor = min(mejor_valor, valor)
            return mejor_valor

    def utilidad(self, estado):
        if self.calcular_ganador(estado, self.figuraJugador1):
            return -1
        elif self.calcular_ganador(estado, self.figuraJugador2):
            return 1
        else:
            return 0

    def calcular_ganador(self, estado, figura):
        for x in range(3):
            if estado[x][0] == estado[x][1] == estado[x][2] == figura:
                return True
            if estado[0][x] == estado[1][x] == estado[2][x] == figura:
                return True
        if estado[0][0] == estado[1][1] == estado[2][2] == figura:
            return True
        if estado[0][2] == estado[1][1] == estado[2][0] == figura:
            return True
        return False

    async def disconnect(self, close_code):
        pass
