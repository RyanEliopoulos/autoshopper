import datetime


class Logger:
    """
    Appends logging files in the working directory
    """

    @staticmethod
    def log_error(message: str):
        dt = datetime.datetime.now()
        with open('./error_log.txt', 'a') as error_file:
            error_file.write(str(dt) + '\n')
            error_file.write(message + '\n')
            error_file.write('\n')
            error_file.write('\n')

    @staticmethod
    def log(message: str):
        dt = datetime.datetime.now()
        with open('./log.txt', 'a') as log_file:
            log_file.write(str(dt) + '\n')
            log_file.write(message + '\n')
            log_file.write('\n')
            log_file.write('\n')
