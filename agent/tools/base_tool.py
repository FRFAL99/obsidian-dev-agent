class BaseTool:
    name = ""
    description = ""

    def execute(self, *args, **kwargs):
        raise NotImplementedError
