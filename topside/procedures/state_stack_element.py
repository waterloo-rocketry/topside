class StackElement:
    """
    A Class meant to represent elements on the procedures engine state stack

    Fields:
        -plumbing_engine: a copy of the plumbing_engine at the time of pushing to the stack
        -procedure_id: the procedure_id at the time of pushing to the stack
        -current_step: the current_step and the time of pushing to the stack
        -step_position: the step_position at the time of pushing ot the stack
    """

    def __init__(self, plumbing_engine, procedure_id, current_step, step_position):
        self.plumb = plumbing_engine
        self.prod_id = procedure_id
        self.curr_step = current_step
        self.step_pos = step_position
