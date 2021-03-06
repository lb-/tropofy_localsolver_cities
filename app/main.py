import csv
import subprocess

import pkg_resources

from sqlalchemy.schema import Column
from sqlalchemy.types import Boolean, Float, Integer, Text

from tropofy.app import AppWithDataSets, Parameter, Step, StepGroup
from tropofy.database.tropofy_orm import DataSetMixin
from tropofy.widgets import (
    Chart, CustomWidget, ExecuteFunction, ParameterForm, SimpleGrid)


# Models

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


class City(DataSetMixin):
    name = Column(Text, nullable=False)
    country = Column(Text, nullable=False)
    latitude = Column(Float)
    longitude = Column(Float)

    # rankings (weights)
    rank_coffee = Column(Integer, nullable=False)
    rank_holiday = Column(Integer, nullable=False)
    rank_working = Column(Integer, nullable=False)

    # costs
    cost_per_day = Column(Float, nullable=False)

    # easily remove places not wanting to visit
    # in_wishlist = Column(Boolean, nullable=False)

    @classmethod
    def get_ordered_list_of_all_items(cls, data_set):
        return data_set.query(cls).order_by(cls.id).all()


class Preferences(DataSetMixin):
    priority_coffee = Column(Integer, nullable=False)
    priority_holiday = Column(Integer, nullable=False)
    priority_working = Column(Integer, nullable=False)
    places_to_visit = Column(Integer, nullable=False)
    budget_per_day = Column(Float, nullable=False)


# Loading Data

def load_data_set_example(app_session):
    data = []

    with open('./app/example.csv') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # basic conversion of floats and integers from csv
            cleaned_row = dict()
            for key, value in row.iteritems():
                try:
                    cleaned_row[key] = int(value)
                except ValueError:
                    try:
                        cleaned_row[key] = float(value)
                    except ValueError:
                        cleaned_row[key] = value
            data.append(City(**cleaned_row))
        app_session.data_set.add_all(data)


# Widgets

class ExecuteLocalSolver(ExecuteFunction):
    def get_button_text(self, app_session):
        return "Make Priority From Wishlit"

    def execute_function(self, app_session):
        call_local_solver(app_session)


class KnapsackAllocationWeightPieChart(Chart):
    def get_chart_type(self, app_session):
        return Chart.PIECHART

    def get_table_schema(self, app_session):
        return {"item": ("string", "Item"), "weight": ("number", "Weight")}

    def get_table_data(self, app_session):
        items_in_knapsack = app_session.data_set.query(
            KnapsackItem).filter_by(in_knapsack=True).all()
        ks_weight = sum([item.weight for item in items_in_knapsack])
        ks_max_weight = app_session.data_set.get_param('max_weight')

        items_in_pie = [
            {"item": item.name, "weight": item.weight}
            for item in items_in_knapsack
        ]
        if ks_weight < ks_max_weight:
            items_in_pie.append(
                {"item": "Unused", "weight": ks_max_weight - ks_weight}
            )
        return items_in_pie

    def get_column_ordering(self, app_session):
        return ["item", "weight"]

    def get_order_by_column(self, app_session):
        return "weight"

    def get_chart_options(self, app_session):
        items_in_knapsack = app_session.data_set.query(
            KnapsackItem).filter_by(in_knapsack=True).all()
        ks_value = sum(item.value for item in items_in_knapsack)
        ks_weight = sum(item.weight for item in items_in_knapsack)
        template = 'Knapsack Value: {value}. Weight used: {weight} / {max}'
        title = template.format(
            value=ks_value,
            weight=ks_weight,
            max=app_session.data_set.get_param('max_weight')
        )
        return {'title': title}


class GoogleMapsWidget(CustomWidget):
    def custom_static_content_locations(self):
        return {
            "js": "google-maps-widget.js",
            "html": "google-maps-widget.html"
        }

    def _serialise(self, app_session):
        """Override internal method to resolve error when concat type."""
        # type: (AppSession) -> Dict[str, Any]
        d = super(CustomWidget, self)._serialise(app_session)
        # this line was causing issues, trying to contatenate type(self)
        # added .__name__ to end
        d.update({"componentName": d['componentName'] + type(self).__name__})
        d.update(self.page_load_serialise())
        return d


# Helper Functions

def generate_ui_step_group(name, steps):
    step_group = StepGroup(name=name)
    for step in steps:
        # each step should be a tuple with the name and an array of widgets
        step_group.add_step(Step(name=step[0], widgets=step[1]))
    return step_group


# Main Application

