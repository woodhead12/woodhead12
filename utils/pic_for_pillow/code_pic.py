import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter


def check_code(width=120, height=30, char_length=6, font_file='./utils/pic_for_pillow/BadScript-Regular.ttf', font_size=20):
    code = []
    img = Image.new(mode='RGB', size=(width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img, mode='RGB')

    # 生成随机字母
    def random_chr():
        return chr(random.randint(65, 90))

    # 生成随机颜色
    def random_color():
        return random.randint(0, 255), random.randint(10, 255), random.randint(64, 255)

    # 根据指定字体书写文字
    font = ImageFont.truetype(font_file, font_size)
    for i in range(char_length):
        char = random_chr()
        code.append(char)
        h = random.randint(0, 4)
        draw.text([i * width / char_length, h], char, font=font, fill=random_color())

    # 写干扰点
    for i in range(40):
        draw.point([random.randint(0, width), random.randint(0, height)], fill=random_color())

    # 写干扰圆圈
    for i in range(40):
        draw.point([random.randint(0, width), random.randint(0, height)], fill=random_color())
        x = random.randint(0, width)
        y = random.randint(0, height)
        draw.arc((x, y, x + 4, y + 4), 0, 90, fill=random_color())

    # 画干扰线
    for i in range(5):
        x1 = random.randint(0, width)
        y1 = random.randint(0, height)
        x2 = random.randint(0, width)
        y2 = random.randint(0, height)

        draw.line((x1, y1, x2, y2), fill=random_color())

    new_img = img.filter(ImageFilter.EDGE_ENHANCE_MORE)
    return new_img, ''.join(code)


if __name__ == '__main__':
    img, code = check_code()
    with open('code.png', 'wb') as f:
        img.save(f, format='png')