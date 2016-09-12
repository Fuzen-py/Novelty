import asyncio

from novelty import Novelty
import linecache
import os
import tracemalloc


def display_top(_snapshot, group_by='lineno'):
    _snapshot = _snapshot.filter_traces((
        tracemalloc.Filter(False, "<frozen importlib._bootstrap>"),
        tracemalloc.Filter(False, "<unknown>"),
    ))
    top_stats = _snapshot.statistics(group_by)
    text_to_write = 'Top {} lines'.format(len(top_stats[0:11]))
    print("Top {} lines".format(len(top_stats)))
    for index, stat in enumerate(top_stats[0:11], 1):
        frame = stat.traceback[0]
        # replace "/path/to/module/file.py" with "module/file.py"
        filename = os.sep.join(frame.filename.split(os.sep)[-2:])
        print("#%s: %s:%s: %.1f KiB"
              % (index, filename, frame.lineno, stat.size / 1024))
        text_to_write += "\n#%s: %s:%s: %.1f KiB" % (index, filename, frame.lineno, stat.size / 1024)
        line = linecache.getline(frame.filename, frame.lineno).strip()
        if line:
            print('    %s' % line)
            text_to_write += '\n    %s' % line
    total = sum(stat.size for stat in top_stats)
    print("Total allocated size: %.1f KiB" % (total / 1024))
    text_to_write += "Total allocated size: %.1f KiB" % (total / 1024)
    if not os.path.exists('Flora.prof'):
        with open('Flora.prof', mode='w', encoding='utf-8', errors='backslashreplace') as F:
            F.write(text_to_write)
        return
    with open('Flora.prof', mode='a', encoding='utf-8', errors='backslashreplace') as F:
        F.write(text_to_write)


novel = Novelty()


def test():
    loop = asyncio.get_event_loop()
    l = loop.run_until_complete(novel.search(term='A', max_results=10, fetch_chapters=True, as_dict=True,))
    print(l.keys(), len(l))
    loop.close()


tracemalloc.start()
test()
snapshot = tracemalloc.take_snapshot()
display_top(snapshot)
