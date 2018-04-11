import pygame, random, time, json, sys

level_name = "level.json"
if len(sys.argv) > 1:
	filename = sys.argv[1]
	if filename.endswith(".json"):
		level_name = filename
	else:
		level_name = filename+".json"

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

class Player(pygame.sprite.Sprite):
	def __init__(self, spawn_x, spawn_y):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.Surface([7, 20])
		self.image.fill((255, 7, 0))

		self.rect = self.image.get_rect()
		self.rect.x = spawn_x
		self.rect.y = spawn_y
		self.mask = pygame.mask.from_surface(self.image)
		self.mask.fill()
		
		self.p_height = 20
		self.falling = True
		self.jumping = False
		self.speed = {"left": 0, "right": 0}
		self.speed_max = 3
		self.sprint_max = 6
		self.sprinting = False
		self.colliding = {"left": False, "right": False, "top": False, "bottom": False}
		self.frame = 0
		self.speed_rate = 5
		self.jump_cycle = 0
		self.last_floor = None
		self.lives = 2
		self.level_pos_x = spawn_x
		self.level_pos_y = spawn_y
		self.floating = False
		self.float_direction = ""
		self.floating_speed = 0
		self.jump_block = False
		self.block_cycle = 0
		self.stop_x_movement = False
		self.exit_reached = False
		self.dead = False
	
	def draw(self, surface):
		pygame.draw.rect(surface, (255, 7, 0), self.rect)
	
	def handle_phys(self):
		if self.jumping:
			self.jump()
		elif self.falling:
			self.fall()
		elif self.floating:
			self.float()
		else:
			self.check_ground()
		pressed = pygame.key.get_pressed()
		if not self.sprinting:
			for direction in self.speed:
				if self.speed[direction] > 3:
					self.speed[direction] -= 1
		if not pressed[pygame.K_LEFT] and not pressed[pygame.K_RIGHT] and self.frame < self.speed_rate:
			for direction in self.speed:
				if self.speed[direction] > 0:
					self.speed[direction] -= 1
	
	def handle_key_event(self):
		pressed = pygame.key.get_pressed()
		speed_max = self.speed_max
		self.sprinting = False
		#if (pressed[pygame.K_LSHIFT] or pressed[pygame.K_RSHIFT]) and (not self.jumping and not self.falling):
		if pressed[pygame.K_LSHIFT] or pressed[pygame.K_RSHIFT]:
			print ("shift")
			self.sprinting = True
			speed_max = self.sprint_max

		if pressed[pygame.K_SPACE] and not self.jumping and not self.falling:
			if not self.jump_block:
				self.jump()
		if pressed[pygame.K_DOWN]:
			## TODO: ducken?
			pass
		if pressed[pygame.K_LEFT]:
			if self.colliding["left"]:
				self.speed["left"] = 0
				return
			if self.frame >= self.speed_rate:
				if self.speed["left"] < speed_max:
					self.speed["left"] += 1
					if self.speed["right"] > 0:
						self.speed["right"] -= 1
				self.frame = 0
			self.move("left")
		elif pressed[pygame.K_RIGHT]:
			if self.colliding["right"]:
				self.speed["right"] = 0
				return
			if self.frame >= self.speed_rate:
				if self.speed["right"] < speed_max:
					self.speed["right"] += 1
					if self.speed["left"] > 0:
						self.speed["left"] -= 1
				self.frame = 0
			self.move("right")
		else:
			if self.speed["left"] > 0:
				self.speed["left"] -= 1
			if self.speed["right"] > 0:
				self.speed["right"] -= 1
	
	def jump(self):
		self.floating = False
		#self.floater = None
		self.jumping = True
		self.jump_block = True
		self.last_floor = None
		if self.jump_cycle < 15:
			self.move("up", 4)
		else:
			self.jumping = False
			self.falling = True
			self.jump_cycle = 0
			return
		self.jump_cycle += 1
	
	def fall(self):
		self.move("down", 4)
	
	def float(self):
		direction = self.float_direction
		speed = self.floating_speed
		if direction == "+":
			self.move("right", speed)
		elif direction == "-":
			self.move("left", speed)
		elif direction == "u":
			self.move("up", speed)
		elif direction == "d":
			self.move("down", speed)

	def check_ground(self):
		if self.last_floor == None:
			self.falling = True
			self.floating = False
	
	def move(self, direction, speed = None, force = False):
		#print ("move "+direction)
		#print ("x: "+str(self.rect.x))
		#print ("level_pos_x: "+str(self.level_pos_x))
		#print ("y: "+str(self.rect.y))
		#print ("hy: "+str(hitbox.rect.y))
		#print ("level_pos_y: "+str(self.level_pos_y))
		#print ("lh: "+str(level_height -100))
		if direction == "left":
			if self.stop_x_movement and not force:
				return
			if speed == None:
				speed = self.speed["left"]
			self.rect.x -= speed
			self.level_pos_x -= speed
			hitbox.rect.x -= speed
			if self.rect.x <= 100 and self.level_pos_x >= 100:
				self.rect.x += speed
				#self.level_pos_x += speed
				hitbox.rect.x += speed
				sprites.update("move", ["right", speed])
				death_zones.update("move", ["right", speed])
		elif direction == "right":
			if self.stop_x_movement and not force:
				return
			if speed == None:
				speed = self.speed["right"]
			self.rect.x += speed
			self.level_pos_x += speed
			hitbox.rect.x += speed
			if self.rect.x >= 300 and self.level_pos_x <= (level_width - 100):
				self.rect.x -= speed
				#self.level_pos_x -= speed
				hitbox.rect.x -= speed
				sprites.update("move", ["left", speed])
				death_zones.update("move", ["left", speed])
		elif direction == "up":
			self.rect.y -= speed
			self.level_pos_y -= speed
			hitbox.rect.y -= speed
			if self.rect.y <= 100 and self.level_pos_y >= 100:
				self.rect.y += speed
				#self.level_pos_y += speed
				hitbox.rect.y += speed
				sprites.update("move", ["down", speed])
				death_zones.update("move", ["down", speed])
		elif direction == "down":
			self.rect.y += speed
			self.level_pos_y += speed
			hitbox.rect.y += speed
			if self.rect.y >= 200 and self.level_pos_y <= (level_height - 100):
				self.rect.y -= speed
				#self.level_pos_y -= speed
				hitbox.rect.y -= speed
				sprites.update("move", ["up", speed])
				death_zones.update("move", ["up", speed])

