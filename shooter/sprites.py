import pygame, random, datetime

class player_object(pygame.sprite.Sprite):
	def __init__(self, spawn_x, spawn_y, width, height, screen_width, screen_height, color = (255, 7, 0)):
		pygame.sprite.Sprite.__init__(self)
		#self.image = pygame.Surface([width, height])
		self.image = pygame.image.load("img/weelchair_zombie.png")
		#self.image.fill(color)
		self.color = color

		self.rect = self.image.get_rect()
		self.height = self.image.get_height()
		self.width = self.image.get_width()
		self.rect.x = spawn_x
		self.rect.y = spawn_y
		self.mask = pygame.mask.from_surface(self.image)
		self.mask.fill()

		self.hitbox = hitbox_object(self.rect)

		self.screen_width = screen_width
		self.screen_height = screen_height
		self.p_height = height
		self.shoot_button_pressed = False
		self.speed = {"left": 0, "right": 0, "down": 0, "up": 0}
		self.relative_speed = {"left": 0, "right": 0, "down": 0, "up": 0}
		self.speed_max = 3
		self.colliding = {"left": False, "right": False, "top": False, "bottom": False}
		self.accel_frame = 0
		self.accel_rate = 10
		self.decel_rate = 5
		self.decel_frame = 0
		self.lives = 4
		self.enemies_destroyed = 0
		self.enemy_kills = 0
		self.level_pos_x = spawn_x
		self.level_pos_y = spawn_y
		self.dead = False
		self.move_left = False
		self.move_right	= False
		self.move_up	= False
		self.move_down	= False
		self.face_direction = "right"
		self.last_projectile_fired = datetime.datetime.now()
		self.fire_rate = 250000
		self.respawning = False
		self.last_death = None
		self.weapon = "normal"

	def shoot(self, projectile_sprites):
		now = datetime.datetime.now()
		ptd = now - self.last_projectile_fired
		if ptd.microseconds < self.fire_rate:
			return
		self.last_projectile_fired = now
		y_center = self.rect.y + (self.height / 2)
		if self.weapon == "spread":
			p1 = projectile(self.face_direction, self.rect.x, y_center, diagonal = "u")
			p2 = projectile(self.face_direction, self.rect.x, y_center)
			p3 = projectile(self.face_direction, self.rect.x, y_center, diagonal = "d")
			projectile_sprites.add([p1, p2, p3])
		elif self.weapon == "laser":
			p = projectile(self.face_direction, self.rect.x, y_center, 20, 4, 4, 7)
			projectile_sprites.add(p)
		else:
			p = projectile(self.face_direction, self.rect.x, y_center)
			projectile_sprites.add(p)

	def move(self, direction, hitbox, speed = None, use_relative = True):
		screen_width = self.screen_width
		screen_height = self.screen_height
		scroll_horizontal = 45 / 100 * screen_width
		scroll_vertical = 45 / 100 * screen_height
		if direction == "left":
			if self.face_direction == "right":
				self.image = pygame.transform.flip(self.image, True, False)
			self.face_direction = "left"
			#if speed == None:
			#	speed = self.speed["left"]
			new_x = self.rect.x - speed
			#speed, collision_object = self.check_path("left", speed, [new_x, self.rect.y], hitbox)
			#self.speed[direction] = speed
			#if use_relative:
			#	self.relative_speed[direction] = speed
			self.rect.x -= speed
			self.level_pos_x -= speed
			hitbox.rect.x -= speed
			#self.check_ground()
			"""if self.rect.x <= scroll_horizontal and self.level_pos_x >= scroll_horizontal:
				self.rect.x += speed
				hitbox.rect.x += speed
				all_sprites.update("move", ["right", hitbox, speed])"""
		elif direction == "right":
			if speed == None:
				speed = self.speed["right"]

			if self.face_direction == "left":
				self.image = pygame.transform.flip(self.image, True, False)
			self.face_direction = "right"
			new_x = self.rect.x + speed
			#speed, collision_object = self.check_path("right", speed, [new_x, self.rect.y], hitbox)
			self.speed[direction] = speed
			self.rect.x += speed
			self.level_pos_x += speed
			hitbox.rect.x += speed
			#self.check_ground()
			#if self.rect.x >= (screen_width - scroll_horizontal) and self.level_pos_x <= (level_width - scroll_horizontal):
			#	self.rect.x -= speed
			#	hitbox.rect.x -= speed
			#	all_sprites.update("move", ["left", hitbox, speed])
		elif direction == "up":
			if speed == None:
				speed = self.speed["up"]
			new_y = self.rect.y - speed
			#speed, collision_object = self.check_path("up", speed, [self.rect.x, new_y], hitbox)
			self.rect.y -= speed
			self.level_pos_y -= speed
			hitbox.rect.y -= speed
			#self.check_ground()
			#if self.rect.y <= scroll_vertical and self.level_pos_y <= level_height:
			#	self.rect.y += speed
			#	hitbox.rect.y += speed
			#	all_sprites.update("move", ["down", hitbox, speed])
		elif direction == "down":
			if speed == None:
				speed = self.speed["down"]
			new_y = self.rect.y + speed
			#speed, collision_object = self.check_path("down", speed, [self.rect.x, new_y], hitbox)
			self.rect.y += speed
			self.level_pos_y += speed
			hitbox.rect.y += speed
			#self.check_ground()
			#if self.rect.y >= (screen_height - scroll_vertical) and self.level_pos_y <= (level_height - scroll_vertical):
			#	self.rect.y -= speed
			#	hitbox.rect.y -= speed
			#	all_sprites.update("move", ["up", hitbox, speed])

	def check_path(self, direction, speed, new_position, hitbox):
		current_x = self.rect.x
		current_y = self.rect.y
		new_x = new_position[0]
		new_y = new_position[1]
		h_x = hitbox.rect.x
		h_y = hitbox.rect.y
		## FIXME: add an array of elements currently on the screen to check only those for collision
		if direction == "left":
			for x in reversed(range(new_x, current_x)):
				hitbox.rect.x = h_x
				x_diff = current_x - x
				hitbox.rect.x -= x_diff
				#colliding_objects = pygame.sprite.spritecollide(hitbox, sprites, pygame.sprite.collide_mask)
				for o in all_sprites:
					collision = pygame.sprite.spritecollideany(hitbox, [o], pygame.sprite.collide_mask)
					print (collision)
					if collision:
						collided_part = check_collision(hitbox, collision)
						#print (collided_part)
						if collided_part == "right":
							hitbox.rect.x = h_x
							self.colliding["left"] = True
							if self.last_floor == None and not self.jumping:
								self.falling = True
								self.jump_cycle = 0
							if p.floating:
								return [0, collision]
							if x_diff == 1:
								x_diff = 0
							return [x_diff, collision]
		elif direction == "right":
			for x in range(current_x, new_x):
				hitbox.rect.x = h_x
				x_diff = x - current_x
				hitbox.rect.x += x_diff
				#colliding_objects = pygame.sprite.spritecollide(hitbox, sprites, pygame.sprite.collide_mask)
				for o in all_sprites:
					collision = pygame.sprite.spritecollideany(hitbox, [o], pygame.sprite.collide_mask)
					if collision:
						collided_part = check_collision(hitbox, collision)
						#print (collided_part)
						if collided_part == "left":
							hitbox.rect.x = h_x
							self.colliding["right"] = True
							if self.last_floor == None and not self.jumping:
								self.falling = True
								self.jump_cycle = 0
							if p.floating:
								return [0, collision]
							if x_diff == 1:
								x_diff = 0
							return [x_diff, collision]
		elif direction == "up":
			#self.colliding["top"] = True
			for y in reversed(range(new_y, current_y)):
				hitbox.rect.y = h_y
				y_diff = current_y - y
				hitbox.rect.y -= y_diff
				#colliding_objects = pygame.sprite.spritecollide(hitbox, sprites, pygame.sprite.collide_mask)
				for o in all_sprites:
					collision = pygame.sprite.spritecollideany(hitbox, [o], pygame.sprite.collide_mask)
					if collision:
						collided_part = check_collision(hitbox, collision)
						if collided_part == "bottom":
							hitbox.rect.y = h_y
							self.colliding["top"] = True
							self.jumping = False
							if p.floating:
								return [0, collision]
							return [y_diff, collision]
		elif direction == "down":
			#self.colliding["bottom"] = True
			for y in range(current_y, new_y):
				hitbox.rect.y = h_y
				y_diff = y - current_y
				hitbox.rect.y += y_diff
				#colliding_objects = pygame.sprite.spritecollide(hitbox, sprites, pygame.sprite.collide_mask)
				for o in all_sprites:
					collision = pygame.sprite.spritecollideany(hitbox, [o], pygame.sprite.collide_mask)
					if collision:
						#print ("collision: "+str(collision))
						collided_part = check_collision(hitbox, collision)
						if collided_part == "top" or collided_part == "stop":
							hitbox.rect.y = h_y
							self.colliding["bottom"] = True
							self.falling = False
							self.last_floor = collision
							return [y_diff, collision]
		hitbox.rect.x = h_x
		hitbox.rect.y = h_y
		return [speed, None]

	def destroy(self):
		self.lives -= 1
		self.weapon = "normal"
		self.fire_rate = 250000
		self.respawning = True
		self.last_death = datetime.datetime.now()
		self.rect.x = 200
		self.rect.y = 200
		self.hitbox.rect.x = 200
		self.hitbox.rect.y = 200

	def draw(self, surface):
		#print (self.color)
		#pygame.draw.rect(surface, self.color, self.rect)
		surface.blit(self.image, self.rect)


