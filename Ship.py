#!/usr/bin/env python3

import math

import pygame

RADIANS_TO_DEGREES = 180 / math.pi

class Ship:
	def __init__(self, screen, position, position_angular):
		self.screen = screen
		self.center_x = 500
		self.center_y = screen.get_rect().height / 2
		self.image = pygame.image.load('images/ship.png').convert()
		self.rect = self.image.get_rect()
		
		self.velocity_x, self.velocity_y = 0, 0
		self.position_y, self.position_y = position
		
		self.velocity_angular = 0
		self.position_angular = position_angular
		self.finished = False
	
	def status(self):
		speed = math.sqrt(self.velocity_x ** 2 + self.velocity_y ** 2)
		return speed
	
	def camera_position(self):
		absolute_offset_x = abs(self.velocity_x) ** .6 * 20
		offset_x = math.copysign(absolute_offset_x, self.velocity_x)
		
		absolute_offset_y = abs(self.velocity_y) ** .6 * 20
		offset_y = math.copysign(absolute_offset_y, self.velocity_y)
		
		return [offset_x - self.center_x + self.position_x,
				offset_y - self.center_y + self.position_y]
	
	def position(self):
		return (self.position_x, self.position_y)
	
	def update(self):
		self._handle_keyboard_input()

		self.position_angular += self.velocity_angular
		self.position_x += self.velocity_x
		self.position_y += self.velocity_y
		
		return
	
	def _handle_keyboard_input(self):
		pressed_keys = pygame.key.get_pressed()
		if pressed_keys[pygame.K_LEFT]:
			self.velocity_angular += .003
		if pressed_keys[pygame.K_RIGHT]:
			self.velocity_angular -= .003
		if pressed_keys[pygame.K_UP]:
			self.velocity_y -= .1 * math.cos(self.position_angular)
			self.velocity_x -= .1 * math.sin(self.position_angular)
		if pressed_keys[pygame.K_ESCAPE]:
			self.finished = True
		
		return
	
	def draw(self, camera_position):
		camera_x, camera_y = camera_position
		
		rotated_image = pygame.transform.rotozoom(self.image,
												  self.position_angular * RADIANS_TO_DEGREES, 0.5)
		rotated_image.set_colorkey((0, 0, 0))
		tmp_rect = rotated_image.get_rect()
		rotated_rect = self.rect.inflate(tmp_rect.width - self.rect.width,
										 tmp_rect.height - self.rect.height)
		
		rotated_rect.center = (self.position_x - camera_x, self.position_y - camera_y)
		
		self.screen.blit(rotated_image, rotated_rect)
		
		return