class hitbox_object(pygame.sprite.Sprite):
	def __init__(self, x, y, width, height, color):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.Surface([width, height])
		self.image.fill(color)
		self.color = color

		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		self.rect.width = width
		self.rect.height = height
		self.mask = pygame.mask.from_surface(self.image)
		self.mask.fill()
	
	def draw(self, surface):
		pygame.draw.rect(surface, self.color, self.rect)


class sprite_object(pygame.sprite.Sprite):
	def __init__(self, x, y, width, height, color):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.Surface([width, height])
		self.image.fill(color)

		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		self.rect.width = width
		self.rect.height = height
		self.mask = pygame.mask.from_surface(self.image)
		self.mask.fill()
	
	def update(self, action = "none", args = []):
		if action == "move":
			direction, speed = args
			self.move(direction, speed)
	
	def move(self, direction, speed = 1):
		if direction == "up":
			self.rect.y -= speed
		elif direction == "down":
			self.rect.y += speed
		elif direction == "left":
			self.rect.x -= speed
		elif direction == "right":
			self.rect.x += speed


def check_collision(a, b):
	mask_a = a.mask
	mask_b = b.mask
	ax = a.rect.x
	ay = a.rect.y
	bx = b.rect.x
	by = b.rect.y
	
	offset_high_1 = [bx-ax+1, by-ay]
	offset_low_1 = [bx-ax-1, by-ay]
	offset_high_2 = [bx-ax, by-ay+1]
	offset_low_2 = [bx-ax, by-ay-1]
	
	diff_x = mask_a.overlap_area(mask_b, offset_high_1) - mask_a.overlap_area(mask_b, offset_low_1)
	diff_y = mask_a.overlap_area(mask_b, offset_high_2) - mask_a.overlap_area(mask_b, offset_low_2)
	
	abs_diff_x = abs(diff_x)
	abs_diff_y = abs(diff_y)
	
	if abs_diff_x > abs_diff_y:
		if diff_x > 0:
			print ("r")
			return "right"
		else:
			print ("l")
			return "left"
	elif abs_diff_y > abs_diff_x:
		if diff_y > 0:
			print ("b")
			return "bottom"
		else:
			print ("t")
			return "top"
	else:
		return "stop"


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
	gameover = False
	p.lives -= 1
	if p.lives < 0:
		gameover = True
	p.rect.x = spawn_x
	p.rect.y = spawn_y
	p.level_pos_x = spawn_x
	p.level_pos_y = spawn_y
	p.falling = True
	p.floating = False
	p.jumping = False
	hitbox.rect.x = spawn_x -1 
	hitbox.rect.y = spawn_y -1
	sprites.empty()
	exit, obstacles, objects, spawn, level_width, level_height, floaters = load_level(level_name)
	return exit, obstacles, objects, spawn, level_width, level_height, floaters

