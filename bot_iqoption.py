import time
import logging
from iqoptionapi.stable_api import IQ_Option

# Configurações iniciais
IQ_USERNAME = "seu_email"
IQ_PASSWORD = "sua_senha"
PARIDADE = "EURUSD"
VALOR_ENTRADA = 10
MARTINGALE_MULTIPLICADOR = 2
STOP_WIN = 50
STOP_LOSS = -50

def conectar_iqoption():
    """Estabelece conexão com a IQ Option."""
    iq = IQ_Option(IQ_USERNAME, IQ_PASSWORD)
    iq.connect()
    if iq.check_connect():
        logging.info("Conectado com sucesso!")
    else:
        logging.error("Erro ao conectar!")
        exit()
    return iq

def estrategia_rompimento(iq):
    """Verifica rompimentos e toma decisões de compra/venda."""
    velas = iq.get_candles(PARIDADE, 60, 10, time.time())
    suporte = min([vela[3] for vela in velas])
    resistencia = max([vela[2] for vela in velas])
    preco_atual = iq.get_currency_rate(PARIDADE, 'USD')
    
    if preco_atual >= resistencia:
        return "put"
    elif preco_atual <= suporte:
        return "call"
    return None

def realizar_operacao(iq, direcao, valor):
    """Executa uma ordem na IQ Option."""
    status, id_ordem = iq.buy(valor, PARIDADE, direcao, 1)
    return status, id_ordem

def monitorar_ganhos(iq):
    """Controla Stop Win e Stop Loss."""
    lucro_total = 0
    while True:
        direcao = estrategia_rompimento(iq)
        if direcao:
            status, id_ordem = realizar_operacao(iq, direcao, VALOR_ENTRADA)
            if status:
                lucro = iq.check_win_v3(id_ordem)
                lucro_total += lucro
                if lucro < 0:
                    VALOR_ENTRADA *= MARTINGALE_MULTIPLICADOR
                if lucro_total >= STOP_WIN or lucro_total <= STOP_LOSS:
                    logging.info("Stop atingido! Encerrando operações.")
                    break
            time.sleep(60)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    iq = conectar_iqoption()
    monitorar_ganhos(iq)
    iq.disconnect()
