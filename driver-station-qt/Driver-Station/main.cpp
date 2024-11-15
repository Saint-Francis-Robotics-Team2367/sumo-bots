#include "driverstation.h"

#include <QApplication>

int main(int argc, char *argv[])
{
    QApplication a(argc, argv);
    DriverStation w;
    w.show();
    return a.exec();
}
