import pygame, math
from precode2 import Vector2D, intersect_circles
from random import randrange
from config import *

class LonelyBoid(Exception):
	"""my own exception"""
	pass

class GameObject():
	def __init__(self, pos_vec, speed, color, radius):
		self.pos_vec = pos_vec
		self.speed = speed
		self.color = color
		self.radius = radius

class Boids(GameObject):
	def __init__(self, pos_vec, speed, color, radius):
		GameObject.__init__(self, pos_vec, speed, color, radius)

	def find_neighbour(self, boidlist, limit):
		"""
		takes  a list of objects as argument
		checks if the object is close enough to the "self"-boid be added to a list for all the close objects.
		returns this list.
		"""
		in_area = []

		try:
			for i in boidlist:
				if i is not self:
					if i.pos_vec.x - self.pos_vec.x > -limit and i.pos_vec.x -self.pos_vec.x < limit:
						if i.pos_vec.y  - self.pos_vec.y > -limit and i.pos_vec.y -self.pos_vec.y < limit:
							in_area.append(i)

		except:
			raise LonelyBoid("No more boids in list") 

		return in_area

	#separates the boids
	def separate_boid(self, boidlist, magnitude):
		in_area = self.find_neighbour(boidlist, 30)
		
		sum_x = 0
		sum_y = 0 

		if len(in_area)>0:			
			for i in in_area:
				sum_x = self.pos_vec.x - i.pos_vec.x 
				sum_y = self.pos_vec.y - i.pos_vec.y

				try:
					normalize = -math.sqrt((sum_x*sum_x)+(sum_y*sum_y))

					self.speed.x -= (sum_x/normalize) * MAX_SPEED / magnitude
					self.speed.y -= (sum_y/normalize) * MAX_SPEED / magnitude
				except:
					ZeroDivisionError

	#aligns the average vector of the boids in an area
	def align_boid(self, boidlist, magnitude):
		in_area = self.find_neighbour(boidlist, 70)
		
		sum_x = 0
		sum_y = 0 

		if len(in_area) >= 1:
			for i in in_area:
				sum_x += i.speed.x
				sum_y += i.speed.y

		try:
			sum_x /= len(in_area)
			sum_y /= len(in_area)

			normalize = math.sqrt((sum_x*sum_x)+(sum_y*sum_y))
		
			normx = sum_x/normalize * MAX_SPEED
			normy = sum_y/normalize * MAX_SPEED

			self.speed.x += normx / magnitude
			self.speed.y += normy / magnitude

		except:
			ZeroDivisionError

	#finds the center spot of a cluster of boids and tries to get the boids to flock to it
	def cohesion(self, boidlist, magnitude):
		in_area = self.find_neighbour(boidlist, 50)
		
		sum_x = 0
		sum_y = 0 

		if len(in_area) >= 1:
			for i in in_area:
				if i.pos_vec.x == self.pos_vec.x and i.pos_vec.y == self.pos_vec.y:
					continue
				sum_x += self.pos_vec.x - i.pos_vec.x
				sum_y += self.pos_vec.y - i.pos_vec.y

		try:
			sum_x /= len(in_area)
			sum_y /= len(in_area)

			normalize = math.sqrt((sum_x*sum_x)+(sum_y*sum_y))

			normx = sum_x/normalize * MAX_SPEED
			normy = sum_y/normalize * MAX_SPEED

			self.speed.x -= normx / magnitude
			self.speed.y -= normy / magnitude
			
		except:
			ZeroDivisionError

	def intersect(self, obsticle, turnspeed):
		"""
		if the boid is close enough to the obsticle to be appended to the in_area list,
		the boids speed will be incremented, depending on where the boid is relative to the obsticle 
		"""
		in_area = self.find_neighbour(obsticle, 70)
		
		for i in in_area:
			if i.pos_vec.x - self.pos_vec.x > 0:
				i.speed.x += turnspeed
			else:
				i.speed.x -= turnspeed
			if i.pos_vec.y - self.pos_vec.y > 0:
				i.speed.y += turnspeed
			else:
				i.speed.y -= turnspeed

	def edges_boid(self):
		"""
		if the boids or hoiks is close to the edge of the screen,
		the x or y speed will be incremented depending on the location,
		if it is over the edge it will be teleported to the other side of the screen.
		"""
		if self.pos_vec.x < EDGE_LIMIT:
			if self.speed.x < MAX_SPEED:
				self.speed.x += TURN_SPEED_EDGE
			if self.pos_vec.x < -10:
				self.pos_vec.x =  SCREEN_WIDTH + 10

		if self.pos_vec.x > SCREEN_WIDTH - EDGE_LIMIT:
			if self.speed.x > MIN_SPEED:
				self.speed.x -= TURN_SPEED_EDGE
			if self.pos_vec.x > SCREEN_WIDTH +10:
				self.pos_vec.x =  -10

		if self.pos_vec.y < EDGE_LIMIT:
			if self.speed.y < MAX_SPEED:
				self.speed.y += TURN_SPEED_EDGE
			if self.pos_vec.y < -10:
				self.pos_vec.y =  SCREEN_HEIGHT + 10

		if self.pos_vec.y > SCREEN_HEIGHT - EDGE_LIMIT:
			if self.speed.y > MIN_SPEED:
				self.speed.y -= TURN_SPEED_EDGE
			if self.pos_vec.y > SCREEN_HEIGHT + 10:
				self.pos_vec.y =  -10
				

	def move_boid(self):
		"""
		animates the boids and hoiks.
		"""
		self.pos_vec.x += self.speed.x
		self.pos_vec.y += self.speed.y

	def check_speed(self):
		"""
		checks wheter the speed of the object is over or under the max speed,
		if it is lower than minimum speed it gets set to minumum speed
		if it is higher than max speed it gets set to max speed.
		this is to prevent the boids and hoiks flying to fast.
		"""
		if self.speed.x > MAX_SPEED:
			self.speed.x = MAX_SPEED
		if self.speed.x < MIN_SPEED:
			self.speed.x = MIN_SPEED

		if self.speed.y > MAX_SPEED:
			self.speed.y = MAX_SPEED
		if self.speed.y < MIN_SPEED:
			self.speed.y = MIN_SPEED

	def draw_boid(self, screen):
		"""draws a boid on the given screen"""
		pygame.draw.circle(screen, self.color, (int(self.pos_vec.x), int(self.pos_vec.y)), self.radius)

	#from the precode
	def draw_vec_from_ball(self, screen, col):
		pygame.draw.line(screen, col, (self.pos_vec.x, self.pos_vec.y), (self.pos_vec.x + self.speed.x * LINE_LENGTH, self.pos_vec.y + self.speed.y * LINE_LENGTH), 3)


