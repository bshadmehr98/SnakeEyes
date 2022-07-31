from snakeeyes.signals import connect_signal


@connect_signal("recalculate-user-events")
def recalculate_user_events(events):
    # TODO: Recalculate the events and remove the deprecated ones
    print("Not implemented! - Recalculate the events and remove the deprecated ones")
