import matplotlib.pyplot as plt

def plot_stats(xs, ys, players):
	plt.title('TrueSkill Ratings Over Time')
	plt.ylabel('TrueSkill Ranting')
	plt.xlabel('Date')

	index = 0
	for player_stats in ys:
		plt.plot(xs, player_stats, label=players[index])
		plt.legend()
		index += 1

	plt.show()