def load_json(filename):
	f = open(filename)
	j = json.load(f)
	f.close()
	return j

def load_level(level_file):
	j = load_json(level_file)
	level_width = int(j["level_width"])
	level_height = int(j["level_height"])
	s = j["spawn"]
	spawn = [int(s[0]), int(s[1])]
	e = j["exit"]
	exit = sprite_object(int(e[0]), int(e[1]), int(e[2]), int(e[3]), (138, 206, 255))
	obstacles = {}
	objects = {"exit": exit}
	floaters = {}
	ob = j["obstacles"]
	for k in ob:
		obj = ob[k]
		x = int(obj[0])
		y = int(obj[1])
		w = int(obj[2])
		h = int(obj[3])
		floating = bool(int(obj[4]))
		float_x_min = int(obj[5])
		float_x_max = int(obj[6])
		direction = obj[7]
		float_y_min = int(obj[8])
		float_y_max = int(obj[9])
		try:
			color_rgb = obj[10]
			color = (color_rgb[0], color_rgb[1], color_rgb[2])
		except IndexError:
			color = (255, 107, 0)
		try:
			float_speed = int(obj[11])
		except IndexError:
			float_speed = 1
		if direction == "+":
			level_pos_x = float_x_min
			level_pos_y = y
		elif direction == "-":
			level_pos_x = float_x_max
			level_pos_y = y
		elif direction == "u":
			level_pos_x = x
			level_pos_y = float_y_max
		elif direction == "d":
			level_pos_x = x
			level_pos_y = float_y_min
		sprite = sprite_object(x, y, w, h, color)
		sprites.add(sprite)
		obstacles[k] = sprite
		objects[k] = sprite
		if floating:
			f = {"name": k,
			 "x_min": float_x_min, "x_max": float_x_max,
			 "y_min": float_y_min, "y_max": float_y_max,
			 "direction": direction, "level_pos_x": level_pos_x, "level_pos_y": level_pos_y,
			 "level_pos_x_min": float_x_min, "level_pos_x_max": float_x_max,
			 "level_pos_y_min": float_y_min, "level_pos_y_max": float_y_max,
			 "speed": float_speed}
			floaters[k] = f
	
	dzones = j["death_zones"]
	for key in dzones:
		obj = dzones[key]
		x = int(obj[0])
		y = int(obj[1])
		w = int(obj[2])
		h = int(obj[3])
		try:
			color_rgb = obj[4]
			color = (color_rgb[0], color_rgb[1], color_rgb[2])
		except IndexError:
			color = (255, 107, 0)
		sprite = sprite_object(key, x, y, w, h, color, group=death_zones)
	return exit, obstacles, objects, spawn, level_width, level_height, floaters

ending = False
gameover = False
font = pygame.font.SysFont("comicsansms", 30)
sprites = pygame.sprite.Group()
death_zones = pygame.sprite.Group()
exit, obstacles, objects, spawn, level_width, level_height, floaters = load_level(level_name)
spawn_x = spawn[0]
spawn_y = spawn[1]
p = Player(spawn_x, spawn_y)
#print (p.rect.x)
print (p.level_pos_x)
print (p.level_pos_y)
#hitbox = sprite_object(spawn_x-1, spawn_y-1, 10,24, (0, 0, 0), True)
hitbox = hitbox_object(spawn_x-1, spawn_y-1, 9,22, (255, 255, 255))
dpass = 0

