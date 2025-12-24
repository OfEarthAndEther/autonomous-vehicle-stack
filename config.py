"""
Configuration file for Autonomous Vehicle Control Stack
All constants and settings in one place for easy customization
"""

import math
from enum import Enum

# ============================================================================
# TIMING CONFIGURATION
# ============================================================================

# Task periods (milliseconds)
CONTROL_PERIOD_MS = 5          # Safety-critical steering/brake command
PLANNING_PERIOD_MS = 30        # Path planning
PERCEPTION_PERIOD_MS = 50      # Object detection
LOGGING_PERIOD_MS = 100        # Telemetry buffer flush

# Deadlines (milliseconds, relative to start of task)
CONTROL_DEADLINE_MS = 5        # Hard real-time: must complete by period
PLANNING_DEADLINE_MS = 35      # Firm deadline: some slack allowed
PERCEPTION_DEADLINE_MS = 100   # Soft deadline: can be skipped if late
LOGGING_DEADLINE_MS = 500      # Low priority: batched

# Worst-case execution times (microseconds)
CONTROL_WCET_US = 500          # Very fast: simple PID
PLANNING_WCET_US = 5000        # Moderate: A* on small grid
PERCEPTION_WCET_US = 8000      # Slower: ML-style processing
LOGGING_WCET_US = 2000         # Fast: buffer write

# Simulation parameters
SIMULATION_TICK_MS = 1         # Clock granularity
SIMULATION_DURATION_MS = 60000 # 60 seconds
SIMULATION_FPS = 100           # For visualization

# ============================================================================
# PHYSICAL PARAMETERS
# ============================================================================

# Car dimensions and dynamics
CAR_LENGTH_M = 2.5             # Vehicle length
CAR_WIDTH_M = 1.5              # Vehicle width
MAX_SPEED_MPS = 15.0           # 54 km/h
MAX_STEERING_ANGLE_DEG = 30.0  # Max steering angle
MAX_ACCELERATION = 5.0         # m/s^2
MAX_DECELERATION = 8.0         # m/s^2

# Simulation world
WORLD_WIDTH_M = 500.0
WORLD_HEIGHT_M = 500.0
LANE_WIDTH_M = 3.5
GRID_RESOLUTION_M = 1.0

# ============================================================================
# PID CONTROLLER GAINS
# ============================================================================

# Lane-keeping controller
KP_STEERING = 2.0              # Proportional gain
KI_STEERING = 0.1              # Integral gain
KD_STEERING = 0.5              # Derivative gain

# Speed controller
KP_SPEED = 1.0
KI_SPEED = 0.05
KD_SPEED = 0.2

# ============================================================================
# PERCEPTION PARAMETERS
# ============================================================================

# Sensor range and accuracy
LIDAR_RANGE_M = 50.0
LIDAR_FOV_DEG = 120.0
CAMERA_RANGE_M = 100.0

# Obstacle detection thresholds
OBSTACLE_ALERT_DISTANCE_M = 20.0
SAFE_FOLLOWING_DISTANCE_M = 10.0
MINIMUM_STOPPING_DISTANCE_M = 15.0

# ============================================================================
# PLANNING PARAMETERS
# ============================================================================

# Pathfinding
PLANNING_GRID_SIZE = 50        # 50x50 grid for A*
PLANNING_CELL_SIZE_M = 10.0    # Each cell is 10m x 10m
PLANNING_REPLANNING_TRIGGER = 5  # Replan if distance < 5 cells

# Trajectory
WAYPOINT_SPACING_M = 2.0
TRAJECTORY_HORIZON_M = 50.0

# ============================================================================
# LOGGING & DATABASE
# ============================================================================

# Database choice
USE_MONGODB = False            # Set True if MongoDB available
MONGODB_URI = "mongodb://localhost:27017/"
MONGODB_DB = "autonomous_vehicle"
MONGODB_COLLECTION = "telemetry"

# SQLite fallback
SQLITE_DB = "telemetry.db"
SQLITE_TABLE = "telemetry"

# Log buffer
LOG_BUFFER_SIZE = 10000        # Max events in memory
LOG_BATCH_SIZE = 100           # Write batch size to DB
LOG_COMPRESSION_ENABLED = True

# ============================================================================
# COMPRESSION
# ============================================================================

