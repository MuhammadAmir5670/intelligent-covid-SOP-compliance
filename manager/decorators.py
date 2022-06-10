from statistics import mode
from manager.apps import ManagerConfig
from django.http import Http404


def make_model(func):
    def inner(request, model=[]):
        if isinstance(model, list):
            return func(request)

        if model not in ManagerConfig.Models.keys():
            raise Http404("Invalid Model")

        return func(request, [ManagerConfig.Models[model]])

    return inner
