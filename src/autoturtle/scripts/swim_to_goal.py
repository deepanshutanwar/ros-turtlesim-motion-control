#!/usr/bin/env python3
import rospy
import math
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose

# Global variable to store current turtle pose
current_pose = Pose()

def pose_callback(pose_msg):
    global current_pose
    current_pose = pose_msg

def get_goal_from_user():
    while True:
        try:
            x = float(input("Enter x_goal (0-11): "))
            y = float(input("Enter y_goal (0-11): "))
            if 0 <= x <= 11 and 0 <= y <= 11:
                return x, y
            else:
                print("Please enter values between 0 and 11")
        except ValueError:
            print("Invalid input. Please enter numbers only.")

def swim_to_goal():
    rospy.init_node('swim_to_goal')

    # Publisher and Subscriber
    pub = rospy.Publisher('/turtle1/cmd_vel', Twist, queue_size=10)
    rospy.Subscriber('/turtle1/pose', Pose, pose_callback)

    # Wait for pose data to be available
    rospy.sleep(1)

    # Proportional controller gains - tuned for best performance
    K_x = 1.5   # Linear velocity gain
    K_z = 6.0   # Angular velocity gain

    rate = rospy.Rate(50)

    rospy.loginfo("swim_to_goal node started!")

    while not rospy.is_shutdown():
        # Step 2: Get goal from user
        print("\n--- Enter new goal position ---")
        x_goal, y_goal = get_goal_from_user()
        rospy.loginfo(f"Moving to goal: ({x_goal}, {y_goal})")

        # Step 3-5: Control loop
        while not rospy.is_shutdown():
            # Calculate errors
            delta_x = x_goal - current_pose.x
            delta_y = y_goal - current_pose.y

            # Euclidean distance error
            error_position = math.sqrt(delta_x**2 + delta_y**2)

            # Angle to goal
            goal_angle = math.atan2(delta_y, delta_x)

            # Angular error (shortest path)
            error_angle = math.atan2(
                math.sin(goal_angle - current_pose.theta),
                math.cos(goal_angle - current_pose.theta)
            )

            # Step 5: Check if goal reached
            if error_position < 0.5:
                # Stop the turtle
                stop_msg = Twist()
                pub.publish(stop_msg)
                rospy.loginfo(f"Goal reached! Final position: ({current_pose.x:.2f}, {current_pose.y:.2f})")
                print(f" Arrived at goal ({x_goal}, {y_goal})!")
                break

            # Step 4: Proportional velocities
            msg = Twist()

            # Only move forward when roughly facing the goal
            # This prevents the turtle going backwards
            if abs(error_angle) > 0.1:
                msg.linear.x  = K_x * error_position * max(0, math.cos(error_angle))
                msg.angular.z = K_z * error_angle
            else:
                msg.linear.x  = K_x * error_position
                msg.angular.z = K_z * error_angle

            pub.publish(msg)
            rate.sleep()

        # Step 6: Loop back and ask for new goal (handled by outer while loop)

if __name__ == '__main__':
    try:
        swim_to_goal()
    except rospy.ROSInterruptException:
        pass