import csv
import math
import itertools
import random
import time

class BluePlane:
    def __init__(self, id, position, fuel):
        self.id = id
        self.position = position
        self.fuel = fuel
        self.weapons = []

    def add_weapon(self, weapon):
        self.weapons.append(weapon)

    def fire_weapon(self, weapon):
        if weapon in self.weapons:
            self.weapons.remove(weapon)
            return True
        return False

    def move(self):
        # Simulate random movement in 3D space
        self.position = (
            self.position[0] + random.uniform(-5, 5),
            self.position[1] + random.uniform(-5, 5),
            self.position[2] + random.uniform(-5, 5)
        )

class Weapon:
    def __init__(self, range, kinematics, expiring_factor):
        self.range = range
        self.kinematics = kinematics
        self.expiring_factor = expiring_factor

class Target:
    def __init__(self, id, position):
        self.id = id
        self.position = position

    def move(self):
        # Simulate random movement in 3D space
        self.position = (
            self.position[0] + random.uniform(-3, 3),
            self.position[1] + random.uniform(-3, 3),
            self.position[2] + random.uniform(-3, 3)
        )

def load_csv(filename):
    blue_planes = []
    targets = []
    section = None

    with open(filename, 'r') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if row:
                if row[0] == 'Blue Planes':
                    section = 'blue_planes'
                    next(reader)  # Skip header row
                elif row[0] == 'Weapons':
                    section = 'weapons'
                    next(reader)  # Skip header row
                elif row[0] == 'Targets':
                    section = 'targets'
                    next(reader)  # Skip header row
                else:
                    if section == 'blue_planes':
                        blue_planes.append(BluePlane(int(row[0]), (float(row[1]), float(row[2]), float(row[3])), float(row[4])))
                    elif section == 'weapons':
                        plane_id = int(row[0])
                        for plane in blue_planes:
                            if plane.id == plane_id:
                                plane.add_weapon(Weapon(float(row[1]), float(row[2]), float(row[3])))
                    elif section == 'targets':
                        targets.append(Target(int(row[0]), (float(row[1]), float(row[2]), float(row[3]))))
    
    return blue_planes, targets

def distance_3d(p1, p2):
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2 + (p1[2] - p2[2])**2)

def angle_between(s1, s2, target):
    v1 = (target.position[0] - s1.position[0], target.position[1] - s1.position[1], target.position[2] - s1.position[2])
    v2 = (target.position[0] - s2.position[0], target.position[1] - s2.position[1], target.position[2] - s2.position[2])
    dot_product = sum(v1[i] * v2[i] for i in range(3))
    mag_v1 = math.sqrt(sum(v1[i]**2 for i in range(3)))
    mag_v2 = math.sqrt(sum(v2[i]**2 for i in range(3)))
    angle = math.degrees(math.acos(dot_product / (mag_v1 * mag_v2)))
    return angle

def probability_of_guide(plane, weapon, target):
    """
    Calculate the Probability of Guide (PG) for a weapon-target pair.
    PG is a relative measure of the likelihood that the weapon can effectively engage the target.
    A higher PG indicates a better likelihood of engagement success, but it is not an absolute probability of kill.
    """
    distance = distance_3d(plane.position, target.position)
    if distance > weapon.range:
        return 0  # Weapon cannot reach the target
    pg = (1 / distance) * weapon.kinematics * weapon.expiring_factor * (plane.fuel / 100)
    print(f"PG Calculation for Plane {plane.id} with weapon range {weapon.range} and Target {target.id}: "
          f"Distance = {distance:.2f}, Kinematics = {weapon.kinematics}, Expiring Factor = {weapon.expiring_factor}, "
          f"Fuel = {plane.fuel}, PG = {pg:.4f}")
    return pg

def get_reporting_sensors(target, reports):
    return [report[0] for report in reports if report[1] == target]

def select_best_pair(sensors, target):
    best_pair = None
    best_angle = float('inf')
    for s1, s2 in itertools.combinations(sensors, 2):
        angle = abs(angle_between(s1, s2, target) - 90)
        if angle < best_angle:
            best_angle = angle
            best_pair = (s1, s2)
    if best_pair:
        print(f"Selected best pair for Target {target.id}: Plane {best_pair[0].id} and Plane {best_pair[1].id} with angle {best_angle:.2f} degrees")
    return best_pair

