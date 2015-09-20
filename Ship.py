#!/usr/bin/env python3

import math

import pygame

RADIANS_TO_DEGREES = 180 / math.pi

class Ship:
	def __init__(self, screen, position, angular_position):
		self.screen = screen
		self.x_center = 500
		self.y_center = screen.get_rect().height / 2
		self.image = pygame.image.load('images/ship.png').convert()
		self.rect = self.image.get_rect()
		
		self.x_velocity, self.y_velocity = 0, 0
		self.x_position, self.y_position = position
		
		self.angular_position = angular_position
		self.angular_velocity = 0
		self.finished = False
	
	def status(self):
		speed = math.sqrt(self.x_velocity ** 2 + self.y_velocity ** 2)
		return speed
	
	def camera_position(self):
		x_absolute_offset = abs(self.x_velocity) ** .6 * 20
		x_offset = math.copysign(x_absolute_offset, self.x_velocity)
		
		y_absolute_offset = abs(self.y_velocity) ** .6 * 20
		y_offset = math.copysign(y_absolute_offset, self.y_velocity)
		
		return [x_offset - self.x_center + self.x_position,
				y_offset - self.y_center + self.y_position]
	
	def position(self):
		return (self.x_position, self.y_position)
	
	def update(self):
		self._handle_keyboard_input()

		self.angular_position += self.angular_velocity
		self.x_position += self.x_velocity
		self.y_position += self.y_velocity
		
		return
	
	def _handle_keyboard_input(self):
		pressed_keys = pygame.key.get_pressed()
		if pressed_keys[pygame.K_LEFT]:
			self.angular_velocity += .003
		if pressed_keys[pygame.K_RIGHT]:
			self.angular_velocity -= .003
		if pressed_keys[pygame.K_UP]:
			self.y_velocity -= .1 * math.cos(self.angular_position)
			self.x_velocity -= .1 * math.sin(self.angular_position)
		if pressed_keys[pygame.K_ESCAPE]:
			self.finished = True
		
		return
	
	def draw(self, camera_position):
		camera_x, camera_y = camera_position
		
		rotated_image = pygame.transform.rotozoom(self.image,
												  self.angular_position * RADIANS_TO_DEGREES, 0.5)
		rotated_image.set_colorkey((0, 0, 0))
		tmp_rect = rotated_image.get_rect()
		rotated_rect = self.rect.inflate(tmp_rect.width - self.rect.width,
										 tmp_rect.height - self.rect.height)
		
		rotated_rect.center = (self.x_position - camera_x, self.y_position - camera_y)
		
		self.screen.blit(rotated_image, rotated_rect)
		
		return