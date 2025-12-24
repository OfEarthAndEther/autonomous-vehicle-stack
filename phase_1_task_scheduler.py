"""
PHASE 1: Task Definition and Scheduling
Core data structures and RMS/EDF schedulers
"""

import heapq
import time
from dataclasses import dataclass, field
from typing import Callable, List, Optional
from enum import Enum

# ============================================================================
# TASK DEFINITION
# ============================================================================

class TaskCriticality(Enum):
    HARD = 1        # Must never miss deadline (control)
    FIRM = 2        # Occasional miss acceptable (planning)
    SOFT = 3        # Frequent miss acceptable (perception)
    DEFERRED = 4    # Can be batched (logging)

@dataclass
class Task:
    """
    Represents a periodic real-time task
    
    Attributes:
        task_id: Unique identifier
        name: Human-readable name
        period_ms: Time between executions (milliseconds)
        deadline_ms: Maximum time to complete (relative to release)
        wcet_us: Worst-case execution time (microseconds)
        priority: Base priority (higher = more important)
        criticality: Hard/Firm/Soft deadline classification
        function: Callable to execute
    """
    task_id: int
    name: str
    period_ms: int
    deadline_ms: int
    wcet_us: int
    priority: int
    criticality: TaskCriticality
    function: Callable
    
    # Runtime information
    last_release_time: float = 0.0
    next_release_time: float = 0.0
    absolute_deadline: float = 0.0
    execution_count: int = 0
    deadline_misses: int = 0
    total_execution_time: float = 0.0
    max_execution_time: float = 0.0
    
    def __lt__(self, other):
        """For priority queue comparison"""
        return self.absolute_deadline < other.absolute_deadline
    
    def release(self, current_time: float):
        """Release task instance at current_time"""
        self.last_release_time = current_time
        self.next_release_time = current_time + self.period_ms / 1000.0
        self.absolute_deadline = current_time + self.deadline_ms / 1000.0
        self.execution_count += 1
    
    def execute(self) -> float:
        """Execute task, return execution time in seconds"""
        start = time.perf_counter()
        self.function()
        elapsed = time.perf_counter() - start
        
        self.total_execution_time += elapsed
        self.max_execution_time = max(self.max_execution_time, elapsed)
        
        return elapsed
    
    def check_deadline(self, current_time: float) -> bool:
        """Check if deadline was met, return True if met"""
        met = current_time <= self.absolute_deadline
        if not met:
            self.deadline_misses += 1
        return met
    
    def get_stats(self):
        """Get task statistics"""
        avg_exec_time = (self.total_execution_time / self.execution_count 
                        if self.execution_count > 0 else 0)
        miss_rate = (self.deadline_misses / self.execution_count 
                    if self.execution_count > 0 else 0)
        
        return {
            'task_id': self.task_id,
            'name': self.name,
            'execution_count': self.execution_count,
            'deadline_misses': self.deadline_misses,
            'miss_rate': miss_rate,
            'avg_exec_time_us': avg_exec_time * 1_000_000,
            'max_exec_time_us': self.max_execution_time * 1_000_000,
        }

# ============================================================================
# RATE MONOTONIC SCHEDULER (RMS)
# ============================================================================

class RMSScheduler:
    """
    Rate Monotonic Scheduling
    - Shorter period = higher priority
    - Optimal for periodic tasks with hard deadlines
    """
    
    def __init__(self, tasks: List[Task]):
        self.tasks = sorted(tasks, key=lambda t: t.period_ms)  # Sort by period
        self.ready_queue: List[Task] = []
        self.current_time = 0.0
        
        print(f"✓ RMS Scheduler initialized with {len(self.tasks)} tasks")
        for t in self.tasks:
            print(f"  [{t.task_id}] {t.name:20s} Period:{t.period_ms:3d}ms Priority:{t.priority}")
    
    def tick(self, elapsed_time_s: float):
        """Advance time and execute ready tasks"""
        self.current_time += elapsed_time_s
        
        # Release tasks whose period has come
        for task in self.tasks:
            if self.current_time >= task.next_release_time:
                task.release(self.current_time)
                self.ready_queue.append(task)
        
        # Sort by priority (lower priority = execute first)
        self.ready_queue.sort(key=lambda t: t.priority, reverse=True)
        
        # Execute ready tasks
        executed = []
        for task in self.ready_queue:
            exec_time = task.execute()
            task.check_deadline(self.current_time + exec_time)
            executed.append(task)
        
        self.ready_queue = []
    
    def get_cpu_utilization(self) -> float:
        """Calculate CPU utilization (total WCET / period sum)"""
        if not self.tasks:
            return 0.0
        
        total_wcet = sum(t.wcet_us for t in self.tasks)
        min_period = min(t.period_ms for t in self.tasks)
        
        return (total_wcet / 1000) / min_period
    
    def get_stats(self):
        """Get scheduler statistics"""
        total_deadline_misses = sum(t.deadline_misses for t in self.tasks)
        total_executions = sum(t.execution_count for t in self.tasks)
        
        return {
            'scheduler': 'RMS',
            'current_time_s': self.current_time,
            'total_executions': total_executions,
            'total_deadline_misses': total_deadline_misses,
            'miss_rate': total_deadline_misses / total_executions if total_executions > 0 else 0,
            'cpu_utilization': self.get_cpu_utilization(),
            'task_stats': [t.get_stats() for t in self.tasks],
        }

