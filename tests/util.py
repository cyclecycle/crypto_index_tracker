

class TestClient:

    def __init__(self, name):
        self.name = name

    def describe(self):
        return {
            'name': self.name,
            'fees': {
                'funding': {
                    'withdraw': {
                        'B': 0.01,
                        'Q': 0.02
                    }
                },
                'trading': {
                    'taker': 0.001
                }
            }
        }


TESTCLIENTS = {
    'C0': TestClient('C0'),
    'C1': TestClient('C1')
}

if __name__ == "__main__":
    # print(get_spread('B', 'Q', TESTCLIENTS['C0'], TESTCLIENTS['C1']))
    pass