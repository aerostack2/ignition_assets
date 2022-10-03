#include <iostream>
#include <memory>
#include <string>

#include <as2_core/names/topics.hpp>
#include "sensor_msgs/msg/nav_sat_fix.hpp"

#include <ignition/msgs.hh>
#include <ignition/transport.hh>
#include <ros_ign_bridge/convert.hpp>

class GPSBridge : public rclcpp::Node {
public:
  GPSBridge() : Node("gps_bridge") {
    RCLCPP_INFO(this->get_logger(), "-1");

    this->declare_parameter<std::string>("world_name");
    this->get_parameter("world_name", world_name);

    this->declare_parameter<std::string>("name_space");
    this->get_parameter("name_space", name_space);

    this->declare_parameter<std::string>("sensor_name");
    this->get_parameter("sensor_name", sensor_name);

    this->declare_parameter<std::string>("link_name");
    this->get_parameter("link_name", link_name);

    this->declare_parameter<std::string>("sensor_type");
    this->get_parameter("sensor_type", sensor_type);

    RCLCPP_INFO(this->get_logger(), "0");

    // Initialize the ignition node
    ign_node_ptr_         = std::make_shared<ignition::transport::Node>();
    std::string gps_topic = "/world/" + world_name + "/model/" + name_space + "/model/" +
                            sensor_name + "/link/" + link_name + "/sensor/" + sensor_type +
                            "/navsat";
    RCLCPP_INFO(this->get_logger(), "1");
    ign_node_ptr_->Subscribe(gps_topic, this->ignitionGPSCallback);
  }

private:
  std::shared_ptr<ignition::transport::Node> ign_node_ptr_;
  std::string world_name, name_space, sensor_name, link_name, sensor_type;

private:
  static std::string replace_delimiter(const std::string &input,
                                       const std::string &old_delim,
                                       const std::string new_delim) {
    std::string output;
    output.reserve(input.size());

    std::size_t last_pos = 0;

    while (last_pos < input.size()) {
      std::size_t pos = input.find(old_delim, last_pos);
      output += input.substr(last_pos, pos - last_pos);
      if (pos != std::string::npos) {
        output += new_delim;
        pos += old_delim.size();
      }
      last_pos = pos;
    }
    return output;
  }

  static void ignitionGPSCallback(const ignition::msgs::NavSat &ign_msg,
                                  const ignition::transport::MessageInfo &msg_info) {
    sensor_msgs::msg::NavSatFix ros_msg;
    // ros_ign_bridge::convert_ign_to_ros(msg, ros_gps_msg);

    ros_ign_bridge::convert_ign_to_ros(ign_msg.header(), ros_msg.header);
    ros_msg.header.frame_id = GPSBridge::replace_delimiter(ign_msg.frame_id(), "::", "/");
    ros_msg.latitude        = ign_msg.latitude_deg();
    ros_msg.longitude       = ign_msg.longitude_deg();
    ros_msg.altitude        = ign_msg.altitude();

    // position_covariance is not supported in Ignition::Msgs::NavSat.
    ros_msg.position_covariance_type = sensor_msgs::msg::NavSatFix::COVARIANCE_TYPE_UNKNOWN;
    ros_msg.status.status            = sensor_msgs::msg::NavSatStatus::STATUS_FIX;

    // RCLCPP_INFO(this->get_logger(), "test");
    std::cout << "Hola" << std::endl;
  };
};

int main(int argc, char *argv[]) {
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<GPSBridge>());
  rclcpp::shutdown();
  return 0;
}