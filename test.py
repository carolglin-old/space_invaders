class AlienTypeOne:
	def __init__(self):
		print("Aliens!")

class Barrier:
	def __init__(self):
		print("Barriers!")

levels = {
	"one": [ 
		{ 
			"type": AlienTypeOne,
			"rows": 5,
			"columns": 12,
			"xborder": 25,
			"yborder": 50,
			"dx": 6,
			"dy": 0,
			"xspacing": 40,
			"yspacing": 40,
			"movement": [
				("right", 18),
				("down", 1),
				("left", 18),
				("down", 1)
			]
		}, {
			"type": Barrier,
			"rows": 3,
			"columns": 6,
			"xborder": 100,
			"yborder": 400
		}, {
			"type": Barrier,
			"rows": 3,
			"columns": 6,
			"xborder": 340,
			"yborder": 400
		}, {
			"type": Barrier,
			"rows": 3,
			"columns": 6,
			"xborder": 580,
			"yborder": 400
		}
	], "two": [ 
		{
			"type": AlienTypeOne,
			"rows": 5,
			"columns": 6,
			"xborder": 25,
			"yborder": 50,
			"dx": 6,
			"dy": 0,
			"xspacing": 40,
			"yspacing": 40,
			"movement": [
				("right", 9),
				("down", 1),
				("left", 9),
				("down", 1)	
				]
		}, {
			"type": AlienTypeOne,
			"rows": 5,
			"columns": 6,
			"xborder": 535,
			"yborder": 50,
			"dx": -6,
			"dy": 0,
			"xspacing": 40,
			"yspacing": 40,
			"movement": [
				("left", 9),
				("down", 1),
				("right", 9),
				("down", 1)	
			]
		}, {
			"type": Barrier,
			"rows": 3,
			"columns": 6,
			"xborder": 100,
			"yborder": 400
		}, {
			"type": Barrier,
			"rows": 3,
			"columns": 6,
			"xborder": 340,
			"yborder": 400
		}, {
			"type": Barrier,
			"rows": 3,
			"columns": 6,
			"xborder": 580,
			"yborder": 400
		}
	]		
}


# for i in range(len(levels["one"])):
# 	if levels["one"][i]["type"] == AlienTypeOne:
# 		print("pass through alien function")
# 	if levels["one"][i]["type"] == Barrier:
# 		print("pass through barrier function")

# doobie = [[3, 5], [4, 5], [6, 5]]
# doobie[0].append(4)
# print(doobie)

derp = [("right", 18), ("down", 1), ("left", 18), ("down", 1)]
underp = []

for i in levels["one"][0]["movement"]:
	j = 0
	while j < i[1]:
		underp.append(i[0])
		j += 1

print(underp)





