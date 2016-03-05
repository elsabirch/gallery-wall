"""
A quick (& dirty) parser of my time tracking into a dictionary for cartjs bar

Format is:
YYYYMMDD- X min activity, feature, other
(multiple activities or features may be seperated by spaces)

Example:
20160209- 15 min meeting, scrum, notes

"""

import datetime

CHART_COLORS = {
                # Activities
                'planning': (165, 21, 53, 1),  # Burgundy
                'code': (75, 173, 158, 1),  # Teal
                'meeting': (227, 173, 53, 1),  # gold
                'setup': (121, 130, 56, 1),  # olive
                'research': (251, 109, 80, 1),  # peach
                'documentation': (121, 121, 121, 1),
                'Total': (121, 121, 121, 1),  # charcoal
                # Features
                'algorithm': (165, 21, 53, 1),  # Burgundy
                'seed-data': (75, 173, 158, 1),  # Teal
                'page-flow': (255, 211, 0, 1),  # (227, 173, 53, 1),  # gold
                'upload': (0, 209, 66, 1),  # lime
                'data-model': (79, 143, 0, 1),  # olive
                'data-structures': (251, 109, 80, 1),  # peach
                'time-track': (121, 121, 121, 1),  # charcoal
                'display': (255, 124, 0, 1),
                'tools': (64, 125, 214, 1),  # light blue
                'setup': (0, 72, 170, 1),  # cobalt
                'design': (171, 77, 169, 1),  # violet
                'scrum': (121, 121, 121, 1),  # charcoal
                'code-review': (122, 74, 169, 1),  # purple
                'advisor-mentor': (0, 72, 170, 1),  # cobalt
                'testing': (0, 209, 66, 1),  # lime
                }

DEFAULT_COLOR = (194, 185, 162, 1)  # ivory


