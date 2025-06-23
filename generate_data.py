import csv
import random

def generate_csv(filename):
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        
        # Write blue planes
        writer.writerow(['Blue Planes'])
        writer.writerow(['id', 'x_position', 'y_position', 'z_position', 'fuel'])
        for i in range(1, 11):  # 10 blue planes
            if i == 10:
                fuel = 30  # Ensure plane 10 gets 30 pounds of fuel
            else:
                fuel = random.uniform(10, 100)
            writer.writerow([i, random.uniform(0, 100), random.uniform(0, 100), random.uniform(0, 10), fuel])
        
        # Write weapons
        writer.writerow(['Weapons'])
        writer.writerow(['plane_id', 'range', 'kinematics', 'expiring_factor'])
        weapons = {
            1: [100, 200, 300, 400, 500],
            2: [100, 200, 300, 100, 100],
            3: [200, 300, 500, 500, 100],
            4: [100, 100, 500, 500, 500],
            5: [200, 300, 200, 400, 100],
            6: [600, 600, 600, 600, 600],
            7: [400, 600, 100, 600, 200],
            8: [500, 500, 500, 500, 500],
            9: [300, 300, 400, 600, 500],
            10: [1000, 1000, 1000, 1000, 1000]
        }
        for plane_id, ranges in weapons.items():
            for r in ranges:
                writer.writerow([plane_id, r, random.uniform(1, 2), random.uniform(1, 2)])
        
        # Write red planes (targets)
        writer.writerow(['Targets'])
        writer.writerow(['id', 'x_position', 'y_position', 'z_position'])
        for i in range(1, 51):  # 50 red planes
            writer.writerow([i, random.uniform(0, 100), random.uniform(0, 100), random.uniform(10, 100)])

generate_csv('input_data_3d_beastmode.csv')
