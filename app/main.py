from timefold.solver import SolverFactory
from timefold.solver.config import SolverConfig, ScoreDirectorFactoryConfig

from domain.problem_fact import *
from domain.scheduling_entity import SchedulingSolution, OperationAllocation
from solver.score import define_constraints


def generate_data() -> SchedulingSolution:
    resource_1 = Resource(id="resource_1", timeslots=[[1, 5]], capacity=1, local_time=0)
    resource_2 = Resource(id="resource_2", timeslots=[[3, 7]], capacity=1, local_time=0)

    task_1 = Task(id="001", type=TaskType.MO, due_date=100)

    operation_1_1 = Operation(id="op_1_1", task=task_1, quantity=10, sequence_type=SequenceType.SOURCE)
    operation_1_2 = Operation(id="op_1_2", task=task_1, quantity=20, sequence_type=SequenceType.SINK)

    operation_1_1.successor_operations = operation_1_2
    operation_1_2.predecessor_operations = operation_1_1

    task_1.craft_paths = [operation_1_1, operation_1_2]

    # 执行模式定义
    exc1_1 = ExecutionMode(id="exc1_1", task=task_1, operation=operation_1_1)
    exc1_2 = ExecutionMode(id="exc1_2", task=task_1, operation=operation_1_1)
    exc2_1 = ExecutionMode(id="exc2_1", task=task_1, operation=operation_1_2)
    operation_1_1.execution_modes = [exc1_1, exc1_2]
    operation_1_2.execution_modes = [exc2_1]

    # 每个执行模式对应一种资源需求
    requirement_1_1 = Requirement(resource=resource_1, execution_mode=exc1_1, beat_seconds=5, priority=1, operation=operation_1_1, id="req_1_1")
    requirement_1_2 = Requirement(resource=resource_1, execution_mode=exc1_2, beat_seconds=7, priority=1, operation=operation_1_1, id="req_1_2")
    requirement_2_1 = Requirement(resource=resource_2, execution_mode=exc2_1, beat_seconds=10, priority=1, operation=operation_1_2, id="req_2_1")

    exc1_1.requirements = [requirement_1_1]
    exc1_2.requirements = [requirement_1_2]
    exc2_1.requirements = [requirement_2_1]

    # operation  allocation 实体
    allocation_1_1 = OperationAllocation(operation=operation_1_1)
    allocation_1_2 = OperationAllocation(operation=operation_1_2)

    return SchedulingSolution(
        id="1",
        resources=[resource_1, resource_2],
        tasks=[task_1],
        execution_modes=[exc1_1, exc1_2, exc2_1],
        requirements=[requirement_1_1, requirement_1_2, requirement_2_1],
        allocations=[allocation_1_1, allocation_1_2]
    )


def main():
    solver_factory = SolverFactory.create(
        SolverConfig(
            solution_class=SchedulingSolution,
            entity_class_list=[OperationAllocation],
            score_director_factory_config=ScoreDirectorFactoryConfig(
                constraint_provider_function=define_constraints
            )
        )
    )
    problem = generate_data()
    solver = solver_factory.build_solver()
    solution = solver.solve(problem)


if __name__ == "__main__":
    main()
