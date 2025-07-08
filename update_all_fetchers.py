import time
from src.fetchers.binance import get_binance_data
from src.fetchers.coinbase import get_coinbase_data
from src.fetchers.yahoo import get_yahoo_data
from src.fetchers.coingecko import get_coingecko_data
from src.fetchers.coincap import get_coincap_data
from src.fetchers.cryptocompare import get_cryptocompare_data
from src.fetchers.unirate import get_unirate_data

def update_all():
    pairs = {
        "BTCUSDT": "BTC-USD",
        # "ETHUSDT": "ETH-USD",
        # "XRPUSDT": "XRP-USD",
        # "ADAUSDT": "ADA-USD",
        # "SOLUSDT": "SOL-USD",
    }

    for binance_symbol, yahoo_symbol in pairs.items():
        coin = binance_symbol.replace("USDT", "").lower()
        print(f"\n====== AGGIORNO {binance_symbol} / {yahoo_symbol} ======")

        # Binance - 1000 righe 1 minuto
        get_binance_data(symbol=binance_symbol, interval="1m", limit=1000)

        # Coinbase - spot price
        get_coinbase_data(symbol=yahoo_symbol)

        # Yahoo Finance - ultimi 5 giorni con granularità 5 minuti
        get_yahoo_data(symbol=yahoo_symbol, interval="5m", period="5d")

        # CoinGecko - ultimi 7 giorni
        get_coingecko_data(symbol=coin, vs_currency="usd", days=7)

        # CoinCap - spot
        get_coincap_data(symbol=coin)

        # CryptoCompare - 200 ore (~8 giorni)
        get_cryptocompare_data()

        # UniRate - conversioni base
        get_unirate_data(base=coin.upper())

if __name__ == "__main__":
    print("🔄 Inizio aggiornamento fetcher...")
    update_all()
    print("\n✅ Aggiornamento completato.")
 
