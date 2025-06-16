class AlwaysErrorNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "message": ("STRING", {"default": "Forced error from AlwaysErrorNode!"}),
                "any": ("*", ),
            }
        }

    RETURN_TYPES = ( "*", "IMAGE" )
    FUNCTION = "run"
    CATEGORY = "errors"

    def run(self, message, any=None):
        raise Exception(message)
        return (any, any)
    
        
    @classmethod
    def VALIDATE_INPUTS(s, input_types):
        return True
