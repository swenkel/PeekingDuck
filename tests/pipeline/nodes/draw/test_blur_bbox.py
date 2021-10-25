# Copyright 2021 AI Singapore
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Test for draw blur_bbox node
"""
import os
from pathlib import Path
import pytest
import numpy as np
import cv2
from peekingduck.pipeline.nodes.draw.blur_bbox import Node

TEST_IMAGE = ["tcar1.jpg"]
PKD_DIR = os.path.join(
    Path(__file__).parents[3]
)  # path to reach 4 file levels up from test_blur_bbox.py


@pytest.fixture(params=TEST_IMAGE)
def test_image(request):
    test_img_dir = os.path.join(PKD_DIR, "..", "images", "testing")

    yield os.path.join(test_img_dir, request.param)


@pytest.fixture
def draw_blur_node():
    node = Node({"input": ["bboxes", "img", "bbox_labels"], "output": ["img"],"blur_kernel_size": 30})
    return node


class TestBlur:
    def test_no_bbox(self, draw_blur_node, test_image):
        original_img = cv2.imread(test_image)
        output_img = original_img.copy()

        input = {"bboxes": [], "img": output_img, "bbox_labels": []}

        draw_blur_node.run(input)
        np.testing.assert_equal(original_img, output_img)

    def test_single_bbox(self, draw_blur_node, test_image):

        original_img = cv2.imread(test_image)
        frameHeight = original_img.shape[0]
        frameWidth = original_img.shape[1]
        x1, x2 = int(0.4 * frameWidth), int(0.6 * frameWidth)
        y1, y2 = int(0.6 * frameHeight), int(0.7 * frameHeight)
        original_bbox_bounded_area = original_img[y1:y2, x1:x2, :]

        output_img = original_img.copy()
        input = {
            # x1,y1,x2,y2
            "bboxes": [np.asarray([0.4, 0.6, 0.6, 0.7])],
            "img": output_img,
            "bbox_labels": ["LP"],
        }

        draw_blur_node.run(input)
        output_bbox_bounded_area = output_img[y1:y2, x1:x2, :]

        # does not fail if the area of image are different
        # after applying blurring
        np.testing.assert_raises(
            AssertionError,
            np.testing.assert_array_equal,
            original_bbox_bounded_area,
            output_bbox_bounded_area,
        )

    def test_multiple_bbox(self, draw_blur_node, test_image):
        original_img = cv2.imread(test_image)
        frameHeight = original_img.shape[0]
        frameWidth = original_img.shape[1]

        output_img = original_img.copy()

        input = {
            # x1,y1,x2,y2
            "bboxes": [
                np.asarray([0.4, 0.6, 0.6, 0.7]),
                np.asarray([0.2, 0.1, 0.4, 0.2]),
            ],
            "img": output_img,
            "bbox_labels": ["LP"],
        }
        draw_blur_node.run(input)
        for bbox in input["bboxes"]:
            x1, y1, x2, y2 = bbox
            x1, x2 = int(x1 * frameWidth), int(x2 * frameWidth)
            y1, y2 = int(y1 * frameHeight), int(y2 * frameHeight)

            original_bbox_bounded_area = original_img[y1:y2, x1:x2, :]
            output_bbox_bounded_area = output_img[y1:y2, x1:x2, :]

            # test each bbox the area is the pixel values diff
            # does not fail if the area of image are different
            # after applying blurring
            np.testing.assert_raises(
                AssertionError,
                np.testing.assert_array_equal,
                original_bbox_bounded_area,
                output_bbox_bounded_area,
            )
