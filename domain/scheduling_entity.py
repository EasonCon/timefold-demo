from __future__ import annotations

from dataclasses import dataclass
from typing import Annotated, List, Optional
from typing import TYPE_CHECKING

from timefold.solver.domain import planning_entity, PlanningVariable, planning_solution, ShadowVariable, ProblemFactCollectionProperty, \
    PlanningEntityCollectionProperty, PlanningScore, ValueRangeProvider
from timefold.solver.score import HardSoftScore

from domain.problem_fact import Operation, Task, Resource, Requirement, ExecutionMode

if TYPE_CHECKING:
    from solver.listener import PreviousOperationsDoneDate

# class NotSourceOrSinkAllocationFilter(PinningFilter):
#     def accept(self, solution: SchedulingSolution, allocation: OperationAllocation) -> bool:
#         return allocation.operation.task.type == SequenceType.SINK or allocation.operation.task.type == SequenceType.SOURCE


@dataclass
@planning_solution
class SchedulingSolution:
    id: str
    tasks: List[Task]

    resources: Annotated[List[Resource], ProblemFactCollectionProperty]
    execution_modes: Annotated[List[ExecutionMode], ProblemFactCollectionProperty]
    requirements: Annotated[List[Requirement], ProblemFactCollectionProperty]

    allocations: Annotated[List[OperationAllocation], PlanningEntityCollectionProperty]
    score: Annotated[Optional[HardSoftScore], PlanningScore] = None


@dataclass
@planning_entity
class OperationAllocation:
    """
    工序分配关系
    """
    operation: Operation

    # 前工序的结束时间最大值
    previous_done_time: Annotated[
        float | None,
        ShadowVariable(variable_listener_class=PreviousOperationsDoneDate, source_variable_name="execution_mode"),
        ShadowVariable(variable_listener_class=PreviousOperationsDoneDate, source_variable_name="delay")
    ] = None

    execution_mode: Annotated[ExecutionMode, PlanningVariable] = None  # 软约束定义实现资源倾向
    delay: Annotated[float | None, PlanningVariable] = None
    source_allocation: OperationAllocation | None = None
    sink_allocation: OperationAllocation | None = None

    # 工序只关心临近工序的分配关系
    predecessorAllocationList: List[OperationAllocation] | None = None
    successorAllocationList: List[OperationAllocation] | None = None

    @ValueRangeProvider
    def execution_mode_range(self):
        return self.operation.execution_modes

    def get_previous_allocations(self):
        return self.predecessorAllocationList

    def get_end_at(self):
        return self.previous_done_time + self.delay + self.execution_mode.operation.quantity * self.execution_mode.requirement.beat_seconds

    def get_start_at(self):
        return self.previous_done_time + self.delay
