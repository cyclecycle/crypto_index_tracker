# Bots

## Rule set

Determines what the bot looks at how it responds.

Comprised of four sections:

### vars

Variables used throughout the rule set.

### observables

What the bot looks at to make decisions.

Observables are refreshed each step by their corresponding methods.

### actions

Methods to trigger when conditions are met (see below: `rules`)

### rules

Specifies `conditions` that trigger that an `action`, where each condition is described in terms of a value check on an `observable`.

The first set of conditions to be met will determine the resulting `action`. Only one action is triggered per `step`. The default action is 'wait'.



# Notes on exchanges #
These are exchanges I have attempted to make accounts with, so this also serves as a whitelist as I have researched many more and deemed
them untrustworthy.

### GDAX ###
Works reliably.

### Kraken ###
Very unreliable when site is busy. Will time out or accuse you of spam often.
Use https://status.kraken.com/ to check site status. If response time >1400ms it craps out. Could maybe automate this check?
When not busy, works OK. Looks like it can give a timeout error but still execute the request. Be careful I guess.

### Binance ###
Reliable. Site is chinese so try not to store too much on it.

### Kucoin ###
Untested but looks deec. Hong kong exchange.

### BitTrex ###
[Currently not able to make new accounts]

### Bitfinex ###
[Currently not able to make new accounts]

### Abucoin ###
Small exchange not supported by ccxt. Using to hold SC until I can make a BitTrex account.

### Gatecoin ###
[untested]

### Exmo ###
[untested]

### Bitstamp ###
[untested]