import matplotlib.pyplot as plt
import random

# Random HEX color strings if needed
# r = lambda: random.randint(0,255)
# color='#%02X%02X%02X' % (r(),r(),r())

def plot_stats(xs, ys, players):
	plt.title('TrueSkill Rankings Over Time')
	plt.ylabel('TrueSkill Ranking')
	plt.xlabel('Date')

	for player_stats in ys:
		plt.plot(xs, player_stats, label=players[ys.index(player_stats)])
		plt.legend()

	plt.show()