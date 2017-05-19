---
layout:     post
title:      "Simulation of ball collision"
author:     "dusmart"
tags:
    - project
    - code
---

>  Simulate the motion of N moving particles that behave according to the laws of elastic collision.

<!--more-->

> [This is a project of Algorithms course from coursera.](https://www.coursera.org/learn/algorithms-part1/)

## time-driven vs event-driven

Instead of using time-driven simulation, we use event-driven simulation for these reasons.

1. Time-driven simulation need O(N<sup>2</sup>) checks for every step while event-driven only need O(NlogN) checks for every step in average.
2. Time-driven simulation depends on the dt(the minimum time piece) very much. Lots of collisions may be missed if dt is too large while process will be slow if dt is too small. But dt depends on specific scene, we can't determine it easily. In event-driven simulation, dt doesn't matter.

## main idea

The main idea of event-driven simulation to this is to maintain a min-heap that contains every possible collision event in the future. 

Therefore, most of those events will be invalid after one collision. For example, assuming that ball1 and ball2 collide with each other, all events calculated by last step which related to ball1 and ball2 will be invalid. To detect if a event is valid, we need to add some extra information besides the event's time. How many times the balls related to the event have collide others is a good information. Because if the balls have collided others before the event happened, that event must be invalid. 

Everytime when we found that there will be a collision within time dt, we pop that collision event and check if it's still valid. If it's valid, calculate the new states after that collision and update the animation. If it's not valid, just throw away the event and update all positions by every ball's speed.

## analyze

The most difficult thing is how to predict when a two balls collision event will happen and what is the new speed after a collision. The new possible event time can be calculated by geometry tricks. The new speed is not that easy. Here is a paper related to this.[click me](/assets/material/2017-05-19-paper.pdf)

![img](/assets/img/2017-05-19-1.jpg)

Figure 1: How to calculate the new speed of two balls after collision


The size of the min-heap depend on the balls number. After executing the program for a long time, the heap size will be dynamically stable. That is to say, every time you pop 2n events, there will be one valid event because you insert 2n new events to the heap after every valid collision. Therefore, the actual time complexity is O(2n*2nlog(2n)) = O(n<sup>2</sup>logn) for every valid collision.

## code structure

```
public class Particle
{
    private double rx, ry; // position
    private double vx, vy; // velocity
    private final double radius; // radius
    private final double mass; // mass
    private int count; // number of collisions
    private Color color;

    public Particle(double rx, double ry, double vx, double vy, double radius, double mass, Color color);
    public void move(double dt);
    public double timeToHit(Particle that);
    public void bounceOff(Particle that);
}
private class Event implements Comparable<Event> {
    private double time; // time of event
    private Particle a, b; // particles involved in event
    private int countA, countB; // collision counts for a and b
    public Event(double t, Particle a, Particle b);
    public int compareTo(Event that);
    public boolean isValid();
}
public class CollisionSystem
{
    private MinPQ<Event> pq; // the priority queue
    private double t = 0.0; // simulation clock time
    private Particle[] particles; // the array of particles
    public CollisionSystem(Particle[] particles);
    private void predict(Particle a);
    private void redraw();
    public void simulate();
    private class Event implements Comparable<Event>{}
    public static void main(String[] args);
}
```

This is a jar file with source code in it(based on a drawing package). [click me](/assets/material/2017-05-19-ballcollision.jar)

This is a Python file translated from java. [click me](/assets/material/2017-05-19-ballcollision.py)

![img](/assets/img/2017-05-19-2.png)

Figure 2: A collision example