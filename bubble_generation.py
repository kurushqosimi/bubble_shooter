import cv2
import numpy as np
import os

# Папка для сохранения
os.makedirs("assets", exist_ok=True)

# Цвета шаров и имена файлов
balls = {
    "red": (255, 0, 0),
    "green": (0, 255, 0),
    "blue": (0, 0, 255),
    "yellow": (255, 255, 0),
    "purple": (128, 0, 128),
}

BALL_SIZE = 40  # 40x40 пикселей
RADIUS = BALL_SIZE // 2

for name, color in balls.items():
    # Создаем изображение с альфа-каналом (RGBA)
    img = np.zeros((BALL_SIZE, BALL_SIZE, 4), dtype=np.uint8)

    # Рисуем круг в центре
    center = (RADIUS, RADIUS)
    cv2.circle(img, center, RADIUS, color + (255,), thickness=-1)

    # Сохраняем в файл
    filepath = os.path.join("assets", f"{name}.png")
    cv2.imwrite(filepath, img)
    print(f"Saved: {filepath}")
