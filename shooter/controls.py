import pygame, json

config_file = "config.json"
f = open(config_file)
config = json.load(f)
f.close()
controls = config["controls"]

pygame.joystick.init()
for x in range(pygame.joystick.get_count()):
	j = pygame.joystick.Joystick(x)
	j.init()

def handle_key_event(player, menu_event, single_frame, projectile_sprites):
	events = pygame.event.get()
	hitbox = player.hitbox
	speed_max = player.speed_max
	player_controls = {"Shoot": [], "Up": [], "Down": [], "Left": [], "Right": [], "Start": [], "Pause": [], "horizontal_stop": [], "vertical_stop": []}
	for g in controls["gamepad"]:
		for key in player_controls:
			player_controls[key].append(g[key])
	for key in player_controls:
		if not key in controls["keyboard"]:
			continue
		player_controls[key].append(controls["keyboard"][key])
	for event in events:
		if event.type == pygame.JOYBUTTONDOWN:
			button = event.button
			if button in player_controls["Shoot"]:
				player.shoot_button_pressed = True
			elif button in player_controls["Pause"] or button in player_controls["Start"]:
				menu_event = True
		elif event.type == pygame.JOYBUTTONUP:
			button = event.button
			if button in player_controls["Shoot"]:
				player.shoot_button_pressed = False
		elif event.type == pygame.JOYAXISMOTION or event.type == pygame.JOYHATMOTION:
			if event.type == pygame.JOYHATMOTION:
				axis = event.hat
				value = int(event.value[0])
			else:
				axis = event.axis
				value = int(event.value)
			if [axis,value] in player_controls["Left"]:
				player.move_left = True
			elif [axis,value] in player_controls["Right"]:
				player.move_right = True
			elif [axis,value] in player_controls["Up"]:
				player.move_up = True
			elif [axis,value] in player_controls["Down"]:
				player.move_down = True
			elif [axis,value] in player_controls["horizontal_stop"]:
				player.move_left = False
				player.move_right = False
			elif [axis,value] in player_controls["vertical_stop"]:
				player.move_up = False
				player.move_down = False
		elif event.type == pygame.QUIT:
			sys.exit(0)
		elif event.type == pygame.KEYDOWN:
			key = event.key
			if key in player_controls["Pause"] or key in player_controls["Start"]:
				menu_event = True
			elif key in player_controls["Shoot"]:
				player.shoot_button_pressed = True
			elif key in player_controls["Left"]:
				player.move_left = True
			elif key in player_controls["Right"]:
				player.move_right = True
			elif key in player_controls["Up"]:
				player.move_up = True
			elif key in player_controls["Down"]:
				player.move_down = True
			elif key == pygame.K_F1:
				single_frame = True
		elif event.type == pygame.KEYUP:
			key = event.key
			if key in player_controls["Left"]:
				player.move_left = False
			elif key in player_controls["Shoot"]:
				player.shoot_button_pressed = False
			elif key in player_controls["Right"]:
				player.move_right = False
			elif key in player_controls["Up"]:
				player.move_up = False
			elif key in player_controls["Down"]:
				player.move_down = False

	if player.shoot_button_pressed:
		player.shoot(projectile_sprites)

	if player.move_left:
		if player.colliding["left"]:
			player.relative_speed["left"] = 0
			return [menu_event, single_frame]
		if player.accel_frame >= player.accel_rate:
			if player.relative_speed["left"] < speed_max:
				player.relative_speed["left"] += 1
				if player.relative_speed["right"] > 0:
					player.relative_speed["right"] -= 1
			player.accel_frame = 0
		player.move("left", hitbox, 4)
	elif player.move_right:
		if player.colliding["right"]:
			player.relative_speed["right"] = 0
			return [menu_event, single_frame]
		if player.accel_frame >= player.accel_rate:
			if player.relative_speed["right"] < speed_max:
				player.relative_speed["right"] += 1
				if player.relative_speed["left"] > 0:
					player.relative_speed["left"] -= 1
			player.accel_frame = 0
		player.move("right", hitbox, 4)
	if player.move_up:
		if player.colliding["top"]:
			player.relative_speed["up"] = 0
			return [menu_event, single_frame]
		if player.accel_frame >= player.accel_rate:
			if player.relative_speed["up"] < speed_max:
				player.relative_speed["up"] += 1
				if player.relative_speed["down"] > 0:
					player.relative_speed["down"] -= 1
			player.accel_frame = 0
		player.move("up", hitbox, 4)
	elif player.move_down:
		if player.colliding["bottom"]:
			player.relative_speed["down"] = 0
			return [menu_event, single_frame]
		if player.accel_frame >= player.accel_rate:
			if player.relative_speed["down"] < speed_max:
				player.relative_speed["down"] += 1
				if player.relative_speed["up"] > 0:
					player.relative_speed["up"] -= 1
			player.accel_frame = 0
		player.move("down", hitbox, 4)
