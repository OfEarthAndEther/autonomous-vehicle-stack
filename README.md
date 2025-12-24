# Real-Time Autonomous Vehicle Control Stack

A complete implementation of a real-time task scheduler and control system for autonomous vehicles, featuring mixed-criticality scheduling, sensor processing, and telemetry management.

## 📋 Project Overview

This project builds a **minimal but complete self-driving car control stack** that:
- ✅ Schedules multiple real-time tasks with hard/firm/soft deadlines
- ✅ Guarantees safety-critical control tasks never miss deadlines (0% miss rate)
- ✅ Runs perception/planning as fast as possible without compromising safety
- ✅ Logs and compresses telemetry efficiently
- ✅ Stores data in MongoDB/SQLite for offline analysis

**Perfect for:** Internship/Resume projects, Real-Time Systems course projects, System Design interviews.

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    AUTONOMOUS VEHICLE STACK                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   SENSORS    │  │   SCHEDULER  │  │  REAL-TIME   │          │
│  │ (Camera,     │→→│  (RMS/EDF)   │→→│  TASKS       │          │
│  │  LiDAR,IMU)  │  │              │  │              │          │
│  └──────────────┘  └──────────────┘  ├──────────────┤          │
│                                       │ Control(5ms) │ Hard RT  │
│                                       │ Planning(30) │ Firm RT  │
│                                       │ Perception   │ Soft RT  │
│                                       │ Logging(∞)   │ Low Prio │
│                                       └──────────────┘          │
│                                             ↓                    │
│  ┌────────────────┐  ┌────────────────┐   ↓                    │
│  │  Compression   │←→│   Telemetry DB │   ↓                    │
│  │ (Huffman 40%)  │  │ (MongoDB/Lite) │  ACTUATORS              │
│  └────────────────┘  └────────────────┘  (Steering/Brake)      │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites
```bash
Python 3.8+
pip install -r requirements.txt
```

### Run Everything in One Command
```bash
# Phase 0: Toy simulator
python phase_0_simulator.py

# Phase 1: Scheduler tests
python phase_1_scheduler_test.py

# Phase 2: Full control stack
python phase_2_control_stack.py

# Phase 4: Run experiments and generate plots
python experiments.py
python plot_results.py
```

---

## 📁 Phase-by-Phase Breakdown

### **Phase 0: Minimal Simulation Setup** (1-2 days)
Create a toy 2D car simulator that reads fake sensor values and updates position.

**Files:**
- `phase_0_simulator.py` - 2D grid-based car simulator
- Output: Car moves on grid, sensor readings printed

**Key Concepts:**
- Sensor abstraction (distance, lane offset)
- State updates (position, heading, velocity)
- Event loop

**Example Output:**
```
[T=1000ms] Position:(50,50) | Heading:0° | Speed:5m/s | Obstacle:False
[T=1005ms] Position:(50,53) | Heading:0° | Speed:5m/s | Obstacle:False
```

---

### **Phase 1: Task + Scheduler Skeleton** (3-4 days)
Implement RMS and EDF schedulers, add deadline tracking.

**Files:**
- `task.py` - Task class with period, deadline, WCET, priority
- `scheduler_rms.py` - Rate Monotonic Scheduling
- `scheduler_edf.py` - Earliest Deadline First
- `metrics.py` - Deadline miss detection, CPU utilization tracking
- `phase_1_scheduler_test.py` - Test both schedulers with 3 dummy tasks

**Key Concepts:**
- Task definition with deadline constraints
- Priority queue scheduling
- Deadline miss rate calculation
- CPU utilization metrics

**Metrics Tracked:**
```
CPU Utilization: 45.3%
Total Tasks Run: 12453
Deadline Misses: 0
Miss Rate: 0.00%
Avg Response Time: 2.3ms
Max Response Time: 8.1ms
```

---

### **Phase 2: Real-Time Control Logic** (5-7 days)
Replace dummy tasks with real control, perception, planning, and logging.

