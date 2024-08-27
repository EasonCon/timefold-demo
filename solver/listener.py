from collections import deque

from timefold.solver.domain import VariableListener
from timefold.solver.score import ScoreDirector

from domain.scheduling_entity import OperationAllocation


class PreviousOperationsDoneDate(VariableListener):
    def after_entity_added(self, score_director: ScoreDirector, new_allocation: OperationAllocation) -> None:
        self.update_allocation(score_director, new_allocation)

    def after_variable_changed(self, score_director: ScoreDirector, new_allocation: OperationAllocation) -> None:
        self.update_allocation(score_director, new_allocation)

    def update_allocation(self, score_director: ScoreDirector, allocation: OperationAllocation) -> None:
        q = deque([])
        q.extend(allocation.successorAllocationList)
        while q:
            node = q.popleft()
            update_flag: bool = self.update_previous_done_date(score_director, allocation)
            if update_flag:
                q.extend(node.successorAllocationList)

    def update_previous_done_date(self, score_director: ScoreDirector, allocation: OperationAllocation) -> bool:
        done_date: float = 0
        for elem in allocation.predecessorAllocationList:
            done_date = max(done_date, elem.get_end_at())
        if done_date == allocation.previous_done_time:
            return False

        # 告知求解器变量更新
        score_director.before_variable_changed(allocation, "previous_done_time")
        allocation.previous_done_time = done_date
        score_director.after_variable_changed(allocation, "previous_done_time")
        return True
