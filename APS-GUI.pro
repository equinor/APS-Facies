#-------------------------------------------------
#
# Project created by QtCreator 2017-06-30T11:13:57
#
#-------------------------------------------------

QT       += core gui

greaterThan(QT_MAJOR_VERSION, 4): QT += widgets printsupport

TARGET = APS-GUI
TEMPLATE = app

# The following define makes your compiler emit warnings if you use
# any feature of Qt which as been marked as deprecated (the exact warnings
# depend on your compiler). Please consult the documentation of the
# deprecated API in order to know how to port your code away from it.
DEFINES += QT_DEPRECATED_WARNINGS

# You can also make your code fail to compile if you use deprecated APIs.
# In order to do so, uncomment the following line.
# You can also select to disable deprecated APIs only up to a certain version of Qt.
#DEFINES += QT_DISABLE_DEPRECATED_BEFORE=0x060000    # disables all the APIs deprecated before Qt 6.0.0


SOURCES += \
        main.cpp \
        mainview.cpp \
        libraries/QCustomPlot/qcustomplot.cpp

HEADERS += \
        mainview.h \
        libraries/QCustomPlot/qcustomplot.h

FORMS += \
        mainview.ui \
        ui/APS_prototype.ui \
        ui/Gaussian.ui \
        ui/TruncRuleCubic.ui \
        ui/Assign_Probs.ui \
        ui/Project.ui \
        ui/Selection.ui \
        ui/TruncRuleTypeBayfill.ui \
        ui/Gaussian_menu.ui \
        ui/TruncationLibrary.ui \
        ui/TruncRuleTypeNonCubic.ui \

