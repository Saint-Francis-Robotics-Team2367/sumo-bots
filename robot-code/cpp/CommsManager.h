#pragma once
#include <string>
#include <cstring>
#include <array>

#include <WiFi.h>
#include <AsyncUDP.h>

#define ROBOT_NAME_LENGTH 16
typedef struct 
{
    char name[ROBOT_NAME_LENGTH];
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
    char robot_1[ROBOT_NAME_LENGTH];
    char robot_2[ROBOT_NAME_LENGTH];
    char robot_3[ROBOT_NAME_LENGTH];
    char robot_4[ROBOT_NAME_LENGTH];
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
        static std::string g_robot_name;
        GameState p_game_state;
        AsyncUDP p_udp;
        static JoystickBuffer g_js_buffer;
        static ManagerBuffer g_manger_buffer;
        static uint8_t g_command_hint;
        static void UdpCallback(AsyncUDPPacket packet);
    public:
        CommsManager(std::string ssid,
                     std::string password,
                     std::string robot_name):
                    p_ssid{ssid},
                    p_pwd{password}
                    {
                        if(robot_name.length());
                        g_robot_name = robot_name;
                    };
        GameState getGameState() const{return p_game_state;};
        void Initialize();
};

//static allocations
JoystickBuffer CommsManager::g_js_buffer{0};
ManagerBuffer CommsManager::g_manger_buffer{0};
std::string CommsManager::g_robot_name;
uint8_t CommsManager::g_command_hint{0};

void CommsManager::UdpCallback(AsyncUDPPacket packet)
{
    if(packet.length() == sizeof(JoystickBuffer))
    {
        if(memcmp(packet.data(), g_robot_name.c_str(),g_robot_name.length()))
        {
            memcpy(&g_js_buffer, packet.data(), sizeof(g_js_buffer));
        }
    }

    if(packet.length() == sizeof(ManagerBuffer))
    {
        bool in_match = false;
        auto data_peek = reinterpret_cast<ManagerBuffer *>(packet.data());
 
        switch (g_command_hint)
        {
        case 0:
            {
                std::array data = {data_peek->robot_1, // There might be a faster way to make these references, if performace limits are hit take a look here
                        data_peek->robot_2,
                        data_peek->robot_3,
                        data_peek->robot_4}; 

                for(int i = 0; i < data.size(); i++)
                {
                    if(memcmp(data[i],g_robot_name.c_str(), g_robot_name.length()))
                    {
                        g_command_hint = i+1; // The case statement is 1 indexed since the zero case is for no hint
                        in_match = true;
                    }
                }
            }        
            break;
        case 1:
            if(memcmp(data_peek->robot_1,g_robot_name.c_str(), g_robot_name.length())) in_match = true;
            break;
        case 2:
            if(memcmp(data_peek->robot_2,g_robot_name.c_str(), g_robot_name.length())) in_match = true;
            break;
        case 3:
            if(memcmp(data_peek->robot_3,g_robot_name.c_str(), g_robot_name.length())) in_match = true;
            break;
        case 4:
            if(memcmp(data_peek->robot_4,g_robot_name.c_str(), g_robot_name.length())) in_match = true;
            break;
        }

        if(in_match)
        {
            g_manger_buffer.command_word = packet.data()[0];
        }
    }
}

void CommsManager::Initialize()
{
    WiFi.mode(WIFI_STA);
    WiFi.begin(p_ssid.c_str(), p_pwd.c_str());
    if (WiFi.waitForConnectResult() != WL_CONNECTED)
    {
        for(;;);//halt and catch fire for now, maybe handle it latter. At least blink aggressivly. 
    }

    //get the local ip then convert to the broadcast address
    auto broadcast_ip = WiFi.localIP();
    broadcast_ip[3] = 255;

    if (p_udp.connect(broadcast_ip, p_port))
    {
        p_udp.onPacket(UdpCallback);
    } 
}