from timefold.solver import score
from timefold.solver.score import ConstraintFactory, Constraint, ConstraintCollectors, HardMediumSoftScore, constraint_provider
from timefold.solver.score import (Joiners, constraint_provider)

from domain.problem_fact import Requirement, SequenceType
from domain.scheduling_entity import OperationAllocation

"""
约束定义：
1.所有的operation都要分配资源
2.所有任务的延期最小：工序 + 工序类型计算
"""


@constraint_provider
def define_constraints(constraint_factory: ConstraintFactory):
    return [
        resource_capacity(constraint_factory),
        total_project_delay(constraint_factory),
        total_span(constraint_factory)
    ]


def resource_capacity(constraint_factory: ConstraintFactory) -> Constraint:
    return (
        constraint_factory.for_each(Requirement)
        .join(OperationAllocation,
              Joiners.equal(lambda req: req.execution_mode, lambda alloc: alloc.execution_mode))  # 方法引用
        .flatten_last(lambda a: list(range(a.get_start_at, a.get_end_at, 5)))
        .group_by(lambda resource_req, date: (resource_req.resource, date),
                  ConstraintCollectors.sum(lambda resource_req, date: resource_req.requirement))
        .filter(lambda resource_req, date, total_requirement: total_requirement > resource_req.capacity)
        .penalize(HardMediumSoftScore.ONE_HARD,
                  lambda resource_req, date, total_requirement: total_requirement - resource_req.capacity)
        .as_constraint("Renewable resource capacity")
    )


def total_project_delay(constraint_factory: ConstraintFactory) -> Constraint:
    return (
        constraint_factory.for_each(OperationAllocation)
        .filter(lambda allocation: allocation.get_end_at() is not None)
        .filter(lambda allocation: allocation.operation.sequence_type == SequenceType.SINK)
        .impact(
            HardMediumSoftScore.ONE_MEDIUM,
            lambda allocation: allocation.operation.task.due_date - allocation.get_end_at()
        )
        .as_constraint("Total project delay")
    )


def total_span(constraint_factory: ConstraintFactory) -> Constraint:
    return (
        constraint_factory.for_each(OperationAllocation)
        .filter(lambda allocation: allocation.get_end_at is not None)
        .filter(lambda allocation: allocation.operation.task.type == SequenceType.SINK)
        .group_by(
            lambda allocation: True,
            max(lambda allocation: allocation.get_end_at())
        )
        .penalize(
            HardMediumSoftScore.ONE_SOFT,
            lambda max_end_date: max_end_date
        )
        .as_constraint("Total makespan")
    )
