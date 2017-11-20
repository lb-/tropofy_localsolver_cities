"""
Authors: www.tropofy.com

Copyright 2015 Tropofy Pty Ltd, all rights reserved.

This source file is part of Tropofy and governed by the Tropofy terms of service
available at: http://www.tropofy.com/terms_of_service.html

The LocalSolver example this app is based on can be found at
http://www.localsolver.com/exampletour.html?file=knapsack.zip

Used with permission.

This source file is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
or FITNESS FOR A PARTICULAR PURPOSE. See the license files for details.


Problem Description:
"The knapsack problem is defined as follows: given a set of items, each with a
weight and a value, determine a subset of items in such a way that their total
weight is less than a given bound and their total value is as large as possible.
This problem is hard to solve in theory.

Note that the way to model is exactly the same than in integer programming:
for each item, a 0-1 decision variable is defined which is equal to 1 if the
item belongs to the knapsack and 0 otherwise.

Knapsack instances involving 1 million objects can be tackled using LocalSolver."
[http://www.localsolver.com/exampletour.html?file=knapsack.zip]
"""

import subprocess
import pkg_resources
from sqlalchemy.types import Integer, Text, Boolean
from sqlalchemy.schema import Column

from tropofy.app import AppWithDataSets, Parameter, Step, StepGroup
from tropofy.widgets import ExecuteFunction, SimpleGrid, Chart, ParameterForm
from tropofy.database.tropofy_orm import DataSetMixin


class KnapsackItem(DataSetMixin):
    name = Column(Text, nullable=False)
    weight = Column(Integer, nullable=False)
    value = Column(Integer, nullable=False)
    in_knapsack = Column(Boolean, nullable=False)

    def __init__(self, name, weight, value, in_knapsack=False):
        self.name = name
        self.weight = weight
        self.value = value
        self.in_knapsack = in_knapsack

    @classmethod
    def get_ordered_list_of_all_items(cls, data_set):
        return data_set.query(cls).order_by(cls.id).all()


class ExecuteLocalSolver(ExecuteFunction):
    def get_button_text(self, app_session):
        return "Solve Knapsack Problem"

    def execute_function(self, app_session):
        call_local_solver(app_session)


class KnapsackAllocationWeightPieChart(Chart):
    def get_chart_type(self, app_session):
        return Chart.PIECHART

    def get_table_schema(self, app_session):
        return {"item": ("string", "Item"), "weight": ("number", "Weight")}

    def get_table_data(self, app_session):
        items_in_knapsack = app_session.data_set.query(KnapsackItem).filter_by(in_knapsack=True).all()
        ks_weight = sum([item.weight for item in items_in_knapsack])
        ks_max_weight = app_session.data_set.get_param('max_weight')

        items_in_pie = [{"item": item.name, "weight": item.weight} for item in items_in_knapsack]
        if ks_weight < ks_max_weight:
            items_in_pie.append({"item": "Unused", "weight": ks_max_weight - ks_weight})
        return items_in_pie

    def get_column_ordering(self, app_session):
        return ["item", "weight"]

    def get_order_by_column(self, app_session):
        return "weight"

    def get_chart_options(self, app_session):
        items_in_knapsack = app_session.data_set.query(KnapsackItem).filter_by(in_knapsack=True).all()
        ks_value = sum(item.value for item in items_in_knapsack)
        ks_weight = sum(item.weight for item in items_in_knapsack)
        return {'title': 'Knapsack Value: {value}. Weight used: {weight} / {max}'.format(value=ks_value, weight=ks_weight, max=app_session.data_set.get_param('max_weight'))}


class LocalSolverApplication(AppWithDataSets):
    def get_name(self):
        return 'LocalSolver Knapsack Optimiser'

    def get_static_content_path(self, app_session):
        return pkg_resources.resource_filename('te_ls_knapsack', 'static')

    def get_gui(self):
        step_group1 = StepGroup(name='Enter your Data')
        step_group1.add_step(Step(name='Knapsack Items', widgets=[SimpleGrid(KnapsackItem)]))
        step_group1.add_step(Step(
            name='Knapsack Weight',
            widgets=[{"widget": ParameterForm(), "cols": 6}],
        ))

        step_group2 = StepGroup(name='Solve')
        step_group2.add_step(Step(name='Solve Knapsack Problem using LocalSolver', widgets=[ExecuteLocalSolver()]))

        step_group3 = StepGroup(name='View the Solution')
        step_group3.add_step(Step(name='Knapsack Allocation', widgets=[KnapsackAllocationWeightPieChart(), SimpleGrid(KnapsackItem)]))

        return [step_group1, step_group2, step_group3]

    def get_examples(self):
        return {
            "Demo French Shopping Knapsack": load_data_set_toy,
            "Demo 100 Item Knapsack": load_data_set_100,
        }

    def get_parameters(self):
        return [Parameter(name='max_weight', label='Max Knapsack Weight', default=10, allowed_type=int, validator=validate_value_g_zero)]

    def get_default_example_data_set_name(self):
        return "Demo French Shopping Knapsack"

    def get_icon_url(self):
        return "/{}/static/{}/knapsack.png".format(
            self.url_name,
            self.get_app_version(),
        )


