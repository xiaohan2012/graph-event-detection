# Useful links that helped me learn

## DB

- [MySQL "INTO OUTFILE"](http://stackoverflow.com/questions/356578/how-to-output-mysql-query-results-in-csv-format)

## Python

- [Summing two counters](http://stackoverflow.com/questions/19356055/summing-the-contents-of-two-collections-counter-objects)
- [Remove all contents under some directory](http://stackoverflow.com/questions/185936/delete-folder-contents-in-python)
- [Python Logging datetime formatter](https://docs.python.org/3/library/logging.html)
- [Numpy logical_and](http://docs.scipy.org/doc/numpy/reference/generated/numpy.logical_and.html)
- [Python lambda function keep value of local variable](http://stackoverflow.com/questions/10452770/python-lambdas-binding-to-local-values)
- [matplotlib multiple figures and axes](http://matplotlib.org/users/pyplot_tutorial.html)
- [subplot in loop](http://stackoverflow.com/questions/17210646/python-subplot-within-a-loop-first-panel-appears-in-wrong-position)
- [histogram given bins and weights](http://stackoverflow.com/questions/17238087/histogram-from-data-which-is-already-binned-i-have-bins-and-frequency-values)
- [savefig without X](http://stackoverflow.com/questions/4931376/generating-matplotlib-graphs-without-a-running-x-server)
- [bar chart](http://matplotlib.org/examples/api/barchart_demo.html)
- [GNU Parallel run multiple commands](https://www.gnu.org/software/parallel/parallel_tutorial.html#A-single-input-source)
- [GNU parallel working directory](https://www.gnu.org/software/parallel/parallel_tutorial.html#Working-dir)
- [Bash iterate through array](http://www.cyberciti.biz/faq/bash-iterate-array/)
- [argparse action="store_true|false"](https://docs.python.org/3/library/argparse.html#action)
- [Python subprocess](https://docs.python.org/2/library/subprocess.html)
- [datetime.strftime cheatsheet](http://strftime.org/)
- [No such file or directory when subprocess](http://stackoverflow.com/questions/24306205/file-not-found-error-when-launching-a-subprocess)
- [memory_profiler line by line](http://www.huyng.com/posts/python-performance-analysis/)
- [time_profiler line by line](https://github.com/rkern/line_profiler)
- [nosetest --nocapture](http://stackoverflow.com/questions/5975194/nosetests-is-capturing-the-output-of-my-print-statements-how-to-circumvent-this)
- multiprocessing
  - allows shared object event custom object
  - can only pickle top level functions, classmethods not good, alternative, `pathos` 
- [nose assert_equal.__self__.maxDiff=None](http://stackoverflow.com/questions/14493670/how-to-set-self-maxdiff-in-nose-to-get-full-diff-output)

## Pandas

- [Pandas read_csv skip bad lines](http://stackoverflow.com/questions/18039057/python-pandas-error-tokenizing-data): pass `error_bad_lines=False`
- [nth group](http://stackoverflow.com/questions/20087713/pandas-dataframe-groupby-and-get-nth-row)
- `Series.tolist`
- `DataFrame.iterrows`
- [ith row in DataFrame](http://stackoverflow.com/questions/25254016/pandas-get-first-row-value-of-a-given-column): `DataFrame.iloc[i]`
- add column: `df.columns.tolist() + [something]`
- `df.rename(columns={'old': 'new', ...}, inplace=True)`
- `df.to_json(orient="records)"`
- `df.equals`
- `df.values` to get data array
- filter rows by condition: `df[df.map(func) > 0]`

## JavaScript

- [Optional argument](http://stackoverflow.com/questions/3147640/javascript-optional-arguments-in-function)
- Category palettes: `d3.scale.ordinal().domain([...]).range(d3.scale.category10().range());`
- d3 time format: `d3.time.format("%Y-%m-%d")`


## Github issues

- [PyGithub](https://github.com/PyGithub/PyGithub)
- [Github API: issues](https://developer.github.com/v3/issues/)

## Git
- [undo merge](http://stackoverflow.com/questions/2389361/undo-a-git-merge)