import virtualenv

virtualenv.logger = virtualenv.Logger(consumers=[])

def create_virtualenv(path):
    virtualenv.create_environment(path, False, True)
