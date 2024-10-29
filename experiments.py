# examples = [None, '1', 0, [1], (1), {1}]
# for thing in examples:
#     if thing:
#         print(type(thing), ' is True.')
#     else:
#         print(f'{thing} is False.')


# print(__name__)
# print(__file__)


# my_dict = {'a': 1, 'b': 2, 'c': 3}

# # Accessing dictionary values dynamically
# print(getattr(my_dict, 'a'))  # Output: 1
# print(getattr(my_dict, 'b'))  # Output: 2



# dict1 = {'a': 1, 'b': 2}
# list_of_tuples = [('b', 3), ('c', 4)]

# dict1.update(list_of_tuples)

# print(dict1)  # Output: {'a': 1, 'b': 3, 'c': 4}

# # Define two dictionaries
# dict1 = {'a': 1, 'b': 2}
# dict2 = {'b': 3, 'c': 4}

# # Update dict1 with elements from dict2
# dict2.update(**dict1)

# print("Updated Dictionary:", dict2)



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
