class Dude(self):
	variables
		self.length 
		self.width
		self.start (x,y)
		self.speed
		self.graphic
		self.shoot noise
		self.immunity_time - amount of time dude gets immunity
		self.location - stores the current x,y starting point of the dude
		self.tag - tag of what type of object it is 

	functions
		left_move(self, event) - move to the left, listen for left_button event
		left_arrow(self) - bind left arrow to left_move
		update_location(self, location) - remove the location in location variable, and update with current
		listen_bullet_event - listen to the event that the dude bullet has disappeared
		stop_shoot - activate after shooting, until the bullet event is heard
		right_move(self, event) - move to the right, litsen for the right_button event
		right_arrow(self) - bind right arrow to right_move
		shoot(self, event, type, dude_location) - listen for shoot_button event and create an instance of bullet starting from the location of the dude, moving upwards until it hits something or goes off screen
		shoot_button(self) - bind space key to shoot function
		immunity(self) - immunity_time seconds of immunity against alien bullets when the instance of dude is created

class Bullet(self, type, start_location, direction):
	variables
		self.length
		self.width
		self.start (x,y)
		self.speed
		self.graphic

	functions
		check_collision(self, bullet, object) 
		check_type(self, type) - checks to see if the object type is equal to the bullet type 
		remove_bullet(self, event, type) - if a bullet hits a valid target or goes off screen, call disappear on bullet and dispatch event
		barrier_collision(self, location) - calls the disappear function of the barrier that is located at hit_barrier
		alien_collision(self, location) - calls the disappear function of the alien that is located at hit_alien
		dude_collision(self) - calls the dude_death function that is located in the game class

class Barrier(self, start_location):
	variables
		self.length
		self.width
		self.start (x,y)
		self.graphic

class AlienTypeOne(self, start_location):
	variables
		self.length
		self.width
		self.start (x,y)
		self.shoot_noise
		self.hit_noise
		self.start_direction 
		self.points - 10 for each alien killed
		self.paces - how many spaces the aliens move right and left
		self.vertical_space - how many spaces the aliens move vertically
		self.horizontal_space - how many spaces the aliens move horizontally
		self.shoot_frequency - random numbers inside
		self.touchdown_y - y coordinate where game over happens
		
	functions
		horizontal_movement(self, paces) - move paces in one direction then call vertical movement before switching directions
		vertical_movement(self, paces) - move down before switching direction 
		shoot(self, tag) - creates an instance of bullet, tagged alien when one number out of shoot_frequency is called at random
		check_for_touchdown(self) - check to see if the y coordinate equals the touchdown_y coordinate every time the alien moves down

class MasterFunctions(self):
	functions
		disappear(self, object, object list) - removes object from object list and the game 
		view_converter(self, object) - converts the model coordinates to pixel display coordinates
		time_converter(self) - converts the model time to actual display time 
		play_sound(self, sound) - plays the sound when event happens
		display(self, object, object location) - displays the object to the object location
		add_score(self, type_score) - adds alien_points 

class Level(self, alien start locations, barrier start locations):
	variables
		self.barrer_locations - list of start locations for all the instances of barrier in the level
		self.alien_locations - list of start locations for all instances of alientypeone in the level

	static variables
		One = Level(alien start locations list, barrier start locations list)
		Two = Level(alien start locations list, barrier start locations list)

class Game(self):
	variables
		self.screen_length
		self.screen_width
		self.game_music
		self.frame
		self.score - total points on the frame
		self.lives_left - on frame
		self.level - on frame
		self.barrier_list - list of barrier objects
		self.alien_list - list of alien objects
		self.canvas - create a canvas
		canvas bindings

	functions
		start(self, dude, level) - creates an instance of the dude, calls load_level on the level indicated by self.level
		load_level(self, level) - calls create_aliens and create_barriers on that level
		create_aliens(self, level, alien start locations) - create an instance of alien at each start location on the list, append these to alien_list
		create_barriers(self, level, barrier start locations) - create an instance of barrier at each start location on the list, append these to barrier_list
		check_lives(self, lives) - check to see if lives are below zero
		remove_life(self) - remove a life from self.lives_left
		game_over(self) - display gg on the screen, restart button appears, disable key bindings
		game_restart(self) - sets score to 0, lives_left to 3, and load_level one
		level_up(self, level) - changes self.level and calls load_level on that level 
		mainloop(self) - calls movement of all items, display movement, check collision, collision reactions (disappear, display, check lives, change score, etc)
			shoot alien shots, display shots, check if valid shot has been fired by dude, shoot dude bullet, display shot


		









