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