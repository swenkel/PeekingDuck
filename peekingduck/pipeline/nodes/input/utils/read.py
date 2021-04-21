from threading import Thread, Lock

import cv2

from peekingduck.pipeline.nodes.input.utils.preprocess import set_res, mirror


class VideoThread:
    '''
    Videos will be threaded to prevent I/O blocking from affecting FPS.
    '''

    def __init__(self, res, input_source, mirror_image):
        self.stream = cv2.VideoCapture(input_source)
        self.mirror = mirror_image
        if not self.stream.isOpened():
            raise ValueError("Camera or video input not detected: %s" % input_source)

        width, height = res['width'], res['height']
        set_res(self.stream, width, height)
        self._lock = Lock()
        thread = Thread(target=self._reading_thread, args=(), daemon=True)
        thread.start()
    
    def __del__(self):
        self.stream.release()

    def _reading_thread(self):
        '''
        A thread that continuously polls the camera for frames.
        '''
        while True:
            _, self.frame = self.stream.read()

    def read_frame(self):
        '''
        Reads the frame.
        '''
        self._lock.acquire()
        if self.frame is not None:
            frame = self.frame.copy()
            self._lock.release()
            if self.mirror:
                frame = mirror(frame)
            return True, frame

        self._lock.release()
        return False, None


class VideoNoThread:
    '''
    No threading to deal with recorded videos and images.
    '''

    def __init__(self, res, input_source, mirror_image):
        self.stream = cv2.VideoCapture(input_source)
        self.mirror = mirror_image
        if not self.stream.isOpened():
            raise ValueError("Video or image path incorrect: %s" % input_source)

        width, height = res['width'], res['height']
        set_res(self.stream, width, height)
    
    def __del__(self):
        self.stream.release()

    def read_frame(self):
        '''
        Reads the frame.
        '''
        return self.stream.read()
