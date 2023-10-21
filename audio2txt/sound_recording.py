import sys

import sounddevice as sd
import numpy as np
import keyboard

# 定义录音参数
sample_rate = 16000  # 采样率
duration = 30.0  # 录音时长（秒）

# 初始化录音状态
recording = False
audio_data = []


# 检测空格键按下事件
def key_pressed(e):
    global recording
    global audio_data

    if e.event_type == keyboard.KEY_DOWN:
        if e.name == 'space':
            if not recording:
                print("开始录音...")
                audio_data = []
                recording = True
                sd.default.samplerate = sample_rate
                sd.default.channels = 1
                sd.default.dtype = np.int16
                sd.default.blocksize = 1024
                sd.default.latency = 'low'
                sd.InputStream(callback=audio_callback).start()
            else:
                print("停止录音...")
                recording = False
                sd.stop()
                save_audio(audio_data, sample_rate)


# 录音回调函数
def audio_callback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    if recording:
        audio_data.extend(indata)


# 保存录音为PCM文件
def save_audio(data, sample_rate):
    audio_data = np.array(data)
    file_name = "recorded_audio.pcm"
    with open(file_name, 'wb') as f:
        audio_data.tofile(f)
    print(f"录音已保存为 {file_name}")
    exit()


# 监听空格键事件
keyboard.hook(key_pressed)

# 进入事件监听循环
keyboard.wait('esc')  # 监听退出事件
