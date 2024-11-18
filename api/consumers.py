import json
from channels.generic.websocket import AsyncWebsocketConsumer

class TriquiConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        self.tablero = [[" ", " ", " "] for _ in range(3)]  # Inicializar el tablero
        self.modoNormal = True  # Modo normal activo por defecto
        self.figuraJugador1 = 'X'
        self.figuraJugador2 = 'O'
        self.juegaJugador1 = True
        self.listaJugadasJ1 = []  # Almacena las jugadas del Jugador 1
        self.listaJugadasJ2 = []  # Almacena las jugadas del Jugador 2
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
            if self.modoNormal:
                self.tablero = self.jugar(casilla, self.figuraJugador1 if self.juegaJugador1 else self.figuraJugador2)
            else:
                self.tablero = self.jugar_especial(casilla)

            # Actualizar listas de jugadas
            if self.juegaJugador1:
                self.listaJugadasJ1.append(casilla)
            else:
                self.listaJugadasJ2.append(casilla)

            # Cambiar el turno
            self.juegaJugador1 = not self.juegaJugador1

            # Verificar si es el fin del juego
            if self.es_fin_del_juego(self.tablero):
                await self.send(text_data=json.dumps({
                    'action': 'fin_juego',
                    'tablero': self.tablero,
                    'mensaje': "Fin del juego"
                }))
            else:
                # Si es el turno de la máquina, realizar jugada
                if not self.juegaJugador1 and not self.modoNormal:
                    mejor_jugada = self.obtener_mejor_jugada()
                    if mejor_jugada is not None:
                        self.tablero = self.jugar(mejor_jugada, self.figuraJugador2)
                        self.listaJugadasJ2.append(mejor_jugada)  # Actualizar lista de jugadas de la máquina
                        self.juegaJugador1 = not self.juegaJugador1

                        if self.es_fin_del_juego(self.tablero):
                            await self.send(text_data=json.dumps({
                                'action': 'fin_juego',
                                'tablero': self.tablero,
                                'mensaje': "La máquina ha ganado"
                            }))
                            return

                # Enviar el tablero actualizado
                await self.send(text_data=json.dumps({
                    'action': 'actualizar_tablero',
                    'tablero': self.tablero,
                    'turno': 'Jugador 1' if self.juegaJugador1 else 'Jugador 2'
                }))
        else:
            await self.send(text_data=json.dumps({
                'action': 'error',
                'mensaje': 'Celda ocupada o inválida'
            }))

    async def iniciar_juego(self, data):
        self.modoNormal = data.get('modoNormal', True)
        self.figuraJugador1 = data.get('figuraJugador1', 'X')
        self.figuraJugador2 = 'O' if self.figuraJugador1 == 'X' else 'X'
        self.juegaJugador1 = data.get('juegaPrimero', True)
        self.listaJugadasJ1.clear()  # Reiniciar lista de jugadas
        self.listaJugadasJ2.clear()  # Reiniciar lista de jugadas
        self.tablero = [[" ", " ", " "] for _ in range(3)]  # Reiniciar el tablero
        await self.send(text_data=json.dumps({
            'action': 'juego_iniciado',
            'tablero': self.tablero,
            'turno': 'Jugador 1' if self.juegaJugador1 else 'Jugador 2'
        }))

    def celda_disponible(self, celda):
        columna = ord(celda[0]) - ord('a')
        fila = int(celda[1]) - 1
        if self.modoNormal:
            return self.tablero[fila][columna] == ' '
        else:
            return celda not in self.listaJugadasJ1 and celda not in self.listaJugadasJ2

    def jugar(self, casilla, figura):
        columna = ord(casilla[0]) - ord('a')
        fila = int(casilla[1]) - 1
        copiaEstado = self.obtener_copia_tablero()
        copiaEstado[fila][columna] = figura
        return copiaEstado

    def obtener_copia_tablero(self):
        return [row[:] for row in self.tablero]

    def es_fin_del_juego(self, estado):
        for x in range(3):
            if estado[x][0] == estado[x][1] == estado[x][2] != ' ':
                return True
        for x in range(3):
            if estado[0][x] == estado[1][x] == estado[2][x] != ' ':
                return True
        if estado[0][0] == estado[1][1] == estado[2][2] != ' ':
            return True
        if estado[0][2] == estado[1][1] == estado[2][0] != ' ':
            return True
        return len(self.obtener_casillas_libres()) == 0

    def obtener_casillas_libres(self):
        return [(chr(y + ord('a')), x + 1) for x in range(3) for y in range(3) if self.tablero[x][y] == ' ']

    def obtener_mejor_jugada(self):
        mejor_valor = float("-inf")
        mejor_movimiento = None
        for casilla in self.obtener_casillas_libres():
            tablero_simulado = self.jugar(casilla, self.figuraJugador2)
            valor = self.minimax(tablero_simulado, profundidad=0, es_maximizador=False)
            if valor > mejor_valor:
                mejor_valor = valor
                mejor_movimiento = casilla
        return mejor_movimiento

    def minimax(self, estado, profundidad, es_maximizador):
        if self.es_fin_del_juego(estado):
            return self.Utilidad(estado)
        if es_maximizador:
            mejor_valor = float("-inf")
            for casilla in self.obtener_casillas_libres():
                valor = self.minimax(self.jugar(casilla, self.figuraJugador2), profundidad + 1, False)
                mejor_valor = max(mejor_valor, valor)
            return mejor_valor
        else:
            mejor_valor = float("inf")
            for casilla in self.obtener_casillas_libres():
                valor = self.minimax(self.jugar(casilla, self.figuraJugador1), profundidad + 1, True)
                mejor_valor = min(mejor_valor, valor)
            return mejor_valor

    def Utilidad(self, estado):
        cantLineasJ1 = self.contar_lineas(estado, self.figuraJugador1)
        cantLineasJ2 = self.contar_lineas(estado, self.figuraJugador2)
        ganaJugador1 = self.calcular_ganador(estado, self.figuraJugador1)
        ganaJugador2 = self.calcular_ganador(estado, self.figuraJugador2)

        if ganaJugador1:
            return float("-inf")
        elif ganaJugador2:
            return float("inf")
        else:
            return cantLineasJ2 - cantLineasJ1

    def contar_lineas(self, estado, figura):
        count = 0
        for x in range(3):
            if estado[x].count(figura) == 3:  # Línea horizontal
                count += 1
        for x in range(3):
            if all(estado[i][x] == figura for i in range(3)):  # Línea vertical
                count += 1
        if estado[0][0] == estado[1][1] == estado[2][2] == figura:  # Diagonal
            count += 1
        if estado[0][2] == estado[1][1] == estado[2][0] == figura:  # Diagonal
            count += 1
        return count

    def calcular_ganador(self, estado, figura):
        for x in range(3):
            if estado[x][0] == estado[x][1] == estado[x][2] == figura:
                return True
        for x in range(3):
            if estado[0][x] == estado[1][x] == estado[2][x] == figura:
                return True
        if estado[0][0] == estado[1][1] == estado[2][2] == figura:
            return True
        if estado[0][2] == estado[1][1] == estado[2][0] == figura:
            return True
        return False

    async def disconnect(self, close_code):
        # Lógica para limpiar al desconectarse, si es necesario
        pass
    
