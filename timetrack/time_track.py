"""
A quick (& dirty) parser of my time tracking into a dictionary for cartjs bar

Format is:
YYYYMMDD- X min activity, function, other
(multiple activities or functions may be seperated by spaces)

Example:
20160209- 15 min meeting, scrum, notes

"""

import datetime


def parse_time():

    activities = {}
    functions = {}

    with open("timetrack/time.txt") as file:
        for line in file:

            # Split the string of the line
            date_raw = line[:8]
            minutes_raw, task_annotation = line[9:].rstrip().split('min')
            task_tokens = task_annotation.split(',')

            activity_tokens = task_tokens[0].split()
            function_tokens = task_tokens[1].split()

            min = int(minutes_raw)

            # Store temporarily in dictionaries (analogous for functions)
            #
            # dict = {'activityA': { 'date1': minutes
            #                        'date2': minutes},
            #         'activityB': { 'date1': minutes
            #                        'date3': minutes},
            #         }
            #

            n_act = len(activity_tokens)
            for activity in activity_tokens:
                activities.setdefault(activity, {})
                activities[activity].setdefault(date_raw, 0)
                activities[activity][date_raw] += min / n_act

            n_fun = len(function_tokens)
            for function in function_tokens:
                functions.setdefault(function, {})
                functions[function].setdefault(date_raw, 0)
                functions[function][date_raw] += min / n_fun

    # Now sort out into lists by date with color annotation etc used by chartjs
    # see format example at end of file

    # TODO: set to date detection from parsed time
    first_date_str = '20160131'
    first_date = datetime.datetime.strptime(first_date_str, '%Y%m%d')
    days = 30

    date_labels = []
    activity_data = {a: [] for a in activities.keys()}
    function_data = {f: [] for f in functions.keys()}

    date = first_date
    for days in range(days):
        date_labels.append(date.strftime('%Y%m%d'))
        for activity in activity_data:
            activity_data[activity].append(activities[activity].get(date_labels[-1], 0))
        for function in function_data:
            function_data[function].append(functions[function].get(date_labels[-1], 0))
        date += datetime.timedelta(days=1)

    plots = {'all_plots': []}

    chart_colors = {'planning': (165, 21, 53, 1),  # Burgundy
                    'code': (75, 173, 158, 1),  # Teal
                    'meeting': (227, 173, 53, 1),  # gold
                    'setup': (121, 130, 56, 1),  # olive
                    'research': (251, 109, 80, 1),  # peach
                    'documentation': (121, 121, 121, 1),
    }
    default_color = (194, 185, 162, 1)  # ivory

    data_activities = {'labels': date_labels,
                       'datasets': []}
    for activity in activity_data:
        activity_dataset = {}
        activity_dataset['label'] = activity
        color = chart_colors.get(activity, default_color)
        activity_dataset['strokeColor'] = "rgba({:d}, {:d}, {:d}, 1)".format(color[0], color[1], color[2])
        activity_dataset['fillColor'] = "rgba({:d}, {:d}, {:d}, 1)".format(color[0], color[1], color[2])
        activity_dataset['data'] = activity_data[activity]
        data_activities['datasets'].append(activity_dataset)

    plots["all_plots"].append(data_activities)

    # Functions
    chart_colors = {'algorithm': (165, 21, 53, 1),  # Burgundy
                    'seed-data': (75, 173, 158, 1),  # Teal
                    'page-flow': (227, 173, 53, 1),  # gold
                    'upload': (168, 210, 0, 1),  # lime
                    'data-model': (121, 130, 56, 1),  # olive
                    'data-structures': (251, 109, 80, 1),  # peach
                    'time-track': (121, 121, 121, 1),  # charcoal
                    'display': (255, 124, 0, 1),
                    'tools': (64, 125, 214, 1),  # light blue
                    "setup": (0, 72, 170, 1),  # cobalt
                    'advisor-mentor': (171, 77, 169, 1),  # violet
                    'scrum': (121, 121, 121, 1),  # charcoal
                    'code-review': (122, 74, 169, 1),  #purple
                    "help": (0, 72, 170, 1),  # cobalt
                    }


    # User defined groups to plot together, and finding the other functions
    function_groups = [('algorithm', 'data-structures'),
                       ('page-flow',  'display'),
                       ('scrum', 'help', 'code-review', 'advisor-mentor'),
                       ('data-model', 'seed-data'),
                       ('upload',),
                       ]
    functions_all = set(function_data.keys())
    functons_grouped = set([f  for g in function_groups for f in g])
    functions_other = functions_all - functons_grouped
    function_groups.append(functions_other)

    for this_group in function_groups:
        data_functions = {'labels': date_labels,
                           'datasets': []}
        for function in this_group:
            function_dataset = {}
            function_dataset['label'] = function
            color = chart_colors.get(function, default_color)
            function_dataset['strokeColor'] = "rgba({:d}, {:d}, {:d}, 1)".format(color[0], color[1], color[2])
            function_dataset['fillColor'] = "rgba({:d}, {:d}, {:d}, 1)".format(color[0], color[1], color[2])
            function_dataset['data'] = function_data[function]
            data_functions['datasets'].append(function_dataset)
        plots["all_plots"].append(data_functions)

    return plots

# EXAMPLE CHART JS FORMAT
#
# data = {
#     labels: ["January", "February", "March", "April", "May", "June", "July"],
#     datasets: [
#         {
#             label: "My First dataset",
#             fillColor: "rgba(220,220,220,0.5)",
#             strokeColor: "rgba(220,220,220,0.8)",
#             highlightFill: "rgba(220,220,220,0.75)",
#             highlightStroke: "rgba(220,220,220,1)",
#             data: [65, 59, 80, 81, 56, 55, 40]
#         },
#         {
#             label: "My Second dataset",
#             fillColor: "rgba(151,187,205,0.5)",
#             strokeColor: "rgba(151,187,205,0.8)",
#             highlightFill: "rgba(151,187,205,0.75)",
#             highlightStroke: "rgba(151,187,205,1)",
#             data: [28, 48, 40, 19, 86, 27, 90]
#         }
#     ]
# }