# ============================================================================
# EARLIEST DEADLINE FIRST SCHEDULER (EDF)
# ============================================================================

class EDFScheduler:
    """
    Earliest Deadline First Scheduling
    - Task with earliest absolute deadline runs first
    - Optimal for meeting all deadlines (when feasible)
    """
    
    def __init__(self, tasks: List[Task]):
        self.tasks = tasks
        self.ready_queue: List[Task] = []
        self.current_time = 0.0
        
        print(f"✓ EDF Scheduler initialized with {len(self.tasks)} tasks")
        for t in self.tasks:
            print(f"  [{t.task_id}] {t.name:20s} Period:{t.period_ms:3d}ms Deadline:{t.deadline_ms:3d}ms")
    
    def tick(self, elapsed_time_s: float):
        """Advance time and execute tasks by deadline"""
        self.current_time += elapsed_time_s
        
        # Release tasks whose period has come
        for task in self.tasks:
            if self.current_time >= task.next_release_time:
                task.release(self.current_time)
                self.ready_queue.append(task)
        
        # Sort by absolute deadline (min-heap style)
        self.ready_queue.sort(key=lambda t: t.absolute_deadline)
        
        # Execute ready tasks
        executed = []
        for task in self.ready_queue:
            exec_time = task.execute()
            task.check_deadline(self.current_time + exec_time)
            executed.append(task)
        
        self.ready_queue = []
    
    def get_cpu_utilization(self) -> float:
        """Calculate CPU utilization"""
        if not self.tasks:
            return 0.0
        
        total_wcet = sum(t.wcet_us for t in self.tasks)
        min_period = min(t.period_ms for t in self.tasks)
        
        return (total_wcet / 1000) / min_period
    
    def get_stats(self):
        """Get scheduler statistics"""
        total_deadline_misses = sum(t.deadline_misses for t in self.tasks)
        total_executions = sum(t.execution_count for t in self.tasks)
        
        return {
            'scheduler': 'EDF',
            'current_time_s': self.current_time,
            'total_executions': total_executions,
            'total_deadline_misses': total_deadline_misses,
            'miss_rate': total_deadline_misses / total_executions if total_executions > 0 else 0,
            'cpu_utilization': self.get_cpu_utilization(),
            'task_stats': [t.get_stats() for t in self.tasks],
        }

# ============================================================================
# UTILITIES
# ============================================================================

def print_scheduler_stats(stats: dict):
    """Pretty-print scheduler statistics"""
    print("\n" + "=" * 80)
    print(f"SCHEDULER: {stats['scheduler']}")
    print("=" * 80)
    print(f"Simulation time: {stats['current_time_s']:.2f}s")
    print(f"Total executions: {stats['total_executions']}")
    print(f"Total deadline misses: {stats['total_deadline_misses']}")
    print(f"Deadline miss rate: {stats['miss_rate']*100:.2f}%")
    print(f"CPU utilization: {stats['cpu_utilization']*100:.2f}%")
    
    print("\n" + "─" * 80)
    print("Per-Task Statistics:")
    print("─" * 80)
    print(f"{'Task':<20s} {'Exec':>8s} {'Misses':>8s} {'Miss Rate':>10s} {'Avg Time':>10s}")
    print("─" * 80)
    
    for task_stat in stats['task_stats']:
        print(f"{task_stat['name']:<20s} {task_stat['execution_count']:>8d} "
              f"{task_stat['deadline_misses']:>8d} {task_stat['miss_rate']*100:>9.2f}% "
              f"{task_stat['avg_exec_time_us']:>9.2f}µs")

if __name__ == "__main__":
    print("Phase 1 modules loaded successfully")
    print("Use: from phase_1_task import Task, RMSScheduler, EDFScheduler")
