from machine import Pin, PWM, time_pulse_us, ADC
import time


# motor control

motors_left1 = PWM(Pin(5))	#IN4
motors_left2 = PWM(Pin(6))	#IN3
motors_right1 = PWM(Pin(7))	#IN4
motors_right2 = PWM(Pin(8))	#IN3

motors_left1.freq(2000)
motors_left2.freq(2000)
motors_right1.freq(2000)
motors_right2.freq(2000)

max_speed = int(0.85 * 65535)    # fresh batteries give 7v at driver outputs, used give 6v, do 85% of max voltage (65535 duty cycle aka 7v) to supply safe ~6v with fresh batteries

current_action = ""  # keep track of what the current motor movement is so you don't stop motor over and over if repeated same movement in super fast main while loop (ie fwd over and over every 0.005s)

def motor_stop():
    
    motors_left1.duty_u16(0)
    motors_left2.duty_u16(0)
    motors_right1.duty_u16(0)
    motors_right2.duty_u16(0)
    
def fwd():
    # only stop motor if the action is different (ie going from fwd to turn or turn to fwd), without motor_stop() overshooting happens and old signal interferes with new signal
    global current_action
    if current_action != "fwd":
        motor_stop()
        current_action = "fwd"
        
    motors_left1.duty_u16(max_speed)
    motors_left2.duty_u16(0)
    motors_right1.duty_u16(max_speed)
    motors_right2.duty_u16(0)


    
def bwd():
    global current_action
    if current_action != "bwd":
        motor_stop()
        current_action = "bwd"
    motors_left1.duty_u16(0)
    motors_left2.duty_u16(max_speed)
    motors_right1.duty_u16(0)
    motors_right2.duty_u16(max_speed)

# consider adding softer turns by just lowering one side PWM by 0.5 or more like in line_follower_AI code
# can use softer turns for regular turns from 101 and hard turns (other side reversed not slowed) from 111
# then the code will behave like the AI code basically but IMO only hard turns is better (and faster) but more jittery 
def slight_right():
    global current_action
    if current_action != "right":
        motor_stop()
        current_action = "right"
    motors_left1.duty_u16(max_speed)
    motors_left2.duty_u16(0)
    motors_right1.duty_u16(0)
    motors_right2.duty_u16(max_speed)
    
    
def slight_left():
    global current_action
    if current_action != "left": 
        motor_stop()
        current_action = "left"
    motors_left1.duty_u16(0)
    motors_left2.duty_u16(max_speed)
    motors_right1.duty_u16(max_speed)
    motors_right2.duty_u16(0)
    

# IR control

ir_left = Pin(15, Pin.IN)
ir_center = Pin(14, Pin.IN)
ir_right = Pin(13, Pin.IN)


# try while l_c_r == (1, 0, 1) move fwd otherwise etc as well

last_seen = ""

while True:
    
    #debounce IR readings to keep them stable
    first_read = (ir_left.value(), ir_center.value(), ir_right.value())
    time.sleep(0.005 )
    second_read = (ir_left.value(), ir_center.value(), ir_right.value())
    
    if first_read == second_read:
        
        l_c_r = first_read
            
        if l_c_r == (1, 0, 1):
            fwd()
            last_seen = "straight"
            
        elif l_c_r == (1, 1, 0) or l_c_r == (1, 0, 0):
            slight_right()
            last_seen = "left"

        elif l_c_r == (0, 1, 1) or l_c_r == (0, 0, 1):
            slight_left()
            last_seen = "right"

        
        elif l_c_r == (1, 1, 1) or l_c_r == (0, 0, 0):
            
            if last_seen == "left":			# if it goes from 110 or 100 to 111
                slight_right()

            elif last_seen == "right":		# if it goes from 011 or 001 to 111
                slight_left()
            elif last_seen == "straight":	# sometimes it will go from 101 (straight) to 111 even if a sensor is over black line (it glitches)
                fwd()                       # in those cases move forward so that eventually one of the left or right sensors goes low and turn left or right
            
    time.sleep(0.005)



# # servo control
# 
# right = 500
# center = 1375
# left = 2400
# 
# servo = PWM(Pin(10))
# 
# servo.freq(50)
# 
# while True:
#     servo.duty_u16(int((left / 20000) * 65535))
#     time.sleep(1)
#     servo.duty_u16(int((center / 20000) * 65535))
#     time.sleep(1)
#     servo.duty_u16(int((right / 20000) * 65535))
#     time.sleep(1)
#     servo.duty_u16(int((center / 20000) * 65535))
#     time.sleep(1)
# 
# 
# # ultrasonic control
# 
# trig = Pin(11, Pin.OUT)
# echo = Pin(12, Pin.IN)
# 
# while True:
#     #initialize to 0 state to prevent false readings
#     trig.value(0)
#     time.sleep_us(5)
# 
#     # for 10 microseconds the sensor fires 8 40khz ultrasonic sound bursts
#     # the moment it sends these bursts, the sensor raises echo pin to 1 (high) and only sets it to 0 (low) when the sound bounces back to it
#     trig.value(1)
#     time.sleep_us(10)
#     trig.value(0)
#     
# 
#     # for below we can try time.ticks_us() followed by a while loop with time.ticks_diff() but you lose accuracy measuring the time of sound wave to hit and bounce back
#     # because of background python interpreter processes, whereas time_pulse_us is optimized to be less slow (more accurate)
# 
#     # time_pulse_us function starts a microsecond timer when the specified pin (echo pin 12) goes high (because we specified 1 in second argument)
#     # and then stops the timer when that pin goes low (which our sensor will do when sound bounces back to it)
#     # with a 30,000 microsecond delay so it isn't stuck on timer waiting for pin to go low (30,000 us will let sound travel outside sensor range anyway)
#     duration = time_pulse_us(echo, 1, 30000)
#     
#     # 0.0343 cm per microsecond = speed of sound, multiply by duration of full bounce and divide by 2 to get distance for half bounce
#     distance = (0.0343 * duration)/2
#         
#     print(duration, distance)
#     
#     time.sleep(0.5)
# 
# 


