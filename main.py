import pygame, sys
from enum import Enum

class State(Enum):
    NO = 0
    POINT = 1
    SIDE = 2

class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y)

    def mul(self, c):
        return Vector(self.x * c, self.y * c)

    def size(self):
        return (self.x ** 2 + self.y ** 2) ** 0.5

    def normalize(self):
        return Vector(self.x / self.size(), self.y / self.size())

class Rect:
    next_id = 1
    def __init__(self, mid, h, w, set_id = True):
        # 중점 좌표 벡터 / 너비,높이 벡터
        self.mid = mid
        self.h = h
        self.w = w
        if set_id:
            self.id = Rect.next_id
            Rect.next_id += 1
        else:
            self.id = -1

    def to_coord(self):
        ret = []
        dx = (1, -1, -1, 1)
        dy = (1, 1, -1, -1)
        for a, b in zip(dx, dy):
            nowx = self.mid.x + self.h.x * a + self.w.x * b
            nowy = self.mid.y + self.h.y * a + self.w.y * b
            ret.append((nowx, nowy))
        return ret

    def draw(self):
        if self.id == -1:
            pygame.draw.polygon(screen, RED, self.to_coord(), 3)
            return
        pygame.draw.polygon(screen, BLACK, self.to_coord(), 3)
        id_render = font_consolas.render(f'#{self.id}', True, BLACK)
        screen.blit(id_render, id_render.get_rect(center=(self.mid.x, self.mid.y)))

def dot(va, vb):
    return va.x * vb.x + va.y * vb.y

def is_colide(rectA, rectB):
    axisList = (rectA.h, rectA.w, rectB.h, rectB.w)
    diff = rectA.mid - rectB.mid
    for axis in axisList:
        now = 0
        unit = axis.normalize()
        dist = abs(dot(diff, unit))
        for v in axisList:
            now += abs(dot(v, unit))
        if now <= dist:
            return False
    return True

def add_rect(new_rect):
    for r in rect_list:
        if is_colide(r, new_rect):
            collision_list.append((r.id, new_rect.id))
    rect_list.append(new_rect)

def write_collision():
    global WIDTH
    for idx, c in enumerate(collision_list):
        txt_render = font_consolas.render(f'#{c[0]} - #{c[1]}', True, BLACK)
        screen.blit(txt_render, (WIDTH - 200 + 30, 30 + idx * 40))

def update_state(pos):
    global MOUSE_STATE, WIDTH, drawing
    if pos[0] > WIDTH - 200:
        return
    drawing.append(pos)
    if MOUSE_STATE == State.NO:
        MOUSE_STATE = State.POINT
    elif MOUSE_STATE == State.POINT:
        MOUSE_STATE = State.SIDE
    else:
        v1 = Vector(drawing[1][0] - drawing[0][0], drawing[1][1] - drawing[0][1])
        # normal = v1의 법선단위벡터
        normal = Vector(drawing[0][1] - drawing[1][1], drawing[1][0] - drawing[0][0]).normalize()
        tmp = Vector(drawing[2][0] - drawing[1][0], drawing[2][1] - drawing[1][1])
        v2 = normal.mul(dot(tmp, normal))
        add_rect(Rect(Vector(*drawing[0]), v1, v2))
        drawing = []
        MOUSE_STATE = State.NO

def draw_screen():
    global WIDTH, HEIGHT, MOUSE_STATE
    screen.fill('#ece6cc')
    for r in rect_list:
        r.draw()

    now = pygame.mouse.get_pos()
    if MOUSE_STATE == State.POINT:
        pygame.draw.line(screen, RED, now, (drawing[0][0] * 2 - now[0], drawing[0][1] * 2 - now[1]), 3)
    elif MOUSE_STATE == State.SIDE:
        v1 = Vector(drawing[1][0] - drawing[0][0], drawing[1][1] - drawing[0][1])
        # normal = v1의 법선단위벡터
        normal = Vector(drawing[0][1] - drawing[1][1], drawing[1][0] - drawing[0][0]).normalize()
        tmp = Vector(now[0] - drawing[1][0], now[1] - drawing[1][1])
        v2 = normal.mul(dot(tmp, normal))
        Rect(Vector(*drawing[0]), v1, v2, False).draw()

    pygame.draw.rect(screen, WHITE, (WIDTH - 200, 0, 200, HEIGHT))
    write_collision()
    

pygame.init()
WIDTH = pygame.display.Info().current_w - 100
HEIGHT = pygame.display.Info().current_h - 100
BLACK = (0,0,0)
WHITE = (255,255,255)
RED = (255,0,0)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('OBB')

MOUSE_STATE = State.NO
drawing = []
rect_list = []
collision_list = []
font_consolas = pygame.font.SysFont('consolas', 25)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONUP:
            update_state(pygame.mouse.get_pos())
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                MOUSE_STATE = State.NO
                drawing = []
            elif event.key == pygame.K_BACKSPACE:
                collision_list = []
                rect_list = []
                Rect.next_id = 1
    draw_screen()
    pygame.display.update()