def get_time_spark():

    # Parse into dicts from file, these are a sparse representation of the data
    # in that they include only non-zero time durration activities/features.
    #
    # dict = {'activityA': { 'date1': minutes
    #                        'date2': minutes},
    #         'activityB': { 'date1': minutes
    #                        'date3': minutes},
    #        }
    activities_sparse, features_sparse = parse_time()

    # Date detection from parsed time
    all_date_str = sorted([d for a in activities_sparse for d in activities_sparse[a]])
    first_date_str = all_date_str[0]
    last_date_str = all_date_str[-1]
    first_date = datetime.datetime.strptime(first_date_str, '%Y%m%d')
    last_date = datetime.datetime.strptime(last_date_str, '%Y%m%d')
    days = (last_date - first_date).days + 2  # I like to see the next day too

    # create the lists of dates and data needed for chartjs
    t_norm = 400.0
    date_labels = [(first_date + datetime.timedelta(days=d)).strftime('%Y%m%d')
                   for d in range(days)]
    activities_vects = {a: [(activities_sparse[a].get(d, 0)/t_norm) for d in date_labels]
                        for a in activities_sparse}
    features_vects = {f: [(features_sparse[f].get(d, 0)/t_norm) for d in date_labels]
                      for f in features_sparse}

    # Display bar labels only at week starts
    date_labels_display = []
    start_idx = None
    for i in range(len(date_labels)):
        if date_labels[i] == '20160208':
            start_idx = i
        if start_idx and ((i-start_idx) % 7) == 0:
            date_labels_display.append('w{}'.format(1+(i-start_idx)/7))
        else:
            date_labels_display.append('')

    # Now sort out into lists by date with color annotation etc used by chartjs
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

    # All plots will be stored as a list of dicts to maintain order,
    # within another dict for jasonification
    plots = {'all_plots': [],
             'all_labels': [],
             'all_types': []}

    # Total time
    data_chartjs = {'labels': date_labels_display,
                    'datasets': []}
    dataset = {}
    dataset['label'] = 'Total'
    color = CHART_COLORS.get(dataset['label'], DEFAULT_COLOR)
    dataset['strokeColor'] = "rgba({:d}, {:d}, {:d}, 1)".format(color[0], color[1], color[2])
    dataset['fillColor'] = "rgba({:d}, {:d}, {:d}, 1)".format(color[0], color[1], color[2])
    dataset['data'] = [sum([activities_vects[a][i] for a in activities_vects]) for i in range(len(date_labels)) ]
    data_chartjs['datasets'].append(dataset)
    plots["all_plots"].append(data_chartjs)
    plots["all_labels"].append('Total Time')
    plots["all_types"].append('total-plots')


    # Activities (all plotted on a single set of axes)
    activities_sort_by_total = activities_vects.keys()
    activities_sort_by_total.sort(key=lambda a: sum(activities_vects[a]), reverse=True)

    for activity in activities_sort_by_total:
        data_chartjs = {'labels': date_labels_display,
                    'datasets': []}
        dataset = {}
        dataset['label'] = activity.title()
        color = CHART_COLORS.get(activity, DEFAULT_COLOR)
        dataset['strokeColor'] = "rgba({:d}, {:d}, {:d}, 1)".format(color[0], color[1], color[2])
        dataset['fillColor'] = "rgba({:d}, {:d}, {:d}, 1)".format(color[0], color[1], color[2])
        dataset['data'] = activities_vects[activity]
        data_chartjs['datasets'].append(dataset)

        plots["all_plots"].append(data_chartjs)
        plots["all_labels"].append(activity.title())
        plots["all_types"].append('activity-plots')

    # Features
    features_sort_by_total = features_vects.keys()
    features_sort_by_total.sort(key=lambda f: sum(features_vects[f]), reverse=True)

    for feature in features_sort_by_total:
        data_chartjs = {'labels': date_labels_display,
                        'datasets': []}
        dataset = {}
        dataset['label'] = feature.title()
        color = CHART_COLORS.get(feature, DEFAULT_COLOR)
        dataset['strokeColor'] = "rgba({:d}, {:d}, {:d}, 1)".format(color[0], color[1], color[2])
        dataset['fillColor'] = "rgba({:d}, {:d}, {:d}, 1)".format(color[0], color[1], color[2])
        dataset['data'] = features_vects[feature]
        data_chartjs['datasets'].append(dataset)
        plots["all_plots"].append(data_chartjs)
        plots["all_labels"].append(feature.title())
        plots["all_types"].append('feature-plots')


    return plots

def parse_time():
    """Parses time from text file into dicts for activities and features.

    Text file format:
    <date>- <minutes> min <activities space delimited>, <features space delimited>, <notes ignored>
    YYYYMMDD- X min activityA activityB, featureA, notesthatareignored, otherignored...

    Store/output in dictionaries (analogous for features):

    dict = {'activityA': { 'date1': minutes
                           'date2': minutes},
            'activityB': { 'date1': minutes
                           'date3': minutes},
            }
    """
    activities = {}
    features = {}

    with open("timetrack/time.txt") as file:
        for line in file:

            # Split the string of the line
            date_raw = line[:8]
            minutes_raw, task_annotation = line[9:].rstrip().split('min')
            task_tokens = task_annotation.split(',')

            activity_tokens = task_tokens[0].split()
            feature_tokens = task_tokens[1].split()

            min = int(minutes_raw)

            # If multiple activities are listed, split time between them evenly
            n_act = len(activity_tokens)
            for activity in activity_tokens:
                activities.setdefault(activity, {})
                activities[activity].setdefault(date_raw, 0)
                activities[activity][date_raw] += min / n_act

            # If multiple features are listed, split time between them evenly
            n_fun = len(feature_tokens)
            for feature in feature_tokens:
                features.setdefault(feature, {})
                features[feature].setdefault(date_raw, 0)
                features[feature][date_raw] += min / n_fun

    return activities, features


