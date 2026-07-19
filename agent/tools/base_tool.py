class BaseTool:
    name = ""
    description = ""
    parameters = {"type": "object", "properties": {}, "required": []}

    def execute(self, *args, **kwargs):
        raise NotImplementedError

    def to_openai_schema(self):
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }
