#!/usr/bin/env python3
import rospy
import numpy as np
from geometry_msgs.msg import Twist

def swim():
    rospy.init_node('swim_node')
    pub = rospy.Publisher('/turtle1/cmd_vel', Twist, queue_size=10)

    # Wait for publisher to connect
    rospy.sleep(1)

    # Random velocities
    linear_vel  = abs(np.random.normal(1.0, 0.2))
    angular_vel = abs(np.random.normal(1.5, 0.2))

    # Time to complete a full circle = 2*pi / angular_vel
    # So one full loop of the 8 = 2 full circles
    full_circle_time = 2 * np.pi / angular_vel

    rate = rospy.Rate(50)  # Higher rate = smoother motion

    rospy.loginfo(f"Linear vel: {linear_vel:.2f}, Angular vel: {angular_vel:.2f}")
    rospy.loginfo(f"Full circle time: {full_circle_time:.2f}s")

    while not rospy.is_shutdown():
        # First circle: turn LEFT (positive angular)
        start = rospy.Time.now()
        while (rospy.Time.now() - start).to_sec() < full_circle_time:
            msg = Twist()
            msg.linear.x = linear_vel
            msg.angular.z = angular_vel      # LEFT
            pub.publish(msg)
            rate.sleep()

        # Second circle: turn RIGHT (negative angular)
        start = rospy.Time.now()
        while (rospy.Time.now() - start).to_sec() < full_circle_time:
            msg = Twist()
            msg.linear.x = linear_vel
            msg.angular.z = -angular_vel     # RIGHT
            pub.publish(msg)
            rate.sleep()

if __name__ == '__main__':
    try:
        swim()
    except rospy.ROSInterruptException:
        pass