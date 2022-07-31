from snakeeyes.signals import connect_signal


@connect_signal("sample")
def sample_signal(x):
    print("sample signal is being called", x)
