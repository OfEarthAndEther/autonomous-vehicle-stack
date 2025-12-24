"""
PHASE 2: Real-Time Control Logic
Control task (PID steering), Perception, Planning, and Logging tasks
"""

import math
import time
from dataclasses import dataclass
from typing import List, Optional
from phase_0_simulator import ToySimulator, CarState
from phase_1_task_scheduler import Task, TaskCriticality, RMSScheduler

# ============================================================================
# CONTROL TASK: Steering Controller
# ============================================================================

@dataclass
class PIDController:
    """PID controller for steering"""
    kp: float
    ki: float
    kd: float
    
    def __post_init__(self):
        self.integral = 0.0
        self.prev_error = 0.0
    
    def update(self, error: float, dt: float) -> float:
        """Calculate PID output"""
        self.integral += error * dt
        derivative = (error - self.prev_error) / dt if dt > 0 else 0
        self.prev_error = error
        
        output = (self.kp * error + 
                 self.ki * self.integral + 
                 self.kd * derivative)
        
        return max(-1.0, min(1.0, output))  # Clamp to [-1, 1]

class ControlTaskManager:
    """Manages vehicle steering and speed control"""
    
    def __init__(self, simulator: ToySimulator):
        self.sim = simulator
        self.steering_pid = PIDController(kp=2.0, ki=0.1, kd=0.5)
        self.speed_pid = PIDController(kp=1.0, ki=0.05, kd=0.2)
        
        self.target_speed = 5.0  # m/s
        self.target_lane_offset = 0.0  # meters
        self.last_control_time = 0.0
        self.control_count = 0
    
    def execute(self, current_time: float = 0.0):
        """Execute control task"""
        state = self.sim.get_state()
        dt = 0.005  # 5ms
        
        # Lane keeping: steer to maintain lane center
        lane_error = state.lane_offset - self.target_lane_offset
        steering = self.steering_pid.update(lane_error, dt)
        
        # Speed control
        speed_error = self.target_speed - state.speed
        throttle = self.speed_pid.update(speed_error, dt)
        
        # Obstacle avoidance: brake if obstacle ahead
        brake = 0.0
        if state.front_distance < 20.0:
            brake = (20.0 - state.front_distance) / 20.0
        
        # Apply commands to simulator
        self.sim.update(steering, throttle, brake)
        self.control_count += 1
        self.last_control_time = current_time

# ============================================================================
# PERCEPTION TASK: Obstacle Detection
# ============================================================================

@dataclass
class DetectedObject:
    """Detected object in scene"""
    obj_type: str  # "car", "pedestrian", "obstacle"
    distance: float
    angle: float
    confidence: float

class PerceptionTaskManager:
    """Obstacle detection and scene understanding"""
    
    def __init__(self, simulator: ToySimulator):
        self.sim = simulator
        self.objects: List[DetectedObject] = []
        self.perception_count = 0
        self.last_perception_time = 0.0
    
    def execute(self, current_time: float = 0.0):
        """Execute perception task"""
        state = self.sim.get_state()
        
        # Simple object detection based on sensor readings
        self.objects = []
        
        # Front obstacle
        if state.front_distance < 50:
            self.objects.append(DetectedObject(
                obj_type="vehicle",
                distance=state.front_distance,
                angle=0,
                confidence=min(1.0, 1.0 - state.front_distance / 50.0)
            ))
        
        # Right obstacle
        if state.right_distance < 50:
            self.objects.append(DetectedObject(
                obj_type="obstacle",
                distance=state.right_distance,
                angle=-math.pi / 2,
                confidence=0.7
            ))
        
        # Left obstacle
        if state.left_distance < 50:
            self.objects.append(DetectedObject(
                obj_type="obstacle",
                distance=state.left_distance,
                angle=math.pi / 2,
                confidence=0.7
            ))
        
        self.perception_count += 1
        self.last_perception_time = current_time
    
    def get_objects(self) -> List[DetectedObject]:
        return self.objects

# ============================================================================
# PLANNING TASK: Path Planning
# ============================================================================

@dataclass
class Waypoint:
    """Navigation waypoint"""
    x: float
    y: float
    heading: float

