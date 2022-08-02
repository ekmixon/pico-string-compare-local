import webbrowser
import subprocess

import plotly.plotly as py
import plotly.graph_objs as go

from os.path import exists, dirname, getsize


def load_results_from_csv(file_name):
    """
    Load results generated by other languages from file
    :return: A list of tuples with the results
    """
    #
    #   First we sort the CSV in order to be able to read it faster (only one
    #   time from top to bottom)
    #
    name, extension = file_name.rsplit('.', 1)
    name += '-sorted'
    sorted_file_name = f'{name}.{extension}'

    sort_file_dir = dirname(file_name)

    if not exists(sorted_file_name) or getsize(sorted_file_name) == 0:
        print('Sorting results...')

        env = {'LC_ALL': 'C'}
        command = ['sort', '-n', file_name, '-o', sorted_file_name,

                   # compress temp files, reduces disk usage
                   '--compress-program', 'gzip',

                   # use at most 2G ram
                   '-S', '2G',

                   # use the directory where the file is to store temp files
                   # should avoid my /tmp/ to fill up with temp files.
                   '-T', sort_file_dir
                   ]

        subprocess.check_output(command, env=env)

        print('Done!')

    #
    #   Load the results
    #
    test_num = 0
    str_test_num = str(test_num)
    measurements = []

    for line in open(sorted_file_name):
        line = line.strip()

        if not line:
            continue

        line_test_num, data_point = line.split(',')
        data_point = float(data_point)

        if line_test_num != str_test_num:
            # The test number in the file changed, its time to yield
            yield test_num, measurements

            # +1
            test_num += 1
            str_test_num = str(test_num)

            # Start a new measurements for the new set
            measurements = [data_point]
        else:
            # We're still in the same test number
            measurements.append(data_point)

    yield test_num, measurements


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

    print(f'Time difference between #8 and #7: {diff_1}')
    print(f'Time difference between #16 and #15: {diff_2}')
    print(f'Time difference between #100 and #7: {diff_3}')


def create_graph(measurements, samples, language, title, stats_method_name):
    args = (language, samples, stats_method_name, title)
    final_title = '%s - %s samples - %s - %s' % args

    x_axis = []
    y_axis = []

    for i, result in measurements:
        x_axis.append(i)
        y_axis.append(result)

    # Create a trace
    trace = go.Scatter(
        x=x_axis,
        y=y_axis,
        mode='markers'
    )

    layout = go.Layout(
        title=final_title,
        xaxis=dict(title='Numbers of character in common'),
        yaxis=dict(title='Time spent comparing strings (ns)'),
    )

    fig = go.Figure(data=[trace], layout=layout)

    plot_url = py.plot(
        fig,
        filename=f'{language}-str-cmp-{title}',
        fileopt='new',
        auto_open=False,
    )


    plot_url += '.embed'
    print(f'Plot URL: {plot_url}')

    subprocess.check_output(['google-chrome-stable', plot_url])
