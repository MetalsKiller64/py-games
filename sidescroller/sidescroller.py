import pygame, random, time, json

pygame.init()
screen = pygame.display.set_mode((400, 300))
clock = pygame.time.Clock()
done = False
x = 10
y = 260

jumping = False
falling = False
jump_cycle = 0
floor = ""

class Player():
	def __init__(self):
		self.p_rect = pygame.Rect(10, 250, 7, 20)
		self.p_height = 20
		self.falling = True
		self.jumping = False
		self.jump_cycle = 0
		self.last_floor = None
		self.lives = 2
		self.level_pos = 10
		self.floating = False
		self.floater = None
		self.jump_block = False
		self.block_cycle = 0
		self.exit_reached = False
	
	def jump(self):
		self.floating = False
		self.floater = None
		self.jumping = True
		self.jump_block = True
		if self.jump_cycle < 15:
			for name in obstacles:
				o = obstacles[name]
				if self.p_rect.colliderect(o):
					self.jumping = False
					self.falling = True
					self.jump_cycle = 0
					return
			self.p_rect.y -= 4
		else:
			self.jumping = False
			self.falling = True
			self.jump_cycle = 0
			return
		self.jump_cycle += 1
		if self.p_rect.colliderect(exit):
			self.exit_reached = True
	
	def fall(self):
		self.p_rect.y += 4
		for name in obstacles:
			obstacle = obstacles[name]
			if self.p_rect.colliderect(obstacle):
				self.falling = False
				self.p_rect.y = obstacle.y - self.p_height
				self.last_floor = obstacle
				if name in floaters:
					self.floating = True
					self.floater = name
				return
		if self.p_rect.colliderect(exit):
			self.exit_reached = True
	
	def float(self):
		f = floaters[self.floater]
		direction = f["direction"]
		if direction == "+":
			#self.p_rect.x += 1
			self.move("right", 2)
		else:
			#self.p_rect.x -= 1
			self.move("left", 2)
		if self.p_rect.colliderect(exit):
			self.exit_reached = True

	def check_ground(self):
		last_floor = None
		for name in obstacles:
			o = obstacles[name]
			if self.p_rect.colliderect(o):
				last_floor = o
		if last_floor == None:
			self.falling = True
			self.floating = False
		else:
			self.last_floor = last_floor
		if self.p_rect.colliderect(exit):
			self.exit_reached = True
	
	def move(self, direction, speed = 2):
		self.floating = False
		self.floater = None
		if direction == "left":
			if self.p_rect.x <= 100 and self.level_pos >= 100:
				for name in objects:
					o = objects[name]
					cx = o.x
					o.x = cx + speed
				self.p_rect.x = 100
				self.level_pos -= speed
				for name in obstacles:
					obstacle = obstacles[name]
					if self.p_rect.colliderect(obstacle):
						for n in objects:
							o = objects[n]
							cx = o.x
							o.x = cx - speed
						self.p_rect.x = 100
						self.level_pos += speed
			else:
				self.p_rect.x -= speed
				self.level_pos -= speed
				for name in obstacles:
					obstacle = obstacles[name]
					if self.p_rect.colliderect(obstacle):
						self.p_rect.x += speed
						self.level_pos += speed
		elif direction == "right":
			if self.p_rect.x >= 300 and self.level_pos <= (level_width - 100):
				for name in objects:
					o = objects[name]
					cx = o.x
					o.x = cx - speed
				self.p_rect.x = 300
				self.level_pos += speed
				for name in obstacles:
					obstacle = obstacles[name]
					if self.p_rect.colliderect(obstacle):
						for n in objects:
							o = objects[n]
							cx = o.x
							o.x = cx + speed
						self.p_rect.x = 300
						self.level_pos -= speed
			else:
				self.p_rect.x += speed
				self.level_pos += speed
				for name in obstacles:
					obstacle = obstacles[name]
					if self.p_rect.colliderect(obstacle):
						self.p_rect.x -= speed
						self.level_pos -= speed
		if self.last_floor:
			if not self.p_rect.colliderect(self.last_floor):
				self.falling = True
		if self.p_rect.colliderect(exit):
			self.exit_reached = True


