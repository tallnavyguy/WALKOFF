class JsonElementCreator(object):
    playbook_class_ordering = None

    @classmethod
    def create(cls, json_in, element_class=None):
        from core.executionelements.playbook import Playbook
        cls._setup_ordering()
        if element_class is None:
            element_class = Playbook
        class_iterator = iter(cls.playbook_class_ordering)
        current_class, current_subfield_name = next(class_iterator)
        while current_class != element_class:
            try:
                current_class, current_subfield_name = next(class_iterator)
            except StopIteration:
                raise ValueError('Unknown class {}'.format(element_class.__class__.__name__))
        try:
            if current_subfield_name is not None:
                next_class, _ = next(class_iterator)
                subfield_json = json_in[current_subfield_name]
                json_in[current_subfield_name] = [next_class.create(element_json) for element_json in subfield_json]
                if hasattr(current_class, '_templatable'):
                    json_in['raw_representation'] = dict(json_in)
            return current_class(**json_in)
        except (KeyError, TypeError) as e:
            from core.helpers import format_exception_message
            raise ValueError('Improperly formatted JSON for ExecutionElement object {}'.format(format_exception_message(e)))

    @classmethod
    def _setup_ordering(cls):
        if cls.playbook_class_ordering is None:
            from core.executionelements.playbook import Playbook
            from core.executionelements.workflow import Workflow
            from core.executionelements.step import Step
            from core.executionelements.nextstep import NextStep
            from core.executionelements.condition import Condition
            from core.executionelements.transform import Transform
            cls.playbook_class_ordering = (
                (Playbook, 'workflows'), (Workflow, 'steps'), (Step, 'next_steps'), (NextStep, 'conditions'),
                (Condition, 'transforms'), (Transform, None))