from load_data import load_initial_data



rounds = load_initial_data()

for round in rounds:
    print(round.round_num)