class Application(AppWithDataSets):
    def get_name(self):
        return 'App'

    def get_static_content_path(self, app_session):
        return pkg_resources.resource_filename('app', 'static')

    def get_gui(self):
        step_groups = []
        step_groups.append(
            generate_ui_step_group(
                'Enter Your Data', [('Cities', [SimpleGrid(City)])]
            )
        )
        step_groups.append(
            generate_ui_step_group(
                'Preview', [('Map', [GoogleMapsWidget()])]
            )
        )
        step_groups.append(
            generate_ui_step_group(
                'Solve', [('Solve Priority Wish list', [ExecuteLocalSolver()])]
            )
        )
        step_groups.append(
            generate_ui_step_group(
                'See Solution', [
                    (
                        'Prioritised Wish List',
                        [
                            KnapsackAllocationWeightPieChart(),
                            SimpleGrid(KnapsackItem)
                        ]
                    )
                ]
            )
        )
        return step_groups

    def get_examples(self):
        return {
            'Example - LB 2017 Cities': load_data_set_example,
        }

    def get_parameters(self):
        return [
            Parameter(
                name='max_weight',
                label='Max Knapsack Weight',
                default=10,
                allowed_type=int,
                validator=validate_value_g_zero
            )
        ]

    def get_default_example_data_set_name(self):
        return "Demo French Shopping Knapsack"

    def get_icon_url(self):
        return "/{}/static/{}/logo.png".format(
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
        361, 949, 30, 448, 516, 54, 492, 762, 720, 855, 78, 678, 474, 263,
        96, 845, 85, 876, 242, 321, 144, 889, 525, 948, 653, 261, 504, 883,
        693, 224, 746, 246, 38, 388, 603, 863, 126, 654, 939, 636, 961, 376,
        556, 731, 199, 692, 75, 337, 113, 63, 320, 878, 417, 647, 208, 617,
        609, 738, 144, 748, 388, 789, 106, 259, 409, 518, 452, 719, 359,
        119, 739, 73, 458, 552, 727, 581, 298, 663, 136, 221, 268, 774, 118,
        670, 906, 153, 790, 244, 902, 242, 224, 381, 669, 515, 917, 724, 958,
        223, 606, 372
    ]
    values = [
        537, 566, 320, 654, 668, 68, 332, 298, 689, 964, 731, 726, 299, 22,
        798, 558, 287, 642, 291, 152, 272, 535, 731, 866, 987, 5, 985, 763,
        793, 451, 429, 754, 50, 246, 142, 711, 326, 863, 295, 860, 518, 912,
        672, 224, 578, 779, 917, 872, 836, 542, 987, 594, 914, 358, 359, 479,
        617, 959, 441, 76, 156, 646, 509, 30, 716, 276, 634, 791, 442, 7, 99,
        233, 79, 942, 68, 30, 540, 792, 703, 82, 478, 482, 979, 902, 785, 564,
        590, 713, 861, 374, 873, 316, 14, 692, 954, 603, 381, 835, 735, 779
    ]

    items = []
    for i in range(len(weights)):
        items.append(
            KnapsackItem(
                name="Item_%s" % i, weight=weights[i], value=values[i]
            )
        )

    app_session.data_set.add_all(items)
    app_session.data_set.set_param('max_weight', 24379, app_session.app)


def call_local_solver(app_session):
    invoke_localsolver_using_lsp_file(
        app_session, write_localsolver_input_file(app_session))


def write_localsolver_input_file(app_session):
    file_name = 'input.in'

    file_path = app_session.get_file_path_in_local_data_set_dir(file_name)
    f = open(file_path, 'w')

    items = KnapsackItem.get_ordered_list_of_all_items(app_session.data_set)
    weights = [str(item.weight) for item in items]
    values = [str(item.value) for item in items]

    f.write('%s\n' % len(items))
    f.write('%s\n' % " ".join(weights))
    f.write('%s\n' % " ".join(values))

    f.write('%s' % app_session.data_set.get_param('max_weight'))

    f.close()
    return file_name


def invoke_localsolver_using_lsp_file(app_session, input_file_name):
    for item in app_session.data_set.query(KnapsackItem).all():
        item.in_knapsack = False  # Reset solution

    lsp_file_path = pkg_resources.resource_filename('app', 'solver.lsp')
    file_name = 'output.txt'
    file_path = app_session.get_file_path_in_local_data_set_dir(file_name)
    open(file_path, 'w').close()  # clear the solution file if it exists
    p = subprocess.Popen(
        [
            "localsolver",
            lsp_file_path,
            "inFileName=%s" % input_file_name,
            "solFileName=%s" % file_name,
            "lsTimeLimit=2"
        ],
        cwd=app_session.local_data_set_dir,
        stdout=subprocess.PIPE
    )
    out, _ = p.communicate()
    with open(file_path) as f:
        content = f.readlines()
        if content:
            app_session.task_manager.send_progress_message(out)
            items = KnapsackItem.get_ordered_list_of_all_items(
                app_session.data_set)
            item_indexes_in_knapsack = [int(i) for i in content]
            for i, item in enumerate(items):
                item.in_knapsack = i in item_indexes_in_knapsack
        else:
            app_session.task_manager.send_progress_message(
                '''The data you have entered exceeds the limits of the trial
                version of LocalSolver used to run this app. LocalSolver's
                Trial Version does not allow more than 1000 expressions
                and 100 decisions.'''
            )


def validate_value_g_zero(value):
    return True if value > 0 else "Value must be > 0."
