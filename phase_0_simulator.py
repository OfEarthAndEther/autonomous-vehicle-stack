"""
PHASE 0: Toy Simulator - 2D Car Moving on Grid
A simple simulation that reads fake sensor values and updates car state.
"""

import math
import random
from dataclasses import dataclass, field
from typing import List, Tuple

@dataclass
class Vector2D:
    """2D vector for position"""
    x: float = 0.0
    y: float = 0.0
    
    def __add__(self, other):
        return Vector2D(self.x + other.x, self.y + other.y)
    
    def __mul__(self, scalar):
        return Vector2D(self.x * scalar, self.y * scalar)
    
    def distance_to(self, other):
        dx = self.x - other.x
        dy = self.y - other.y
        return math.sqrt(dx*dx + dy*dy)

@dataclass
class Obstacle:
    """Obstacle in the world"""
    position: Vector2D
    radius: float = 5.0
    
    def distance_to(self, pos: Vector2D):
        return pos.distance_to(self.position) - self.radius

@dataclass
class CarState:
    """Vehicle state"""
    position: Vector2D = field(default_factory=lambda: Vector2D(250, 250))
    heading: float = 0.0          # Radians (0 = right, pi/2 = up)
    speed: float = 5.0            # m/s
    steering: float = 0.0         # -1 to 1 (left to right)
    acceleration: float = 0.0     # m/s^2
    
    # Sensor readings
    lane_offset: float = 0.0      # Distance from lane center (m)
    front_distance: float = 50.0  # Distance to obstacle ahead (m)
    right_distance: float = 50.0  # Distance to right obstacle
    left_distance: float = 50.0   # Distance to left obstacle
    
    def __str__(self):
        return (f"Pos:({self.position.x:.1f},{self.position.y:.1f}) "
                f"Heading:{math.degrees(self.heading):.1f}° "
                f"Speed:{self.speed:.2f}m/s "
                f"LaneOffset:{self.lane_offset:.2f}m "
                f"FrontDist:{self.front_distance:.2f}m")

class ToySimulator:
    """Simple 2D car simulator"""
    
    def __init__(self, world_width=500, world_height=500):
        self.world_width = world_width
        self.world_height = world_height
        self.car = CarState()
        self.obstacles: List[Obstacle] = []
        self.time_ms = 0
        self.lane_center_y = world_height / 2
        self.dt = 0.005  # 5ms per simulation step
        
        # Generate random obstacles
        self._generate_obstacles()
    
    def _generate_obstacles(self):
        """Create random obstacles"""
        self.obstacles = [
            Obstacle(Vector2D(150, 250), 8.0),
            Obstacle(Vector2D(300, 200), 8.0),
            Obstacle(Vector2D(350, 280), 8.0),
        ]
    
    def update(self, steering_command: float = 0.0, 
               throttle_command: float = 0.0,
               brake_command: float = 0.0):
        """
        Update car state
        steering: -1 (left) to 1 (right)
        throttle: 0-1
        brake: 0-1
        """
        # Update steering
        max_steering_angle = math.radians(30)
        self.car.steering = max(-1, min(1, steering_command))
        
        # Update speed
        accel = throttle_command * 5.0 - brake_command * 8.0
        self.car.speed = max(0, min(15, self.car.speed + accel * self.dt))
        
        # Update heading (bicycle model)
        if abs(self.car.speed) > 0.1:
            wheelbase = 2.5  # Car length
            turning_angle = self.car.steering * max_steering_angle
            yaw_rate = (self.car.speed / wheelbase) * math.tan(turning_angle)
            self.car.heading += yaw_rate * self.dt
            self.car.heading = self.car.heading % (2 * math.pi)
        
        # Update position
        dx = self.car.speed * math.cos(self.car.heading) * self.dt
        dy = self.car.speed * math.sin(self.car.heading) * self.dt
        self.car.position = self.car.position + Vector2D(dx, dy)
        
        # Wrap around world
        self.car.position.x = self.car.position.x % self.world_width
        self.car.position.y = self.car.position.y % self.world_height
        
        # Update sensors
        self._update_sensors()
        self.time_ms += 5
    
    def _update_sensors(self):
        """Read sensor values"""
        # Lane keeping
        self.car.lane_offset = self.car.position.y - self.lane_center_y
        
        # Obstacle detection
        front_heading = self.car.heading
        right_heading = self.car.heading - math.pi / 2
        left_heading = self.car.heading + math.pi / 2
        
        # Check distance to obstacles in various directions
        self.car.front_distance = self._scan_direction(front_heading)
        self.car.right_distance = self._scan_direction(right_heading)
        self.car.left_distance = self._scan_direction(left_heading)
    
    def _scan_direction(self, heading: float, max_range=50) -> float:
        """Scan for obstacles in a direction (LiDAR-like)"""
        min_dist = max_range
        
        for obstacle in self.obstacles:
            # Simple: check if obstacle is roughly in this direction
            to_obs = Vector2D(
                obstacle.position.x - self.car.position.x,
                obstacle.position.y - self.car.position.y
            )
            obs_distance = math.sqrt(to_obs.x**2 + to_obs.y**2)
            
            if obs_distance < max_range:
                # Rough angle check (within 45 degrees)
                obs_angle = math.atan2(to_obs.y, to_obs.x)
                angle_diff = abs(obs_angle - heading)
                if angle_diff > math.pi:
                    angle_diff = 2*math.pi - angle_diff
                
                if angle_diff < math.pi / 4:
                    min_dist = min(min_dist, obs_distance - obstacle.radius)
        
        return min_dist
    
    def get_state(self) -> CarState:
        """Get current car state"""
        return self.car
    
    def get_time_ms(self) -> int:
        """Get simulation time"""
        return int(self.time_ms)
    
    def print_state(self):
        """Print current state"""
        print(f"[T={self.get_time_ms():6d}ms] {self.car}")


def phase_0_demo():
    """Run Phase 0 demo"""
    print("=" * 80)
    print("PHASE 0: TOY SIMULATOR DEMO")
    print("=" * 80)
    print("\nSimulating a car driving down the lane with obstacle avoidance...")
    print()
    
    sim = ToySimulator()
    
    # Simulate 2 seconds
    for tick in range(400):  # 400 * 5ms = 2000ms
        # Simple control logic
        state = sim.get_state()
        
        # Lane keeping: steer toward lane center
        steering = -state.lane_offset * 0.1
        steering = max(-1, min(1, steering))
        
        # Obstacle avoidance: brake if obstacle ahead
        throttle = 1.0
        brake = 0.0
        if state.front_distance < 20:
            brake = 1.0
            throttle = 0.0
        
        sim.update(steering, throttle, brake)
        
        # Print every 100ms
        if tick % 20 == 0:
            sim.print_state()
    
    print("\n✓ Phase 0 complete! Car successfully navigated the world.")
    print(f"Final position: ({sim.car.position.x:.1f}, {sim.car.position.y:.1f})")


if __name__ == "__main__":
    phase_0_demo()
