import numpy as np
import matplotlib.pyplot as plt
from bed import Bed
from city import City
from hospital import Hospital
from people import People
from peoplepool import PeoplePool
from matplotlib import animation

line = ['l', 'line']

def graph(city, pool, hos, mode=line[0]):
	#0未感染, 1潜伏期, 2确诊, 3住院(在地图上无), 4免疫期, 5病死, 6总体得病(仅包含确诊), 7总存活人数, 8传染源, 
	colors_people = ['white', 'yellow', 'red', 'black', 'green', 'black', 'purple', 'grey', 'blue'] 
	colors_bed = ['red', 'black'] #0有人，1无人

	fig = plt.figure(figsize=(20, 10))
	plt.style.use('dark_background')
	fig.patch.set_facecolor('black')
	grid = plt.GridSpec(3, 5, wspace=0.4, hspace=0.3)
	ax1 = plt.subplot(grid[0:3, 0:3])
	ax2 = plt.subplot(grid[0:3, 3])

	ax3 = plt.subplot(grid[0, 4])
	ax4 = plt.subplot(grid[1, 4])
	ax5 = plt.subplot(grid[2, 4])

	if mode in line:
		ax3_susceptible_data = [0, 0]
		ax3_total_data = [0, 0]
		ax3_recover_data = [0, 0]
		ax4_exposed_data = [0, 0]
		ax4_contagious_data = [0, 0]
		ax5_infective_data = [0, 0]
		ax5_diagnosed_data = [0, 0]

	hosX = hos.getX()
	hosY = hos.getY()

	axbackground = fig.canvas.copy_from_bbox(ax1.bbox)
	ax2background = fig.canvas.copy_from_bbox(ax2.bbox)

	def animate(time):
		boundry = 5 * pool.SCALE
		status = pool.getStatus()
		status_hos = hos.getStatus()
		susceptible = np.sum(status == 0)
		exposed = np.sum(status == 1)
		infective = np.sum(status == 2)
		recovered = np.sum(status == 4)
		hospitalized = np.sum(status_hos == False)
		diagnosed = infective + hospitalized # 仅包含确诊
		contagious = exposed + infective # 能传染给他人的
		total = susceptible + exposed + diagnosed + recovered # SEIR
		
		if time > 0 and sum(pool.Ti) != 0:
			Ti = sum(pool.Ti)/len(pool.Ti)
			Tg = sum(pool.Tg)/len(pool.Tg)
			Te = sum(pool.Te)/len(pool.Te)
			if pool.can_exposed_infect:
				k = pool.in_touch / contagious if contagious != 0 else 0
				R0 = k * pool.BROAD_RATE * (Ti + Te) 
				# R0 = k*b*D (Lipsitch M，Cohen T, Cooper B, et al. TransmissionDynamics and Control of Severe Acute Respiratory Syndrome. Science, 2003,300(5627): 1966-1970.)
			else:
				k = pool.in_touch / infective if infective != 0 else 0
				R0 = k * pool.BROAD_RATE * Ti
			# lamda = np.log(diagnosed) / time
			# rho = Te / Tg
			# R0 = 1 + lamda * Tg + rho * (1 - rho) * (lamda * Tg) ** 2
		else:
			R0 = np.nan
			Ti = np.nan
			Tg = np.nan
			Te = np.nan

		if mode in line:
			ax3_susceptible_data[1] = susceptible
			ax3_total_data[1] = total
			ax3_recover_data[1] = recovered
			ax4_exposed_data[1] = exposed
			ax4_contagious_data[1] = contagious
			ax5_infective_data[1] = infective
			ax5_diagnosed_data[1] = diagnosed

		fig.canvas.restore_region(axbackground)
		fig.canvas.restore_region(ax2background)

		ax1.clear()
		ax1.scatter(pool.getX(), pool.getY(), c = [colors_people[j] for j in status], marker = '.', \
					alpha = 0.6, s = 10)
		ax1.set_title(f'Te:{Te:<10.2f}Ti:{Ti:<10.2f}Tg:{Tg:<10.2f}R0:{R0:.2f}\nTime:{time:<10}Susceptible:{susceptible:<10}Exposed:{exposed:<10}Infective:{infective:<10}Recovered:{recovered}')
		ax1.set_xticks([])
		ax1.set_yticks([])
		ax1.set_xlim(-boundry, boundry)
		ax1.set_ylim(-boundry, boundry)

		ax2.clear()
		ax2.scatter(hosX, hosY, c = [colors_bed[j] for j in status_hos], marker = '.', \
					alpha = 1, s = 10)
		ax2.set_title(f'Hospitalized:{hospitalized}/{hos.bed_counts}')
		ax2.set_xticks([])
		ax2.set_yticks([])

		color_total = colors_people[7]
		color_contagious = colors_people[8]
		color_diagnosed = colors_people[6]
		color_susceptible = colors_people[0]
		color_exposed = colors_people[1]
		color_infective = colors_people[2]
		color_recovered = colors_people[4]

		if mode in line:
			if (time >= 1):
				ax3.plot([time-1, time], ax3_susceptible_data, color = color_susceptible)
				ax3.plot([time-1, time], ax3_total_data, color = color_total)
				ax3.plot([time-1, time], ax5_infective_data, color = color_infective)
				ax3.plot([time-1, time], ax4_exposed_data, color = color_exposed)
				ax3.plot([time-1, time], ax3_recover_data, color = color_recovered) if pool.recovered_included == True else None
				ax4.plot([time-1, time], ax4_exposed_data, color = color_exposed)
				ax4.plot([time-1, time], ax4_contagious_data, color = color_contagious)
				ax5.plot([time-1, time], ax5_infective_data, color = color_infective)
				ax5.plot([time-1, time], ax5_diagnosed_data, color = color_diagnosed)
		else:
			ax3.bar(time, total, color = color_total, width=1)
			ax3.bar(time, susceptible, color = color_susceptible, width=1)
			ax3.bar(time, exposed, color = color_exposed, width=1)
			ax3.bar(time, infective, color = color_infective, width=1)
			ax3.bar(time, recovered, color = color_recovered, width=1) if pool.recovered_included == True else None
			ax4.bar(time, contagious, color = color_contagious, width=1)
			ax4.bar(time, exposed, color = color_exposed, width=1)
			ax5.bar(time, diagnosed, color = color_diagnosed, width=1)
			ax5.bar(time, infective, color = color_infective, width=1)

		ax3.set_title(f'total({color_total}):{total}\nsusceptible({color_susceptible}):{susceptible}\nrecovered({color_recovered}):{recovered}\nexposed({color_exposed}):{exposed}\ninfective({color_infective}):{infective}')
		ax4.set_title(f'contagious({color_contagious}):{contagious}\nexposed({color_exposed}):{exposed}')
		ax5.set_title(f'diagnosed({color_diagnosed}):{diagnosed}\ninfective({color_infective}):{infective}')

		pool.update(time, hos)
		# plt.pause(0.00001)
		if mode in line:
			ax3_susceptible_data[0] = susceptible
			ax3_total_data[0] = total
			ax3_recover_data[0] = recovered
			ax4_exposed_data[0] = exposed
			ax4_contagious_data[0] = contagious
			ax5_infective_data[0] = infective
			ax5_diagnosed_data[0] = diagnosed

		return 0

	ani = animation.FuncAnimation(fig=fig, func=animate)

	plt.show()
