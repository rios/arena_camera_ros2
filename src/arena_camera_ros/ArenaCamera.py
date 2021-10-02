# Copyright RIOS AI, Inc. Licensed under the Apache License, Version 2.0.

import numpy as np
import cv2
import rospy
from actionlib import SimpleActionServer
from camera_control_msgs.msg import GrabImagesAction, GrabImagesResult, GrabImagesFeedback
from cv_bridge import CvBridge
from sensor_msgs.msg import CameraInfo, Image
from camera_control_msgs.srv import GetCamProperties, GetCamPropertiesResponse
from camera_control_msgs.srv import SetExposure, SetExposureResponse
from camera_control_msgs.srv import SetGain, SetGainResponse
from camera_control_msgs.srv import SetGamma, SetGammaResponse
from arena_api.system import system
from . import ArenaUtils as utils


class ArenaCamera(object):
    """ Represents a Arena (LUCID) camera.

    This class uses ``cam_serial`` to identify the camera to be managed.

    If ``stream`` is set to ``True``, Action Server will be disabled.

    Keyword Arguments:
        * ``cam_name``: camera name
        * ``node_name``: used as a prefix to ``cam_name``
        * ``config``: camera configuration file in JSON format
        * ``resize``: flag to activate image resizing (default: ``False``)
        * ``resize_res``: resize resolution as a tuple(default:``(640, 480)``)
        * ``stream``: flag to control streaming (default: ``True``)

    :param cam_serial: camera serial
    """
    def __init__(self, cam_serial, **kwargs):
        self._cam = None
        self._cam_info = []
        self._cam_serial = cam_serial
        self._cam_name = kwargs.get("cam_name", "camera")
        self._topic_prefix = kwargs.get("node_name", "/arena_camera_node") + "/" + self._cam_name
        self._cam_config = kwargs.get("config", None)
        self._resize = kwargs.get("resize", False)
        self._resize_res = kwargs.get("resize_res", (640, 480))
        self._stream = kwargs.get("stream", True)
        self._encoding = {
            "camera": "RGB8",
            "ros": "rgb8"
        }

        # Find the camera from the serial number
        self._cam_found = False
        device_infos = system.device_infos
        for i, cam in enumerate(device_infos):
            if cam["serial"] == self._cam_serial:
                self._cam_info = [cam]
                device = system.create_device(self._cam_info)
                self._cam = device[0]
                self._cam_found = True
                break

        if not self._cam_found:
            rospy.logerr("Cannot find the camera with serial {}".format(self._cam_serial))

        # Camera data
        self._buff_size = 1
        self._buff_timeout = 200  # milliseconds

        # Init camera info
        self._camera_info = CameraInfo()

        # Init cache
        self._cache = dict()

    def __del__(self):
        # Deinitialize camera
        if self._cam_info:
            system.destroy_device(self._cam)

    @property
    def cam_active(self):
        return self._cam_found

    @property
    def binning_x(self):
        return self._cam.nodemap["BinningHorizontal"].value

    @binning_x.setter
    def binning_x(self, value):
        if not isinstance(value, int):
            rospy.logerr("Cannot set binning_x, the value must be an integer")
        else:
            self._cam.nodemap["BinningHorizontal"].value =  value

    @property
    def binning_y(self):
        return self._cam_nodemap["BinningVertical"].value

    @binning_x.setter
    def binning_y(self, value):
        if not isinstance(value, int):
            rospy.logerr("Cannot set binning_y, the value must be an integer")
        else:
            self._cam.nodemap["BinningVertical"].value =  value

    @property
    def framerate(self):
        return self._cam.nodemap["AcquisitionFrameRate"].value

    @property
    def exposure(self):
        """ Exposure time

        :getter: Gets exposure time
        :setter: Sets exposure time
        """
        return self._cam.nodemap["ExposureTime"].value

    @exposure.setter
    def exposure(self, value):
        if self.exposure_auto:
            self.exposure_auto = False
        self._cam.nodemap["ExposureTime"].value = value

    @property
    def gamma(self):
        """ Gamma correction value

        :getter: Gets gamma correction
        :setter: Sets gamma correction
        """
        return self._cam.nodemap["Gamma"].value

    @gamma.setter
    def gamma(self, value):
        if not self.gamma_enable:
            self.gamma_enable = True
        self._cam.nodemap["Gamma"].value = value

    @property
    def gain(self):
        """ Gain value

        :getter: Gets gain
        :setter: Sets gain
        """
        return self._cam.nodemap["Gain"].value / 48

    @gain.setter
    def gain(self, value):
        if self.gain_auto:
            self.gain_auto = False
        self._cam.nodemap["Gain"].value = value

    @property
    def exposure_auto(self):
        """ Exposure auto status

        :getter: Gets exposure auto
        :setter: Sets exposute auto
        """
        return True if self._cam.nodemap["ExposureAuto"].value == "Continuous" else False

    @exposure_auto.setter
    def exposure_auto(self, value):
        self._cam.nodemap["ExposureAuto"].value = "Continuous" if value else "Off"

    @property
    def gain_auto(self):
        """ Gain auto status

        :getter: Gets gain auto
        :setter: Sets gain auto
        """
        return True if self._cam.nodemap["GainAuto"].value == "Continuous" else False

    @gain_auto.setter
    def gain_auto(self, value):
        self._cam.nodemap["GainAuto"].value = "Continuous" if value else "Off"

    @property
    def gamma_enable(self):
        """ Gamma enabled status

        :getter: Gets gamma enabled status
        :setter: Sets gamma enabled status
        """
        return self._cam.nodemap["GammaEnable"].value

    @gamma_enable.setter
    def gamma_enable(self, value):
        self._cam.nodemap["GammaEnable"].value = True

    def init(self):
        """ Initializes the camera and ROS topics/services. """
        if not self.cam_active:
            rospy.logerr("Cannot init camera with serial {}: Camera not active!".format(self._cam_serial))
            return

        # Print device serial number
        rospy.loginfo("Device serial number: {}".format(self._cam_serial))

        # Initialize camera
        self._init_camera()

        # Create ROS publishers
        self._init_ros_publishers()

        # Create ROS services
        self._init_ros_services()

    def start(self):
        """ Starts the camera and the image acquisition. """
        if not self.cam_active:
            rospy.logerr("Cannot start camera with serial {}: Camera not active!".format(self._cam_serial))
            return

        # Start the action server
        if not self._stream:
            self._action_server.start()

        # Start image acquisition
        self._cam.start_stream(self._buff_size)

        while not rospy.is_shutdown():
            if self._stream:
                self._grab_image(publish=True)

        # Stop image acquisition
        self._cam.stop_stream()


    def _init_camera(self):
        """ Initializes the camera. """
        # Set camera image encoding to RGB8
        self._cam.nodemap["PixelFormat"].value = self._encoding["camera"]

        # Make sure trigger mode is off before setup
        self._cam.nodemap["TriggerMode"].value = "Off"

        # Set trigger to frame start
        self._cam.nodemap["TriggerSelector"].value = "FrameStart"

        # Set trigger source to software
        self._cam.nodemap["TriggerSource"].value = "Software"

        # Activate trigger mode
        self._cam.nodemap["TriggerMode"].value = "On"

        # Enable stream auto negotiate packet size
        self._cam.tl_stream_nodemap["StreamAutoNegotiatePacketSize"].value = True

        # Enable stream packet resend
        self._cam.tl_stream_nodemap["StreamPacketResendEnable"].value = True

        # Enable precision time protocol (PTP)
        self._cam.nodemap["PtpEnable"].value = True
        self._cam.nodemap["PtpSlaveOnly"].value = True

        # Update camera info
        self._camera_info.width = self._cam.nodemap["Width"].value
        self._camera_info.height = self._cam.nodemap["Height"].value
        self._camera_info.binning_x = self._cam.nodemap["BinningHorizontal"].value
        self._camera_info.binning_y = self._cam.nodemap["BinningVertical"].value

    def _init_ros_publishers(self):
        """ Initializes the ROS publishers. """
        # Publish camera info
        self._pub_camera_info = rospy.Publisher(
            "{}/camera_info".format(self._topic_prefix),
            CameraInfo,
            queue_size=10
        )

        # Publish camera raw image
        self._pub_image_raw = rospy.Publisher(
            "{}/image_raw".format(self._topic_prefix),
            Image,
            queue_size=3
        )

        # If resize is set to True, publish resized image
        if self._resize:
            self._pub_image_color = rospy.Publisher(
            "{}/image_color".format(self._topic_prefix),
            Image,
            queue_size=3
        )

        # Create action server
        if not self._stream:
            self._action_server = SimpleActionServer(
                "{}/grab_images".format(self._topic_prefix),    # name
                GrabImagesAction,                               # action
                execute_cb=self.__callback_grab_images,         # callback
                auto_start=False                                # needs to be False
            )

    def _init_ros_services(self):
        """ Advertises the ROS services. """
        self._srv_get_cam_info = rospy.Service(
            "{}/get_cam_properties".format(self._topic_prefix),
            GetCamProperties,
            self.__callback_get_cam_properties
        )

        self._srv_set_exposure = rospy.Service(
            "{}/set_exposure".format(self._topic_prefix),
            SetExposure,
            self.__callback_set_exposure
        )

        self._srv_set_gain = rospy.Service(
            "{}/set_gain".format(self._topic_prefix),
            SetGain,
            self.__callback_set_gain
        )

        self._srv_set_gamma = rospy.Service(
            "{}/set_gamma".format(self._topic_prefix),
            SetGamma,
            self.__callback_set_gamma
        )

    def _grab_image(self, publish=True):
        """ Grabs an image from the camera buffer.

        :returns: image in ROS Image format
        """
        # Update camera info header
        self._camera_info.header.stamp = rospy.Time.now()
        self._camera_info.header.frame_id = self._cam_name

        for _ in range(self._buff_size):
            # Wait for camera trigger to get armed
            while not self._cam.nodemap["TriggerArmed"].value:
                continue

            # Activate camera trigger
            self._cam.nodemap["TriggerSoftware"].execute()

            # Wait for the next image
            if self._buff_size > 1:
                self._cam.wait_for_next_leader(self._buff_timeout)

        # Initialize ROS image message
        img = Image()

        # Get image buffer
        buff = self._cam.get_buffer()

        if buff.is_incomplete:
            rospy.logwarn("Device {} image incomplete".format(self._cam_serial))
        else:
            # Create ROS image message
            img.encoding = self._encoding["ros"]
            img.height = buff.height
            img.width = buff.width
            img.step = int(buff.width * (buff.bits_per_pixel / 8))
            img.data = np.array(buff.data, dtype=np.uint8).reshape(-1).tobytes()
            img.header.stamp = rospy.Time.from_sec(buff.timestamp_ns / 1e9)
            img.header.frame_id = self._cam_name

            # Publish image
            if publish:
                self._pub_image_raw.publish(img)

            # Resize the image and publish
            if self._resize:
                bridge = CvBridge()
                cv_img = bridge.imgmsg_to_cv2(img, desired_encoding=self._encoding["ros"])
                cv_res = cv2.resize(cv_img, self._resize_res)
                img = bridge.cv2_to_imgmsg(cv_res, encoding=self._encoding["ros"])
                if publish:
                    self._pub_image_color.publish(img)

        # Requeue the image buffer
        self._cam.requeue_buffer(buff)

        # Publish camera info
        if publish:
            self._pub_camera_info.publish(self._camera_info)

        # Return the image message
        return img

    def __callback_grab_images(self, goal):
        """ Callback for SimpleActionServer.

        :param goal: goal object received from action client
        :returns: result object
        """
        # Initialize result and feedback
        result = GrabImagesResult()
        feedback = GrabImagesFeedback()

        # Validate incoming goal
        result.success, num_images = utils.validate_goal(goal)

        # Continue updading result if the goal is successfully validated
        if result.success:
            # Update camera info in the result
            result.cam_info = self._camera_info

            # Cache variables
            self._cache["exposure"] = self.exposure
            self._cache["exposure_auto"] = self.exposure_auto
            self._cache["gain"] = self.gain
            self._cache["gain_auto"] = self.gain_auto
            self._cache["gamma"] = self.gamma
            self._cache["gamma_enable"] = self.gamma_enable

            for i in range(0, num_images):
                # Update camera settings using the values from goal
                if goal.exposure_given and not goal.exposure_auto:
                    self.exposure = goal.exposure_times[i]
                if goal.gain_given and not goal.gain_auto:
                    self.gain = goal.gain_values[i]
                if goal.gain_given and len(goal.gamma_values) == num_images:
                    self.gamma = goal.gamma_values[i]

                img = self._grab_image(publish=True)

                # Update result with the image
                result.images.append(img)

                # Update result with the values
                result.reached_exposure_times.append(self.exposure)
                result.reached_gain_values.append(self.gain)
                result.reached_gamma_values.append(self.gamma)

                # Update and publish feedback
                feedback.curr_nr_images_taken += 1
                self._action_server.publish_feedback(feedback)

            # Restore variables
            self.exposure = self._cache["exposure"]
            self.exposure_auto = self._cache["exposure_auto"]
            self.gain = self._cache["gain"]
            self.gain_auto = self._cache["gain_auto"]
            self.gamma = self._cache["gamma"]
            self.gamma_enable = self._cache["gamma_enable"]

        # This is required by the action server implementation
        self._action_server.set_succeeded(result)

    def __callback_get_cam_properties(self, request):
        """ Callback for GetGamProperties service.

        :param request: client request
        :returns: server response
        """
        response = GetCamPropertiesResponse()
        response.success = True
        response.current_binning_x = self.binning_x
        response.current_binning_y = self.binning_y
        response.current_exposure = self.exposure
        response.current_gain = self.gain
        response.current_gamma = self.gamma
        response.current_framerate = self.framerate
        response.gain_auto = self.gain_auto
        response.exposure_auto = self.exposure_auto
        return response

    def __callback_set_exposure(self, request):
        """ Callback for SetExposure service.

        :param request: client request
        :returns: server response
        """
        response = SetExposureResponse()
        self.exposure = request.target_exposure
        response.success = True
        response.reached_exposure = self.exposure
        return response

    def __callback_set_gain(self, request):
        """ Callback for SetGain service.

        :param request: client request
        :returns: server response
        """
        response = SetGainResponse()
        self.gain = request.target_gain
        response.success = True
        response.reached_gain = self.gain
        return response

    def __callback_set_gamma(self, request):
        """ Callback for SetGamma service.

        :param request: client request
        :returns: server response
        """
        response = SetGammaResponse()
        self.gamma = request.target_gamma
        response.success = True
        response.reached_gamma = self.gamma
        return response
