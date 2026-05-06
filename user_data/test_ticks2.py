import datetime
from ib_insync import IB, Forex, util
util.patchAsyncio()
ib = IB()
parsed = ib.connect('ib-gateway', 4004, clientId=6)
contract = Forex('EURUSD')
end_dt = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=1)
try:
    ticks1 = ib.reqHistoricalTicks(
        contract, 
        startDateTime=end_dt - datetime.timedelta(hours=1),
        endDateTime=end_dt,
        numberOfTicks=100,
        whatToShow='MIDPOINT',
        useRth=False
    )
    print(f"With both: {len(ticks1)}")
except Exception as e:
    print(f"Error with both: {e}")

try:
    ticks2 = ib.reqHistoricalTicks(
        contract, 
        startDateTime=end_dt - datetime.timedelta(hours=1),
        endDateTime='',
        numberOfTicks=100,
        whatToShow='MIDPOINT',
        useRth=False
    )
    print(f"With start only: {len(ticks2)}")
except Exception as e:
    print(f"Error start only: {e}")

ib.disconnect()
