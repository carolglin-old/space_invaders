
class Levels:
    def __init__(self):
        self.data = [
            [ 
                {
                    "type": Dude
                }, 
                {
                    "type": Alien,
                    "id": "two",
                    "rows": 2,
                    "columns": 11,
                    "xcorner": 30,
                    "ycorner": 50,
                    "xspacing": 40,
                    "yspacing": 40,
                    "movement": [
                        ("right", 15),
                        ("down", 1),
                        ("left", 15),
                        ("down", 1)
                    ]
                }, {
                    "type": Alien,
                    "id": "one",
                    "rows": 3,
                    "columns": 11,
                    "xcorner": 30,
                    "ycorner": 130,
                    "xspacing": 40,
                    "yspacing": 40,
                    "movement": [
                        ("right", 15),
                        ("down", 1),
                        ("left", 15),
                        ("down", 1)
                    ]
                }, {
                    "type": Barrier,
                    "rows": 3,
                    "columns": 6,
                    "xcorner": 100,
                    "ycorner": 450,
                    "xspacing": 30,
                    "yspacing": 20
                }, {
                    "type": Barrier,
                    "rows": 3,
                    "columns": 6,
                    "xcorner": 340,
                    "ycorner": 450,
                    "xspacing": 30,
                    "yspacing": 20
                }, {
                    "type": Barrier,
                    "rows": 3,
                    "columns": 6,
                    "xcorner": 580,
                    "ycorner": 450,
                    "xspacing": 30,
                    "yspacing": 20
                }
            ], [ 
                {
                    "type": Alien,
                    "id": "three",
                    "rows": 1,
                    "columns": 1,
                    "xcorner": 25,
                    "ycorner": 40,
                    "xspacing": 40,
                    "yspacing": 40,
                    "movement": [
                        ("right", 145),
                        ("left", 145),
                    ]
                }, {
                    "type": Alien,
                    "id": "three",
                    "rows": 1,
                    "columns": 1,
                    "xcorner": 735,
                    "ycorner": 70,
                    "xspacing": 40,
                    "yspacing": 40,
                    "movement": [
                        ("left", 145),
                        ("right", 145),
                    ] 
                }, {
                    "type": Alien,
                    "id": "two",
                    "rows": 2,
                    "columns": 6,
                    "xcorner": 25,
                    "ycorner": 110,
                    "xspacing": 40,
                    "yspacing": 40,
                    "movement": [
                        ("right", 6),
                        ("down", 1),
                        ("left", 6),
                        ("down", 1) 
                    ]
                }, {
                    "type": Alien,
                    "id": "two",
                    "rows": 2,
                    "columns": 6,
                    "xcorner": 535,
                    "ycorner": 110,
                    "xspacing": 40,
                    "yspacing": 40,
                    "movement": [
                        ("left", 6),
                        ("down", 1),
                        ("right", 6),
                        ("down", 1) 
                    ]
                }, {
                    "type": Alien,
                    "id": "one",
                    "rows": 2,
                    "columns": 6,
                    "xcorner": 25,
                    "ycorner": 190,
                    "xspacing": 40,
                    "yspacing": 40,
                    "movement": [
                        ("right", 6),
                        ("down", 1),
                        ("left", 6),
                        ("down", 1) 
                    ]
                }, {
                    "type": Alien,
                    "id": "one",
                    "rows": 2,
                    "columns": 6,
                    "xcorner": 535,
                    "ycorner": 190,
                    "xspacing": 40,
                    "yspacing": 40,
                    "movement": [
                        ("left", 6),
                        ("down", 1),
                        ("right", 6),
                        ("down", 1) 
                    ]
                }, {
                    "type": Barrier,
                    "rows": 3,
                    "columns": 6,
                    "xcorner": 100,
                    "ycorner": 450,
                    "xspacing": 30,
                    "yspacing": 20
                }, {
                    "type": Barrier,
                    "rows": 3,
                    "columns": 6,
                    "xcorner": 340,
                    "ycorner": 450,
                    "xspacing": 30,
                    "yspacing": 20
                }, {
                    "type": Barrier,
                    "rows": 3,
                    "columns": 6,
                    "xcorner": 580,
                    "ycorner": 450,
                    "xspacing": 30,
                    "yspacing": 20
                }
            ]       
        ]