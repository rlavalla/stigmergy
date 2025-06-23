import csv
import math
import itertools
import random
import time

class BluePlane:
    def __init__(self, id, position, fuel):
        # Constructor method to initialize a BluePlane object with an id, position, and fuel
        self.id = id  # Unique identifier for the plane
        self.position = position  # 3D position of the plane (x, y, z coordinates)
        self.fuel = fuel  # Amount of fuel the plane has, in pounds
        self.weapons = []  # List to store the weapons the plane carries
        self.fuel_burn_rate = 2  # The rate at which the plane burns fuel per second, in pounds

    def add_weapon(self, weapon):
        # Method to add a weapon to the plane's inventory
        self.weapons.append(weapon)  # Add the given weapon to the weapons list

    def fire_weapon(self, weapon):
        # Method to fire a weapon
        if weapon in self.weapons:  # Check if the weapon is in the plane's inventory
            self.weapons.remove(weapon)  # Remove the weapon from the inventory
            return True  # Return True indicating the weapon was fired
        return False  # Return False if the weapon was not found in the inventory

    def move(self):
        # Method to move the plane to a new random position and consume fuel
        if self.fuel > 0:  # Check if the plane has fuel remaining
            # Update the plane's position by adding a random value between -20 and 20 to each coordinate
            self.position = (
                self.position[0] + random.uniform(-20, 20),
                self.position[1] + random.uniform(-20, 20),
                self.position[2] + random.uniform(-20, 20)
            )
            self.fuel -= self.fuel_burn_rate  # Reduce the fuel by the burn rate
            self.fuel = max(self.fuel, 0)  # Ensure the fuel does not go below zero
            # Print the plane's new position and remaining fuel
            print(f"Plane {self.id} moved to {self.position} and now has {self.fuel} pounds of fuel remaining")
        else:
            # Print a message if the plane has run out of fuel
            print(f"Plane {self.id} has run out of fuel")

class Weapon:
    def __init__(self, range, kinematics, expiring_factor):
        # Constructor method to initialize a Weapon object with range, kinematics, and expiring_factor
        self.range = range  # The maximum range of the weapon
        self.kinematics = kinematics  # The kinematic performance of the weapon
        self.expiring_factor = expiring_factor  # The expiring factor of the weapon

class Target:
    def __init__(self, id, position):
        # Constructor method to initialize a Target object with an id and position
        self.id = id  # Unique identifier for the target
        self.position = position  # 3D position of the target (x, y, z coordinates)

    def move(self):
        # Method to move the target to a new random position
        # Update the target's position by adding a random value between -25 and 25 to each coordinate
        self.position = (
            self.position[0] + random.uniform(-25, 25),
            self.position[1] + random.uniform(-25, 25),
            self.position[2] + random.uniform(-25, 25)
        )


def load_csv(filename):
    blue_planes = []  # List to store BluePlane objects
    targets = []  # List to store Target objects
    section = None  # Variable to keep track of the current section in the CSV file

    with open(filename, 'r') as csvfile:
        reader = csv.reader(csvfile)  # Create a CSV reader object
        for row in reader:
            if row:
                if row[0] == 'Blue Planes':  # Check if the section is 'Blue Planes'
                    section = 'blue_planes'
                    next(reader)  # Skip the header row
                elif row[0] == 'Weapons':  # Check if the section is 'Weapons'
                    section = 'weapons'
                    next(reader)  # Skip the header row
                elif row[0] == 'Targets':  # Check if the section is 'Targets'
                    section = 'targets'
                    next(reader)  # Skip the header row
                else:
                    if section == 'blue_planes':  # Process BluePlane data
                        # Create a new BluePlane object and add it to the list
                        blue_planes.append(BluePlane(int(row[0]), (float(row[1]), float(row[2]), float(row[3])), float(row[4])))
                    elif section == 'weapons':  # Process Weapon data
                        plane_id = int(row[0])  # Get the plane ID
                        for plane in blue_planes:  # Find the corresponding plane
                            if plane.id == plane_id:
                                # Add a new Weapon object to the plane
                                plane.add_weapon(Weapon(float(row[1]), float(row[2]), float(row[3])))
                    elif section == 'targets':  # Process Target data
                        # Create a new Target object and add it to the list
                        targets.append(Target(int(row[0]), (float(row[1]), float(row[2]), float(row[3]))))
    return blue_planes, targets  # Return the lists of blue planes and targets

def distance_3d(p1, p2):
    # Calculate the Euclidean distance between two 3D points
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2 + (p1[2] - p2[2])**2)

