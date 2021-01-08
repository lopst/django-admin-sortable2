# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json
from django.apps import apps
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    args = '<model model ...>'
    help = 'Restore the primary ordering fields of a model containing a special ordering field'

    def add_arguments(self, parser):
        parser.add_argument('models', nargs='+', type=str, help='Models list.')
        parser.add_argument('-f', '--filter', type=str, help='Extra filter.')

    def handle(self, *args, **options):

        qs_filter = options['filter'] if options['filter'] else None

        for modelname in options['models']:
            try:
                app_label, model_name = modelname.rsplit('.', 1)
                Model = apps.get_model(app_label, model_name)
            except ImportError:
                raise CommandError('Unable to load model "%s"' % modelname)

            if not hasattr(Model._meta, 'ordering') or len(Model._meta.ordering) == 0:
                raise CommandError('Model "{0}" does not define field "ordering" in its Meta class'.format(modelname))

            orderfield = Model._meta.ordering[0]
            if orderfield[0] == '-':
                orderfield = orderfield[1:]

            qs = Model.objects

            if qs_filter:
                qs_filter = json.loads(qs_filter)
                qs = qs.filter(**qs_filter)

            for order, obj in enumerate(qs.iterator(), start=1):
                setattr(obj, orderfield, order)
                obj.save()

            self.stdout.write('Successfully reordered model "{0}"'.format(modelname))
