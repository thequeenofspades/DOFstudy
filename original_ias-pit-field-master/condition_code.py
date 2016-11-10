import random

# Create 64 random conditions
conditions = [x for x in xrange(64)]

# Shuffle the conditions
random.seed()
random.shuffle(conditions)

def pick_condition():
    if conditions:
        return conditions.pop()

def set_condition(condition):
    status = []

    latency_toggle(condition & (1 << 0))
    status.extend(["latency: " + str(bool(condition & (1 << 0)))])

    stereo_toggle(condition & (1 << 1))
    status.extend(["stereo: " + str(bool(condition & (1 << 1)))])

    fov_toggle(condition & (1 << 2))
    status.extend(["fov: " + str(bool(condition & (1 << 2)))])

    fps_toggle(condition & (1 << 3))
    status.extend(["fps: " + str(bool(condition & (1 << 3)))])

    dof_toggle(condition & (1 << 4))
    status.extend(["dof: " + str(bool(condition & (1 << 4)))])

    timewarp_toggle(condition & (1 << 5))
    status.extend(["timewarp: " + str(bool(condition & (1 << 5)))])

    print status