def show_end():
	screen.fill((0,0,0))
	text = font.render("Ende", True, (0, 128, 0))
	screen.blit(text, (200 - text.get_width() // 2, 150 - text.get_height() // 2))

def show_gameover():
	screen.fill((0,0,0))
	text = font.render("Game Over", True, (128, 0, 0))
	screen.blit(text, (200 - text.get_width() // 2, 150 - text.get_height() // 2))

def show_live_count():
	text = font.render("Leben: "+str(p.lives), True, (0, 128, 0))
	screen.blit(text, (50 - text.get_width() // 2, 10 - text.get_height() // 2))

def respawn():
	p.p_rect.x = 10
	p.p_rect.y = 250
	p.level_pos = 10
	p.falling = True
	exit, obstacles, objects, level_width, floaters = load_level("level")
	return exit, obstacles, objects, level_width, floaters

def load_level(name):
	f = open(name+".json")
	j = json.load(f)
	f.close()
	level_width = j["level_width"]
	e = j["exit"]
	exit = pygame.Rect(int(e[0]), int(e[1]), int(e[2]), int(e[3]))
	obstacles = {}
	objects = {"exit": exit}
	floaters = {}
	ob = j["obstacles"]
	for k in ob:
		x = int(ob[k][0])
		y = int(ob[k][1])
		w = int(ob[k][2])
		h = int(ob[k][3])
		floating = bool(int(ob[k][4]))
		float_min = int(ob[k][5])
		float_max = int(ob[k][6])
		direction = ob[k][7]
		if direction == "+":
			level_pos = float_min
		else:
			level_pos = float_max
		rect = pygame.Rect(x, y, w, h)
		obstacles[k] = rect
		objects[k] = rect
		if floating:
			f = {"name": k,
			 "min": float_min, "max": float_max,
			 "direction": direction, "level_pos": level_pos,
			 "level_pos_min": float_min, "level_pos_max": float_max}
			floaters[k] = f
	return exit, obstacles, objects, level_width, floaters

ending = False
font = pygame.font.SysFont("comicsansms", 30)
exit, obstacles, objects, level_width, floaters = load_level("level")
p = Player()

while not done:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			done = True
	clock.tick(60)
	if ending:
		time.sleep(5)
		break
	screen.fill((0, 0, 0))
	for ob in obstacles:
		o = obstacles[ob]
		pygame.draw.rect(screen, (255, 107, 0), o)
	
	for obj in floaters:
		o = floaters[obj]
		f = obstacles[o["name"]]
		f_min = o["min"]
		f_max = o["max"]
		f_level_pos = o["level_pos"]
		f_level_pos_min = o["level_pos_min"]
		f_level_pos_max = o["level_pos_max"]
		direction = o["direction"]
		if direction == "+" and f_level_pos < f_level_pos_max:
			f.x += 1
			f_level_pos += 1
		elif direction == "+":
			direction = "-"
		elif direction == "-" and f_level_pos > f_level_pos_min:
			f.x -= 1
			f_level_pos -= 1
		elif direction == "-":
			direction = "+"
		o["direction"] = direction
		o["level_pos"] = f_level_pos
		floaters[obj] = o
	
	pressed = pygame.key.get_pressed()
	if pressed[pygame.K_SPACE] and not p.jumping and not p.falling:
		if not p.jump_block:
			p.jump()
	if pressed[pygame.K_DOWN]:
		pass
	if pressed[pygame.K_LEFT]:
		p.move("left")
	if pressed[pygame.K_RIGHT]:
		p.move("right")
	
	if p.p_rect.colliderect(exit):
		p.exit_reached = True
	
	if p.exit_reached:
		show_end()
		ending = True

	if p.p_rect.y >= 300:
		print (p.lives)
		if p.lives <= 0:
			show_gameover()
		else:
			p.lives -= 1
			exit, obstacles, objects, level_width, floaters = respawn()
	if p.jumping:
		p.jump()
	elif p.falling:
		p.fall()
	elif p.floating:
		p.float()
	else:
		p.check_ground()
	if p.block_cycle >= 10:
		p.block_cycle = 0
		p.jump_block = False
	if p.jump_block:
		p.block_cycle += 1
	pygame.draw.rect(screen, (255, 7, 0), p.p_rect)
	pygame.draw.rect(screen, (138, 206, 255), exit)
	show_live_count()
	pygame.display.flip()