while not done:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			done = True
	clock.tick(60)
	#print (str(clock.get_fps()))
	if p.dead:
		if dpass < 30:
			dpass += 1
			continue
		dpass = 0
		p.dead = False
		exit, obstacles, objects, spawn, level_width, level_height, floaters, gameover = respawn()
	if ending:
		show_end()
		pygame.display.flip()
		continue
	if gameover:
		show_gameover()
		pygame.display.flip()
		continue
	screen.fill((0, 0, 0))
	sprites.draw(screen)
	death_zones.draw(screen)
	p.draw(screen)
	if p.frame >= p.speed_rate:
		p.frame = 0
	else:
		p.frame += 1
	print (p.speed)
	
	p.colliding["right"] = False
	p.colliding["left"] = False
	p.colliding["top"] = False
	p.colliding["bottom"] = False
	l = pygame.sprite.spritecollide(hitbox, sprites, False)
	d = pygame.sprite.spritecollide(hitbox, death_zones, False)
	#print (l)
	recent_collisions = []
	if l or d:
		if d:
			collision = pygame.sprite.spritecollideany(p, d, pygame.sprite.collide_mask)
			if collision:
				p.dead = True
		else:
			collision = pygame.sprite.spritecollideany(p, l, pygame.sprite.collide_mask)
			while collision:
				collided_part = check_collision(p, collision)
				if collided_part == "top":
					if recent_collisions.count("bottom") >= 50:
						p.dead = True
					p.falling = False
					p.floating = False
					p.last_floor = collision
					p.stop_x_movement = False
					p.move("up", 1)
				elif collided_part == "bottom":
					if recent_collisions.count("top") >= 50:
						p.dead = True
					p.jumping = False
					p.falling = True
					p.move("down", 1)
				elif collided_part == "left":
					#if not p.jumping and not p.falling:
					#	p.stop_x_movement = True
					if p.floating:
						p.move("left", p.floating_speed, force = True)
						continue
					p.move("left", 1, force = True)
					p.speed["left"] = 0
					p.colliding["right"] = True
					if p.last_floor == None and not p.jumping:
						p.falling = True
				elif collided_part == "right":
					#if not p.jumping and not p.falling:
					#	p.stop_x_movement = True
					if p.floating:
						p.move("right", p.floating_speed, force = True)
						continue
					p.move("right", 1, force = True)
					p.speed["right"] = 0
					p.colliding["left"] = True
					if p.last_floor == None and not p.jumping:
						p.falling = True
				elif collided_part == "stop":
					p.stop_x_movement = True
					p.falling = True
				else:
					print ("fail")
				p.handle_phys()
				collision = pygame.sprite.spritecollideany(p, l, pygame.sprite.collide_mask)
				recent_collisions.append(collided_part)
	elif not p.falling and not p.jumping:
		p.last_floor = None
		p.floating = False
		p.colliding["right"] = False
		p.colliding["left"] = False
		p.colliding["top"] = False
		p.colliding["bottom"] = False
	
	for name in floaters:
		f = floaters[name]
		obj = obstacles[name]
		if p.last_floor == obj:
			p.floating = True
			p.float_direction = f["direction"]
			p.floating_speed = f["speed"]
	
	#print (p.falling)
	#print (p.floating)
	#print (p.jumping)
	p.handle_key_event()
	p.handle_phys()
	
	for name in floaters:
		f = floaters[name]
		obj = obstacles[name]
		rect = obj.rect
		y = rect.y;
		x_min = f["x_min"]
		x_max = f["x_max"]
		y_min = f["y_min"]
		y_max = f["y_max"]
		f_level_pos_x = f["level_pos_x"]
		f_level_pos_x_min = f["level_pos_x_min"]
		f_level_pos_x_max = f["level_pos_x_max"]
		f_level_pos_y = f["level_pos_y"]
		f_level_pos_y_min = f["level_pos_y_min"]
		f_level_pos_y_max = f["level_pos_y_max"]
		direction = f["direction"]
		speed = f["speed"]
		if direction == "+" and f_level_pos_x < f_level_pos_x_max:
			obj.move("right", speed)
			f_level_pos_x += speed
		elif direction == "+":
			direction = "-"
		elif direction == "-" and f_level_pos_x > f_level_pos_x_min:
			obj.move("left", speed)
			f_level_pos_x -= speed
		elif direction == "-":
			direction = "+"
		elif direction == "u" and f_level_pos_y > f_level_pos_y_min:
			obj.move("up", speed)
			f_level_pos_y -= speed
			#print (direction)
		elif direction == "u":
			direction = "d"
			#print (direction)
		elif direction == "d" and f_level_pos_y < f_level_pos_y_max:
			obj.move("down", speed)
			f_level_pos_y += speed
			#print (direction)
		elif direction == "d":
			direction = "u"
			#print (direction)
		f["direction"] = direction
		f["level_pos_x"] = f_level_pos_x
		f["level_pos_y"] = f_level_pos_y
		floaters[name] = f
	
	if p.rect.colliderect(exit):
		p.exit_reached = True
	
	if p.exit_reached:
		show_end()
		ending = True

	if p.rect.y >= 300:
		p.dead = True
		#respawn()
	
	if p.block_cycle >= 10:
		p.block_cycle = 0
		p.jump_block = False
	if p.jump_block:
		p.block_cycle += 1
	
	show_live_count()
	pygame.display.flip()
