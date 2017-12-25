import datetime
from cryptocompy import price
import time

""" Historical day data from cryptocompy """


def historical_compare(bases, quote, e1, e2, no_days=7):
    """Compare historical day data between 2 exhcnages. Defaults to 7 days."""
    date = datetime.datetime.now().date()
    pairs = {}
    for base in bases:
        pairs[base + '-' + quote] = []
        pairs[base + '-' + quote + ' ' + e1] = []
        pairs[base + '-' + quote + ' ' + e2] = []
        for _ in range(no_days):
            date -= datetime.timedelta(days=1)
            gdict = price.get_historical_eod_price(base, quote, str(date), e=e1)
            odict = price.get_historical_eod_price(base, quote, str(date), e=e2)
            print(gdict, odict)
            time.sleep(0.5)

            for b in gdict:
                for q in gdict[b]:
                    pair = b + '-' + q
                    e1_price = gdict[b][q]
                    e2_price = odict[b][q]
                    if e2_price != 0:
                        perc_diff = 100 * (e1_price/e2_price - 1)
                    else:
                        perc_diff = 0

                    pairs[pair].append(perc_diff)
                    pairs[pair + ' ' + e1].append(e1_price)
                    pairs[pair + ' ' + e2].append(e2_price)