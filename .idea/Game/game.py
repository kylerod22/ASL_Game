import pygame
import cv2 as cv
import hand_tracking_module as htm
import time
import sys
import numpy as np
import random
import configparser
import tensorflow as tf


keras = tf.keras
model = tf.keras.models.load_model('model/asl.h5')
detector = htm.HandDetector(maxHands=1, detectionCon=0.6)

wCam, hCam = 640, 480
SPELL_WIN_WIDTH = 300

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
    while "j" in potential_word or "z" in potential_word or len(potential_word) < 4 or len(potential_word) > 9:
        potential_word = random.choice(words)
    return potential_word

font = pygame.font.Font('freesansbold.ttf', 40)

def main():

    word = gen_word()
    attempted_word = ""

    curr_word_count = 1
    max_word_count = 2
    word_delay = 2
    total_letters = 0
    correct_letters = 0

    curr_time = 0
    time_since_last_sample = 0
    sample_delay = 1.75
    last_letter = ""
    curr_letter = ""
    alphabet = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "k", "l", "m",
                "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y"]
    run = True

    config = configparser.ConfigParser()
    config.read("config.properties")

    cam_id = int(config["Camera"]["CamId"])
    cam_inverted_str = config["Camera"]["CamInverted"]
    cam_inverted = False
    if cam_inverted_str == "True":
        cam_inverted = True
    max_word_count = int(config["Game"]["MaxWords"])

    cam = cv.VideoCapture(cam_id)
    cam.set(3, wCam) #Set width of camera
    cam.set(4, hCam) #Set height of camera

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        curr_time = time.time()

        success, img = cam.read()
        hands, img = detector.findHands(img, draw=True)

        if cam_inverted:
            img = cv.flip(img, flipCode=1)

        if hands:
            if curr_time - time_since_last_sample >= sample_delay:

                hand = hands[0]
                curr_data = [hand["worldLmList"]]
                prediction = model.predict(curr_data)
                accuracy = int(max(prediction[0]) * 100)
                curr_letter = alphabet[np.argmax(prediction)]

                if curr_letter == last_letter:
                    #print(curr_letter, flush=True)
                    if curr_word_count <= max_word_count:
                        if len(attempted_word) < len(word):
                            attempted_word += curr_letter
                            total_letters += 1
                            if word[len(attempted_word) - 1] == curr_letter:
                                correct_letters += 1
                            curr_letter = ""
                last_letter = curr_letter
                time_since_last_sample = curr_time

            cv.putText(img, alphabet[np.argmax(prediction)] + ": " + str(accuracy) + "%", (10, 430), cv.FONT_HERSHEY_PLAIN,
                       2, (255, 0, 255), 2)

        WIN.fill(BLACK)
        img = cvt_cv_image(img)
        WIN.blit(img, (0, 0))

        target_word_rect = display_target_word(word)
        display_attempt(word, target_word_rect, attempted_word, WIN)




        if len(attempted_word) >= len(word):
            pygame.display.update()
            time.sleep(word_delay)
            word = gen_word()
            attempted_word = ""
            curr_word_count += 1
        if curr_word_count > max_word_count:
            WIN.fill(BLACK)
            accuracy_text = font.render("Accuracy: " + '{0:.2f}'.format(correct_letters / total_letters * 100) + "%", True, WHITE, BLACK)
            text_rect = accuracy_text.get_rect()
            text_rect.center = ((wCam + SPELL_WIN_WIDTH) // 2, hCam // 2)
            WIN.blit(accuracy_text, text_rect)
        pygame.display.update()

    pygame.quit()

def display_target_word(target_word):
    text = font.render(target_word, True, WHITE, BLACK)
    text_rect = text.get_rect()
    text_rect.center = (wCam + SPELL_WIN_WIDTH // 2, hCam // 2)

    WIN.blit(text, text_rect)
    return text_rect

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
