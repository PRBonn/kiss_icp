# MIT License
#
# Copyright (c) 2023 Ignacio Vizzo, Tiziano Guadagnino, Benedikt Mersch, Cyrill
# Stachniss.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import sys


class McapDataloader:
    def __init__(self, data_dir: str, topic: str, *_, **__):
        # Conditional imports to avoid injecting dependencies for non mcap users
        try:
            from mcap_ros2.reader import read_ros2_messages
        except ImportError as e:
            raise ImportError("mcap_ros2 not installed: 'pip install mcap-ros2-support'") from e

        try:
            import rosbag2_py
        except ImportError as e:
            raise ImportError(
                "rosbag2_py not installed: 'sudo apt-get install ros-$ROS_DISTRO-rosbag2 ros-$ROS_DISTRO-rosbag2-storage-mcap'"
            ) from e
        from kiss_icp.tools.point_cloud2 import read_point_cloud

        # we expect `data_dir` param to be a path to the .mcap file, so rename for clarity
        assert os.path.isfile(data_dir), "mcap dataloader expects an existing MCAP file"
        mcap_file = str(data_dir)
        self.data_dir = os.path.dirname(data_dir)
        self.bag = rosbag2_py.SequentialReader()
        self.bag.open(
            rosbag2_py.StorageOptions(uri=mcap_file, storage_id="mcap"),
            rosbag2_py.ConverterOptions(
                input_serialization_format="cdr", output_serialization_format="cdr"
            ),
        )
        self.topic = self.check_topic(topic)
        self.msgs = read_ros2_messages(mcap_file, topics=topic)
        self.read_point_cloud = read_point_cloud
        self.use_global_visualizer = True

    def __del__(self):
        if hasattr(self, "bag"):
            del self.bag

    def __getitem__(self, idx):
        msg = next(self.msgs).ros_msg
        return self.read_point_cloud(msg)

    def __len__(self):
        # TODO: get_metadata is not available on ros-humble. How to get the msg_count?
        return -1

    def check_topic(self, topic: str) -> str:
        # when user specified the topic don't check
        if topic:
            return topic

        # Extract all PointCloud2 msg topics from the bagfile
        point_cloud_topics = [
            topic_metadata
            for topic_metadata in self.bag.get_all_topics_and_types()
            if topic_metadata.type == "sensor_msgs/msg/PointCloud2"
        ]
        # this is the string topic name, go figure out
        if len(point_cloud_topics) == 1:
            return point_cloud_topics[0]
        # In any other case we consider this an error
        if len(point_cloud_topics) == 0:
            print("[ERROR] Your mcap does not contain any sensor_msgs/msg/PointCloud2 topic")
        if len(point_cloud_topics) > 1:
            print("Multiple sensor_msgs/msg/PointCloud2 topics available.")
            print("Please provide one of the following topics with the --topic flag")
            for topic_metadata in point_cloud_topics:
                print(50 * "-")
                print(f"Topic: {topic_metadata.name}")
                print(f"Type : {topic_metadata.type}")
            print(50 * "-")
        sys.exit(1)
