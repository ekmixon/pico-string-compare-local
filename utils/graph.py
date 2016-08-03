#!/bin/env python2.7

import sys

import plotly.plotly as py
import plotly.graph_objs as go


def load_results(file_name):
    """
    Load results generated by other languages from file
    :return: A list of tuples with the results
    """
    measurements = []

    for line in file(file_name):
        line = line.strip()

        if not line:
            continue

        test_num, str_a, str_b, samples, time_sum = line.split(',')
        measurements.append((test_num, str_a, str_b, samples, time_sum))

    return measurements


def analyze_differences(measurements):
    samples = measurements[0][3]

    measurement_7 = measurements[7][4] * 1e9
    measurement_8 = measurements[8][4] * 1e9
    diff_1 = (measurement_8 - measurement_7) / samples

    measurement_15 = measurements[15][4] * 1e9
    measurement_16 = measurements[16][4] * 1e9
    diff_2 = (measurement_16 - measurement_15) / samples

    measurement_100 = measurements[100][4] * 1e9
    diff_3 = (measurement_100 - measurement_7) / samples

    print('Time difference between #8 and #7: %s' % diff_1)
    print('Time difference between #16 and #15: %s' % diff_2)
    print('Time difference between #100 and #7: %s' % diff_3)


def create_graph(measurements, samples, language, title):
    x_axys = []
    y_axys = []

    for i, (str_a, str_b, samples, result) in enumerate(measurements):
        x_axys.append(i)
        y_axys.append(result)

    # Create a trace
    trace = go.Scatter(
        x=x_axys,
        y=y_axys,
        mode='markers'
    )

    layout = go.Layout(
        title='%s - %s samples - %s' % (language, samples, title)
    )

    fig = go.Figure(data=[trace], layout=layout)

    plot_url = py.plot(fig,
                       filename='%s-str-cmp-%s' % (language, title),
                       fileopt='new')
    print('Plot URL: %s.embed' % plot_url)


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print('Usage: ./graph.py <measurements> <language> <title>')
        sys.exit(1)

    # Load results from file
    file_name = sys.argv[1]
    measurements = load_results(file_name)

    analyze_differences(measurements)

    # Graph
    samples = measurements[0][3]
    language = sys.argv[2]
    title = sys.argv[3]
    create_graph(measurements, samples, language, title)
