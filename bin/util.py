
def error_and_exit(error_message: str, suggestion: str = None):
    print(f'ERROR: {error_message}')
    print(f'\tSUGGESTION:{suggestion}')
    exit(-1)