class PlanningTaskManager:
    """Path planning and trajectory generation"""
    
    def __init__(self, simulator: ToySimulator):
        self.sim = simulator
        self.waypoints: List[Waypoint] = []
        self.planning_count = 0
        self.last_planning_time = 0.0
        self._generate_initial_path()
    
    def _generate_initial_path(self):
        """Generate initial waypoint path"""
        state = self.sim.get_state()
        
        # Simple: straight ahead with some lookahead
        self.waypoints = []
        for i in range(10):
            distance = (i + 1) * 5.0
            new_x = state.position.x + distance
            self.waypoints.append(Waypoint(
                x=new_x,
                y=state.position.y,
                heading=0.0
            ))
    
    def execute(self, current_time: float = 0.0, 
                obstacles: List[DetectedObject] = None):
        """Execute planning task"""
        state = self.sim.get_state()
        
        # Check if we need to replan (obstacle in path)
        should_replan = False
        if obstacles:
            for obj in obstacles:
                if obj.distance < 15:
                    should_replan = True
                    break
        
        if should_replan:
            self._replan_avoiding_obstacles(obstacles)
        else:
            self._generate_initial_path()
        
        self.planning_count += 1
        self.last_planning_time = current_time
    
    def _replan_avoiding_obstacles(self, obstacles: List[DetectedObject]):
        """Simple obstacle avoidance planning"""
        state = self.sim.get_state()
        
        # Move waypoints away from obstacles
        self.waypoints = []
        for i in range(10):
            distance = (i + 1) * 5.0
            offset = 0.0
            
            if obstacles:
                # Steer away from detected obstacles
                for obj in obstacles:
                    if obj.angle < -math.pi / 4:  # Right side
                        offset = max(offset, 2.0)  # Move left
                    elif obj.angle > math.pi / 4:  # Left side
                        offset = min(offset, -2.0)  # Move right
            
            self.waypoints.append(Waypoint(
                x=state.position.x + distance,
                y=state.position.y + offset,
                heading=0.0
            ))
    
    def get_waypoints(self) -> List[Waypoint]:
        return self.waypoints

# ============================================================================
# LOGGING TASK: Telemetry Logging
# ============================================================================

@dataclass
class LogEntry:
    """Single log entry"""
    timestamp: float
    position_x: float
    position_y: float
    heading: float
    speed: float
    steering: float
    front_distance: float
    object_count: int

class LoggingTaskManager:
    """Telemetry logging and buffering"""
    
    def __init__(self, max_buffer_size: int = 10000):
        self.buffer: List[LogEntry] = []
        self.max_buffer_size = max_buffer_size
        self.logging_count = 0
        self.last_logging_time = 0.0
        self.total_logged = 0
    
    def execute(self, current_time: float,
                state: CarState,
                object_count: int = 0):
        """Execute logging task"""
        entry = LogEntry(
            timestamp=current_time,
            position_x=state.position.x,
            position_y=state.position.y,
            heading=state.heading,
            speed=state.speed,
            steering=state.steering,
            front_distance=state.front_distance,
            object_count=object_count
        )
        
        self.buffer.append(entry)
        if len(self.buffer) > self.max_buffer_size:
            self.buffer.pop(0)  # Keep circular buffer
        
        self.logging_count += 1
        self.last_logging_time = current_time
        self.total_logged += 1
    
    def get_buffer_size(self) -> int:
        return len(self.buffer)
    
    def flush(self) -> List[LogEntry]:
        """Return and clear buffer"""
        result = self.buffer.copy()
        self.buffer.clear()
        return result

# ============================================================================
# MIXED-CRITICALITY SCHEDULER
# ============================================================================

class MixedCriticalityScheduler:
    """
    Scheduler with mixed-criticality support
    - Hard deadlines (Control) are never skipped
    - Firm/Soft deadlines are skipped under load
    """
    
    def __init__(self, tasks: List[Task]):
        self.tasks = tasks
        self.current_time = 0.0
        self.control_overruns = 0
        self.perception_skips = 0
    
    def tick(self, elapsed_time_s: float, cpu_load: float = 0.0):
        """Execute tasks with mixed-criticality awareness"""
        self.current_time += elapsed_time_s
        
        # Release tasks
        for task in self.tasks:
            if self.current_time >= task.next_release_time:
                task.release(self.current_time)
        
        # Sort by priority
        self.tasks.sort(key=lambda t: t.priority, reverse=True)
        
        # Execute tasks with adaptive dropping under load
        for task in self.tasks:
            # Skip low-priority tasks under extreme load
            if cpu_load > 0.95 and task.criticality in [TaskCriticality.SOFT, 
                                                         TaskCriticality.DEFERRED]:
                if task.criticality == TaskCriticality.SOFT:
                    self.perception_skips += 1
                continue
            
            # Execute task
            start_time = self.current_time
            exec_time = task.execute()
            task.check_deadline(self.current_time + exec_time)
            
            # Track control task overruns
            if task.criticality == TaskCriticality.HARD:
                if not task.check_deadline(self.current_time + exec_time):
                    self.control_overruns += 1
    
    def get_stats(self) -> dict:
        """Get scheduler statistics"""
        return {
            'current_time': self.current_time,
            'control_overruns': self.control_overruns,
            'perception_skips': self.perception_skips,
            'task_stats': [t.get_stats() for t in self.tasks],
        }

if __name__ == "__main__":
    print("Phase 2 modules loaded:")
    print("  - ControlTaskManager (PID steering)")
    print("  - PerceptionTaskManager (obstacle detection)")
    print("  - PlanningTaskManager (path planning)")
    print("  - LoggingTaskManager (telemetry)")
    print("  - MixedCriticalityScheduler")
