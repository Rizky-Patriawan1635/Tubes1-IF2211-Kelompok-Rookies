class Hello:
    def __init__(self) -> None:
        self.a = 19


class_name = "Hello"

dict = {"Hello": Hello}

obj = dict[class_name]()
print(obj.a)
