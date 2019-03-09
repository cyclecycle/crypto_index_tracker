

arb_rate = 0.05
max_wait = 10  # days

init_funds = 16000
funds = init_funds


for i in range(3):
    funds += 0.05 * init_funds

print(funds - init_funds, 100 * funds/init_funds)