import pygame, random, time, json, sys, argparse, math, subprocess

def color_tuple(arg_string):
	r, g, b = (int(x) for x in arg_string.split(","))
	return (r,g,b)

parser = argparse.ArgumentParser()
parser.add_argument("-l", "--level", dest="level_name", default=None, help="Pfad zur Level-Datei")
parser.add_argument("-g", "--geometry", dest="screen_geometry", default="800x600", help="Bildschirmgröße (Breite, Höhe)")
parser.add_argument("-f", "--frame-rate", dest="frame_rate", action="store", type=int, default=60, help="FPS")
parser.add_argument("-dh", "--draw-hitbox", dest="draw_hitbox", action="store_true", default=False, help="Spieler Hitbox anzeigen")
parser.add_argument("-bg", "--background-color", dest="bg_color", default=(184, 207, 245), type=color_tuple, help="Hintergrundfarbe (r,g,b)")
parser.add_argument("-c", "--config", dest="config_file", action="store", default=None, help="Konfigurationsdatei angeben")
args = parser.parse_args()

level_name = args.level_name
if level_name != None:
	if not level_name.endswith(".json"):
		level_name+= ".json"
geometry = args.screen_geometry
frame_rate = args.frame_rate
draw_hitbox = args.draw_hitbox
bg_color = args.bg_color
if not geometry.count("x") == 1:
	print ("diese Bildschirmgröße verstehe ich nicht!")
	sys.exit()
screen_width, screen_height = (int(x) for x in geometry.split("x"))
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.init()
pygame.joystick.init()

config_file = "config.json"
if args.config_file:
	config_file = args.config_file
f = open(config_file)
config = json.load(f)
f.close()
controls = config["controls"]

for x in range(pygame.joystick.get_count()):
	j = pygame.joystick.Joystick(x)
	j.init()

