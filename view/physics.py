import math


def limit_speed(vx, vy, max_speed):
    speed = math.hypot(vx, vy)
    if speed <= max_speed or max_speed <= 0:
        return vx, vy
    scale = max_speed / speed
    return vx * scale, vy * scale


def resolve_circle_collision(a, b, restitution=0.8):
    dx = b.center_x - a.center_x
    dy = b.center_y - a.center_y
    distance = math.hypot(dx, dy)
    min_distance = a.radius + b.radius
    if distance <= 0 or distance > min_distance:
        return False

    nx = dx / distance
    ny = dy / distance
    overlap = min_distance - distance

    total_mass = a.mass + b.mass
    if total_mass <= 0:
        total_mass = 1.0
    a_share = b.mass / total_mass
    b_share = a.mass / total_mass

    a.center_x -= nx * overlap * a_share
    a.center_y -= ny * overlap * a_share
    b.center_x += nx * overlap * b_share
    b.center_y += ny * overlap * b_share

    rvx = b.velocity[0] - a.velocity[0]
    rvy = b.velocity[1] - a.velocity[1]
    vel_along_normal = rvx * nx + rvy * ny
    if vel_along_normal > 0:
        return True

    e = max(0.0, min(1.0, restitution))
    j = -(1 + e) * vel_along_normal
    j /= (1 / a.mass) + (1 / b.mass)

    impulse_x = j * nx
    impulse_y = j * ny

    a.velocity[0] -= impulse_x / a.mass
    a.velocity[1] -= impulse_y / a.mass
    b.velocity[0] += impulse_x / b.mass
    b.velocity[1] += impulse_y / b.mass
    return True
