import matplotlib.pyplot as plt

def plot_stats(xs, ys, players, safety):
	plt.title('TrueSkill Ratings Over Time')
	plt.ylabel('TrueSkill Rating')
	plt.xlabel('Date')

	index = 0
	for player_stats in ys:
		plt.plot(xs, [p.mu - p.sigma*safety for p in player_stats], label=players[index])
		plt.legend()
		index += 1

	plt.show()