def select_best_weapon(blue_planes, target):
    best_weapon = None
    best_pg = -float('inf')
    best_plane = None
    for plane in blue_planes:
        for weapon in plane.weapons:
            pg = probability_of_guide(plane, weapon, target)
            if pg > best_pg:
                best_pg = pg
                best_weapon = weapon
                best_plane = plane
    if best_plane and best_weapon:
        print(f"Selected best weapon for Target {target.id}: Plane {best_plane.id} with weapon range {best_weapon.range} and PG {best_pg:.4f}")
    return best_plane, best_weapon

def update_reports(reports, target, best_pair):
    reports = [(s, t) for s, t in reports if t != target]
    reports.append((best_pair[0], target))
    reports.append((best_pair[1], target))
    return reports

def ensure_make_before_break_handoff(current_report, new_report):
    """
    Ensure that the new sensor is ready to take over tracking before the current sensor stops reporting.
    """
    current_plane, target = current_report
    new_plane, _ = new_report
    print(f"Handoff: Plane {new_plane.id} will take over reporting Target {target.id} from Plane {current_plane.id}")
    # Perform any additional handoff logic here, such as notifying the planes or updating the state

def move_entities(blue_planes, targets):
    for plane in blue_planes:
        plane.move()
    for target in targets:
        target.move()

def main():
    blue_planes, targets = load_csv('input_data_3d.csv')
    reports = []
    weapon_target_pairs = []

    # Stigmergic Novel Track Reporting
    plane_index = 0
    for target in targets:
        plane = blue_planes[plane_index % len(blue_planes)]
        reports.append((plane, target))
        print(f"Plane {plane.id} is initially reporting Target {target.id}")
        plane_index += 1

    while targets:
    # Simulate movement of planes and targets
    	move_entities(blue_planes, targets)

	# Clear previous reports
    	reports = []

    	# Stigmergic Novel Track Reporting
    	plane_index = 0
    	for target in targets:
        	plane = blue_planes[plane_index % len(blue_planes)]
        	reports.append((plane, target))
        	plane_index += 1

    	# Print reports for demonstration
    	print("\nAfter Novel Track Reporting:")
    	for report in reports:
        	print(f"Plane {report[0].id} is reporting Target {report[1].id}")

    	# Stigmergic Conflict Resolution and Pair Selection
    	for target in targets:
        	reporting_sensors = get_reporting_sensors(target, reports)
        	if len(reporting_sensors) > 2:
            		best_pair = select_best_pair(reporting_sensors, target)
            		reports = update_reports(reports, target, best_pair)

    	# Print reports for demonstration
    	print("\nAfter Conflict Resolution and Pair Selection:")
    	for report in reports:
        	print(f"Plane {report[0].id} is reporting Target {report[1].id}")

    	# Stigmergic Weapon Selection using PG Algorithm
    	for target in targets[:]:  # Iterate over a copy of the list to allow removal
        	best_plane, best_weapon = select_best_weapon(blue_planes, target)
        	if best_plane and best_weapon:
            		if best_plane.fire_weapon(best_weapon):
                		weapon_target_pairs.append((best_plane, best_weapon, target))
                		targets.remove(target)  # Target is shot down
                		reports = [(s, t) for s, t in reports if t != target]  # Update reports
                		print(f"Target {target.id} shot down by Plane {best_plane.id} with weapon range {best_weapon.range}")
            		else:
                		print(f"Plane {best_plane.id} is unable to fire weapon range {best_weapon.range} for Target {target.id} because it has already been used")

    	# Print weapon to target pairs
    	print("\nWeapon to target pairs:")
    	for pair in weapon_target_pairs:
        	print(f"Plane {pair[0].id} with weapon range {pair[1].range} is assigned to Target {pair[2].id}")

    	# Redundant Sensor Reallocation
    	for target in targets:
        	reporting_sensors = get_reporting_sensors(target, reports)
        	if len(reporting_sensors) > 2:
            		best_pair = select_best_pair(reporting_sensors, target)
            		for sensor in reporting_sensors:
                		if sensor not in best_pair:
                    			current_report = (sensor, target)
                    			new_report = (best_pair[0], target) if best_pair[0] != sensor else (best_pair[1], target)
                    			ensure_make_before_break_handoff(current_report, new_report)
                    			reports = [(s, t) for s, t in reports if (s, t) != (sensor, target)]
                    			print(f"Plane {sensor.id} stops reporting Target {target.id} to reduce redundancy")

    	# Print final sensor reports for demonstration
    	print("\nFinal sensor reports:")
    	for report in reports:
        	print(f"Plane {report[0].id} is reporting Target {report[1].id}")

   	 # Simulate real-time updates with a delay
    	time.sleep(2)

if __name__ == "__main__":
    main()
