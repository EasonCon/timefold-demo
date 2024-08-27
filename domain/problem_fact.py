from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Annotated, Optional
from typing import List

from timefold.solver.domain import PlanningId


@dataclass
class Base(object):
    id: Annotated[str, PlanningId]

    def __str__(self):
        return f"{self.id}"

    def __hash__(self):
        return hash(self.id)


class TaskType(Enum):
    MO = "MO"
    MRP = "MRP"


class SequenceType(Enum):
    SINK = "SINK"
    SOURCE = "SOURCE"
    STANDARD = "STANDARD"


@dataclass
class Operation(Base):
    task: Task
    quantity: float
    sequence_type: SequenceType
    waiting_time: float = 0.0

    # 工序只关心临近前后工序
    predecessor_operations: Optional[List['Operation']] = None
    successor_operations: Optional[List['Operation']] = None
    execution_modes: List[ExecutionMode] = None


@dataclass
class Task(Base):
    """将task关系拼接成图"""
    type: TaskType
    due_date: float = 0
    sequence_type: SequenceType = SequenceType.SINK
    previous_tasks: Optional[List['Task']] = None
    successor_task: Optional[List['Task']] = None
    craft_paths: Optional[List['Operation']] = None


@dataclass
class Resource(Base):
    timeslots: List[list]
    local_time: float
    capacity: int


@dataclass
class ExecutionMode(Base):
    """一个执行模式对应一个资源需求"""
    task: Task
    operation: Operation
    requirement: Optional[Requirement] = None


@dataclass
class Requirement(Base):
    resource: Resource
    beat_seconds: float
    priority: int
    operation: Optional[Operation] = None
    execution_mode: Optional[ExecutionMode] = None