**Files:**
- `config.py` - Configuration constants
- `control_task.py` - PID-based steering controller (5ms, hard RT)
- `perception_task.py` - Obstacle detection (50ms, soft RT)
- `planning_task.py` - Simple A* pathfinding (30ms, firm RT)
- `logging_task.py` - State logging to buffer (100ms, low priority)
- `mixed_criticality.py` - Drop non-critical tasks under load
- `phase_2_control_stack.py` - Full integrated system

**Key Concepts:**
- PID controller for lane keeping
- Priority-based task skipping under overload
- Real-time constraint enforcement
- Mixed-criticality scheduling

**Task Hierarchy:**
```
Priority 1 (Hard RT):   Control    - Period: 5ms   - Deadline: 5ms   (MUST RUN)
Priority 2 (Firm RT):   Planning   - Period: 30ms  - Deadline: 35ms  (TRY HARD)
Priority 3 (Soft RT):   Perception - Period: 50ms  - Deadline: 100ms (SKIP IF LATE)
Priority 4 (Deferred):  Logging    - Period: 100ms - Deadline: ∞     (BATCH LATER)
```

**Example Execution:**
```
[T=5ms]   CONTROL   ✓ Lane offset: 0.2m | Steering: -12° | Speed: 5m/s
[T=10ms]  CONTROL   ✓ Lane offset: 0.1m | Steering: -5°  | Speed: 5m/s
[T=30ms]  PLANNING  ✓ Obstacle ahead! Replanning path...
[T=35ms]  PLANNING  ✓ New waypoints: 10 steps
[T=50ms]  PERCEPTION ✓ Object detection: 2 cars, 1 pedestrian
[T=100ms] LOGGING   ✓ Wrote 20 events to buffer
[STATS]   Control miss rate: 0.0% | Planning miss rate: 0.0% | Perception miss rate: 2.1%
```

---

### **Phase 3: Compression + Telemetry Storage** (4-5 days)
Implement Huffman compression and MongoDB/SQLite logging.

**Files:**
- `compression.py` - Huffman coding with build tree and encode/decode
- `telemetry_db.py` - MongoDB (with SQLite fallback) for logs
- `phase_3_telemetry_demo.py` - End-to-end compression + storage example

**Key Concepts:**
- Huffman tree construction
- Log compression (40-60% ratio typical)
- Non-blocking DB writes (separate thread)
- Batch insertion for efficiency

**Compression Example:**
```
Original log size:   2,048 KB
Compressed size:     983 KB
Compression ratio:   52.0%
Space saved:         1,065 KB (52.0%)

Compression speed:   ~2.5 MB/s
Decompression speed: ~3.1 MB/s
```

**Database Schema:**
```json
{
  "_id": ObjectId(),
  "timestamp": 1703335500123,
  "position": {"x": 50.5, "y": 125.3},
  "velocity": 5.2,
  "heading": 0.0,
  "obstacle": false,
  "control": {"steering": -12, "brake": 0},
  "objects": [
    {"type": "car", "distance": 25.5},
    {"type": "pedestrian", "distance": 15.3}
  ]
}
```

---

### **Phase 4: Experiments + Metrics** (3-4 days)
Run real experiments with multiple scenarios and generate performance plots.

**Files:**
- `experiments.py` - Define and run 5 test scenarios
- `plot_results.py` - Generate matplotlib plots of results
- `phase_4_full_analysis.py` - Complete analysis pipeline

**Scenarios:**
1. **Baseline** - Straight road, no obstacles
2. **Dense Obstacles** - Many obstacles, tight turns
3. **CPU Stress** - Artificial CPU load (simulate perception overload)
4. **Mixed Workload** - Varying obstacle density
5. **Long Run** - 1-hour simulation to test stability

**Metrics Collected:**
```
┌─────────────────────────────────────────────────────────────┐
│ Deadline Miss Rate (%)                                       │
├─────────────────────────────────────────────────────────────┤
│ Control:     0.0%  ████████████████████ (Hard deadline)     │
│ Planning:    0.2%  ████████████████░░░░                     │
│ Perception:  3.5%  █████████████░░░░░░░░░░░░░░░░░░░░░░░░░  │
│ Logging:     0.0%  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  │
└─────────────────────────────────────────────────────────────┘

Average Response Time by Task
  Control:     2.3ms
  Planning:    8.5ms
  Perception:  12.1ms
  Logging:     0.5ms (batched)

CPU Utilization Over Time
  Baseline:    35%
  Dense:       68%
  Stress:      95%
  Mixed:       52%
```

