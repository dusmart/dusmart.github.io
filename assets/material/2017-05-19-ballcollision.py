import time
import math
from random import random
import Tkinter


class ball:
    """ ball class, description of the ball
    """
    canvas = None
    pic_handler = None
    rx, ry, vx, vy = 0.0, 0.0, 0.0, 0.0
    radius = 0.0
    mass = 0.0
    count = 0
    color = "black"

    def __init__(self, canvas, pos=(0, 0), speed=(0, 0), r=0, m=0, color="black"):
        self.canvas = canvas
        self.rx, self.ry = pos
        self.vx, self.vy = speed
        self.radius = r
        self.mass = m
        self.color = color

        width = int(self.canvas["width"])
        height = int(self.canvas["height"])
        self.pic_handler = canvas.create_oval((self.rx-r)*width, (self.ry-r)*height, (self.rx+r)*width, (self.ry+r)*height, fill=color)

    def move(self, dt):
        self.rx += self.vx * dt
        self.ry += self.vy * dt

        width = int(self.canvas["width"])
        height = int(self.canvas["height"])
        self.canvas.move(self.pic_handler, self.vx*dt*width, self.vy*dt*height)
        if dt<0 and dt>-0.0000000001: return
        time.sleep(dt)

    def timeToHit(self, other):
        if self == other: return -1  # one ball can not hit itself
        dx, dy = other.rx - self.rx, other.ry - self.ry
        dvx, dvy = other.vx - self.vx, other.vy - self.vy
        dvdr = dx * dvx + dy * dvy
        if dvdr > 0: return -1  # two balls is in different direction
        dvdv = dvx * dvx + dvy * dvy
        drdr = dx * dx + dy * dy
        sigma = self.radius + other.radius
        tmp_distance = (dvdr * dvdr) - dvdv * (drdr - sigma * sigma)
        if tmp_distance < 0 or dvdv == 0: return -1  # two balls won't collide when they are near
        return -(dvdr + math.sqrt(tmp_distance)) / dvdv

    def timeToHitHorizontalWall(self):
        if self.vy > 0:
            return (1.0 - self.ry - self.radius) / self.vy
        elif self.vy < 0:
            return (self.ry - self.radius) / -self.vy
        else:
            return -1

    def timeToHitVerticalWall(self):
        if self.vx > 0:
            return (1.0 - self.rx - self.radius) / self.vx
        elif self.vx < 0:
            return (self.rx - self.radius) / -self.vx
        else:
            return -1

    def hit(self, other):
        dx, dy = other.rx - self.rx, other.ry - self.ry
        dvx, dvy = other.vx - self.vx, other.vy - self.vy
        dvdr = dx * dvx + dy * dvy
        dist = self.radius + other.radius
        J = 2 * self.mass * other.mass * dvdr / ((self.mass + other.mass) * dist)
        Jx = J * dx / dist
        Jy = J * dy / dist
        self.vx += Jx / self.mass
        self.vy += Jy / self.mass
        other.vx -= Jx / other.mass
        other.vy -= Jy / other.mass
        self.count += 1
        other.count += 1

    def hitHorizontalWall(self):
        self.vy = -self.vy
        self.count += 1

    def hitVerticalWall(self):
        self.vx = -self.vx
        self.count += 1


class event:
    time = -1
    ball_a, ball_b = None, None  # two ball
    count_a, count_b = None, None

    def __init__(self, the_time, ball_a, ball_b):
        self.time = the_time
        self.ball_a = ball_a
        self.ball_b = ball_b
        if ball_a is not None: self.count_a = ball_a.count
        if ball_b is not None: self.count_b = ball_b.count

    def is_valid(self):
        if self.ball_a is not None and self.ball_a.count != self.count_a: return False
        if self.ball_b is not None and self.ball_b.count != self.count_b: return False
        return True


class minpq:
    queue = [None]

    def float(self, num):
        while num > 1 and self.queue[num / 2].time > self.queue[num].time:
            tmp = self.queue[num / 2]
            self.queue[num / 2] = self.queue[num]
            self.queue[num] = tmp
            num /= 2

    def sink(self, num):
        while num * 2 < len(self.queue):
            son = num * 2
            if num * 2 + 1 < len(self.queue) and self.queue[num * 2 + 1].time < self.queue[son].time:
                son = num * 2 + 1
            if self.queue[son].time < self.queue[num].time:
                tmp = self.queue[son]
                self.queue[son] = self.queue[num]
                self.queue[num] = tmp
                num = son
            else:
                break

    def insert(self, new_event):
        self.queue.append(new_event)
        self.float(len(self.queue) - 1)

    def pop(self):
        assert not self.isEmpty()
        soon_event = self.queue[1]
        self.queue[1] = self.queue[len(self.queue) - 1]
        self.sink(1)
        self.queue.pop()
        return soon_event

    def isEmpty(self):
        return len(self.queue) <= 1


class collision:
    pq = minpq()
    t = 0.0
    balls = []
    tk = None

    def __init__(self, tk, balls):
        self.balls = balls
        self.tk = tk

    def predict(self, ball_a):
        if ball_a is None: return
        for other in self.balls:
            dt = ball_a.timeToHit(other)
            if dt != -1: self.pq.insert(event(self.t+dt, ball_a, other))
        dt = ball_a.timeToHitHorizontalWall()
        if dt != -1: self.pq.insert(event(self.t+dt, None, ball_a))
        dt = ball_a.timeToHitVerticalWall()
        if dt != -1: self.pq.insert(event(self.t+dt, ball_a, None))

    def redraw(self):
        pass

    def simulate(self):
        timepiece = 0.003
        pq = self.pq
        balls = self.balls
        for i in self.balls: self.predict(i)
        # pq.insert(event(0, None, None))
        while not pq.isEmpty():
            newevent = pq.pop()
            if not newevent.is_valid(): continue
            a = newevent.ball_a
            b = newevent.ball_b
            while newevent.time - self.t > timepiece:
                for i in balls:
                    i.move(timepiece)
                self.t += timepiece
                self.tk.update()
            for i in balls:
                i.move(newevent.time - self.t)
            self.t = newevent.time
            self.tk.update()

            if a is not None and b is not None:
                a.hit(b)
            elif a is not None and b is None:
                a.hitVerticalWall()
            elif a is None and b is not None:
                b.hitHorizontalWall()
            else:
                self.redraw()
            self.predict(a)
            self.predict(b)


def main():
    tk = Tkinter.Tk()
    canvas = Tkinter.Canvas(tk, width=400, height=400)
    canvas.pack()

    balls = []
    for i in range(3):
        for j in range(3):
            r = random() / 30 + 0.02
            new = ball(canvas, (0.3*(i+1), 0.3*(j+1)), (random()+0.1, random()+0.1), r, r*r)
            balls.append(new)


    test = collision(tk, balls)
    test.simulate()
if __name__ == "__main__":
    main()