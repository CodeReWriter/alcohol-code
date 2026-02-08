from enum import Enum


class Sheet(Enum):
    JOBS = "jobs"
    MATERIALS = "materials"


# print(Sheet.JOBS)  # Output: Sheet.JOBS
# print(Sheet.JOBS.name)  # Output: JOBS
# print(Sheet.JOBS.value)  # Output: jobs
#
# print(type(Sheet.JOBS))  # Output: <enum 'Sheet'>
# print(type(Sheet.JOBS.name))  # Output: <class 'str'>
# print(type(Sheet.JOBS.value))  # Output: <class 'str'>