clock = pygame.time.Clock()

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
		self.jump_frames = 0
		self.jump_button_pressed = False
		self.jump_frame_factor = 0
		self.jump_frame_factor_max = 10
		self.speed = {"left": 0, "right": 0, "down": 0, "up": 0}
		self.speed_max = 3
		self.fall_speed_max = 4
		self.sprint_max = 6
		self.air_speed_max = 2
		self.sprinting = False
		self.colliding = {"left": False, "right": False, "top": False, "bottom": False}
		self.accel_frame = 0
		self.accel_rate = 10
		self.decel_rate = 5
		self.decel_frame = 0
		self.jump_cycle = 0
		self.last_floor = None
		self.lives = 2
		self.level_pos_x = spawn_x
		self.level_pos_y = spawn_y
		self.floating = False
		self.jump_block = False
		self.block_cycle = 0
		self.exit_reached = False
		self.dead = False
		self.move_left = False
		self.move_right	= False
	
	def draw(self, surface):
		pygame.draw.rect(surface, (255, 7, 0), self.rect)
	
	def handle_phys(self):
		if self.jumping:
			self.jump()
		elif self.falling:
			self.fall()
		elif not self.floating:
			self.last_floor = None
			self.falling = True
		
		self.decel_frame += 1
		if not self.sprinting:
			for direction in self.speed:
				if direction == "left" or direction == "right" and not self.jumping and not self.falling:
					if self.decel_frame >= self.decel_rate:
						if self.speed[direction] > 3:
							self.speed[direction] -= 1
		if not self.move_left and not self.move_right:
			for direction in self.speed:
				if direction == "left" or direction == "right":
					if self.speed[direction] > 0:
						if self.decel_frame >= self.decel_rate:
							self.speed[direction] -= 1
						if self.floating:
							self.speed[direction] = 0
						self.move(direction, self.speed[direction])
		if self.decel_frame > self.decel_rate:
			self.decel_frame = 0
	
	def handle_key_event(self):
		events = pygame.event.get()
		global menu_event
		speed_max = self.speed_max
		shift_keys = [pygame.K_LSHIFT, pygame.K_RSHIFT]
		jump_buttons = [0,1]
		axes = {"0": {"-1": "left", "1": "right", "0": "stop"}, "1": {"-1": "up", "1": "down", "0": ""}}
		player_controls = {"Jump": [], "Run": [], "Up": [], "Down": [], "Left": [], "Right": [], "Start": [], "Pause": []}
		for g in controls["gamepad"]:
			for key in player_controls:
				player_controls[key].append(g[key])
		for key in player_controls:
			player_controls[key].append(controls["keyboard"][key])
		for event in events:
			if event.type == pygame.JOYBUTTONDOWN:
				button = event.button
				if button in player_controls["Run"]:
					self.sprinting = True
				elif button in player_controls["Jump"]:
					if not self.jumping and self.speed["down"] == 0:
						self.speed["up"] = 4
						self.jumping = True
						self.jump_button_pressed = True
						self.jump()
				elif button in player_controls["Pause"] or button in player_controls["Start"]:
					menu_event = True
			elif event.type == pygame.JOYBUTTONUP:
				button = event.button
				if button in player_controls["Run"]:
					self.sprinting = False
				elif button in player_controls["Jump"]:
					self.jump_button_pressed = False
			elif event.type == pygame.JOYAXISMOTION or event.type == pygame.JOYHATMOTION:
				if event.type == pygame.JOYHATMOTION:
					axis = event.hat
					value = int(event.value[0])
				else:
					axis = event.axis
					value = int(event.value)
				if [axis,value] in player_controls["Left"]:
					self.move_left = True
				elif [axis,value] in player_controls["Right"]:
					self.move_right = True
				elif not [axis,value] in player_controls["Left"] and not [axis,value] in player_controls["Right"]:
					self.move_left = False
					self.move_right = False
			elif event.type == pygame.QUIT:
				sys.exit(0)
			elif event.type == pygame.KEYDOWN:
				key = event.key
				if key in player_controls["Run"]:
					self.sprinting = True
				elif key in player_controls["Pause"] or key in player_controls["Start"]:
					menu_event = True
				elif key in player_controls["Jump"]:
					if not self.jumping and self.speed["down"] == 0:
						self.speed["up"] = 4
						self.jumping = True
						self.jump_button_pressed = True
						self.jump()
				elif key in player_controls["Left"]:
					self.move_left = True
				elif key in player_controls["Right"]:
					self.move_right = True
			elif event.type == pygame.KEYUP:
				key = event.key
				if key in player_controls["Run"]:
					self.sprinting = False
				elif key in player_controls["Jump"]:
					self.jump_button_pressed = False
				elif key in player_controls["Left"]:
					self.move_left = False
				elif key in player_controls["Right"]:
					self.move_right = False
		
		if self.sprinting:
			speed_max = self.sprint_max
		if self.jumping:
			speed_max = self.air_speed_max

		if self.move_left:
			if self.colliding["left"]:
				self.speed["left"] = 0
				return
			if self.accel_frame >= self.accel_rate:
				if self.speed["left"] < speed_max:
					self.speed["left"] += 1
					if self.speed["right"] > 0:
						self.speed["right"] -= 1
				self.accel_frame = 0
			self.move("left")
		elif self.move_right:
			if self.colliding["right"]:
				self.speed["right"] = 0
				return
			if self.accel_frame >= self.accel_rate:
				if self.speed["right"] < speed_max:
					self.speed["right"] += 1
					if self.speed["left"] > 0:
						self.speed["left"] -= 1
				self.accel_frame = 0
			self.move("right")
 
	def jump(self):
		self.floating = False
		#self.floater = None
		self.jumping = True
		self.jump_block = True
		self.last_floor = None
		frame_max = 3
		self.jump_frames += 1
		if self.jump_button_pressed:
			if self.jump_frame_factor < self.jump_frame_factor_max:
				self.jump_frame_factor += 1
		frame_max *= self.jump_frame_factor
		jump_cycle_max = int(frame_max / 4)
		jcm = jump_cycle_max if jump_cycle_max > 3 else 3
		if self.jump_cycle == jcm:
			self.speed["up"] -= 1
			self.jump_cycle = 0
		else:
			self.jump_cycle += 1
		
		if self.speed["up"] <= 0:
			self.speed["up"] = 0
			self.jump_cycle = 0
			self.jumping = False
			self.jump_frames = 0
			self.jump_frame_factor = 0
			self.fall()
		
		self.move("up")
	
	def fall(self):
		self.falling = True
		if self.speed["up"] > 0:
			self.speed["up"] -= 1
		elif self.speed["down"] < self.fall_speed_max:
			self.speed["down"] += 1
		self.move("down")

	def check_ground(self):
		self.last_floor = None
		colliding_objects = pygame.sprite.spritecollide(hitbox, sprites, False)
		for o in colliding_objects:
			collision = pygame.sprite.spritecollideany(hitbox, [o], pygame.sprite.collide_mask)
			if collision:
				collided_part = check_collision(hitbox, collision)
				if collided_part == "top":
					self.last_floor = collision
					self.speed["down"] = 0
					break
		if self.last_floor == None:
			self.falling = True
			self.floating = False
	
	def check_path(self, direction, speed, new_position):
		current_x = self.rect.x
		current_y = self.rect.y
		new_x = new_position[0]
		new_y = new_position[1]
		h_x = hitbox.rect.x
		h_y = hitbox.rect.y
		if direction == "left":
			for x in reversed(range(new_x, current_x)):
				x_diff = current_x - x
				hitbox.rect.x -= x_diff
				colliding_objects = pygame.sprite.spritecollide(hitbox, sprites, False)
				for o in colliding_objects:
					collision = pygame.sprite.spritecollideany(hitbox, [o], pygame.sprite.collide_mask)
					if collision:
						collided_part = check_collision(hitbox, collision)
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
				x_diff = x - current_x
				hitbox.rect.x += x_diff
				colliding_objects = pygame.sprite.spritecollide(hitbox, sprites, False)
				for o in colliding_objects:
					collision = pygame.sprite.spritecollideany(hitbox, [o], pygame.sprite.collide_mask)
					if collision:
						collided_part = check_collision(hitbox, collision)
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
				y_diff = current_y - y
				hitbox.rect.y -= y_diff
				colliding_objects = pygame.sprite.spritecollide(hitbox, sprites, False)
				for o in colliding_objects:
					collision = pygame.sprite.spritecollideany(hitbox, [o], pygame.sprite.collide_mask)
					if collision:
						collided_part = check_collision(hitbox, collision)
						if collided_part == "bottom":
							hitbox.rect.y = h_y
							self.colliding["top"] = True
							self.jumping = False
							self.falling = True
							self.jump_cycle = 0
							if p.floating:
								return [0, collision]
							return [y_diff, collision]
		elif direction == "down":
			#self.colliding["bottom"] = True
			for y in range(current_y, new_y):
				y_diff = y - current_y
				hitbox.rect.y += y_diff
				colliding_objects = pygame.sprite.spritecollide(hitbox, sprites, False)
				for o in colliding_objects:
					collision = pygame.sprite.spritecollideany(hitbox, [o], pygame.sprite.collide_mask)
					if collision:
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
				
	
	def move(self, direction, speed = None):
		if direction == "left":
			if speed == None:
				speed = self.speed["left"]
			new_x = self.rect.x - speed
			speed, collision_object = self.check_path("left", speed, [new_x, self.rect.y])
			self.speed[direction] = speed
			self.rect.x -= speed
			self.level_pos_x -= speed
			hitbox.rect.x -= speed
			self.check_ground()
			if self.rect.x <= 100 and self.level_pos_x >= 100:
				self.rect.x += speed
				hitbox.rect.x += speed
				all_sprite_objects.update("move", ["right", speed])
		elif direction == "right":
			if speed == None:
				speed = self.speed["right"]
			new_x = self.rect.x + speed
			speed, collision_object = self.check_path("right", speed, [new_x, self.rect.y])
			self.speed[direction] = speed
			self.rect.x += speed
			self.level_pos_x += speed
			hitbox.rect.x += speed
			self.check_ground()
			if self.rect.x >= (screen_width - 100) and self.level_pos_x <= (level_width - 100):
				self.rect.x -= speed
				hitbox.rect.x -= speed
				all_sprite_objects.update("move", ["left", speed])
		elif direction == "up":
			if speed == None:
				speed = self.speed["up"]
			new_y = self.rect.y - speed
			speed, collision_object = self.check_path("up", speed, [self.rect.x, new_y])
			self.rect.y -= speed
			self.level_pos_y -= speed
			hitbox.rect.y -= speed
			self.check_ground()
			if self.rect.y <= 100 and self.level_pos_y >= level_height:
				self.rect.y += speed
				hitbox.rect.y += speed
				all_sprite_objects.update("move", ["down", speed])
		elif direction == "down":
			if speed == None:
				speed = self.speed["down"]
			new_y = self.rect.y + speed
			speed, collision_object = self.check_path("down", speed, [self.rect.x, new_y])
			self.rect.y += speed
			self.level_pos_y += speed
			hitbox.rect.y += speed
			self.check_ground()
			if self.rect.y >= (screen_height - 100) and self.level_pos_y <= (level_height - 100):
				self.rect.y -= speed
				hitbox.rect.y -= speed
				all_sprite_objects.update("move", ["up", speed])

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
	def __init__(self, x, y, width, height, color, name, floating = False):
		pygame.sprite.Sprite.__init__(self)
		self.name = name
		self.image = pygame.Surface([width, height])
		self.image.fill((0,0,0))
		self.image.fill(color, [1, 1, width-2, height-2])

		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		self.rect.width = width
		self.rect.height = height
		self.mask = pygame.mask.from_surface(self.image)
		self.floating = floating
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
		if self.floating:
			fobj = floaters[self.name]
			for point in fobj["points"]:
				if direction == "up":
					point["y"] -= speed
				if direction == "down":
					point["y"] += speed
				if direction == "left":
					point["x"] -= speed
				if direction == "right":
					point["x"] += speed
			reverse_points = []
			reverse_points += (x for x in reversed(fobj["points"]))
			fobj["reverse_points"] = reverse_points


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
			return "right"
		else:
			return "left"
	elif abs_diff_y > abs_diff_x:
		if diff_y > 0:
			return "bottom"
		else:
			return "top"
	else:
		if diff_y > 0:
			return "bottom"
		elif diff_y <= 0:
			return "top"
		elif diff_x > 0:
			return "right"
		elif diff_x <= 0:
			return "left"
		else:
			return "stop"


