import cv2 as cv
import curses as cr
import threading
from queue import Queue

def read_frames(video, frame_queue, stop_event):
    while not stop_event.is_set():
        ret, frame = video.read()
        if not ret:
            stop_event.set()
            break
        frame_queue.put(frame)

def process_frame(frame, max_row, max_col):
    frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    frame = cv.resize(frame, (max_col, max_row), interpolation=cv.INTER_NEAREST)
    return frame

def main(stdscr):
    video = cv.VideoCapture('BadApple.mp4')
    cr.start_color()
    cr.init_pair(1, cr.COLOR_WHITE, cr.COLOR_BLACK)

    max_row, max_col = stdscr.getmaxyx()
    stdscr.clear()
    stdscr.nodelay(True)

    frame_queue = Queue(maxsize=8)
    stop_event = threading.Event()

    read_thread = threading.Thread(target=read_frames, args=(video, frame_queue, stop_event))
    read_thread.start()

    while not stop_event.is_set():
        if not frame_queue.empty():
            frame = frame_queue.get()
            frame = process_frame(frame, max_row, max_col)
            
            screen_buf = []
            for y in range(max_row):
                row_str = ""
                for x in range(max_col):
                    row_str += " " if frame[y, x] > 127 else "█"
                screen_buf.append(row_str)
            
            for y, row_str in enumerate(screen_buf):
                try:
                    stdscr.addstr(y, 0, row_str, cr.color_pair(1))
                except cr.error:
                    pass

            stdscr.refresh()

    stop_event.set()
    read_thread.join()
    video.release()
    stdscr.getch()
    cv.destroyAllWindows()

if __name__ == "__main__":
    cr.wrapper(main)
