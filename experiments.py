# from enum import Enum

# class Color(Enum):
#     RED = 1
#     GREEN = 2
#     BLUE = 3



# class Parent:
#     def __init__(self, *args, **kwargs):
#         print("Parent class initialized with parameters:", args, kwargs)
#         for k,v in kwargs.items():
#             setattr(self, k, v)

# class Child(Parent):
#     def __init__(self, child_param, *args, **kwargs):
#         super().__init__(*args, **kwargs)  # Pass all arguments to Parent's __init__
#         self.child_param = child_param
#         print("Child class initialized with parameter:", child_param)

# # Creating an instance of the Child class with parameters for both Child and Parent
# child_instance = Child("Hello", "ParentParam1", "ParentParam2", name='bobby')


# # sample_dict.py

# class SampleClass:
#     class_attr = 100

#     def __init__(self, instance_attr):
#         self.instance_attr = instance_attr

#     def method(self):
#         print(f"Class attribute: {self.class_attr}")
#         print(f"Instance attribute: {self.instance_attr}")

# print(SampleClass(200).__dict__)