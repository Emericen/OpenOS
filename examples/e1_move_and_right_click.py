import time
import cv2
from openos import OpenOS


def show_frame(frame, video_writer=None):
    frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
    cv2.imshow("Frame", frame)
    cv2.waitKey(1)
    if video_writer is not None:
        video_writer.write(frame)


if __name__ == "__main__":
    ubuntu = OpenOS.create(debug=True)
    ubuntu.start(headless=True)

    # Initialize video writer
    height, width = ubuntu.read_frame().shape[:2]
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    video_writer = cv2.VideoWriter("output.mp4", fourcc, 30.0, (width, height))

    print("Start")

    # Move mouse to upper left smoothly
    STEP_SIZE = 3
    for i in range(200):
        frame = ubuntu.read_frame()
        show_frame(frame, video_writer)
        ubuntu.move_mouse(-STEP_SIZE, -STEP_SIZE)
        time.sleep(0.01)

    # Perform a right click
    ubuntu.mouse_button_down("RIGHT")
    time.sleep(0.1)  # don't click too fast
    ubuntu.mouse_button_up("RIGHT")
    time.sleep(0.1)  # don't read frame too soon so we see drop down menu
    show_frame(ubuntu.read_frame(), video_writer)

    print("Done")

    # Release video writer
    video_writer.release()
    cv2.destroyAllWindows()
    ubuntu.stop()
