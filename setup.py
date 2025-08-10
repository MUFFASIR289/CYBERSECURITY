from setuptools import find_packages, setup
from typing import List


requirement_lst:List[str]=[]
def get_requirements()->List[str]:
    '''
    This function will return list of requirements'''

    try:
        with open('requirements.txt','r') as file:
            #Read lines from the file
            lines = file.readlines()
            #proces lines
            for line in lines:
                requirement=line.strip()
                if requirement and requirement!='-e .':
                    requirement_lst.append(requirement)
    except FileNotFoundError:
        print("requirements.txt File not found")

    return requirement_lst


print(get_requirements())


setup(
    name='CYBERSECURITY',
    version='0.0.1',
    author='Muffasir',
    author_email='mohdmuffasir18@gmail.com',
    packages=find_packages(),
    install_requires=get_requirements()
)