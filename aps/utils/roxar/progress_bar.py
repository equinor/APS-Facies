import roxar

class APSProgressBar:
    """
    Keep track of progress step when using progress bar
    """
    use_progress_bar = False
    number_of_steps = 100
    progress_step = None

    @classmethod
    def increment(cls):
        if cls.use_progress_bar:
            cls.progress_step += 1
            roxar.rms.set_progress_value(cls.progress_step, '')

    @classmethod
    def initialize_progress_bar(cls, number_of_steps=100, use_progress_bar=True):
        cls.progress_step = None
        try:
            cls.use_progress_bar = use_progress_bar
            if cls.use_progress_bar:
                cls.progress_step = 0
                cls.number_of_steps = number_of_steps
                roxar.rms.create_progress_bar(cls.number_of_steps, "Running APS job")
        except:
            cls.use_progress_bar = False



    @classmethod
    def close_progress_bar(cls):
        if cls.use_progress_bar:
            cls.use_progress_bar = False
            cls.progress_step = None
            roxar.rms.close_progress()
