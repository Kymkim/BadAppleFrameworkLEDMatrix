import threading
import os
import moviepy.editor as mv
from moviepy.video.fx.all import crop

PANEL= ["/dev/ttyACM0","/dev/ttyACM1"]
VIDEO = "./badapple.mp4"
SPLIT_VID = ["A.mp4", "B.mp4"]
    
def play_panel_thread(name, panel, video):
    os.system("ledmatrixctl --video " + str(video) + " --serial-dev " + str(panel))

def process_video(video):

    #Frame Reduction
    vid = mv.VideoFileClip(video)
    vid = vid.set_fps(5)

    #Rotate Image
    vid = vid.rotate(90)

    #Reduce to 10:34 ratio
    target_w = 20
    target_h = 34

    target_ratio = target_w/target_h

    orig_w, orig_h = vid.size

    if (orig_w / orig_h) > target_ratio:
        new_w = int(orig_h * target_ratio)
        crop_x = (orig_w - new_w) // 2
        crop_y = 0
        vid = vid.crop(x1=crop_x, x2=crop_x + new_w)
    else:
        new_h = int(orig_w/target_ratio)
        crop_y = (orig_h - new_h)//2
        crop_x = 0
        vid = vid.crop(y1=crop_y, y2=crop_y + new_h)

    vid = vid.resize((target_w,target_h))

    #Split Into Two
    orig_w, orig_h = vid.size
    middle_x = orig_w//2
    vidA = vid.crop(x1=0, y1=0, x2=middle_x, y2=orig_h)
    vidB = vid.crop(x1=middle_x, y1=0, x2=orig_w, y2=orig_h)

    #Write Video
    vidA.write_videofile(SPLIT_VID[0], codec="mpeg4")
    vidB.write_videofile(SPLIT_VID[1], codec="mpeg4")


if __name__ == "__main__":
    process_video(VIDEO)
    threads = list()
    for index in range(2):
        x = threading.Thread(target=play_panel_thread, args=(index, PANEL[index], SPLIT_VID[index]))
        threads.append(x)
        x.start()
    for index, thread in enumerate(threads):
        thread.join()