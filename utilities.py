
def split_activity_file(activityType):
    with open('raw_data/higgs-activity_time.txt') as data:
        with open('processed_data/higgs-activity_time_{}.txt'.format(activityType), 'w') as f:
            for item in data:
                start_id, end_id, timestamp, activity = item.split()
                if activity == activityType:
                    f.write('%s %s %s %s\n' % (start_id, end_id, timestamp, activity))