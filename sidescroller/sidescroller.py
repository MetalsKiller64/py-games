import pygame, random, time, json, sys

level_name = "level"
if len(sys.argv) > 1:
	level_name = sys.argv[1]

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
		self.jump_cycle = 0
		self.last_floor = None
		self.lives = 2
		self.level_pos_x = spawn_x
		self.level_pos_y = spawn_y
		self.floating = False
		self.float_direction = ""
		self.jump_block = False
		self.block_cycle = 0
		self.stop_x_movement = False
		self.exit_reached = False
	
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
	
	def handle_key_event(self):
		pressed = pygame.key.get_pressed()
		if pressed[pygame.K_SPACE] and not self.jumping and not self.falling:
			if not self.jump_block:
				self.jump()
		if pressed[pygame.K_DOWN]:
			## TODO: ducken?
			pass
		if pressed[pygame.K_LEFT]:
			self.move("left", 2)
		if pressed[pygame.K_RIGHT]:
			self.move("right", 2)
	
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
		if direction == "+":
			self.move("right", 1)
		elif direction == "-":
			self.move("left", 1)
		elif direction == "u":
			self.move("up", 1)
		elif direction == "d":
			self.move("down", 1)

	def check_ground(self):
		if self.last_floor == None:
			self.falling = True
			self.floating = False
	
	def move(self, direction, speed = 1, force = False):
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
			self.rect.x -= speed
			self.level_pos_x -= speed
			hitbox.rect.x -= speed
			if self.rect.x <= 100 and self.level_pos_x >= 100:
				self.rect.x += speed
				#self.level_pos_x += speed
				hitbox.rect.x += speed
				sprites.update("move", ["right", speed])
		elif direction == "right":
			if self.stop_x_movement and not force:
				return
			self.rect.x += speed
			self.level_pos_x += speed
			hitbox.rect.x += speed
			if self.rect.x >= 300 and self.level_pos_x <= (level_width - 100):
				self.rect.x -= speed
				#self.level_pos_x -= speed
				hitbox.rect.x -= speed
				sprites.update("move", ["left", speed])
		elif direction == "up":
			self.rect.y -= speed
			self.level_pos_y -= speed
			hitbox.rect.y -= speed
			if self.rect.y <= 100 and self.level_pos_y >= 100:
				self.rect.y += speed
				#self.level_pos_y += speed
				hitbox.rect.y += speed
				sprites.update("move", ["down", speed])
		elif direction == "down":
			self.rect.y += speed
			self.level_pos_y += speed
			hitbox.rect.y += speed
			if self.rect.y >= 200 and self.level_pos_y <= (level_height - 100):
				self.rect.y -= speed
				#self.level_pos_y -= speed
				hitbox.rect.y -= speed
				sprites.update("move", ["up", speed])

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
	def __init__(self, x, y, width, height, color, invisible = False):
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
		if not invisible:
			sprites.add(self)
	
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
	p.rect.x = spawn_x
	p.rect.y = spawn_y
	p.level_pos_x = spawn_x
	p.level_pos_y = spawn_y
	p.falling = True
	hitbox.rect.x = spawn_x
	hitbox.rect.y = spawn_y
	sprites.empty()
	exit, obstacles, objects, spawn, level_width, level_height, floaters = load_level(level_name)
	return exit, obstacles, objects, spawn, level_width, level_height, floaters

def load_level(name):
	f = open(name+".json")
	j = json.load(f)
	f.close()
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
		x = int(ob[k][0])
		y = int(ob[k][1])
		w = int(ob[k][2])
		h = int(ob[k][3])
		floating = bool(int(ob[k][4]))
		float_x_min = int(ob[k][5])
		float_x_max = int(ob[k][6])
		direction = ob[k][7]
		float_y_min = int(ob[k][8])
		float_y_max = int(ob[k][9])
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
		sprite = sprite_object(x, y, w, h, (255, 107, 0))
		obstacles[k] = sprite
		objects[k] = sprite
		if floating:
			f = {"name": k,
			 "x_min": float_x_min, "x_max": float_x_max,
			 "y_min": float_y_min, "y_max": float_y_max,
			 "direction": direction, "level_pos_x": level_pos_x, "level_pos_y": level_pos_y,
			 "level_pos_x_min": float_x_min, "level_pos_x_max": float_x_max,
			 "level_pos_y_min": float_y_min, "level_pos_y_max": float_y_max}
			floaters[k] = f
	return exit, obstacles, objects, spawn, level_width, level_height, floaters

