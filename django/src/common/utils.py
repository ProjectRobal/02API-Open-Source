
def version_to_number(ver:str)->list[int]:
    '''
    A function that converts version string in format:
    a.b.c into list of numbers
    '''

    numbers:list[int]=[int(x) for x in ver.split('.')]

    return numbers

def version_difference(ver1:list[int],ver2:list[int])->list[int]:

    output:list[int]=[]

    for v1,v2 in zip(ver1,ver2):
        output.append(v1-v2)

    return output


def compare_versions(ver1:list[int],ver2:list[int])->int:

    '''
        Return 0 when both versions are the same,
        Return 1 when first verion is ahead of second version
        Return -1 when first version is behind of second version
    '''

    diff=version_difference(ver1,ver2)

    output=0

    for d in diff:
        if d>0:
            output=1
        elif d<0:
            output=-1

    return output
