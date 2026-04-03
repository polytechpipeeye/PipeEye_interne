#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/image.hpp>
#include <sensor_msgs/image_encodings.hpp>
#include <rcl_interfaces/msg/log.hpp>
#include <cv_bridge/cv_bridge.hpp>
#include <opencv2/opencv.hpp>
#include <string>
#include "std_msgs/msg/bool.hpp"

class HudNode : public rclcpp::Node {
public:
    HudNode() : Node("hud_camera_node") {
        rclcpp::QoS qos(1);
        zoom_sub = this->create_subscription<std_msgs::msg::Bool>("/camera/zoom",10, std::bind(&HudNode::zoom_callback, this, std::placeholders::_1));  
        
        log_sub=this->create_subscription<rcl_interfaces::msg::Log>("/rosout",10,std::bind(&HudNode::log_callback, this, std::placeholders::_1)); 
        
        sub_ = this->create_subscription<sensor_msgs::msg::Image>("/camera/image_raw", rclcpp::SensorDataQoS(), std::bind(&HudNode::image_callback, this, std::placeholders::_1));           
   
        pub_ = this->create_publisher<sensor_msgs::msg::Image>("/camera/image_hud", qos);  
        RCLCPP_INFO(this->get_logger(), "Caméra activé. En attente d'images...");                      
    }

private:
	
	
	void zoom_callback(const std_msgs::msg::Bool::SharedPtr msg){
		zoom_active=msg->data;
	}
	
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
            if (zoom_active){
		    int w=cv_ptr->image.cols;
		    int h=cv_ptr->image.rows;
		    float zoom_facteur=2.0;
		    int new_w=w/zoom_facteur;
		    int new_h=h/zoom_facteur;
		    int x=(w-new_w)/2;
		    int y=(h-new_h)/2;
		    cv::Rect roi(x,y,new_w,new_h);
		    cv_ptr->image=cv_ptr->image(roi);
		    cv::putText(cv_ptr->image, "PIPEEYE SYSTEM - EN LIGNE", cv::Point(5, 15),
                        cv::FONT_HERSHEY_SIMPLEX, 0.4, cv::Scalar(0, 0, 0), 2, cv::LINE_AA);
            cv::putText(cv_ptr->image, "PIPEEYE SYSTEM - EN LIGNE", cv::Point(5, 15),
                        cv::FONT_HERSHEY_SIMPLEX, 0.4, cv::Scalar(0, 255, 0), 1, cv::LINE_AA);
            cv::putText(cv_ptr->image, vit_log, cv::Point(5, 30),
                        cv::FONT_HERSHEY_SIMPLEX, 0.3, cv::Scalar(0, 0, 0), 2, cv::LINE_AA);
            cv::putText(cv_ptr->image, vit_log, cv::Point(5, 30),
                        cv::FONT_HERSHEY_SIMPLEX, 0.3, cv::Scalar(255, 100, 0), 1, cv::LINE_AA);
             cv::putText(cv_ptr->image, "ZOOM X2", cv::Point(cv_ptr->image.cols - 65, 15), cv::FONT_HERSHEY_SIMPLEX, 0.4, cv::Scalar(0, 0, 0), 2,cv::LINE_AA);
             cv::putText(cv_ptr->image, "ZOOM X2", cv::Point(cv_ptr->image.cols - 65, 15), cv::FONT_HERSHEY_SIMPLEX, 0.4, cv::Scalar(0, 0, 255), 1,cv::LINE_AA);
            int cx=cv_ptr->image.cols/2;
            int cy=cv_ptr->image.rows/2;
            cv::drawMarker(cv_ptr->image, cv::Point(cx, cy), cv::Scalar(0, 0, 255),
                           cv::MARKER_CROSS, 15, 1,cv::LINE_AA);
            pub_->publish(*cv_ptr->toImageMsg());		    
            }
            else{
            cv::putText(cv_ptr->image, "PIPEEYE SYSTEM - EN LIGNE", cv::Point(10, 30),
                        cv::FONT_HERSHEY_SIMPLEX, 0.7, cv::Scalar(0, 0, 0), 4, cv::LINE_AA);
            cv::putText(cv_ptr->image, "PIPEEYE SYSTEM - EN LIGNE", cv::Point(10, 30),
                        cv::FONT_HERSHEY_SIMPLEX, 0.7, cv::Scalar(0, 255, 0), 2, cv::LINE_AA);
            cv::putText(cv_ptr->image, vit_log, cv::Point(10, 60),
                        cv::FONT_HERSHEY_SIMPLEX, 0.6, cv::Scalar(0, 0, 0), 4, cv::LINE_AA);
            cv::putText(cv_ptr->image, vit_log, cv::Point(10, 60),
                        cv::FONT_HERSHEY_SIMPLEX, 0.6, cv::Scalar(255, 100, 0), 2, cv::LINE_AA);   
            int cx=cv_ptr->image.cols/2;
            int cy=cv_ptr->image.rows/2;
            cv::drawMarker(cv_ptr->image, cv::Point(cx, cy), cv::Scalar(0, 0, 255),
                           cv::MARKER_CROSS, 30, 2,cv::LINE_AA);
            pub_->publish(*cv_ptr->toImageMsg());
            }
        } catch (cv_bridge::Exception& e) {
            RCLCPP_ERROR(this->get_logger(), "Erreur cv_bridge: %s", e.what());
        }
    }
    bool zoom_active=false;
    rclcpp::Subscription<std_msgs::msg::Bool>::SharedPtr zoom_sub;
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