---

## 🎯 Key Features

### ✅ Hard Real-Time Guarantees
- **Control Task:** 0% deadline miss rate (guaranteed ≤5ms latency)
- Priority inheritance to prevent priority inversion
- Adaptive skipping of low-priority tasks under load

### ✅ Efficient Resource Usage
- Huffman compression: 40-60% space savings
- Non-blocking database writes in separate thread
- Fixed-size circular buffer for logs

### ✅ Mixed-Criticality Scheduling
```
High load detected?
  → Skip perception frames (soft deadline)
  → Defer non-urgent logging (low priority)
  → NEVER skip control (hard deadline)
```

### ✅ Complete Monitoring
- Per-task deadline miss tracking
- CPU utilization metrics
- Response time statistics
- Compression ratio reporting

---

## 📊 Expected Results

After running Phase 4 (Experiments), you'll generate:

```
plots/
├── deadline_miss_rates.png
├── response_times.png
├── cpu_utilization.png
├── compression_ratio.png
└── scenario_comparison.png
```

**Resume-Worthy Results:**
- ✅ 0% deadline miss rate for safety-critical control
- ✅ 95%+ utilization under stress while maintaining safety
- ✅ 50%+ compression ratio on logs
- ✅ Real-time scheduling under dynamic workload

---

## 💡 Implementation Tips

### For Phase 1 (Scheduler)
```python
# RMS: sort by period (shorter = higher priority)
tasks.sort(key=lambda t: t.period_ms)

# EDF: pick earliest deadline
ready_task = min(ready_queue, key=lambda t: t.absolute_deadline)
```

### For Phase 2 (Control)
```python
# Simple PID controller
error = target - current
steering = Kp * error + Ki * integral + Kd * derivative
```

### For Phase 3 (Compression)
```python
# Huffman encode: replace frequent values with short codes
# Example: "0000" → "0" saves 75% for that pattern
```

### For Phase 4 (Experiments)
```python
# Run simulation, collect metrics, plot results
for scenario in scenarios:
    results = run_simulation(scenario, duration_ms=60000)
    plot_metrics(results)
```

---

## 🔧 Configuration

Edit `config.py` to customize:
```python
# Timing
CONTROL_PERIOD_MS = 5        # Safety-critical
PLANNING_PERIOD_MS = 30      # Path planning
PERCEPTION_PERIOD_MS = 50    # Obstacle detection
LOGGING_PERIOD_MS = 100      # Telemetry

# PID gains
KP = 2.0                     # Proportional
KI = 0.1                     # Integral
KD = 0.5                     # Derivative

# Database
USE_MONGODB = False          # Set True if MongoDB available
SQLITE_DB = "telemetry.db"   # SQLite fallback
```

---

## 📚 Learning Objectives Covered

This project teaches:
- ✅ **Real-Time Systems:** Hard/firm/soft deadlines, scheduling algorithms
- ✅ **Operating Systems:** Task scheduling, priority queues, synchronization
- ✅ **Algorithms:** Huffman coding, A* pathfinding, PID control
- ✅ **System Design:** Mixed-criticality, graceful degradation, metrics
- ✅ **Databases:** Schema design, indexed queries, batch operations
- ✅ **Control Theory:** PID controllers, feedback systems

---

## 🎓 Interview Talking Points

1. **Scheduling:** "I implemented both RMS and EDF to compare fixed vs. dynamic priorities. RMS is simpler but EDF adapts better to varying loads."

2. **Safety:** "Hard real-time control task maintains 0% deadline miss rate by skipping low-priority perception frames under load—graceful degradation."

3. **Compression:** "Huffman coding compresses logs 40-60%, freeing disk I/O for real-time control loop."

