#include "driverstation.h"
#include "ui_driverstation.h"

DriverStation::DriverStation(QWidget *parent)
    : QMainWindow(parent)
    , ui(new Ui::DriverStation)
{
    ui->setupUi(this);
}

DriverStation::~DriverStation()
{
    delete ui;
}

void DriverStation::on_controller_player_1_currentIndexChanged(int index)
{
    player_1.controller_index = index;
}


void DriverStation::on_controller_player_2_currentIndexChanged(int index)
{
    player_2.controller_index = index;
}

void DriverStation::on_controller_player_3_currentIndexChanged(int index)
{
    player_4.controller_index = index;
}

void DriverStation::on_controler_player_4_currentIndexChanged(int index)
{
    player_3.controller_index = index;
}
