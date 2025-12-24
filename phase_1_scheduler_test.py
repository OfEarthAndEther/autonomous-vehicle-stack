"""
PHASE 1: Scheduler Test - Run RMS and EDF with Dummy Tasks
Compare scheduling algorithms with simple periodic tasks
"""

import time
from phase_1_task_scheduler import Task, RMSScheduler, EDFScheduler, TaskCriticality, print_scheduler_stats

def create_dummy_tasks():
    """Create 3 dummy periodic tasks"""
    
    task1_runs = 0
    task2_runs = 0
    task3_runs = 0
    
    def task1_fn():
        nonlocal task1_runs
        task1_runs += 1
        time.sleep(0.0005)  # 500µs
    
    def task2_fn():
        nonlocal task2_runs
        task2_runs += 1
        time.sleep(0.003)   # 3ms
    
    def task3_fn():
        nonlocal task3_runs
        task3_runs += 1
        time.sleep(0.005)   # 5ms
    
    tasks = [
        Task(
            task_id=1,
            name="Task 1 (Fast)",
            period_ms=5,
            deadline_ms=5,
            wcet_us=500,
            priority=1000,
            criticality=TaskCriticality.HARD,
            function=task1_fn
        ),
        Task(
            task_id=2,
            name="Task 2 (Medium)",
            period_ms=20,
            deadline_ms=20,
            wcet_us=3000,
            priority=800,
            criticality=TaskCriticality.FIRM,
            function=task2_fn
        ),
        Task(
            task_id=3,
            name="Task 3 (Slow)",
            period_ms=50,
            deadline_ms=50,
            wcet_us=5000,
            priority=600,
            criticality=TaskCriticality.SOFT,
            function=task3_fn
        ),
    ]
    
    return tasks

def run_scheduler_test(scheduler_class, scheduler_name: str, duration_s: float = 5.0):
    """Run a scheduler test"""
    
    print("\n" + "=" * 80)
    print(f"PHASE 1: {scheduler_name}")
    print("=" * 80)
    
    tasks = create_dummy_tasks()
    scheduler = scheduler_class(tasks)
    
    # Initialize tasks
    for task in tasks:
        task.next_release_time = 0.0
    
    # Run simulation
    tick_time = 0.001  # 1ms ticks
    ticks = int(duration_s / tick_time)
    
    print(f"\nRunning simulation for {duration_s}s ({ticks} ticks)...")
    start_time = time.perf_counter()
    
    for tick in range(ticks):
        scheduler.tick(tick_time)
        
        if (tick + 1) % 100 == 0 and (tick + 1) <= 500:
            progress = (tick + 1) / ticks * 100
            print(f"  Progress: {progress:.1f}% ({scheduler.current_time:.2f}s)")
    
    elapsed = time.perf_counter() - start_time
    print(f"\n✓ Simulation complete in {elapsed:.2f} seconds (wall time)")
    
    # Print statistics
    stats = scheduler.get_stats()
    print_scheduler_stats(stats)
    
    return stats

def phase_1_demo():
    """Run Phase 1 complete demo"""
    
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "PHASE 1: TASK SCHEDULING DEMO".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("║" + "Real-Time Scheduling: RMS vs EDF".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "=" * 78 + "╝")
    
    # Test RMS
    rms_stats = run_scheduler_test(RMSScheduler, "RATE MONOTONIC SCHEDULING (RMS)", 5.0)
    
    # Test EDF
    edf_stats = run_scheduler_test(EDFScheduler, "EARLIEST DEADLINE FIRST (EDF)", 5.0)
    
    # Comparison
    print("\n" + "=" * 80)
    print("COMPARISON: RMS vs EDF")
    print("=" * 80)
    print(f"{'Metric':<30s} {'RMS':>20s} {'EDF':>20s}")
    print("─" * 80)
    print(f"{'Deadline miss rate':<30s} {rms_stats['miss_rate']*100:>19.2f}% {edf_stats['miss_rate']*100:>19.2f}%")
    print(f"{'CPU utilization':<30s} {rms_stats['cpu_utilization']*100:>19.2f}% {edf_stats['cpu_utilization']*100:>19.2f}%")
    print(f"{'Execution time (wall) s':<30s} {rms_stats['current_time_s']:>20.2f} {edf_stats['current_time_s']:>20.2f}")
    
    print("\n" + "=" * 80)
    print("CONCLUSION")
    print("=" * 80)
    print("""
RMS (Rate Monotonic Scheduling):
  ✓ Fixed priorities based on task period
  ✓ Simpler to implement and understand
  ✓ Best for systems with known, fixed periods
  ⚠ May not meet all deadlines under dynamic loads

EDF (Earliest Deadline First):
  ✓ Optimal for meeting deadlines when feasible
  ✓ Dynamic priorities adapt to changing deadlines
  ✓ Better for mixed-criticality systems
  ⚠ Slightly more complex to implement
    """)
    
    print("\n✓ Phase 1 demo complete!")
    print("Ready to move to Phase 2: Real-Time Control Logic")

if __name__ == "__main__":
    phase_1_demo()
