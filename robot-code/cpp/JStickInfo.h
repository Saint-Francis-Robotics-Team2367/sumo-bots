#pragma once

#include <cstdint>
typedef struct 
{
  int8_t x;
  int8_t y;
} Stick;

typedef struct
{
  Stick left;
  Stick right;
  int8_t left_trigger;
  int8_t right_trigger;
  uint16_t buttons;
} JStickStatus;

class Joystick
{
  private:
    JStickStatus jStick;
  public:
    auto getLeftStick() const -> const Stick& {return jStick.left;}
    auto getRightStick() const -> const Stick& {return jStick.right;}
    auto getLeftTrigger() const -> const int8_t {return jStick.left_trigger;}
    auto getRightTrigger() const -> const int8_t {return jStick.right_trigger;}
    auto getButtonRaw(int button_index) const -> const bool {return (jStick.buttons & (1 << button_index));}
};