EXPLAIN_VALIDATION_ERRORS = False


class ExplainValidationErrors:

    def __enter__(self):
        global EXPLAIN_VALIDATION_ERRORS
        EXPLAIN_VALIDATION_ERRORS = True
        return self

    def __exit__(self, *args, **kwargs):
        global EXPLAIN_VALIDATION_ERRORS
        EXPLAIN_VALIDATION_ERRORS = False
        return