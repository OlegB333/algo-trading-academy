import asyncio
from ib_insync import *
import datetime

ib = IB()
ib.connect('127.0.0.1', 4004, clientId=9)

contract = Forex('EURUSD')
end_dt = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=1)

ticks = ib.reqHistoricalTicks(
    contract, 
    startDateTime=end_dt - datetime.timedelta(hours=1),
    endDateTime=end_dt,
    numberOfTicks=100,
    whatToShow='MIDPOINT',
    useRth=False
)

print(f"Midpoint Ticks: {len(ticks)}")

try:
    ticks2 = ib.reqHistoricalTicks(
        contract, 
        startDateTime=end_dt - datetime.timedelta(hours=1),
        endDateTime=end_dt,
        numberOfTicks=100,
        whatToShow='TRADES',
        useRth=False
    )
    print(f"Trades Ticks: {len(ticks2)}")
except Exception as e:
    print(f"Error trades: {e}")

ib.disconnect()
