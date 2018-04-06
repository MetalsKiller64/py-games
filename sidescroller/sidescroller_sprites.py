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
		self.level_pos = spawn_x
		self.floating = False
		self.float_direction = ""
		self.jump_block = False
		self.block_cycle = 0
		self.stop_x_movement = False
		self.exit_reached = False
	
	def draw(self, surface):
		self.rect = self.rect.clamp(surface.get_rect())
		surface.blit(self.image, self.rect)
	
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
			self.move("left")
		if pressed[pygame.K_RIGHT]:
			self.move("right")
	
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
		print ("x: "+str(self.rect.x))
		print ("level_pos: "+str(self.level_pos))
		if direction == "left":
			if self.stop_x_movement and not force:
				return
			self.rect.x -= speed
			self.level_pos -= speed
			hitbox.rect.x -= speed
			if self.rect.x <= 100 and self.level_pos >= 100:
				self.rect.x += speed
				self.level_pos += speed
				hitbox.rect.x += speed
				sprites.update("move", ["right", speed])
		elif direction == "right":
			if self.stop_x_movement and not force:
				return
			self.rect.x += speed
			self.level_pos += speed
			hitbox.rect.x += speed
			if self.rect.x >= 300 and self.level_pos <= (level_width - 100):
				self.rect.x -= speed
				self.level_pos -= speed
				hitbox.rect.x -= speed
				sprites.update("move", ["left", speed])
		elif direction == "up":
			self.rect.y -= speed
			hitbox.rect.y -= speed
		elif direction == "down":
			self.rect.y += speed
			hitbox.rect.y += speed

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
		print ("update")
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
	p.level_pos = spawn_x
	p.falling = True
	hitbox.rect.x = spawn_x
	hitbox.rect.y = spawn_y
	sprites.empty()
	exit, obstacles, objects, spawn, level_width, floaters = load_level("level")
	return exit, obstacles, objects, spawn, level_width, floaters

def load_level(name):
	f = open(name+".json")
	j = json.load(f)
	f.close()
	level_width = int(j["level_width"])
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
		float_min = int(ob[k][5])
		float_max = int(ob[k][6])
		direction = ob[k][7]
		y_min = int(ob[k][8])
		y_max = int(ob[k][9])
		if direction == "+":
			level_pos = float_min
		elif direction == "-":
			level_pos = float_max
		elif direction == "u" or direction == "d":
			level_pos = x
		sprite = sprite_object(x, y, w, h, (255, 107, 0))
		obstacles[k] = sprite
		objects[k] = sprite
		if floating:
			f = {"name": k,
			 "x_min": float_min, "x_max": float_max,
			 "y_min": y_min, "y_max": y_max,
			 "direction": direction, "level_pos": level_pos,
			 "level_pos_min": float_min, "level_pos_max": float_max}
			floaters[k] = f
	return exit, obstacles, objects, spawn, level_width, floaters

ending = False
font = pygame.font.SysFont("comicsansms", 30)
sprites = pygame.sprite.Group()
exit, obstacles, objects, spawn, level_width, floaters = load_level("level")
spawn_x = spawn[0]
spawn_y = spawn[1]
p = Player(spawn_x, spawn_y)
print (p.rect.x)
print (p.level_pos)
hitbox = sprite_object(spawn_x-1, spawn_y-1, 10,24, (0, 0, 0), True)

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
				p.stop_x_movement = True
				p.move("left", 1, force = True)
				if p.last_floor == None and not p.jumping:
					p.falling = True
			elif collided_part == "right":
				p.stop_x_movement = True
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
	
	## FIXME: verlassen eines vertical floaters wird der fall nicht richtig getriggert
	## während einer abwärtsbewegung "segelt" der player langsam nach unten
	## während einer aufwärtsbewegung hebt der spieler ab
	for name in floaters:
		f = floaters[name]
		obj = obstacles[name]
		if p.last_floor == obj:
			p.floating = True
			p.float_direction = f["direction"]
	
	print (p.floating)
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
		f_level_pos = f["level_pos"]
		f_level_pos_min = f["level_pos_min"]
		f_level_pos_max = f["level_pos_max"]
		direction = f["direction"]
		if direction == "+" and f_level_pos < f_level_pos_max:
			obj.move("right")
			f_level_pos += 1
		elif direction == "+":
			direction = "-"
		elif direction == "-" and f_level_pos > f_level_pos_min:
			obj.move("left")
			f_level_pos -= 1
		elif direction == "-":
			direction = "+"
		elif direction == "u" and y > y_min:
			obj.move("up")
			#print (direction)
		elif direction == "u":
			direction = "d"
			#print (direction)
		elif direction == "d" and y < y_max:
			obj.move("down")
			#print (direction)
		elif direction == "d":
			direction = "u"
			#print (direction)
		f["direction"] = direction
		f["level_pos"] = f_level_pos
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
			exit, obstacles, objects, spawn, level_width, floaters = respawn()
	
	if p.block_cycle >= 10:
		p.block_cycle = 0
		p.jump_block = False
	if p.jump_block:
		p.block_cycle += 1
	
	show_live_count()
	pygame.display.flip()
