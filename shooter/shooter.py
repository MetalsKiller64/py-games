import pygame, sprites, controls, argparse, datetime, random

def gameover(screen, font):
	screen.fill((0,0,0))
	text = font.render("Game Over", True, (128, 0, 0))
	screen.blit(text, ((screen.get_width() - text.get_width()) // 2, screen.get_height() // 2 - text.get_height()))

def color_tuple(arg_string):
	r, g, b = (int(x) for x in arg_string.split(","))
	return (r,g,b)

def spawn_enemy(enemies, enemy_sprites, last_enemy_spawn):
	if last_enemy_spawn != None:
		if (datetime.datetime.now() - last_enemy_spawn).seconds < 2:
			return enemies, enemy_sprites, last_enemy_spawn
	spawn_rate = 10
	#print (enemies)
	spawn_rate -= len(enemies)
	spawn = spawn_rate * 0.1 + random.random()
	if spawn >= 1:
		pos_x = random.randint(10, 500)
		pos_y = random.randint(10, 500)
		enemy = sprites.enemy(pos_x, pos_y, 10, 10)
		last_enemy_spawn = datetime.datetime.now()
		enemies.append(enemy)
		enemy_sprites.add(enemy)
		enemy.groups.append(enemy_sprites)
		enemy.arrays.append(enemies)
	return enemies, enemy_sprites, last_enemy_spawn

def spawn_large_enemy(last_large_spawn, player):
	global large_enemies
	global large_enemy_sprites
	if last_large_spawn != None:
		if (datetime.datetime.now() - last_large_spawn).seconds < 30:
			return last_large_spawn
	if player.enemies_destroyed > 5:
		pos_x = random.randint(10, 500)
		pos_y = random.randint(400, 500)
		enemy = sprites.enemy(pos_x, pos_y, 70, 20, 10, large = True)
		last_large_spawn = datetime.datetime.now()
		large_enemies.append(enemy)
		large_enemy_sprites.add(enemy)
		enemy.groups.append(large_enemy_sprites)
		enemy.arrays.append(large_enemies)
		player.enemies_destroyed = 0
	return last_large_spawn

parser = argparse.ArgumentParser()
#parser.add_argument("-l", "--level", dest="level_name", default=None, help="Pfad zur Level-Datei")
parser.add_argument("-g", "--geometry", dest="screen_geometry", default="800x800", help="Bildschirmgröße (Breite, Höhe)")
parser.add_argument("-f", "--frame-rate", dest="frame_rate", action="store", type=int, default=60, help="FPS")
#parser.add_argument("-dh", "--draw-hitbox", dest="draw_hitbox", action="store_true", default=False, help="Spieler Hitbox anzeigen")
#parser.add_argument("-bg", "--background-color", dest="bg_color", default=(184, 207, 245), type=color_tuple, help="Hintergrundfarbe (r,g,b)")
#parser.add_argument("-c", "--config", dest="config_file", action="store", default=None, help="Konfigurationsdatei angeben")
args = parser.parse_args()

"""level_name = args.level_name
if level_name != None:
	if not level_name.endswith(".json"):
		level_name+= ".json"
"""
geometry = args.screen_geometry
frame_rate = args.frame_rate
#draw_hitbox = args.draw_hitbox
#bg_color = args.bg_color
if not geometry.count("x") == 1:
	print ("diese Bildschirmgröße verstehe ich nicht!")
	sys.exit()
screen_width, screen_height = (int(x) for x in geometry.split("x"))
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.init()
font = pygame.font.SysFont("comicsansms", 30)
clock = pygame.time.Clock()

enemy_sprites = pygame.sprite.Group()
large_enemy_sprites = pygame.sprite.Group()
projectile_sprites = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()
upgrades = pygame.sprite.Group()
player = sprites.player_object(100, 100, 10, 5, screen_width, screen_height)
#hitbox = sprites.hitbox_object(player.rect)
enemies = []
large_enemies = []
#all_sprites.add(player)
status_bar = sprites.status_bar(0, 0, screen_width, 20)
all_sprites.add(status_bar)

menu_event = False
single_frame = False
done = False
background = (184, 207, 245)
last_enemy_spawn = None
last_large_spawn = None
spawn = False
frame = 0
while not done:
	clock.tick(frame_rate)
	screen.fill(background)
	status_bar.update_status(player, screen, font)
	if not player.respawning:
		enemies, enemy_sprites, last_enemy_spawn = spawn_enemy(enemies, enemy_sprites, last_enemy_spawn)
		last_large_spawn = spawn_large_enemy(last_large_spawn, player)
	enemy_sprites.draw(screen)
	large_enemy_sprites.draw(screen)
	print (player.enemies_destroyed)
	print (large_enemies)
	print (large_enemy_sprites)
	all_sprites.draw(screen)
	controls.handle_key_event(player, menu_event, single_frame, projectile_sprites)
	projectile_sprites.update("move", [enemy_sprites, large_enemy_sprites, player, upgrades])
	projectile_sprites.draw(screen)
	enemy_sprites.update("move", [player, upgrades])
	enemy_sprites.update("shoot", [projectile_sprites, player])
	large_enemy_sprites.update("move", [player, upgrades])
	large_enemy_sprites.update("shoot", [projectile_sprites, player])
	if player.lives < 0:
		gameover(screen, font)
	if player.respawning:
		enemy_sprites.empty()
		all_sprites.remove(enemies)
		projectile_sprites.empty()
		enemies = []
		if (frame % 10) == 0:
			if player.color == (255, 7, 0):
				player.color = (0, 248, 255)
			else:
				player.color = (255, 7, 0)
		if (datetime.datetime.now() - player.last_death).seconds > 3:
			player.respawning = False
			player.color = (255, 7, 0)
	"""if spawn == False:
		u = sprites.upgrade(200, 200, "weapon", "laser")
		upgrades.add(u)
		u2 = sprites.upgrade(200, 300, "weapon", "spread")
		upgrades.add(u2)
		spawn = True"""
	upgrades.draw(screen)
	upgrades.update("check", [player])
	player.draw(screen)
	pygame.display.flip()
	frame += 1
	if frame > 60:
		frame = 0
