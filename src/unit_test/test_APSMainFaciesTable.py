#!/bin/env python
from src.algorithms.APSMainFaciesTable import APSMainFaciesTable


def test_mainFaciesTable():
    mainFaciesTable1 = APSMainFaciesTable()
    # Test example of facies table
    mainFaciesTable1.addFacies('F1', 1)
    mainFaciesTable1.addFacies('F2', 2)
    mainFaciesTable1.addFacies('F8', 8)
    mainFaciesTable1.addFacies('F3', 3)
    mainFaciesTable1.addFacies('F7', 7)
    mainFaciesTable1.addFacies('F4', 4)
    mainFaciesTable1.addFacies('F5', 5)
    mainFaciesTable1.addFacies('F6', 6)

    mainFaciesTable1.removeFacies('F7')
    mainFaciesTable1.removeFacies('F8')

    fTable = {1: 'F1', 2: 'F2', 3: 'F3', 4: 'F4', 5: 'F5', 6: 'F6'}
    mainFaciesTable2 = APSMainFaciesTable(fTable=fTable)

    nFacies1 = len(mainFaciesTable1)
    nFacies2 = len(mainFaciesTable2)
    assert nFacies1 == nFacies2

    for i in range(nFacies1):
        fName1 = mainFaciesTable1.getFaciesName(i)
        fName2 = mainFaciesTable2.getFaciesName(i)
        assert fName1 == fName2

        fCode1 = mainFaciesTable1.getFaciesCode(i)
        fCode2 = mainFaciesTable2.getFaciesCode(i)
        assert fCode1 == fCode2

        fCode = mainFaciesTable2.getFaciesCodeForFaciesName(fName1)
        assert fCode == fCode1

        clName = mainFaciesTable1.getClassName()
        assert clName == 'APSMainFaciesTable'

        indx1 = mainFaciesTable1.getFaciesIndx(fName1)
        indx2 = mainFaciesTable2.getFaciesIndx(fName2)
        assert indx1 == indx2

    fTable1 = mainFaciesTable1.getFaciesTable()
    fTable2 = mainFaciesTable2.getFaciesTable()
    for i in range(nFacies1):
        item1 = fTable1
        item2 = fTable2
        assert item1[0] == item2[0]
        assert item1[1] == item2[1]

    faciesList = ['F3', 'F1', 'F4', 'S3', 'F2', 'F5', 'F6']
    for i in range(len(faciesList)):
        fName = faciesList[i]
        if i != 3:
            check = mainFaciesTable1.has_facies_int_facies_table(fName)
            assert check is True
        else:
            check = mainFaciesTable1.has_facies_int_facies_table(fName)
            assert check is False


# --------- Main ---------------

def run():
    test_mainFaciesTable()


if __name__ == '__main__':
    run()
