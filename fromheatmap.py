def summarize_pass(args):
    "pumps a bunch of data back into the args construct"
    freqs = set()
    f_cache = set()
    times = set()
    labels = set()
    min_z = 0
    max_z = -100
    start, stop = None, None

    for line in raw_data():
        line = [s.strip() for s in line.strip().split(',')]
        #line = [line[0], line[1]] + [float(s) for s in line[2:] if s]
        line = [s for s in line if s]

        low  = int(line[2]) + args.offset_freq
        high = int(line[3]) + args.offset_freq
        step = float(line[4])
        t = line[0] + ' ' + line[1]
        if '-' not in line[0]:
            t = line[0]

        if args.low_freq  is not None and high < args.low_freq:
            continue
        if args.high_freq is not None and args.high_freq < low:
            continue
        if args.begin_time is not None and date_parse(t) < args.begin_time:
            continue
        if args.end_time is not None and date_parse(t) > args.end_time:
            break
        times.add(t)
        columns = list(frange(low, high, step))
        start_col, stop_col = slice_columns(columns, args.low_freq, args.high_freq)
        f_key = (columns[start_col], columns[stop_col], step)
        zs = line[6+start_col:6+stop_col+1]
        if not zs:
            continue
        if f_key not in f_cache:
            freq2 = list(frange(*f_key))[:len(zs)]
            freqs.update(freq2)
            #freqs.add(f_key[1])  # high
            #labels.add(f_key[0])  # low
            f_cache.add(f_key)

        if not args.db_limit:
            zs = floatify(zs)
            min_z = min(min_z, min(zs))
            max_z = max(max_z, max(zs))

        if start is None:
            start = date_parse(t)
        stop = date_parse(t)
        if args.head_time is not None and args.end_time is None:
            args.end_time = start + args.head_time

    if not args.db_limit:
        args.db_limit = (min_z, max_z)

    if args.tail_time is not None:
        times = [t for t in times if date_parse(t) >= (stop - args.tail_time)]
        start = date_parse(min(times))

    freqs = list(sorted(list(freqs)))
    times = list(sorted(list(times)))
    labels = list(sorted(list(labels)))

    if len(labels) == 1:
        delta = (max(freqs) - min(freqs)) / (len(freqs) / 500.0)
        delta = round(delta / 10**int(math.log10(delta))) * 10**int(math.log10(delta))
        delta = int(delta)
        lower = int(math.ceil(min(freqs) / delta) * delta)
        labels = list(range(lower, int(max(freqs)), delta))

    height = len(times)
    pix_height = height
    if args.compress:
        if args.compress > height:
            args.compress = 0
            print("Image too short, disabling time compression")
        if 0 < args.compress < 1:
            args.compress *= height
        if args.compress:
            args.compress = -1 / args.compress
            pix_height = time_compression(height, args.compress)

    print("x: %i, y: %i, z: (%f, %f)" % (len(freqs), pix_height, args.db_limit[0], args.db_limit[1]))
    args.freqs = freqs
    args.times = times
    args.labels = labels
    args.pix_height = pix_height
    args.start_stop = (start, stop)
    args.pixel_bandwidth = step