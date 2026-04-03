#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/image.hpp>
#include <sensor_msgs/image_encodings.hpp>
#include <rcl_interfaces/msg/log.hpp>
#include <cv_bridge/cv_bridge.hpp>
#include <opencv2/opencv.hpp>
#include <string>

class HudNode : public rclcpp::Node {
public:
    HudNode() : Node("hud_camera_node") {
        rclcpp::QoS qos(1);
        log_sub=this->create_subscription<rcl_interfaces::msg::Log>("/rosout",10,std::bind(&HudNode::log_callback, this, std::placeholders::_1)); 
        
        sub_ = this->create_subscription<sensor_msgs::msg::Image>("/camera/image_raw", rclcpp::SensorDataQoS(), std::bind(&HudNode::image_callback, this, std::placeholders::_1));           
   
        pub_ = this->create_publisher<sensor_msgs::msg::Image>("/camera/image_hud", qos);  
        RCLCPP_INFO(this->get_logger(), "Caméra activé. En attente d'images...");                      
    }

private:
	std::string vit_log;
	void log_callback(const rcl_interfaces::msg::Log::SharedPtr msg){
		std::string text=msg->msg;
		if (text.find("STICK") != std::string::npos){
		vit_log=text;
		}
	}
	
    void image_callback(const sensor_msgs::msg::Image::SharedPtr msg) {
        try {
            cv_bridge::CvImagePtr cv_ptr=cv_bridge::toCvCopy(msg, sensor_msgs::image_encodings::BGR8);
           cv::putText(cv_ptr->image, "PIPEEYE SYSTEM - EN LIGNE", cv::Point(10, 30),
                        cv::FONT_HERSHEY_SIMPLEX, 0.7, cv::Scalar(0, 0, 0), 4);
            cv::putText(cv_ptr->image, "PIPEEYE SYSTEM - EN LIGNE", cv::Point(10, 30),
                        cv::FONT_HERSHEY_SIMPLEX, 0.7, cv::Scalar(0, 255, 0), 2);
            cv::putText(cv_ptr->image, vit_log, cv::Point(10, 60),
                        cv::FONT_HERSHEY_SIMPLEX, 0.6, cv::Scalar(0, 0, 0), 4);
            cv::putText(cv_ptr->image, vit_log, cv::Point(10, 60),
                        cv::FONT_HERSHEY_SIMPLEX, 0.6, cv::Scalar(255, 100, 0), 2);   
            int cx=cv_ptr->image.cols/2;
            int cy=cv_ptr->image.rows/2;
            cv::drawMarker(cv_ptr->image, cv::Point(cx, cy), cv::Scalar(0, 0, 255),
                           cv::MARKER_CROSS, 30, 2);
            pub_->publish(*cv_ptr->toImageMsg());
        } catch (cv_bridge::Exception& e) {
            RCLCPP_ERROR(this->get_logger(), "Erreur cv_bridge: %s", e.what());
        }
    }
    rclcpp::Subscription<rcl_interfaces::msg::Log>::SharedPtr log_sub;
    rclcpp::Subscription<sensor_msgs::msg::Image>::SharedPtr sub_;
    rclcpp::Publisher<sensor_msgs::msg::Image>::SharedPtr pub_;
    
};

int main(int argc, char** argv) {
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<HudNode>());
    rclcpp::shutdown();
    return 0;
}