def angle_between(s1, s2, target):
    # Calculate the angle between two sensors (planes) relative to a target
    v1 = (target.position[0] - s1.position[0], target.position[1] - s1.position[1], target.position[2] - s1.position[2])
    v2 = (target.position[0] - s2.position[0], target.position[1] - s2.position[1], target.position[2] - s2.position[2])
    dot_product = sum(v1[i] * v2[i] for i in range(3))  # Compute the dot product of v1 and v2
    mag_v1 = math.sqrt(sum(v1[i]**2 for i in range(3)))  # Compute the magnitude of v1
    mag_v2 = math.sqrt(sum(v2[i]**2 for i in range(3)))  # Compute the magnitude of v2
    angle = math.degrees(math.acos(dot_product / (mag_v1 * mag_v2)))  # Calculate the angle in degrees
    return angle  # Return the calculated angle

def probability_of_guide(plane, weapon, target):
    # Calculate the Probability of Guide (PG) for a given plane, weapon, and target
    distance = distance_3d(plane.position, target.position)  # Calculate the distance between the plane and the target
    if distance > weapon.range:  # Check if the target is out of weapon range
        return 0  # Return 0 if the target is out of range
    # Calculate the PG using the provided formula
    pg = (1 / distance) * weapon.kinematics * weapon.expiring_factor * (plane.fuel / 100)
    # Print the details of the PG calculation
    print(f"PG Calculation for Plane {plane.id} with weapon range {weapon.range} km and Target {target.id}: "
          f"Distance = {distance:.2f} km, Kinematics = {weapon.kinematics}, Expiring Factor = {weapon.expiring_factor}, "
          f"Fuel = {plane.fuel}, PG = {pg:.4f}")
    return pg  # Return the calculated PG value

def get_reporting_sensors(target, reports):
    # Get all planes reporting the given target
    return [report[0] for report in reports if report[1] == target]

def select_best_pair(sensors, target):
    best_pair = None  # Initialize the best pair of sensors
    best_angle = float('inf')  # Initialize the best angle to infinity
    # Iterate over all combinations of two sensors
    for s1, s2 in itertools.combinations(sensors, 2):
        angle = abs(angle_between(s1, s2, target) - 90)  # Calculate the angle between the sensors and the target
        if angle < best_angle:  # Check if this angle is better (closer to 90 degrees)
            best_angle = angle  # Update the best angle
            best_pair = (s1, s2)  # Update the best pair
    if best_pair:
        # Print the details of the selected best pair
        print(f"Selected best pair for Target {target.id}: Plane {best_pair[0].id} and Plane {best_pair[1].id} with angle {best_angle:.2f} degrees")
    return best_pair  # Return the best pair of sensors

def select_best_weapon(blue_planes, target):
    best_weapon = None  # Initialize the best weapon
    best_pg = -float('inf')  # Initialize the best PG value
    best_plane = None  # Initialize the best plane
    # Sort planes by fuel to prioritize planes with lower fuel
    sorted_planes = sorted(blue_planes, key=lambda p: p.fuel)
    # Iterate over all sorted planes
    for plane in sorted_planes:
        # Iterate over all weapons of the current plane
        for weapon in plane.weapons:
            pg = probability_of_guide(plane, weapon, target)  # Calculate the PG for the current weapon
            if pg > best_pg:  # Check if this PG is better
                best_pg = pg  # Update the best PG
                best_weapon = weapon  # Update the best weapon
                best_plane = plane  # Update the best plane
    if best_pg > 0:
        # Print the details of the selected best weapon
        print(f"Selected best weapon for Target {target.id}: Plane {best_plane.id} with weapon range {best_weapon.range} km and PG {best_pg:.4f}")
        return best_plane, best_weapon  # Return the best plane and weapon
    else:
        # Print that no suitable weapon was found
        print(f"No suitable weapon found for Target {target.id} with PG > 0")
        return None, None  # Return None if no suitable weapon was found

def update_reports(reports, target, best_pair):
    # Remove any existing reports for the target
    reports = [(s, t) for s, t in reports if t != target]
    # Add new reports for the best pair of sensors
    reports.append((best_pair[0], target))
    reports.append((best_pair[1], target))
    return reports  # Return the updated reports

def ensure_make_before_break_handoff(current_report, new_report):
    current_plane, target = current_report  # Get the current plane and target
    new_plane, _ = new_report  # Get the new plane
    # Print the details of the handoff
    print(f"Handoff: Plane {new_plane.id} will take over reporting Target {target.id} from Plane {current_plane.id}")

