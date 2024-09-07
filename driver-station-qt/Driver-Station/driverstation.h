#ifndef DRIVERSTATION_H
#define DRIVERSTATION_H

#include <QMainWindow>
#include <qstring.h>
#include <joystickhandler.h>

QT_BEGIN_NAMESPACE
namespace Ui {
class DriverStation;
}
QT_END_NAMESPACE

class player
{
public:
    int controller_index{0};
    QString robot_name;
    JoyStickHandler controller;
};

class DriverStation : public QMainWindow
{
    Q_OBJECT


public:
    DriverStation(QWidget *parent = nullptr);
    ~DriverStation();

private slots:
    void on_controller_player_1_currentIndexChanged(int index);

    void on_controller_player_2_currentIndexChanged(int index);

    void on_controler_player_4_currentIndexChanged(int index);

    void on_controller_player_3_currentIndexChanged(int index);

private:
    Ui::DriverStation *ui;
    player player_1, player_2, player_3, player_4;
};
#endif // DRIVERSTATION_H