class hitbox_object(pygame.sprite.Sprite):
	def __init__(self, parent_rect, color = (255, 255, 255)):
		pygame.sprite.Sprite.__init__(self)
		x = parent_rect.x
		y = parent_rect.y
		width = parent_rect.width
		height = parent_rect.height
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

class status_bar(pygame.sprite.Sprite):
	def __init__(self, x, y, width, height, color = (173, 161, 211)):
		pygame.sprite.Sprite.__init__(self)
		self.y = y
		self.x = x
		self.width = width
		self.height = height
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

	def update_status(self, player, screen, font):
		self.image.fill(self.color)
		x = 70
		y = 5
		text = font.render("lives:", True, (0, 0, 0))
		self.image.blit(text, (30 - text.get_width() // 2, 10 - text.get_height() // 2))
		for i in range(player.lives):
			l = live_count_block(x, y, 10, 10)
			x += 12
			l.draw(self.image)
		text = font.render("weapon: "+str(player.weapon), True, (0, 0, 0))
		self.image.blit(text, (200 - text.get_width() // 2, 10 - text.get_height() // 2))
		text = font.render("kills: "+str(player.enemy_kills), True, (0, 0, 0))
		self.image.blit(text, (350 - text.get_width() // 2, 10 - text.get_height() // 2))

	def draw(self, surface):
		pygame.draw.rect(surface, self.color, self.rect)

class upgrade(pygame.sprite.Sprite):
	def __init__(self, x, y, upgrade_type, value):
		pygame.sprite.Sprite.__init__(self)
		src = "img/%s_%s.png" % (upgrade_type, value)
		self.image = pygame.image.load(src)
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		self.value = value
		self.fire_rate = 250000
		if self.value == "laser":
			self.fire_rate = 500000

	def update(self, action = "check", args = []):
		if action == "check":
			player = args[0]
			self.check(player)

	def check(self, player):
		if self.rect.colliderect(player):
			self.kill()
			player.weapon = self.value
			player.fire_rate = self.fire_rate

	def draw(self, surface):
		surface.blit(self.image, self.rect)

class live_count_block(pygame.sprite.Sprite):
	def __init__(self, x, y, width, height, color = (255, 7, 0)):
		self.y = y
		self.x = x
		self.width = width
		self.height = height
		self.image = pygame.Surface([width, height])
		self.image.fill(color)
		self.color = color

		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		self.rect.width = width
		self.rect.height = height

	def draw(self, surface):
		pygame.draw.rect(surface, self.color, self.rect)

class projectile(pygame.sprite.Sprite):
	def __init__(self, direction, x, y, width = 4, height = 4, strength = 1, speed = 9, hostile = False, max_distance = 500, diagonal = "n", angle = 2):
		pygame.sprite.Sprite.__init__(self)
		self.x = x
		self.y = y
		self.x_origin = x
		self.y_origin = y
		self.direction = direction
		self.width = width
		self.height = height
		self.speed = speed
		self.image = pygame.Surface([self.width, self.height])
		self.image.fill((0,0,0))
		self.color = (0,0,0)
		self.hostile = hostile
		self.max_travel_distance = max_distance
		self.diagonal = diagonal
		self.strength = strength
		self.angle = angle

		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		self.rect.width = self.width
		self.rect.height = self.height
		self.mask = pygame.mask.from_surface(self.image)
		self.mask.fill()
		self.cycle = 0

	def update(self, action = "none", args = []):
		if action == "move":
			enemy_sprites, large_enemy_sprites, player, upgrades = args
			self.move(enemy_sprites, large_enemy_sprites, player, upgrades)

	def move(self, enemy_sprites, large_enemy_sprites, player, upgrades):
		speed = self.speed
		direction = self.direction
		if self.diagonal != "n":
			if self.cycle == 1:
				if self.diagonal == "u":
					self.rect.y -= self.angle
				elif self.diagonal == "d":
					self.rect.y += self.angle
				self.cycle = 0
			else:
				self.cycle = 1
		if direction == "left":
			self.rect.x -= speed
		elif direction == "right":
			self.rect.x += speed
		elif direction == "up":
			self.rect.y -= speed
		elif direction == "down":
			self.rect.y += speed
		if self.hostile:
			if self.rect.colliderect(player):
				self.destroy()
				player.destroy()
				return
		else:
			for sprite_group in [enemy_sprites, large_enemy_sprites]:
				print ("group (before): "+str(sprite_group))
				collisions = pygame.sprite.spritecollide(self, sprite_group, False, pygame.sprite.collide_mask)
				print ("group (after): "+str(sprite_group))
				if len(collisions) > 0:
					print ("collisions: "+str(collisions))
					collisions[0].hit(player, self.strength, upgrades)
					self.destroy()
					return
		if abs(self.rect.x - self.x_origin) > self.max_travel_distance or abs(self.rect.y - self.y_origin) > self.max_travel_distance:
			self.destroy()
	def destroy(self):
		self.kill()

	def draw(self, surface):
		pygame.draw.rect(surface, self.color, self.rect)


class enemy(pygame.sprite.Sprite):
	def __init__(self, x, y, width, height, health = 1, color = (150, 150, 150), large = False):
		pygame.sprite.Sprite.__init__(self)
		self.x = x
		self.y = y
		self.width = width
		self.height = height
		#self.image = pygame.Surface([width, height])
		#self.image.fill(color)
		if not large:
			self.image = pygame.image.load("img/enemy_small.png")
		else:
			self.image = pygame.image.load("img/enemy_large.png")
		self.color = color
		self.health = health
		self.large = large
		self.groups = []
		self.arrays = []
		self.last_projectile_fired = datetime.datetime(year=2000, month=1, day=1)
		self.face_direction = "left"

		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		self.rect.width = width
		self.rect.height = height
		self.mask = pygame.mask.from_surface(self.image)
		self.mask.fill()

	def shoot(self, projectile_sprites, player):
		shooting = random.randint(0,1)
		if not shooting:
			return
		now = datetime.datetime.now()
		ptd = now - self.last_projectile_fired
		if ptd.seconds < 3:
			return
		if self.large:
			t = random.randint(0,3)
			angle = random.randint(2, 8)
			if t == 0:
				direction = "left"
				x = self.rect.x + 30
				y = self.rect.y + 5
			if t == 1:
				direction = "left"
				x = self.rect.x + 15
				y = self.rect.y + 10
			if t == 2:
				direction = "right"
				x = self.rect.x + 65
				y = self.rect.y + 5
			if t == 3:
				direction = "right"
				x = self.rect.x + 85
				y = self.rect.y + 10
			p = projectile(direction, x, y, speed = 5, hostile = True, diagonal = "u", angle = angle)
		else:
			direction = self.face_direction
			if player.rect.y <= (self.rect.y - 10):
				direction = "up"
			elif player.rect.y >= (self.rect.y + 10):
				direction = "down"
			p = projectile(direction, self.rect.x, self.rect.y, speed = 5, hostile = True)
		self.last_projectile_fired = now
		projectile_sprites.add(p)

	def update(self, action = "none", args = []):
		if action == "move":
			player, upgrades = args
			self.move(player, upgrades)
		elif action == "shoot":
			projectile_sprites, player = args
			self.shoot(projectile_sprites, player)

	def move(self, player, upgrades):
		speed = random.randint(1, 3)
		if self.large:
			speed = 1
		player_x = player.rect.x - (player.width / 2)
		player_y = player.rect.y + (player.height / 2)
		priority = random.randint(0,1)
		if self.large:
			if priority == 0:
				return
			priority = 0
		if priority == 0:
			if player_x < self.rect.x:
				direction = "left"
			else:
				direction = "right"
			self.face_direction = direction
		else:
			if player_y > self.rect.y:
				direction = "down"
			else:
				direction = "up"

		if direction == "left":
			self.rect.x -= speed
		elif direction == "right":
			self.rect.x += speed
		elif direction == "up":
			self.rect.y -= speed
		elif direction == "down":
			self.rect.y += speed
		if self.rect.colliderect(player):
			self.hit(player, 3, upgrades)
			player.destroy()

	def hit(self, player, damage_points, upgrades):
		self.health -= damage_points
		#self.image.fill((255,255,255))
		if self.health <= 0:
			self.destroy(player, upgrades)

	def destroy(self, player, upgrades):
		self.kill()
		for g in self.groups:
			g.remove(self)
		for a in self.arrays:
			index = a.index(self)
			a.pop(index)
		if self.large:
			b = random.randint(0,10)
			if b * random.random() > 3:
				i = random.randint(0,1)
				weapon_types = ["spread", "laser"]
				u = upgrade(self.rect.x, self.rect.y, "weapon", weapon_types[i])
				upgrades.add(u)
		player.enemies_destroyed += 1
		player.enemy_kills += 1

	def draw(self, surface):
		pygame.draw.rect(surface, self.color, self.rect)
