from manager.apps import ManagerConfig
from django.http import Http404


def make_model(func):
    def inner(request, model=[]):
        if isinstance(model, list):
            return func(request)

        model = model.replace('-', '_')
        if not hasattr(ManagerConfig, model):
            raise Http404("Invalid Model")

        return func(request, [getattr(ManagerConfig, model)])

    return inner
