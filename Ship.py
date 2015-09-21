#!/usr/bin/env python3

import math

import pygame

import config

RADIANS_TO_DEGREES = 180 / math.pi

class Ship:
	DRY_MASS = 1000.0 				# kg
	STARTING_FUEL_MASS = 200.0		# kg
	LENGTH = 2.5 					# m
	ROTATE_THRUSTER_POSITION = 2.0 	# m outboard from center of mass
	ROTATE_INERTIA_FACTOR = LENGTH ** 2 / (ROTATE_THRUSTER_POSITION * 12)
	
	EXHAUST_VELOCITY = 1040.0 		# m/sec
	THRUST_FUEL_RATE = 4.0 			# kg/sec
	ROTATE_FUEL_RATE = 0.8 			# kg/sec
	
	FORCE = EXHAUST_VELOCITY * THRUST_FUEL_RATE
	TORQUE = EXHAUST_VELOCITY * ROTATE_FUEL_RATE * ROTATE_THRUSTER_POSITION
	
	def __init__(self, screen, position, position_angular):
		self.screen = screen
		self.center_x = 500
		self.center_y = screen.get_rect().height / 2
		self.image = pygame.image.load('images/ship.png').convert()
		self.rect = self.image.get_rect()
		
		self.fuel_mass = self.STARTING_FUEL_MASS
		self.velocity_x, self.velocity_y = 0, 0
		self.position_x, self.position_y = position
		
		self.velocity_angular = 0
		self.position_angular = position_angular / RADIANS_TO_DEGREES
	
	def status(self):
		speed = math.sqrt(self.velocity_x ** 2 + self.velocity_y ** 2) * config.METERS_PER_PIXEL
		return (speed, self.fuel_mass)
	
	def camera_position(self):
		absolute_offset_x = abs(self.velocity_x) ** .6 * .5
		offset_x = math.copysign(absolute_offset_x, self.velocity_x)
		
		absolute_offset_y = abs(self.velocity_y) ** .6 * .5
		offset_y = math.copysign(absolute_offset_y, self.velocity_y)
		
		return [offset_x - self.center_x + self.position_x,
				offset_y - self.center_y + self.position_y]
	
	def position(self):
		return (self.position_x, self.position_y)
	
	def update(self):
		if self.fuel_mass > 0:
			self._handle_keyboard_input()

		self.position_angular += self.velocity_angular * config.TICK_SIZE
		self.position_x += self.velocity_x * config.TICK_SIZE
		self.position_y += self.velocity_y * config.TICK_SIZE
		
		return
	
	def _handle_keyboard_input(self):
		pressed_keys = pygame.key.get_pressed()
		mass = self.DRY_MASS + self.fuel_mass
		acceleration = self.FORCE / mass / config.METERS_PER_PIXEL * config.TICK_SIZE
		acceleration_angular = self.TORQUE / (mass * self.ROTATE_INERTIA_FACTOR) * \
				config.TICK_SIZE
		
		if pressed_keys[pygame.K_LEFT]:
			self.velocity_angular += acceleration_angular
			self.fuel_mass -= self.ROTATE_FUEL_RATE * config.TICK_SIZE
		if pressed_keys[pygame.K_RIGHT]:
			self.velocity_angular -= acceleration_angular
			self.fuel_mass -= self.ROTATE_FUEL_RATE * config.TICK_SIZE
		if pressed_keys[pygame.K_UP]:
			self.velocity_y -= acceleration * math.cos(self.position_angular)
			self.velocity_x -= acceleration * math.sin(self.position_angular)
			self.fuel_mass -= self.THRUST_FUEL_RATE * config.TICK_SIZE
		
		return
	
	def draw(self, camera_position):
		camera_x, camera_y = camera_position
		
		rotated_image = pygame.transform.rotozoom(self.image,
												  self.position_angular * RADIANS_TO_DEGREES,
												  config.SCALE_FACTOR)
		rotated_image.set_colorkey((0, 0, 0))
		tmp_rect = rotated_image.get_rect()
		rotated_rect = self.rect.inflate(tmp_rect.width - self.rect.width,
										 tmp_rect.height - self.rect.height)
		
		rotated_rect.center = (self.position_x - camera_x, self.position_y - camera_y)
		
		self.screen.blit(rotated_image, rotated_rect)
		
		return