# Huffman coding
COMPRESSION_RATIO_TARGET = 0.5  # Target 50% compression
ENTROPY_THRESHOLD = 0.7         # Compress if entropy > this

# ============================================================================
# SCHEDULING
# ============================================================================

class TaskCriticality(Enum):
    """Task criticality levels"""
    HARD = 1        # Cannot miss deadline (Control)
    FIRM = 2        # Occasional miss acceptable (Planning)
    SOFT = 3        # Frequent miss acceptable (Perception)
    DEFERRED = 4    # Can be batched (Logging)

# Priority levels (higher = more important)
PRIORITY_CONTROL = 1000
PRIORITY_PLANNING = 800
PRIORITY_PERCEPTION = 500
PRIORITY_LOGGING = 100

# Scheduler type
class SchedulerType(Enum):
    RMS = "Rate Monotonic Scheduling"
    EDF = "Earliest Deadline First"
    MIXED_CRITICALITY = "Mixed-Criticality with Adaptive Dropping"

ACTIVE_SCHEDULER = SchedulerType.MIXED_CRITICALITY

# Adaptive behavior thresholds
CPU_LOAD_HIGH_THRESHOLD = 0.80  # Above 80% = high load
CPU_LOAD_CRITICAL_THRESHOLD = 0.95  # Above 95% = critical

# Task dropping policy under load
DROP_PERCEPTION_FRAMES = True   # Skip perception frames if overloaded
REDUCE_PLANNING_FREQUENCY = True  # Reduce planning updates if overloaded
NEVER_DROP_CONTROL = True       # Always run control (hard deadline)

# ============================================================================
# METRICS & MONITORING
# ============================================================================

# Metrics collection
TRACK_DEADLINE_MISSES = True
TRACK_RESPONSE_TIMES = True
TRACK_CPU_UTILIZATION = True
METRICS_UPDATE_PERIOD_MS = 1000  # Update metrics every 1 second

# Alerting thresholds
ALERT_CONTROL_MISS_RATE = 0.001  # Alert if > 0.1% misses
ALERT_CPU_OVERLOAD = 0.85        # Alert at 85% CPU

# ============================================================================
# EXPERIMENT SCENARIOS
# ============================================================================

class ExperimentScenario(Enum):
    """Test scenarios for Phase 4"""
    BASELINE = "Straight road, no obstacles"
    DENSE_OBSTACLES = "Many obstacles, tight turns"
    CPU_STRESS = "Simulated CPU overload"
    MIXED_WORKLOAD = "Varying obstacle density"
    LONG_RUN = "1-hour stability test"

EXPERIMENTS_TO_RUN = [
    ExperimentScenario.BASELINE,
    ExperimentScenario.DENSE_OBSTACLES,
    ExperimentScenario.CPU_STRESS,
]

# ============================================================================
# DEBUGGING & LOGGING
# ============================================================================

DEBUG_MODE = False
VERBOSE_SCHEDULER = False
VERBOSE_PERCEPTION = False
VERBOSE_PLANNING = False
VERBOSE_CONTROL = False

# Console output verbosity
class LogLevel(Enum):
    SILENT = 0
    ERROR = 1
    WARNING = 2
    INFO = 3
    DEBUG = 4

CONSOLE_LOG_LEVEL = LogLevel.INFO

# ============================================================================
# VALIDATION
# ============================================================================

def validate_config():
    """Validate configuration for consistency"""
    assert CONTROL_PERIOD_MS < PLANNING_PERIOD_MS, "Control should be faster than planning"
    assert PLANNING_PERIOD_MS < PERCEPTION_PERIOD_MS, "Planning should be faster than perception"
    assert CONTROL_DEADLINE_MS <= CONTROL_PERIOD_MS, "Deadline should fit in period"
    assert MAX_SPEED_MPS > 0, "Max speed must be positive"
    assert KP_STEERING > 0, "PID gains must be positive"
    assert PLANNING_GRID_SIZE > 0, "Grid size must be positive"
    print("✓ Configuration validated successfully")

if __name__ == "__main__":
    validate_config()
    print(f"Control period: {CONTROL_PERIOD_MS}ms")
    print(f"Planning period: {PLANNING_PERIOD_MS}ms")
    print(f"Perception period: {PERCEPTION_PERIOD_MS}ms")
    print(f"Logging period: {LOGGING_PERIOD_MS}ms")
