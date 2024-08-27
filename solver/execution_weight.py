from domain.scheduling_entity import OperationAllocation


class ExecutionModeStrengthWeightFactory:
    def create_weight(self, allocation: OperationAllocation):
        allocation.operation.execution_modes.sort(key=lambda x: x.requirement.priority)
