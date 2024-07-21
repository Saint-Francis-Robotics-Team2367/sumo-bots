#pragma once
#include<string>

typedef struct 
{
    char name[16];
    int8_t  lx,
            ly,
            rx,
            ry,
            lt,
            rt;
    uint16_t bttns;
}JoystickBuffer;
static_assert(sizeof(JoystickBuffer) == 24);

typedef struct
{
    uint8_t command_word;
    char robot_1[16];
    char robot_2[16];
    char robot_3[16];
    char robot_4[16];
}ManagerBuffer;
static_assert(sizeof(ManagerBuffer) == 65);

enum GameState
{
    test,
    standby,
    autonomous,
    teleop
};

class CommsManager
{
    private:
        const uint16_t p_port{2367};
        std::string p_ssid;
        std::string p_pwd;
        std::string p_robot_name;
        

    public:
        CommsManager(std::string ssid,
                     std::string password,
                     std::string robot_name):
                    p_ssid{ssid},
                    p_pwd{password},
                    p_robot_name{robot_name}{};
        GameState getGameState() const{return };
};