ending = False
font = pygame.font.SysFont("comicsansms", 30)
sprites = pygame.sprite.Group()
exit, obstacles, objects, spawn, level_width, level_height, floaters = load_level(level_name)
spawn_x = spawn[0]
spawn_y = spawn[1]
p = Player(spawn_x, spawn_y)
#print (p.rect.x)
print (p.level_pos_x)
print (p.level_pos_y)
#hitbox = sprite_object(spawn_x-1, spawn_y-1, 10,24, (0, 0, 0), True)
hitbox = hitbox_object(spawn_x-1, spawn_y-1, 9,22, (255, 255, 255))

while not done:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			done = True
	clock.tick(60)
	if ending:
		time.sleep(5)
		break
	screen.fill((0, 0, 0))
	sprites.draw(screen)
	p.draw(screen)
	
	l = pygame.sprite.spritecollide(hitbox, sprites, False)
	if l:
		collision = pygame.sprite.spritecollideany(p, l, pygame.sprite.collide_mask)
		while collision:
			## FIXME: wenn der spieler eine wand eines objektes berührt und versucht auf das objekt zu springen
			## wird durch die kollision mit der wand die horizontale bewegung abgebrochen (so kommt man nicht seitlich auf hindernisse)
			collided_part = check_collision(p, collision)
			print (collided_part)
			if collided_part == "top":
				p.falling = False
				p.floating = False
				p.last_floor = collision
				p.stop_x_movement = False
				p.move("up", 1)
			elif collided_part == "bottom":
				p.jumping = False
				p.falling = True
				p.move("down", 1)
			elif collided_part == "left":
				#if not p.jumping and not p.falling:
				#	p.stop_x_movement = True
				p.move("left", 1, force = True)
				if p.last_floor == None and not p.jumping:
					p.falling = True
			elif collided_part == "right":
				#if not p.jumping and not p.falling:
				#	p.stop_x_movement = True
				p.move("right", 1, force = True)
				if p.last_floor == None and not p.jumping:
					p.falling = True
			elif collided_part == "stop":
				p.stop_x_movement = True
				p.falling = True
			else:
				print ("fail")
			p.handle_phys()
			collision = pygame.sprite.spritecollideany(p, l, pygame.sprite.collide_mask)
	elif not p.falling and not p.jumping:
		p.last_floor = None
		p.floating = False
	
	for name in floaters:
		f = floaters[name]
		obj = obstacles[name]
		if p.last_floor == obj:
			p.floating = True
			p.float_direction = f["direction"]
	
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
		if direction == "+" and f_level_pos_x < f_level_pos_x_max:
			obj.move("right")
			f_level_pos_x += 1
		elif direction == "+":
			direction = "-"
		elif direction == "-" and f_level_pos_x > f_level_pos_x_min:
			obj.move("left")
			f_level_pos_x -= 1
		elif direction == "-":
			direction = "+"
		elif direction == "u" and f_level_pos_y > f_level_pos_y_min:
			obj.move("up")
			f_level_pos_y -= 1
			#print (direction)
		elif direction == "u":
			direction = "d"
			#print (direction)
		elif direction == "d" and f_level_pos_y < f_level_pos_y_max:
			obj.move("down")
			f_level_pos_y += 1
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

	if p.rect.y >= 280:
		if p.lives <= 0:
			show_gameover()
		else:
			p.lives -= 1
			exit, obstacles, objects, spawn, level_width, level_height, floaters = respawn()
	
	if p.block_cycle >= 10:
		p.block_cycle = 0
		p.jump_block = False
	if p.jump_block:
		p.block_cycle += 1
	
	show_live_count()
	pygame.display.flip()