def show_end():
	for event in pygame.event.get():
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_ESCAPE:
				global menu_event
				menu_event = True
	screen.fill((0,0,0))
	text = font.render("Ende", True, (0, 128, 0))
	screen.blit(text, (screen.get_width() // 2 - text.get_width(), screen.get_height() // 2 - text.get_height()))

def show_gameover():
	for event in pygame.event.get():
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_ESCAPE:
				global menu_event
				menu_event = True
	screen.fill((0,0,0))
	text = font.render("Game Over", True, (128, 0, 0))
	screen.blit(text, (screen.get_width() // 2 - text.get_width(), screen.get_height() // 2 - text.get_height()))

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
	all_sprite_objects.empty()
	death_zones.empty()
	exit, obstacles, objects, spawn, level_width, level_height, floaters = load_level(level_name)
	return exit, obstacles, objects, spawn, level_width, level_height, floaters, gameover

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
	exit = sprite_object(int(e[0]), int(e[1]), int(e[2]), int(e[3]), (138, 206, 255), "exit")
	all_sprite_objects.add(exit)
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
		float_points = obj[5]
		reverse_points = []
		reverse_points += (x for x in reversed(float_points))
		try:
			color_rgb = obj[6]
			color = (color_rgb[0], color_rgb[1], color_rgb[2])
			if color[0] == None or color[1] == None or color[2] == None:
				color = (random.randint(0,255), random.randint(0,255), random.randint(0,255))
		except IndexError:
			color = (random.randint(0,255), random.randint(0,255), random.randint(0,255))
		try:
			float_speed = int(obj[7])
		except IndexError:
			float_speed = 1
		sprite = sprite_object(x, y, w, h, color, k, floating)
		sprites.add(sprite)
		all_sprite_objects.add(sprite)
		obstacles[k] = sprite
		objects[k] = sprite
		if floating:
			f = {"name": k, "target_index": 1, "reverse": False, "player": False,
				"points": float_points, "speed": float_speed, "reverse_points": reverse_points}
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
		sprite = sprite_object(x, y, w, h, color, key)
		all_sprite_objects.add(sprite)
		death_zones.add(sprite);
	return exit, obstacles, objects, spawn, level_width, level_height, floaters

def save_config():
	f = open(config_file, "w")
	json.dump(config, f, indent=4)
	f.close()

def list_levels():
	json_list = []
	file_list = subprocess.run(["ls"], stdout=subprocess.PIPE, universal_newlines=True).stdout.strip().split("\n")
	for item in file_list:
		if item.endswith(".json"):
			if item == "config.json":
				continue
			json_list.append({"text": item.rsplit(".json")[0], "expanded_text": "", "sub_items": [], "action": "load_level", "align": "center"})
	return json_list

def check_button_usage(button_value, keyboard = False, pad_number = None):
	if not keyboard:
		pad = controls["gamepad"][pad_number]
		for key in pad:
			if pad[key] == button_value:
				controls["gamepad"][pad_number][key] = None
	else:
		keyboard = controls["keyboard"]
		for key in keyboard:
			if keyboard[key] == button_value:
				controls["keyboard"][key] = None

def set_button(name):
	while True:
		for event in pygame.event.get():
			if event.type == pygame.KEYDOWN:
				key = event.key
				check_button_usage(key, True)
				controls["keyboard"][name] = key
				return "KEY_"+pygame.key.name(key)
			elif event.type == pygame.JOYBUTTONDOWN:
				button = event.button
				pad = event.joy
				check_button_usage(button, False, pad)
				try:
					c = controls["gamepad"][pad]
					controls["gamepad"][pad][name] = button
				except IndexError:
					new_buttons = {"Jump": None, "Run": None, "Up": None, "Down": None, "Left": None, "Right": None}
					new_buttons[name] = button
					controls["gamepad"].append(new_buttons)
				return "JOY"+str(pad)+"_BTN"+str(button)
			elif event.type == pygame.JOYAXISMOTION:
				if name == "Jump" or name == "Run":
					continue
				axis = event.axis
				pad = event.joy
				value = int(event.value)
				check_button_usage([axis, value], False, pad)
				if pad not in controls["gamepad"]:
					new_buttons = {"Jump": None, "Run": None, "Up": None, "Down": None, "Left": None, "Right": None}
					new_buttons[name] = [axis, value]
				else:
					controls["gamepad"][pad][name] = [axis, value]
				return "JOY"+str(pad)+"_AXIS"+str(axis)+"_"+str(value)
			elif event.type == pygame.JOYHATMOTION:
				pass

def show_menu(menu_items, initial = False):
	done = False
	font = pygame.font.SysFont("comicsansms", 60)
	selected_item = 1
	max_visible_items = screen.get_height() // 60
	visible_menu_items = []
	for i in range(max_visible_items):
		if i < len(menu_items):
			visible_menu_items.append(menu_items[i])
	scroll_up = 2
	scroll_down = max_visible_items - 2
	visible_selected = 0
	while not done:
		screen.fill((255,255,255))
		events = pygame.event.get()
		item_position = 10
		for item in visible_menu_items:
			item_index = visible_menu_items.index(item)
			visible_text = item["text"]+item["expanded_text"]
			if visible_selected == item_index:
				text = font.render(visible_text, True, (100,100,100))
			else:
				text = font.render(visible_text, True, (0,0,0))
			if item["align"] == "center":
				screen.blit(text, ((screen.get_width() - text.get_width()) // 2, item_position))
			elif item["align"] == "left":
				screen.blit(text, ((screen.get_width() // 2) - 200, item_position))
			item_position += 60
		pygame.display.flip()
		menu_controls = {"Up": [], "Down": [], "Start": [], "Pause": []}
		for g in controls["gamepad"]:
			for key in menu_controls:
				menu_controls[key].append(g[key])
		for key in menu_controls:
			menu_controls[key].append(controls["keyboard"][key])
		for event in events:
			event_types = [pygame.KEYDOWN, pygame.JOYBUTTONDOWN, pygame.JOYAXISMOTION]
			if event.type in event_types:
				key = None
				button = None
				axis = None
				value = None
				if event.type == pygame.KEYDOWN:
					key = event.key
				elif event.type == pygame.JOYBUTTONDOWN:
					button = event.button
				else:
					axis = event.axis
					value = int(event.value)
				if key in menu_controls["Pause"] or button in menu_controls["Pause"]:
					if not initial:
						return [False, None, []]
				elif key in menu_controls["Down"] or [axis,value] in menu_controls["Down"]:
					selected_item += 1
					if visible_selected < scroll_down or selected_item == len(menu_items):
						visible_selected += 1
					else:
						if len(menu_items) > max_visible_items:
							visible_menu_items.pop(0)
							try:
								visible_menu_items.append(menu_items[selected_item])
							except IndexError:
								visible_menu_items = []
								for i in range(max_visible_items):
									if i < len(menu_items):
										visible_menu_items.append(menu_items[i])
					if selected_item > len(menu_items):
						selected_item = 1
						visible_selected = 0
						if len(menu_items) > max_visible_items:
							visible_menu_items = []
							for i in range(max_visible_items):
								if i < len(menu_items):
									visible_menu_items.append(menu_items[i])
				elif key in menu_controls["Up"] or [axis,value] in menu_controls["Up"]:
					selected_item -= 1
					if len(menu_items) > max_visible_items:
						if visible_selected > scroll_up or selected_item <= 2:
							visible_selected -= 1
						else:
							visible_menu_items.pop()
							try:
								visible_menu_items.insert(0, menu_items[selected_item - 3])
							except IndexError:
								visible_menu_items = []
								for i in reversed(range(max_visible_items)):
									if i <= len(menu_items):
										visible_menu_items.append(menu_items[(len(menu_items) - 1) - i])
					else:
						visible_selected -= 1
					if selected_item < 1:
						selected_item = len(menu_items)
						if len(menu_items) > max_visible_items:
							visible_selected = max_visible_items - 1
							visible_menu_items = []
							for i in reversed(range(max_visible_items)):
								if i <= len(menu_items):
									visible_menu_items.append(menu_items[(len(menu_items) - 1) - i])
					if visible_selected < 0:
						if len(menu_items) > max_visible_items:
							visible_selected = max_visible_items
						else:
							visible_selected = selected_item - 1
				elif key in menu_controls["Start"] or button in menu_controls["Start"]:
					item = menu_items[selected_item-1]
					action = item["action"]
					if len(item["sub_items"]) > 0:
						break_menu, action, return_values = show_menu(item["sub_items"])
						if break_menu:
							return [True, action, return_values]
					elif action == "load_level":
						return [True, "load_level", item["text"]]
					elif action == "set_button":
						button_text = set_button(item["text"])
						for i in menu_items:
							if i["expanded_text"] == ": "+button_text:
								i["expanded_text"] = ""
						item["expanded_text"] = ": "+button_text
					elif action == "save_config":
						save_config()
					elif action == "exit":
						sys.exit(0)

ending = False
gameover = False

gp = controls["gamepad"][0]
gp_jump_text = ": JOY0_BTN"+str(gp["Jump"])
gp_run_text = ": JOY0_BTN"+str(gp["Run"])
gp_up_text = ": JOY0_AXIS"+str(gp["Up"][0])+"_"+str(gp["Up"][1])
gp_down_text = ": JOY0_AXIS"+str(gp["Down"][0])+"_"+str(gp["Down"][1])
gp_left_text = ": JOY0_AXIS"+str(gp["Left"][0])+"_"+str(gp["Left"][1])
gp_right_text = ": JOY0_AXIS"+str(gp["Right"][0])+"_"+str(gp["Right"][1])
gp_start_text = ": JOY0_BTN"+str(gp["Start"])
gp_pause_text = ": JOY0_BTN"+str(gp["Pause"])
kb = controls["keyboard"]
kb_jump_text = ": KEY_"+pygame.key.name(kb["Jump"])
kb_run_text = ": KEY_"+pygame.key.name(kb["Run"])
kb_up_text = ": KEY_"+pygame.key.name(kb["Up"])
kb_down_text = ": KEY_"+pygame.key.name(kb["Down"])
kb_left_text = ": KEY_"+pygame.key.name(kb["Left"])
kb_right_text = ": KEY_"+pygame.key.name(kb["Right"])
kb_start_text = ": KEY_"+pygame.key.name(kb["Start"])
kb_pause_text = ": KEY_"+pygame.key.name(kb["Pause"])
gamepad_submenu = [{"text": "Jump", "expanded_text": gp_jump_text, "sub_items": [], "action": "set_button", "align": "left"},
		{"text": "Run", "expanded_text": gp_run_text, "sub_items": [], "action": "set_button", "align": "left"},
		{"text": "Left", "expanded_text": gp_left_text, "sub_items": [], "action": "set_button", "align": "left"},
		{"text": "Right", "expanded_text": gp_right_text, "sub_items": [], "action": "set_button", "align": "left"},
		{"text": "Up", "expanded_text": gp_up_text, "sub_items": [], "action": "set_button", "align": "left"},
		{"text": "Down", "expanded_text": gp_down_text, "sub_items": [], "action": "set_button", "align": "left"},
		{"text": "Start", "expanded_text": gp_start_text, "sub_items": [], "action": "set_button", "align": "left"},
		{"text": "Pause", "expanded_text": gp_pause_text, "sub_items": [], "action": "set_button", "align": "left"}]
keyboard_submenu = [{"text": "Jump", "expanded_text": kb_jump_text, "sub_items": [], "action": "set_button", "align": "left"},
		{"text": "Run", "expanded_text": kb_run_text, "sub_items": [], "action": "set_button", "align": "left"},
		{"text": "Left", "expanded_text": kb_left_text, "sub_items": [], "action": "set_button", "align": "left"},
		{"text": "Right", "expanded_text": kb_right_text, "sub_items": [], "action": "set_button", "align": "left"},
		{"text": "Up", "expanded_text": kb_up_text, "sub_items": [], "action": "set_button", "align": "left"},
		{"text": "Down", "expanded_text": kb_down_text, "sub_items": [], "action": "set_button", "align": "left"},
		{"text": "Start", "expanded_text": kb_start_text, "sub_items": [], "action": "set_button", "align": "left"},
		{"text": "Pause", "expanded_text": kb_pause_text, "sub_items": [], "action": "set_button", "align": "left"}]

control_menu = [{"text": "Gamepad", "expanded_text": "", "sub_items": gamepad_submenu, "action": None, "align": "center"},
		{"text": "Keyboard", "expanded_text": "", "sub_items": keyboard_submenu, "action": None, "align": "center"},
		{"text": "Save to config", "expanded_text": "", "sub_items": [], "action": "save_config", "align": "center"}]
menu_items = [{"text": "Level Select", "expanded_text": "", "sub_items": [], "action": None, "align": "center"},
		{"text": "Controls", "expanded_text": "", "sub_items": control_menu, "action": None, "align": "center"},
		{"text": "Exit", "expanded_text": "", "sub_items": [], "action": "exit", "align": "center"}]
menu_items[0]["sub_items"] = list_levels()
font = pygame.font.SysFont("comicsansms", 30)
sprites = pygame.sprite.Group()
all_sprite_objects = pygame.sprite.Group()
death_zones = pygame.sprite.Group()
if level_name != None:
	exit, obstacles, objects, spawn, level_width, level_height, floaters = load_level(level_name)
	spawn_x = spawn[0]
	spawn_y = spawn[1]
	p = Player(spawn_x, spawn_y)
	#hitbox = sprite_object(spawn_x-1, spawn_y-1, 10,24, (0, 0, 0), True)
	hitbox = hitbox_object(spawn_x-1, spawn_y-1, 9,22, (255, 255, 255))
	initial = False
else:
	initial = True

dpass = 0
done = False
menu_event = False
while not done:
	clock.tick(frame_rate)
	if initial or menu_event:
		menu_event = False
		action_trigger, action, return_values = show_menu(menu_items, initial)
		if action_trigger:
			if action == "load_level":
				sprites.empty()
				all_sprite_objects.empty()
				death_zones.empty()
				level_name = return_values+".json"
				exit, obstacles, objects, spawn, level_width, level_height, floaters = load_level(level_name)
				ending = False
				gameover = False
				spawn_x = spawn[0]
				spawn_y = spawn[1]
				p = Player(spawn_x, spawn_y)
				#hitbox = sprite_object(spawn_x-1, spawn_y-1, 10,24, (0, 0, 0), True)
				hitbox = hitbox_object(spawn_x-1, spawn_y-1, 9,22, (255, 255, 255))
		initial = False
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
	screen.fill(bg_color)
	all_sprite_objects.draw(screen)
	if draw_hitbox:
		hitbox.draw(screen)
	p.draw(screen)
	
	p.colliding["right"] = False
	p.colliding["left"] = False
	p.colliding["top"] = False
	p.colliding["bottom"] = False
	
	for name in floaters:
		f = floaters[name]
		obj = obstacles[name]
		f["player"] = False
		if p.last_floor == obj:
			p.floating = True
			f["player"] = True
	
	p.handle_key_event()
	p.handle_phys()
	
	if p.accel_frame > p.accel_rate:
		p.accel_frame = 0
	else:
		p.accel_frame += 1
	if pygame.event.peek([pygame.KEYUP, pygame.KEYDOWN]):
		p.handle_key_event()
	
	for name in floaters:
		f = floaters[name]
		obj = obstacles[name]
		rect = obj.rect
		x = rect.x;
		y = rect.y;
		target_index = f["target_index"]
		speed = f["speed"]
		points = f["points"]
		reverse_points = f["reverse_points"]
		reverse = f["reverse"]
		if not reverse:
			try:
				target = points[target_index]
			except IndexError:
				reverse = True
				target_index = 1
				target = reverse_points[target_index]
		else:
			try:
				target = reverse_points[target_index]
			except IndexError:
				reverse = False
				target_index = 1
				target = points[target_index]
		
		dest_x = target["x"]
		dest_y = target["y"]
		player_x = p.rect.x
		player_y = p.rect.y
		if dest_y > y:
			y_distance = dest_y - y
		else:
			y_distance = y - dest_y
		if dest_x > x:
			x_distance = dest_x - x
		else:
			x_distance = x - dest_x
		
		angle = math.atan2(-y_distance, x_distance) % (2 * math.pi)
		if not reverse:
			if x < dest_x:
				x_pos = x + math.cos(angle) * speed
				player_x = player_x + math.cos(angle) * speed
			else:
				x_pos = x - math.cos(angle) * speed
				player_x = player_x - math.cos(angle) * speed
			if y > dest_y:
				y_pos = y - math.ceil(abs(math.sin(angle) * speed))
				player_y = player_y - math.ceil(abs(math.sin(angle) * speed))
			else:
				y_pos = y - math.sin(angle) * speed
				player_y = player_y - math.sin(angle) * speed
		else:
			if x < dest_x:
				x_pos = x + math.cos(angle) * speed
				player_x = player_x + math.cos(angle) * speed
			else:
				x_pos = x - math.ceil(math.cos(angle) * speed)
				player_x = player_x - math.ceil(math.cos(angle) * speed)
			if y > dest_y:
				y_pos = y - math.ceil(abs(math.sin(angle) * speed))
				player_y = player_y - math.ceil(abs(math.sin(angle) * speed))
			else:
				y_pos = y - math.sin(angle) * speed
				player_y = player_y - math.sin(angle) * speed
		
		player_carrying = f["player"]
		if player_carrying:
			x_diff = p.rect.x - math.ceil(player_x)
			if x_diff > 0:
				p.move("left", speed)
			elif x_diff < 0:
				p.move("right", speed)
			y_diff = p.rect.y - math.ceil(player_y)
			if y_diff > 0:
				p.move("up", speed)
			elif y_diff < 0:
				p.move("down", speed)
		
		if obj.rect.x > dest_x:
			new_x = math.ceil(x_pos) if math.ceil(x_pos) >= dest_x else dest_x
			x_diff = obj.rect.x - new_x
			obj.rect.x -= x_diff
		else:
			new_x = math.ceil(x_pos) if math.ceil(x_pos) <= dest_x else dest_x
			x_diff = new_x - obj.rect.x
			obj.rect.x += x_diff
		if obj.rect.y > dest_y:
			new_y = math.ceil(y_pos) if math.ceil(y_pos) >= dest_y else dest_y
			y_diff = obj.rect.y - new_y
			obj.rect.y -= y_diff
		else:
			new_y = math.ceil(y_pos) if math.ceil(y_pos) <= dest_y else dest_y
			y_diff = new_y - obj.rect.y
			obj.rect.y += y_diff
		
		if obj.rect.x == dest_x and obj.rect.y == dest_y:
			target_index += 1
		f["reverse"] = reverse
		f["target_index"] = target_index
	
	
	if hitbox.rect.colliderect(exit):
		p.exit_reached = True
	
	if p.exit_reached:
		show_end()
		ending = True

	if p.rect.y >= 300:
		p.dead = True
	
	if p.block_cycle >= 10:
		p.block_cycle = 0
		p.jump_block = False
	if p.jump_block:
		p.block_cycle += 1
	
	show_live_count()
	pygame.display.flip()
