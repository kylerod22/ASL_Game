import pygame
import cv2 as cv
import hand_tracking_module as htm
from random_word import RandomWords
import time
import sys
import numpy as np
import random

import tensorflow as tf
keras = tf.keras
model = tf.keras.models.load_model('model/asl.h5')
detector = htm.HandDetector(maxHands=1, detectionCon=0.6)

wCam, hCam = 640, 480
SPELL_WIN_WIDTH = 300
cam_id = 0
cam = cv.VideoCapture(cam_id)
cam_inverted = False
cam.set(3, wCam) #Set width of camera
cam.set(4, hCam) #Set height of camera

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (50, 205, 50)
RED = (255, 0, 0)

WIN = pygame.display.set_mode((wCam + SPELL_WIN_WIDTH, hCam))
pygame.display.set_caption("ASL GAME")

pygame.init()

words = {}
with open('words.txt') as f:
    words = [line.rstrip() for line in f]

def gen_word():
    potential_word = random.choice(words)
    while "i" in potential_word or "z" in potential_word or len(potential_word) < 4 or len(potential_word) > 9:
        potential_word = random.choice(words)
    return potential_word

word = gen_word()
print(word)

font = pygame.font.Font('freesansbold.ttf', 40)
text = font.render(word, True, WHITE, BLACK)
text_rect = text.get_rect()
text_rect.center = (wCam + SPELL_WIN_WIDTH // 2, hCam // 2)

def main():
    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        WIN.fill(BLACK)
        success, img = cam.read()
        hands, img = detector.findHands(img, draw=True)
        img = cvt_cv_image(img)
        WIN.blit(img, (0, 0))
        WIN.blit(text, text_rect)



        pygame.display.update()
    pygame.quit()

def display_attempt(target_word, target_text_rect, attempted_word, WINDOW):
    if attempted_word == "":
        return
    color = GREEN
    if target_word[0] != attempted_word[0]:
        color = RED
    first_letter_render = font.render(attempted_word[0], color, color, BLACK)
    first_letter_rect = first_letter_render.get_rect()
    lastX = first_letter_rect.x = target_text_rect.x
    lastY = first_letter_rect.y = target_text_rect.y + target_text_rect.height
    WIN.blit(first_letter_render, first_letter_rect)
    last_rect = first_letter_rect
    for i, letter in enumerate(target_word):
        if i == 0:
            continue
        if i >= len(attempted_word):
            break

        color = GREEN
        if letter != attempted_word[i]:
            color = RED
        letter_render = font.render(attempted_word[i], True, color, BLACK)
        letter_rect = letter_render.get_rect()
        letter_rect.x = lastX + last_rect.width
        letter_rect.y = lastY
        WIN.blit(letter_render, letter_rect)
        last_rect = letter_rect
        lastX, lastY = letter_rect.x, letter_rect.y


def cvt_cv_image(image):
    image = cv.cvtColor(image, cv.COLOR_BGR2RGB)
    return pygame.image.frombuffer(image.tobytes(), image.shape[1::-1], "RGB")



if __name__ == "__main__":
    main()