class Hoiks(Boids):
	"""
	inherites the class of boids, makes it possible to use polimorphism
	"""
	def __init__(self, pos_vec, speed, color, radius):
		GameObject.__init__(self, pos_vec, speed, color, radius)

	def seek_boid(self, boidlist, magnitude):
		"""
		makes the hoik seek the closest boid. finds the vector of the closest boid,
		normalises it, and adds a normalised "target" vector devided by a given magnitude
		to the speed of the hoik 
		"""
		nearest = None
		shortest = None
	

		for i in boidlist:
			sum_x = self.pos_vec.x - i.pos_vec.x
			sum_y = self.pos_vec.y - i.pos_vec.y
			#the next 4 lines of code is borrowed from stack overflow from a similar problem.
			distance = (sum_x*sum_x+sum_y*sum_y)

			if not shortest or distance < shortest:
				shortest = distance
				nearest = i

		try:
			vectorx = nearest.pos_vec.x - self.pos_vec.x
			vectory = nearest.pos_vec.y - self.pos_vec.y

			norm = math.sqrt((vectorx*vectorx)+(vectory*vectory))

			self.speed.x += (vectorx/norm) * MAX_SPEED / magnitude
			self.speed.y += (vectory/norm) * MAX_SPEED / magnitude 
		except:
			ZeroDivisionError

