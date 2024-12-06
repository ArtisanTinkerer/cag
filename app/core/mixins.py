class StepMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  # type: ignore
        context['step_num'] = self.step_num  # type: ignore

        if hasattr(self, 'back_url_name'):
            context['back_link'] = self.back_url_name  # type: ignore

        return context