def load_data_set_toy(app_session):
    app_session.data_set.add_all([
        KnapsackItem(name="Snail", weight=10, value=1),
        KnapsackItem(name="Frog Leg", weight=60, value=10),
        KnapsackItem(name="Camembert", weight=30, value=15),
        KnapsackItem(name="Baguette", weight=40, value=40),
        KnapsackItem(name="Croissant", weight=30, value=60),
        KnapsackItem(name="Macaroon", weight=20, value=90),
        KnapsackItem(name="Crepe", weight=20, value=100),
        KnapsackItem(name="Aioli", weight=2, value=15),
    ])

    app_session.data_set.set_param('max_weight', 102, app_session.app)


def load_data_set_100(app_session):
    weights = [
        361, 949, 30, 448, 516, 54, 492, 762, 720, 855, 78, 678, 474, 263, 96, 845,
        85, 876, 242, 321, 144, 889, 525, 948, 653, 261, 504, 883, 693, 224, 746,
        246, 38, 388, 603, 863, 126, 654, 939, 636, 961, 376, 556, 731, 199, 692,
        75, 337, 113, 63, 320, 878, 417, 647, 208, 617, 609, 738, 144, 748, 388,
        789, 106, 259, 409, 518, 452, 719, 359, 119, 739, 73, 458, 552, 727, 581,
        298, 663, 136, 221, 268, 774, 118, 670, 906, 153, 790, 244, 902, 242, 224,
        381, 669, 515, 917, 724, 958, 223, 606, 372
    ]
    values = [
        537, 566, 320, 654, 668, 68, 332, 298, 689, 964, 731, 726, 299, 22, 798,
        558, 287, 642, 291, 152, 272, 535, 731, 866, 987, 5, 985, 763, 793, 451,
        429, 754, 50, 246, 142, 711, 326, 863, 295, 860, 518, 912, 672, 224, 578,
        779, 917, 872, 836, 542, 987, 594, 914, 358, 359, 479, 617, 959, 441, 76,
        156, 646, 509, 30, 716, 276, 634, 791, 442, 7, 99, 233, 79, 942, 68, 30,
        540, 792, 703, 82, 478, 482, 979, 902, 785, 564, 590, 713, 861, 374, 873,
        316, 14, 692, 954, 603, 381, 835, 735, 779
    ]

    items = []
    for i in range(len(weights)):
        items.append(KnapsackItem(name="Item_%s" % i, weight=weights[i], value=values[i]))

    app_session.data_set.add_all(items)
    app_session.data_set.set_param('max_weight', 24379, app_session.app)


def call_local_solver(app_session):
    invoke_localsolver_using_lsp_file(app_session, write_localsolver_input_file(app_session))


def write_localsolver_input_file(app_session):
    input_file_name = 'input.in'
    input_file_path = app_session.get_file_path_in_local_data_set_dir(input_file_name)
    f = open(input_file_path, 'w')

    items = KnapsackItem.get_ordered_list_of_all_items(app_session.data_set)
    weights = [str(item.weight) for item in items]
    values = [str(item.value) for item in items]

    f.write('%s\n' % len(items))
    f.write('%s\n' % " ".join(weights))
    f.write('%s\n' % " ".join(values))

    f.write('%s' % app_session.data_set.get_param('max_weight'))

    f.close()
    return input_file_name


def invoke_localsolver_using_lsp_file(app_session, input_file_name):
    for item in app_session.data_set.query(KnapsackItem).all():
        item.in_knapsack = False  # Reset solution

    lsp_file_path = pkg_resources.resource_filename('te_ls_knapsack', 'knapsack.lsp')
    solution_file_name = 'output.txt'
    solution_file_path = app_session.get_file_path_in_local_data_set_dir(solution_file_name)
    open(solution_file_path, 'w').close()  # clear the solution file if it exists
    p = subprocess.Popen(
        ["localsolver", lsp_file_path, "inFileName=%s" % input_file_name, "solFileName=%s" % solution_file_name, "lsTimeLimit=2"],
        cwd=app_session.local_data_set_dir,
        stdout=subprocess.PIPE
    )
    out, _ = p.communicate()
    with open(solution_file_path) as f:
        content = f.readlines()
        if content:
            app_session.task_manager.send_progress_message(out)
            items = KnapsackItem.get_ordered_list_of_all_items(app_session.data_set)
            item_indexes_in_knapsack = [int(i) for i in content]
            for i, item in enumerate(items):
                item.in_knapsack = i in item_indexes_in_knapsack
        else:
            app_session.task_manager.send_progress_message(
                '''The data you have entered exceeds the limits of the trial version of LocalSolver used to run this app.
                LocalSolver's Trial Version does not allow more than 1000 expressions and 100 decisions.'''
            )


def validate_value_g_zero(value):
    return True if value > 0 else "Value must be > 0."