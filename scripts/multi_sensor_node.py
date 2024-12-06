#!/usr/bin/env python3

import rospy
from std_msgs.msg import String, Float64MultiArray, Bool
import TLV
import smbus
from time import sleep
import json

def read_sensors():
    # Initialize ROS node
    rospy.init_node('multi_sensor_node', anonymous=True)
    pub = rospy.Publisher('sensor_data', String, queue_size=10)
    array_pub = rospy.Publisher('sensor_array', Float64MultiArray, queue_size=10)
    status_pub = rospy.Publisher('sensor_status', Bool, queue_size=10)
    rate = rospy.Rate(2)  # Publish at 2 Hz

    # Initialize TLV493D objects for each I2C bus
    sensors = [
        {"sensor": TLV.TLV493D(), "bus": smbus.SMBus(1)},
        {"sensor": TLV.TLV493D(), "bus": smbus.SMBus(2)},
        {"sensor": TLV.TLV493D(), "bus": smbus.SMBus(3)},
        {"sensor": TLV.TLV493D(), "bus": smbus.SMBus(4)},
    ]

    # Assign the appropriate bus to each sensor
    for s in sensors:
        s["sensor"].bus = s["bus"]

    while not rospy.is_shutdown():
        # Collect data from all sensors
        sensor_data = {}
        sensor_array = Float64MultiArray()
        all_sensor_ok = True
        
        for i, s in enumerate(sensors, start=1):
            try:
                s["sensor"].update_data()
                x = round(s["sensor"].get_x(), 3)
                y = round(s["sensor"].get_y(), 3)
                z = round(s["sensor"].get_z(), 3)
                sensor_data[f"sensor_{i}"] = {"x": x, "y": y, "z": z}
            
                sensor_array.data.extend([x, y, z])
            except Exception as e :
                ros.logwarn(f"Error reading sensor {i} : {e}")
                all_sensor_ok = False

        # Convert data to string and publish
        data_str = json.dumps(sensor_data)
        rospy.loginfo("\n" + data_str)
        pub.publish(data_str)
        
        # Publish the flattend array
        array_pub.publish(sensor_array)
        
        # Publish status flug
        status_pub.publish(Bool(data=all_sensor_ok))
        

        rate.sleep()

if __name__ == '__main__':
    try:
        read_sensors()
    except rospy.ROSInterruptException:
        pass