class Game():
	def __init__(self):
		"""setup of the game class."""
		pygame.init()
		self.screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
		self.clock = pygame.time.Clock()
		pygame.display.set_caption("boids")
		self.done = False

		self.boid_list = []
		self.hoik_list = []
		self.obsticle_list = []
		self.all_things_to_draw = []

		#creating instances of boids
		for i in range(BOID_COUNT):
			self.boid = Boids(Vector2D(randrange(0,SCREEN_WIDTH), randrange(0,SCREEN_HEIGHT)), Vector2D(randrange(MIN_SPEED,MAX_SPEED),randrange(MIN_SPEED,MAX_SPEED)), BLACK, BOID_RADIUS)
			self.boid_list.append(self.boid)

		#creating instances of hoiks
		for i in range (HOIK_COUNT):
			self.hoik = Hoiks(Vector2D(randrange(0,SCREEN_WIDTH), randrange(0,SCREEN_HEIGHT)), Vector2D(randrange(MIN_SPEED,MAX_SPEED),randrange(MIN_SPEED,MAX_SPEED)), RED, BOID_RADIUS)
			self.hoik_list.append(self.hoik)

		#appending boidslist and hoikslist to a list of both list, allowing us to easily draw both lists
		self.all_things_to_draw.append(self.boid_list)
		self.all_things_to_draw.append(self.hoik_list)
		
	def handle_events(self):
		"""handles the quit event, and creates a new obsticle if u click the mouse."""
		events = pygame.event.get()
		for event in events:
			#event for quiting
			if event.type == pygame.QUIT:
				self.done = True
			#event for creating a new obsticle when clicking the mousebutton
			if event.type == pygame.MOUSEBUTTONDOWN:
				coordinate = pygame.mouse.get_pos() 
				self.obsticle = Boids(Vector2D(coordinate[0], coordinate[1] ), Vector2D(0,0), RED, OBSTICLE_RADIUS)
				self.obsticle_list.append(self.obsticle)

	def run(self):
		while not self.done:
			self.handle_events()
			self.time_passed = self.clock.tick(30)
			self.screen.fill((GREY))

			#apply the 3 rules for the boid
			for i in self.boid_list:
				i.cohesion(self.boid_list, 1.7)
				i.separate_boid(self.boid_list, 1)
				i.align_boid(self.boid_list, 1.5)
				
				#check for collision with the hoiks
				for u in self.hoik_list:
					if abs(i.pos_vec.x - u.pos_vec.x) < i.radius and abs(i.pos_vec.y - u.pos_vec.y) < i.radius:
						self.boid_list.remove(i) 		

			#make the hoiks steer towards closest boid, make the boids run away from hoiks, 
			#make sure hoiks dont colide and draw a vector from the hoiks to see who they are chasing
			for i in self.hoik_list:
				i.seek_boid(self.boid_list, SEEK_BOID_LIMIT)
				i.intersect(self.boid_list, TURN_SPEED_HOIKS)
				i.separate_boid(self.hoik_list, SEPARATE_HOIK_LIMIT)

			#make the boids and hoiks steer away from obstacles.
			for i in self.obsticle_list:
				i.intersect(self.boid_list, TURN_SPEED_OBSTICLES)
				i.intersect(self.hoik_list, TURN_SPEED_OBSTICLES)
	 		
			#using polimorphism to check the speed of the boids, and make sure they are not over the boundaries
			#Using polimorphism to move both hoiks and boids, and then drawing them.
			for i in self.all_things_to_draw:
				for u in i:
					u.check_speed()
					u.edges_boid()
					u.move_boid()
					u.draw_boid(self.screen)
					u.draw_vec_from_ball(self.screen, BLACK)

			#drawing obsticles
			for i in self.obsticle_list:
				i.draw_boid(self.screen)

			pygame.display.flip()

if __name__ == '__main__':
	my_game = Game()
	my_game.run()