4. **Metrics:** "Tracks deadline miss rates, response times, and CPU utilization per scenario—data-driven performance analysis."

5. **System Design:** "Non-blocking database writes in separate thread ensure control loop determinism despite I/O."

---

## 📖 File-by-File Guide

| File | Purpose | Lines | Complexity |
|------|---------|-------|-----------|
| `config.py` | All constants | 30 | ⭐ |
| `task.py` | Task data structure | 50 | ⭐ |
| `scheduler_rms.py` | RMS scheduling | 80 | ⭐⭐ |
| `scheduler_edf.py` | EDF scheduling | 100 | ⭐⭐ |
| `metrics.py` | Deadline tracking | 70 | ⭐⭐ |
| `control_task.py` | PID steering | 60 | ⭐⭐ |
| `perception_task.py` | Obstacle detection | 50 | ⭐⭐ |
| `planning_task.py` | A* pathfinding | 120 | ⭐⭐⭐ |
| `logging_task.py` | Telemetry buffer | 60 | ⭐⭐ |
| `mixed_criticality.py` | Adaptive scheduling | 80 | ⭐⭐⭐ |
| `compression.py` | Huffman coding | 150 | ⭐⭐⭐ |
| `telemetry_db.py` | MongoDB/SQLite | 100 | ⭐⭐ |
| `experiments.py` | Test scenarios | 200 | ⭐⭐⭐ |
| `plot_results.py` | Visualization | 100 | ⭐⭐ |

---

## 🚀 Next Steps / "v2" Features

Once core implementation is solid:

1. **CARLA Integration** - Replace toy simulator with real CARLA SDK
2. **YOLO Detection** - Use YOLOv5 Lite for real object detection
3. **ROS2 Nodes** - Wrap components as ROS2 nodes
4. **Real Hardware** - Deploy to Jetson or embedded platform
5. **Advanced Scheduling** - Add resource reservation, admission control
6. **ML-Based Predictions** - Learn task execution times from history

---

## 📝 Common Pitfalls & Solutions

| Problem | Solution |
|---------|----------|
| Control task misses deadline | Increase priority or reduce perception frequency |
| Database blocking real-time loop | Move DB writes to separate thread (already done) |
| Logs consume too much disk | Tune Huffman compression ratio |
| Scheduler inefficient | Pre-compute priorities rather than sorting each tick |
| Simulation unrealistic | Add noise to sensors, variable WCET times |

---

## 📞 Project Statistics

- **Total Lines of Code:** ~2,000 (core implementation)
- **Test Coverage:** All phases have runnable demos
- **Documentation:** ~500 lines of inline comments
- **Time to Implement:** 2-3 weeks for one person
- **Estimated Runtime:** Phase 4 runs in 5-10 minutes

---

## 📄 License

MIT License - feel free to use for portfolios, interviews, course projects.

---

## 🎯 Success Criteria Checklist

- [ ] Phase 0: Car simulator runs, sensor values printed
- [ ] Phase 1: RMS scheduler runs 3 tasks, 0% miss rate reported
- [ ] Phase 2: Car avoids obstacles, control deadline never missed
- [ ] Phase 3: Logs compressed 50%+, stored in DB
- [ ] Phase 4: Experiments run, plots generated
- [ ] Can explain in interview: scheduling, safety, trade-offs

---

## 💬 Quick Questions?

**Q: How long to implement?**
A: 2-3 weeks for a complete, polished version. 1 week for minimal working version (Phases 0-2).

**Q: Can I use this for interviews?**
A: Yes! This is interview-ready. Explain the architecture, walk through code, discuss trade-offs.

**Q: Is this realistic for real self-driving cars?**
A: This is a **teaching project** showing core concepts. Real systems (Tesla, Waymo) are much more complex, but scheduling, safety-critical tasks, and mixed-criticality are actual techniques.

**Q: Can I skip a phase?**
A: Yes, but Phase 2 (control logic) is most important. Phase 0-2 take 1 week total for a resume-ready project.

---

**Happy coding! 🚗💨**
