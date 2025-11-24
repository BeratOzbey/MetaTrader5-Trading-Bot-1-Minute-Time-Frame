from tkinter import Label
import MetaTrader5 as mt5
from MetaTrader5 import TIMEFRAME_M1, TRADE_RETCODE_DONE
import tkinter as tk

ekran = tk.Tk()
ekran.geometry("800x800+300+50")
k_value_text = Label(text="%K", font=("Verdena", 40, "bold"), fg="green")
k_value_text.pack()
d_value_text = Label(text="%D", font=("Verdena", 40, "bold"), fg="red")
d_value_text.pack()
trade_count = Label(text="Trade Count : 0", font=("Verdena", 40, "bold"), fg="blue")
trade_count.pack()
price_text = Label(text="Price : ", font=("Verdena", 40, "bold"))
price_text.pack()

print("Meta Trader trading bot by Berat Özbey")

if mt5.initialize():
    print("Successfully Connected to Terminal")
else:
    print("Connection Failed")


k_value = None
d_value = None
Price = 0
Total_trades_made = 0


def stochastic_calculation():
    global k_value, d_value, Price, Total_trades_made

    start_pos = -1
    raw_k_values = []

    for x in range(5):
        start_pos += 1

        # 14 mumluk veri çekme
        Last_14_Rates = mt5.copy_rates_from_pos("EURUSDm", TIMEFRAME_M1, start_pos, 14)

        # Veri gelmezse bekle ve tekrar dene
        if Last_14_Rates is None or len(Last_14_Rates) < 14:
            k_value_text.configure(text="Waiting for MT5 data...")
            d_value_text.configure(text="")
            ekran.after(500, stochastic_calculation)
            return

        Price = Last_14_Rates[13][4]
        Low = min([y[3] for y in Last_14_Rates])
        High = max([z[2] for z in Last_14_Rates])

        k = (Price - Low) / (High - Low) * 100
        raw_k_values.append(k)

    slowed_k = (raw_k_values[0] + raw_k_values[1] + raw_k_values[2]) / 3
    slowed_k2 = (raw_k_values[1] + raw_k_values[2] + raw_k_values[3]) / 3
    slowed_k3 = (raw_k_values[2] + raw_k_values[3] + raw_k_values[4]) / 3
    d_value = (slowed_k + slowed_k2 + slowed_k3) / 3
    k_value = slowed_k

    # GUI güncelle
    k_value_text.configure(text=f"%K : {str(slowed_k)[:5]}")
    d_value_text.configure(text=f"%D : {str(d_value)[:5]}")
    price_text.configure(text=f"Buy : {str(mt5.symbol_info('EURUSDm').ask)[:7]}\nSell : {str(mt5.symbol_info('EURUSDm').bid)[:7]}")

    # Pozisyon yoksa trade araması
    if mt5.positions_total() == 0:

        # Sell
        if k_value >= 80 and d_value >= 80 and k_value < d_value:
            if mt5.symbol_info("EURUSDm").ask - mt5.symbol_info("EURUSDm").bid < 30:
                sell_order = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "symbol": "EURUSDm",
                    "volume": 1,
                    "type": mt5.ORDER_TYPE_SELL,
                    "price": float(str(mt5.symbol_info("EURUSDm").bid)[:7]),
                    "magic": 656565,
                    "comment": "python script open",
                    "sl": float(str(mt5.symbol_info("EURUSDm").bid + 0.00040)[:7]),
                    "tp": float(str(mt5.symbol_info("EURUSDm").bid - 0.00040)[:7]),
                    "deviation": 10
                }
                trade = mt5.order_send(sell_order)
                if trade.retcode == TRADE_RETCODE_DONE:
                    print("Successfully Traded")
                    Total_trades_made += 1
                else:
                    print("Failed to Trade", trade.retcode)

        # Buy
        elif k_value <= 20 and d_value <= 20 and d_value < k_value:
            if mt5.symbol_info("EURUSDm").ask - mt5.symbol_info("EURUSDm").bid < 30:
                buy_order = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "symbol": "EURUSDm",
                    "volume": 1,
                    "type": mt5.ORDER_TYPE_BUY,
                    "price": float(str(mt5.symbol_info("EURUSDm").ask)[:7]),
                    "magic": 656565,
                    "comment": "python script open",
                    "sl": float(str(mt5.symbol_info("EURUSDm").ask - 0.00040)[:7]),
                    "tp": float(str(mt5.symbol_info("EURUSDm").ask + 0.00040)[:7]),
                    "deviation": 10
                }
                trade = mt5.order_send(buy_order)
                if trade.retcode == TRADE_RETCODE_DONE:
                    print("Successfully Traded")
                    Total_trades_made += 1
                else:
                    print("Failed to Trade", trade.retcode)

    trade_count.configure(text=f"Trade Count : {Total_trades_made}")
    ekran.after(16, stochastic_calculation)


stochastic_calculation()
ekran.mainloop()