def move_entities(blue_planes, targets):
    # Move all blue planes
    for plane in blue_planes:
        plane.move()
    # Move all targets
    for target in targets:
        target.move()

def main():
    blue_planes, targets = load_csv('input_data_3d_beastmode.csv')  # Load blue planes and targets from CSV file
    reports = []  # Initialize an empty list for reports

    plane_index = 0  # Initialize the plane index
    for target in targets:  # Assign each target to a plane initially
        plane = blue_planes[plane_index % len(blue_planes)]  # Select a plane in a round-robin manner
        reports.append((plane, target))  # Add the plane-target report
        print(f"Plane {plane.id} is initially reporting Target {target.id}")  # Print the initial assignment
        plane_index += 1  # Increment the plane index

    while targets and blue_planes:  # Continue while there are targets and blue planes
        move_entities(blue_planes, targets)  # Move planes and targets and decrement fuel

        reports = []  # Reset reports
        plane_index = 0  # Reset the plane index
        for target in targets:  # Re-assign each target to a plane
            if not blue_planes:  # Break if no blue planes are available
                break
            plane = blue_planes[plane_index % len(blue_planes)]  # Select a plane in a round-robin manner
            reports.append((plane, target))  # Add the plane-target report
            plane_index += 1  # Increment the plane index

        print("\nAfter Novel Track Reporting:")  # Print after novel track reporting
        for report in reports:
            print(f"Plane {report[0].id} is reporting Target {report[1].id}")  # Print the reports

        for target in targets:  # For each target
            reporting_sensors = get_reporting_sensors(target, reports)  # Get planes reporting the target
            if len(reporting_sensors) > 2:  # If more than two planes are reporting the target
                best_pair = select_best_pair(reporting_sensors, target)  # Select the best pair of planes
                reports = update_reports(reports, target, best_pair)  # Update the reports

        print("\nAfter Conflict Resolution and Pair Selection:")  # Print after conflict resolution and pair selection
        for report in reports:
            print(f"Plane {report[0].id} is reporting Target {report[1].id}")  # Print the reports

        for target in targets[:]:  # Iterate over a copy of the targets list
            best_plane, best_weapon = select_best_weapon(blue_planes, target)  # Select the best plane and weapon for the target
            blue_planes = [plane for plane in blue_planes if plane.fuel > 0]  # Remove planes with zero fuel
            if best_plane and best_weapon:  # If a suitable plane and weapon are found
                if best_plane.fire_weapon(best_weapon):  # Fire the weapon
                    targets.remove(target)  # Remove the target if hit
                    print(f"Target {target.id} shot down by Plane {best_plane.id} with weapon range {best_weapon.range} km")  # Print the result
                else:
                    print(f"Plane {best_plane.id} is unable to fire weapon range {best_weapon.range} km for Target {target.id} because it has already been used")  # Print if unable to fire the weapon

            move_entities(blue_planes, targets)  # Move planes and targets, and decrement fuel

            reports = []  # Reset reports
            plane_index = 0  # Reset the plane index
            for target in targets:  # Re-assign each target to a plane
                if not blue_planes:  # Break if no blue planes are available
                    break
                plane = blue_planes[plane_index % len(blue_planes)]  # Select a plane in a round-robin manner
                reports.append((plane, target))  # Add the plane-target report
                plane_index += 1  # Increment the plane index

            print("\nAfter Novel Track Reporting:")  # Print after novel track reporting
            for report in reports:
                print(f"Plane {report[0].id} is reporting Target {report[1].id}")  # Print the reports

            for target in targets:  # For each target
                reporting_sensors = get_reporting_sensors(target, reports)  # Get planes reporting the target
                if len(reporting_sensors) > 2:  # If more than two planes are reporting the target
                    best_pair = select_best_pair(reporting_sensors, target)  # Select the best pair of planes
                    reports = update_reports(reports, target, best_pair)  # Update the reports

            print("\nAfter Conflict Resolution and Pair Selection:")  # Print after conflict resolution and pair selection
            for report in reports:
                print(f"Plane {report[0].id} is reporting Target {report[1].id}")  # Print the reports

        print("\nRemaining Fuel Levels:")  # Print the remaining fuel levels of planes
        for plane in blue_planes:  # For each plane in the blue planes list
            print(f"Plane {plane.id} has {plane.fuel} pounds of fuel remaining")  # Print the plane's ID and its remaining fuel

        time.sleep(1)  # Wait for 1 second before the next iteration

if __name__ == "__main__":
    main()  # Run the main function if this script is executed directly


